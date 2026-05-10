#!/usr/bin/env python3
"""
Standalone reader for the SIMCom SIM7600X GPS over UART.

Turns on the GNSS engine, polls AT+CGPSINFO (or streams NMEA via AT+CGPSINFOCFG),
parses fix data and prints latitude, longitude, altitude, speed, course and UTC
time. No ROS dependency.

Dependencies:
    pip install pyserial

Wiring (SIM7600X HAT over USB/UART):
    Default USB-to-serial AT port on Raspberry Pi: /dev/ttyUSB2
    Default GPIO UART baud: 115200

Usage:
    python3 test_sim7600.py
    python3 test_sim7600.py --port /dev/ttyUSB2 --baud 115200 --rate 1
    python3 test_sim7600.py --mode nmea
"""

import argparse
import signal
import sys
import time

try:
    import serial
except ImportError:
    sys.stderr.write(
        "Missing dependency 'pyserial'. Install it with:\n"
        "    pip install pyserial\n"
    )
    sys.exit(1)


class SIM7600:
    def __init__(self, port="/dev/ttyUSB2", baud=115200, timeout=1.0):
        # SIM7600 USB-CDC driver on Raspberry Pi often rejects TIOCMBIS
        # (set DTR/RTS), causing pyserial to raise BrokenPipeError on open.
        # Open with dsrdtr=True / rtscts=False so pyserial doesn't try to
        # touch those lines, and fall back to a manual fd open if it still
        # fails.
        try:
            self.ser = serial.Serial(
                port, baud, timeout=timeout,
                dsrdtr=True, rtscts=False, xonxoff=False,
            )
        except (BrokenPipeError, OSError) as e:
            # Build the Serial object without opening, disable DTR/RTS
            # toggling, then open manually.
            self.ser = serial.Serial()
            self.ser.port = port
            self.ser.baudrate = baud
            self.ser.timeout = timeout
            self.ser.dsrdtr = True
            self.ser.rtscts = False
            self.ser.xonxoff = False
            try:
                self.ser.dtr = None  # tell pyserial: don't set DTR
                self.ser.rts = None
            except Exception:
                pass
            try:
                self.ser.open()
            except (BrokenPipeError, OSError):
                # Last resort: ignore the broken pipe from DTR set; the port
                # is usable for read/write even though the ioctl failed.
                if not self.ser.is_open:
                    raise e
        time.sleep(0.1)
        try:
            self.ser.reset_input_buffer()
        except Exception:
            pass

    def send(self, cmd, wait=1.0, expect="OK"):
        """Send an AT command, collect response until 'expect' or timeout."""
        self.ser.reset_input_buffer()
        self.ser.write((cmd + "\r\n").encode("ascii", errors="ignore"))
        deadline = time.time() + wait
        buf = ""
        while time.time() < deadline:
            chunk = self.ser.read(self.ser.in_waiting or 1)
            if chunk:
                buf += chunk.decode("utf-8", errors="ignore")
                if expect and (expect in buf or "ERROR" in buf):
                    break
            else:
                time.sleep(0.02)
        return buf

    def gps_power(self, on=True):
        """Start/stop the GNSS session."""
        resp = self.send("AT+CGPS?", wait=0.5)
        want = "1" if on else "0"
        if f"+CGPS: {want}" in resp:
            return True
        return "OK" in self.send(f"AT+CGPS={'1' if on else '0'}", wait=2.0)

    def cgpsinfo(self):
        """Poll a one-shot fix via AT+CGPSINFO."""
        return self.send("AT+CGPSINFO", wait=1.0)

    def stream_nmea(self, mask=0x00FF):
        """Enable NMEA streaming over the same AT port."""
        self.send(f"AT+CGPSINFOCFG={1},{mask}", wait=0.5)

    def close(self):
        try:
            self.ser.close()
        except Exception:
            pass


# --- CGPSINFO parser -----------------------------------------------------
# Response format:
# +CGPSINFO: <lat>,<N/S>,<lon>,<E/W>,<date>,<UTC time>,<alt>,<speed>,<course>
def _to_decimal(coord, hemi):
    """Convert NMEA ddmm.mmmm / dddmm.mmmm to decimal degrees."""
    if not coord or not hemi:
        return None
    try:
        dot = coord.index(".")
    except ValueError:
        return None
    # Degrees are the leading 2 (lat) or 3 (lon) digits before the 2-digit minutes.
    deg_len = dot - 2
    if deg_len <= 0:
        return None
    deg = int(coord[:deg_len])
    minutes = float(coord[deg_len:])
    val = deg + minutes / 60.0
    if hemi in ("S", "W"):
        val = -val
    return val


