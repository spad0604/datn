import re
from dataclasses import dataclass
from typing import Any


PROTOCOL_PREFIX = "RD"
PROTOCOL_VERSION = "1"


@dataclass(frozen=True)
class MCUFrame:
    kind: str  # CMD / EVT / ACK / ERR
    name: str
    fields: dict[str, str]


_SAFE_VALUE_RE = re.compile(r"^[A-Za-z0-9_\-\.]+$")


def build_cmd(name: str, **fields: Any) -> str:
    parts: list[str] = [f"{PROTOCOL_PREFIX}{PROTOCOL_VERSION}", "CMD", name]
    for k, v in fields.items():
        if v is None:
            continue
        key = str(k).strip().upper()
        value = str(v).strip()
        # Keep MCU parsing easy: only allow simple tokens; caller can pre-encode if needed.
        if not _SAFE_VALUE_RE.match(value):
            value = re.sub(r"[^A-Za-z0-9_\-\.]", "_", value)
        parts.append(f"{key}={value}")
    return ";".join(parts) + "\n"


def parse_line(line: str) -> MCUFrame | None:
    raw = (line or "").strip()
    if not raw:
        return None

    tokens = raw.split(";")
    if len(tokens) < 3:
        return None

    prefix = tokens[0]
    if not prefix.startswith(PROTOCOL_PREFIX):
        return None

    kind = tokens[1].strip().upper()
    name = tokens[2].strip().upper()
    fields: dict[str, str] = {}
    for t in tokens[3:]:
        if not t or "=" not in t:
            continue
        k, v = t.split("=", 1)
        fields[k.strip().upper()] = v.strip()

    return MCUFrame(kind=kind, name=name, fields=fields)


# ---- Convenience commands ----


def cmd_motor(left: int, right: int) -> str:
    return build_cmd("MOTOR", L=int(left), R=int(right))


def cmd_motor_stop() -> str:
    return build_cmd("MOTOR_STOP")


def cmd_mpu_read() -> str:
    return build_cmd("MPU_READ")


def cmd_pin_set(pin: str, order: int | None = None) -> str:
    return build_cmd("PIN_SET", PIN=str(pin), ORDER=order)


def cmd_pin_clear() -> str:
    return build_cmd("PIN_CLEAR")


def cmd_unlock(pin: str) -> str:
    return build_cmd("UNLOCK", PIN=str(pin))


def cmd_signal(mode: str) -> str:
    return build_cmd("SIGNAL", MODE=str(mode).upper())


def cmd_lock_pulse(ms: int = 5000) -> str:
    return build_cmd("LOCK_PULSE", MS=int(ms))
