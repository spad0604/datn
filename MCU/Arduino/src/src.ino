/*
 * ============================================================================
 * MCU_CONTROL_ACCESS - Arduino Nano Firmware
 * ============================================================================
 * Handles access control for the delivery robot:
 *   - DC lock relay (compartment unlock on PIN entry)
 *   - Buzzer relay (feedback tones)
 *   - Turn-signal LEDs (left / right)
 *   - 16x2 I2C LCD (user prompts, PIN masking)
 *   - 4x4 keypad via PCF8574 (PIN input)
 *
 * Serial protocol with Raspberry Pi (9600 baud, '\n' terminated):
 *   Pi -> Arduino:
 *     "UNLOCK <8-digit-pin>"  Set expected PIN, prompt user on LCD
 *     "LCD|<line1>|<line2>"   Push 2x16 text to the idle LCD screen
 *                             (e.g. "LCD|DI LAY DON|#42")
 *                             Fields truncated to 16 chars. Ignored while
 *                             the user is entering a PIN; applied next idle.
 *     "L_ON"                  Blink LEFT turn-signal LED (refreshed while on)
 *     "R_ON"                  Blink RIGHT turn-signal LED (refreshed while on)
 *   Arduino -> Pi:
 *     "OK"                    Sent after the user enters the correct PIN
 *                             and the compartment has been unlocked.
 *
 * Pin map (from schematic MCU_CONTROL_ACCESS):
 *   D2  -> LOCK_DC  (active-LOW optocoupler/relay -> DC lock)
 *   D3  -> BUZZ     (active-LOW optocoupler/relay -> buzzer)
 *   D4  -> R_LED    (right turn signal, via 500 ohm)
 *   D5  -> L_LED    (left turn signal, via 500 ohm)
 *   A7  -> SWITCH   (P6..P9 buttons through resistor ladder) [optional]
 *   SDA/SCL (A4/A5) -> LCD I2C (0x27) + PCF8574 keypad (0x20)
 *
 * Required libraries (Arduino Library Manager):
 *   - LiquidCrystal_I2C
 *   - Keypad          (Mark Stanley / Alexander Brevig)
 *   - Keypad_I2C      (Joe Young, https://github.com/joeyoung/arduino_keypads)
 * ============================================================================
 */

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "Keypad.h"
#include "Keypad_I2C.h"

// ---------------- Pin assignments ----------------
#define PIN_LOCK_DC   2     // Relay for DC lock (active LOW via PC817)
#define PIN_BUZZ      3     // Relay for buzzer  (active LOW via PC817)
#define PIN_R_LED     4     // Right turn signal LED
#define PIN_L_LED     5     // Left turn signal LED
#define PIN_SWITCH    A7    // Resistor-ladder buttons P6..P9

// Relays on the schematic are driven through PC817 optocouplers.
// Polarity observed on the real board: GPIO HIGH energizes the relay.
// (Flip these two defines if a rebuild of the board reverts to active-LOW.)
#define RELAY_ON      HIGH
#define RELAY_OFF     LOW

// Turn-signal LEDs observed on the real board: GPIO LOW lights the LED
// (driven via PNP / common-anode wiring). Flip if the board is rebuilt.
#define LED_ON        HIGH
#define LED_OFF       LOW

// ---------------- I2C addresses ----------------
#define LCD_ADDR      0x27
#define KEYPAD_ADDR   0x20

// ---------------- Timing ----------------
const unsigned long UNLOCK_DURATION_MS  = 4000;   // lock open time
const unsigned long SIGNAL_DURATION_MS  = 1500;   // how long turn signal keeps blinking after last command
const unsigned long SIGNAL_BLINK_MS     = 400;    // blink half-period (on/off duration)
const unsigned long BUZZ_SHORT_MS       = 120;
const unsigned long PIN_TIMEOUT_MS      = 60000;  // 60 s to enter PIN
const uint8_t       PIN_LENGTH          = 8;      // BE generates 8-digit PINs

// ---------------- LCD ----------------
LiquidCrystal_I2C lcd(LCD_ADDR, 16, 2);

// ---------------- Keypad (4x4 via PCF8574) ----------------
const byte KP_ROWS = 4;
const byte KP_COLS = 4;
char keymap[KP_ROWS][KP_COLS] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};
byte rowPins[KP_ROWS] = {0, 1, 2, 3};   // PCF8574 P0..P3
byte colPins[KP_COLS] = {4, 5, 6, 7};   // PCF8574 P4..P7
Keypad_I2C keypad(makeKeymap(keymap), rowPins, colPins,
                  KP_ROWS, KP_COLS, KEYPAD_ADDR, PCF8574);

// ---------------- State ----------------
String rxBuffer   = "";          // incoming serial line buffer
String expectedPin = "";         // PIN pushed from Pi, empty = no active session
String enteredPin  = "";

