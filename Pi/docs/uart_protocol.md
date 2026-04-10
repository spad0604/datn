# UART Protocol (Pi ↔ MCU)

Transport
- UART line-based ASCII
- One frame per line, terminated by `\n` (MCU also accepts `\r`)

Frame format
- `RD1;{KIND};{NAME};K=V;K=V...`
  - `RD1` = protocol prefix + version
  - `KIND` ∈ `CMD`, `EVT`, `ACK`, `ERR`
  - `NAME` = command/event name
  - `K=V` pairs are optional

Commands (Pi → MCU)
- Motor control:
  - `RD1;CMD;MOTOR;L={int};R={int}`  (range suggested `-1000..1000`)
  - `RD1;CMD;MOTOR_STOP`
- MPU data:
  - `RD1;CMD;MPU_READ` (MCU replies with one `EVT;MPU;...` line)
  - MCU also pushes periodic MPU frames automatically while running.
- PIN / unlock:
  - `RD1;CMD;PIN_SET;PIN={4..6 digits};ORDER={orderId}`
  - `RD1;CMD;PIN_CLEAR`
  - `RD1;CMD;UNLOCK;PIN={digits}`
- Relay / lock pulse:
  - `RD1;CMD;SIGNAL;MODE={OFF|LEFT|RIGHT|HAZARD}`
  - `RD1;CMD;LOCK_PULSE;MS={100..10000}` (default `5000`)

Events / Replies (MCU → Pi)
- Acks:
  - `RD1;ACK;MOTOR;OK=1`
  - `RD1;ACK;MOTOR_STOP;OK=1`
  - `RD1;ACK;PIN_SET;OK=1`
  - `RD1;ACK;SIGNAL;OK=1;MODE=...`
  - `RD1;ACK;LOCK_PULSE;OK=1;MS=...`
- Errors:
  - `RD1;ERR;PIN_SET;OK=0;ERR=BAD_PIN`
  - `RD1;ERR;SIGNAL;OK=0;ERR=NO_MODE|BAD_MODE`
  - `RD1;ERR;UNKNOWN;OK=0`
- Unlock result:
  - `RD1;EVT;UNLOCKED;OK=1`
  - `RD1;EVT;UNLOCKED;OK=0;ERR=BAD_PIN|NO_PIN`
- MPU snapshot (raw ints):
  - `RD1;EVT;MPU;AXR=...;AYR=...;AZR=...;GXR=...;GYR=...;GZR=...;T=...`
    - `T` is temperature * 100

Notes
- Pi auto-pushes `PIN_SET` when it receives an assigned order (or via REST polling snapshot).
- If order is cancelled / no active order, Pi sends `PIN_CLEAR`.