def parse_cgpsinfo(line):
    """Return a dict with fix fields, or None if no fix."""
    idx = line.find("+CGPSINFO:")
    if idx < 0:
        return None
    payload = line[idx + len("+CGPSINFO:"):].splitlines()[0].strip()
    parts = [p.strip() for p in payload.split(",")]
    if len(parts) < 9 or not parts[0]:
        return None  # empty => no fix yet
    lat = _to_decimal(parts[0], parts[1])
    lon = _to_decimal(parts[2], parts[3])
    date = parts[4]   # ddmmyy
    utc = parts[5]    # hhmmss.s
    alt = float(parts[6]) if parts[6] else None
    speed = float(parts[7]) if parts[7] else None  # knots
    course = float(parts[8]) if parts[8] else None  # degrees

    utc_fmt = None
    if date and utc and len(date) == 6 and len(utc) >= 6:
        utc_fmt = f"20{date[4:6]}-{date[2:4]}-{date[0:2]} {utc[0:2]}:{utc[2:4]}:{utc[4:]}"

    return {
        "lat": lat,
        "lon": lon,
        "alt_m": alt,
        "speed_knots": speed,
        "speed_mps": speed * 0.514444 if speed is not None else None,
        "course_deg": course,
        "utc": utc_fmt,
    }


def format_fix(fix):
    if fix is None:
        return "No fix yet (waiting for satellites)..."
    lat = f"{fix['lat']:.7f}" if fix["lat"] is not None else "---"
    lon = f"{fix['lon']:.7f}" if fix["lon"] is not None else "---"
    alt = f"{fix['alt_m']:.1f}m" if fix["alt_m"] is not None else "---"
    spd = f"{fix['speed_mps']:.2f} m/s" if fix["speed_mps"] is not None else "---"
    crs = f"{fix['course_deg']:.1f} deg" if fix["course_deg"] is not None else "---"
    utc = fix["utc"] or "---"
    return f"UTC={utc} | Lat={lat} Lon={lon} Alt={alt} | Speed={spd} Course={crs}"


# --- NMEA parsers (for ports that stream GGA/RMC directly, e.g. /dev/ttyUSB3) ---
def _nmea_ok(sentence):
    """Verify NMEA checksum. Returns the payload without $ and *HH if valid."""
    if not sentence.startswith("$") or "*" not in sentence:
        return None
    body, _, chk = sentence[1:].partition("*")
    try:
        want = int(chk[:2], 16)
    except ValueError:
        return None
    got = 0
    for ch in body:
        got ^= ord(ch)
    return body if got == want else None


def parse_gga(sentence):
    """$xxGGA,hhmmss.ss,lat,N/S,lon,E/W,fix,sats,hdop,alt,M,...*CS"""
    body = _nmea_ok(sentence)
    if not body:
        return None
    f = body.split(",")
    if len(f) < 10 or f[6] in ("", "0"):
        return None
    utc_raw = f[1]
    utc_fmt = None
    if len(utc_raw) >= 6:
        utc_fmt = f"{utc_raw[0:2]}:{utc_raw[2:4]}:{utc_raw[4:]} UTC"
    lat = _to_decimal(f[2], f[3])
    lon = _to_decimal(f[4], f[5])
    alt = float(f[9]) if f[9] else None
    return {
        "lat": lat, "lon": lon, "alt_m": alt,
        "speed_knots": None, "speed_mps": None, "course_deg": None,
        "utc": utc_fmt,
    }


def parse_rmc(sentence):
    """$xxRMC,hhmmss.ss,A,lat,N/S,lon,E/W,speed_kn,course,ddmmyy,...*CS"""
    body = _nmea_ok(sentence)
    if not body:
        return None
    f = body.split(",")
    if len(f) < 10 or f[2] != "A":
        return None
    utc_raw = f[1]
    date_raw = f[9]
    utc_fmt = None
    if len(date_raw) == 6 and len(utc_raw) >= 6:
        utc_fmt = (f"20{date_raw[4:6]}-{date_raw[2:4]}-{date_raw[0:2]} "
                   f"{utc_raw[0:2]}:{utc_raw[2:4]}:{utc_raw[4:]}")
    lat = _to_decimal(f[3], f[4])
    lon = _to_decimal(f[5], f[6])
    speed = float(f[7]) if f[7] else None
    course = float(f[8]) if f[8] else None
    return {
        "lat": lat, "lon": lon, "alt_m": None,
        "speed_knots": speed,
        "speed_mps": speed * 0.514444 if speed is not None else None,
        "course_deg": course,
        "utc": utc_fmt,
    }