enum AccessState {
  IDLE_STATE,
  WAIT_PIN,
};
AccessState state = IDLE_STATE;

unsigned long pinStartedAt = 0;

unsigned long lockOffAt   = 0;   // when to release LOCK_DC
unsigned long buzzOffAt   = 0;   // when to stop buzzer
unsigned long lLedOffAt   = 0;   // when to stop blinking L_LED
unsigned long rLedOffAt   = 0;   // when to stop blinking R_LED
unsigned long lLedToggleAt = 0;  // next time to flip L_LED state
unsigned long rLedToggleAt = 0;  // next time to flip R_LED state
bool lLedOn = false;
bool rLedOn = false;

// Idle-screen content, pushed from the Pi via "LCD|<line1>|<line2>".
// Defaults shown at boot until the Pi sends an update.
String lcdLine1 = "Robot Delivery";
String lcdLine2 = "Ready...";

// ---------------- Helpers ----------------
void setLock(bool open) {
  digitalWrite(PIN_LOCK_DC, open ? RELAY_ON : RELAY_OFF);
}

void setBuzz(bool on) {
  // Buzzer temporarily disabled.
  (void)on;
  digitalWrite(PIN_BUZZ, RELAY_OFF);
}

void beep(unsigned long ms) {
  // Buzzer temporarily disabled; keep signature so callers compile.
  (void)ms;
}

void showIdleScreen() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(lcdLine1.substring(0, 16));
  lcd.setCursor(0, 1);
  lcd.print(lcdLine2.substring(0, 16));
}

void showPinPrompt() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Enter PIN:");
  lcd.setCursor(0, 1);
  // masked entry, rendered in loop as user types
}

void renderMaskedPin() {
  lcd.setCursor(0, 1);
  for (uint8_t i = 0; i < PIN_LENGTH; i++) {
    if (i < enteredPin.length())  lcd.print('*');
    else                          lcd.print('_');
  }
  // clear any trailing chars from prior state
  for (uint8_t i = PIN_LENGTH; i < 16; i++) lcd.print(' ');
}

void showMessage(const char *l1, const char *l2, unsigned long holdMs) {
  lcd.clear();
  lcd.setCursor(0, 0); lcd.print(l1);
  lcd.setCursor(0, 1); lcd.print(l2);
  delay(holdMs);
}

void resetSession() {
  expectedPin = "";
  enteredPin  = "";
  state = IDLE_STATE;
  showIdleScreen();
}

// ---------------- Command handlers ----------------
void handleUnlockCmd(const String &pin) {
  if (pin.length() == 0) return;
  expectedPin  = pin;
  enteredPin   = "";
  state        = WAIT_PIN;
  pinStartedAt = millis();
  beep(BUZZ_SHORT_MS);
  showPinPrompt();
  renderMaskedPin();
}

void handleLeftSignal() {
  // Start / refresh left-turn blink window.
  // If already blinking, just extend the off-time so repeated L_ON messages
  // from the Pi keep the signal going without causing a visible glitch.
  if (lLedOffAt == 0) {
    lLedOn = true;
    digitalWrite(PIN_L_LED, LED_ON);
    lLedToggleAt = millis() + SIGNAL_BLINK_MS;
  }
  lLedOffAt = millis() + SIGNAL_DURATION_MS;
}

void handleRightSignal() {
  if (rLedOffAt == 0) {
    rLedOn = true;
    digitalWrite(PIN_R_LED, LED_ON);
    rLedToggleAt = millis() + SIGNAL_BLINK_MS;
  }
  rLedOffAt = millis() + SIGNAL_DURATION_MS;
}

void handleLcdCmd(const String &payload) {
  // payload = "<line1>|<line2>"  (either part may be empty)
  int sep = payload.indexOf('|');
  String l1 = (sep >= 0) ? payload.substring(0, sep) : payload;
  String l2 = (sep >= 0) ? payload.substring(sep + 1) : "";

  if (l1.length() > 16) l1 = l1.substring(0, 16);
  if (l2.length() > 16) l2 = l2.substring(0, 16);

  lcdLine1 = l1;
  lcdLine2 = l2;

  // Only refresh the screen if we are not in the middle of PIN entry,
  // so we don't clobber the "Enter PIN:" prompt.
  if (state == IDLE_STATE) {
    showIdleScreen();
  }
}

void processCommand(String cmd) {
  cmd.trim();
  if (cmd.length() == 0) return;

  if (cmd.startsWith("UNLOCK")) {
    int sp = cmd.indexOf(' ');
    String pin = (sp > 0) ? cmd.substring(sp + 1) : "";
    pin.trim();
    handleUnlockCmd(pin);
  } else if (cmd.startsWith("LCD|")) {
    handleLcdCmd(cmd.substring(4));
  } else if (cmd == "L_ON") {
    handleLeftSignal();
  } else if (cmd == "R_ON") {
    handleRightSignal();
  }
  // silently ignore unknown commands
}

// ---------------- Serial RX ----------------
void readSerial() {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n' || c == '\r') {
      if (rxBuffer.length() > 0) {
        processCommand(rxBuffer);
        rxBuffer = "";
      }
    } else {
      rxBuffer += c;
      if (rxBuffer.length() > 64) rxBuffer = "";  // overflow guard
    }
  }
}

// ---------------- Keypad handling ----------------
void handleKey(char k) {
  if (state != WAIT_PIN) return;

  if (k >= '0' && k <= '9') {
    if (enteredPin.length() < PIN_LENGTH) {
      enteredPin += k;
      beep(40);
      renderMaskedPin();
    }
    if (enteredPin.length() == PIN_LENGTH) {
      if (enteredPin == expectedPin) {
        // success: unlock and notify Pi
        showMessage("PIN OK", "Unlocking...", 800);
        setLock(true);
        lockOffAt = millis() + UNLOCK_DURATION_MS;
        beep(500);
        Serial.println("OK");
        resetSession();
      } else {
        showMessage("Wrong PIN", "Try again", 1200);
        // long error beep
        setBuzz(true); delay(600); setBuzz(false);
        enteredPin = "";
        showPinPrompt();
        renderMaskedPin();
      }
    }
  } else if (k == '*') {
    // backspace
    if (enteredPin.length() > 0) {
      enteredPin.remove(enteredPin.length() - 1);
      beep(30);
      renderMaskedPin();
    }
  } else if (k == '#') {
    // clear all
    enteredPin = "";
    beep(30);
    renderMaskedPin();
  }
  // A/B/C/D ignored
}

// ---------------- Periodic housekeeping ----------------
void tickTimers() {
  unsigned long now = millis();

  if (lockOffAt && (long)(now - lockOffAt) >= 0) {
    setLock(false);
    lockOffAt = 0;
  }
  if (buzzOffAt && (long)(now - buzzOffAt) >= 0) {
    setBuzz(false);
    buzzOffAt = 0;
  }
  // Turn-signal blinking: toggle every SIGNAL_BLINK_MS, stop at lLedOffAt/rLedOffAt.
  if (lLedOffAt) {
    if ((long)(now - lLedOffAt) >= 0) {
      digitalWrite(PIN_L_LED, LED_OFF);
      lLedOn = false;
      lLedOffAt = 0;
      lLedToggleAt = 0;
    } else if ((long)(now - lLedToggleAt) >= 0) {
      lLedOn = !lLedOn;
      digitalWrite(PIN_L_LED, lLedOn ? LED_ON : LED_OFF);
      lLedToggleAt = now + SIGNAL_BLINK_MS;
    }
  }
  if (rLedOffAt) {
    if ((long)(now - rLedOffAt) >= 0) {
      digitalWrite(PIN_R_LED, LED_OFF);
      rLedOn = false;
      rLedOffAt = 0;
      rLedToggleAt = 0;
    } else if ((long)(now - rLedToggleAt) >= 0) {
      rLedOn = !rLedOn;
      digitalWrite(PIN_R_LED, rLedOn ? LED_ON : LED_OFF);
      rLedToggleAt = now + SIGNAL_BLINK_MS;
    }
  }

  // PIN entry timeout
  if (state == WAIT_PIN && (now - pinStartedAt) > PIN_TIMEOUT_MS) {
    showMessage("PIN timeout", "Cancelled", 1000);
    resetSession();
  }
}

// ---------------- Setup / Loop ----------------
void setup() {
  // Set outputs to inactive *before* enabling as OUTPUT, to avoid a brief
  // active pulse at boot while the Arduino bootloader runs.
  digitalWrite(PIN_LOCK_DC, RELAY_OFF);
  digitalWrite(PIN_BUZZ,    RELAY_OFF);
  digitalWrite(PIN_L_LED,   LED_OFF);
  digitalWrite(PIN_R_LED,   LED_OFF);

  pinMode(PIN_LOCK_DC, OUTPUT);
  pinMode(PIN_BUZZ,    OUTPUT);
  pinMode(PIN_L_LED,   OUTPUT);
  pinMode(PIN_R_LED,   OUTPUT);

  setLock(false);
  setBuzz(false);
  digitalWrite(PIN_L_LED, LED_OFF);
  digitalWrite(PIN_R_LED, LED_OFF);

  Serial.begin(9600);

  Wire.begin();
  lcd.init();
  lcd.backlight();
  keypad.begin();

  // startup blip
  beep(100);
  showIdleScreen();
}

void loop() {
  readSerial();

  char k = keypad.getKey();
  if (k) handleKey(k);

  tickTimers();
}