def run_nmea_parsed(sim, rate):
    """Passive listener: port is already streaming NMEA (typical of /dev/ttyUSB3).
    We just read lines, parse GGA + RMC, merge, and print at the given rate.
    """
    print("Listening to NMEA stream (passive, no AT commands). Ctrl+C to stop.\n")

    running = {"flag": True}

    def stop(*_):
        running["flag"] = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    period = 1.0 / max(rate, 0.1)
    last_print = 0.0
    latest = None
    buf = b""

    while running["flag"]:
        chunk = sim.ser.read(sim.ser.in_waiting or 1)
        if chunk:
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                text = line.decode("utf-8", errors="ignore").strip()
                if not text.startswith("$"):
                    continue
                fix = None
                if "GGA" in text[:6]:
                    fix = parse_gga(text)
                elif "RMC" in text[:6]:
                    fix = parse_rmc(text)
                if fix is None:
                    continue
                if latest is None:
                    latest = fix
                else:
                    for k, v in fix.items():
                        if v is not None:
                            latest[k] = v

        now = time.time()
        if now - last_print >= period:
            stamp = time.strftime("%H:%M:%S")
            print(f"[{stamp}] {format_fix(latest)}")
            last_print = now


def run_polling(sim, rate):
    print("Enabling GNSS engine (AT+CGPS=1)...")
    if not sim.gps_power(True):
        print("Warning: could not confirm CGPS=1 response. Continuing anyway.")
    print(f"Polling AT+CGPSINFO at {rate} Hz. Press Ctrl+C to stop.\n")

    period = 1.0 / max(rate, 0.1)
    running = {"flag": True}

    def stop(*_):
        running["flag"] = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    while running["flag"]:
        t0 = time.time()
        resp = sim.cgpsinfo()
        fix = parse_cgpsinfo(resp)
        stamp = time.strftime("%H:%M:%S")
        print(f"[{stamp}] {format_fix(fix)}")

        sleep_for = period - (time.time() - t0)
        if sleep_for > 0:
            time.sleep(sleep_for)


def run_nmea(sim):
    print("Enabling GNSS engine (AT+CGPS=1) + NMEA streaming...")
    sim.gps_power(True)
    sim.stream_nmea(0x00FF)
    print("Streaming NMEA sentences. Press Ctrl+C to stop.\n")

    running = {"flag": True}

    def stop(*_):
        running["flag"] = False

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    buf = b""
    while running["flag"]:
        chunk = sim.ser.read(sim.ser.in_waiting or 1)
        if not chunk:
            continue
        buf += chunk
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            text = line.decode("utf-8", errors="ignore").strip()
            if text.startswith("$"):
                print(text)


def main():
    ap = argparse.ArgumentParser(description="SIM7600X GPS standalone test reader.")
    ap.add_argument("--port", default="/dev/ttyUSB2",
                    help="Serial port. AT-capable on SIM7600 USB HAT is usually "
                         "/dev/ttyUSB2; the raw NMEA stream comes out of /dev/ttyUSB3.")
    ap.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    ap.add_argument("--rate", type=float, default=1.0, help="Print/poll rate in Hz")
    ap.add_argument(
        "--mode",
        choices=("auto", "cgpsinfo", "nmea", "nmea_parsed"),
        default="auto",
        help="auto: probe AT, use cgpsinfo if supported, else nmea_parsed (default). "
             "cgpsinfo: poll AT+CGPSINFO (needs AT port). "
             "nmea: stream raw NMEA lines. "
             "nmea_parsed: read NMEA stream and print parsed lat/lon.",
    )
    args = ap.parse_args()

    print(f"Opening {args.port} @ {args.baud}...")
    sim = SIM7600(port=args.port, baud=args.baud)

    mode = args.mode
    at_ok = False
    if mode in ("auto", "cgpsinfo"):
        probe = sim.send("AT", wait=1.0)
        at_ok = "OK" in probe
        if not at_ok:
            if mode == "cgpsinfo":
                print("Warning: modem did not reply to AT. Check port/wiring/power.")
                print(f"Raw response: {probe!r}")
            else:
                print("No AT reply on this port; falling back to passive NMEA parsing.")
                mode = "nmea_parsed"
        elif mode == "auto":
            mode = "cgpsinfo"

    try:
        if mode == "cgpsinfo":
            run_polling(sim, args.rate)
        elif mode == "nmea":
            run_nmea(sim)
        else:  # nmea_parsed
            run_nmea_parsed(sim, args.rate)
    finally:
        if at_ok and mode == "cgpsinfo":
            print("\nDisabling GNSS engine...")
            try:
                sim.gps_power(False)
            except Exception:
                pass
        sim.close()
        print("Stopped.")


if __name__ == "__main__":
    main()
