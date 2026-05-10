"""LDS-007 LiDAR UART reader/decoder.

Based on a public reverse-engineered implementation (packet format matches the
classic Neato/XV-11 style frames):

- Baudrate: 115200 8N1
- Frame length: 22 bytes
- Frame header: 0xFA
- Index byte: 0xA0..0xF9 (90 blocks)
- Each frame contains 4 measurements
- Angle (deg): (index - 0xA0) * 4 + i, i in [0..3]
- Checksum: little-endian uint16 at bytes [20..21], computed over bytes [0..19]

The module typically starts streaming after receiving ASCII command: "startlds$".
"""

from __future__ import annotations

import csv
import math
import numpy as np
import sys
import time
from dataclasses import dataclass
from typing import Iterable, Optional


try:
    import serial  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: pyserial. Install with: pip install pyserial"
    ) from exc


FRAME_HEADER = 0xFA
FRAME_LEN = 22
IDX_MIN = 0xA0
IDX_MAX = 0xF9


@dataclass(frozen=True)
class Lds007Point:
    angle_deg: int
    distance_mm: int
    intensity: int
    invalid: bool
    warning: bool


@dataclass(frozen=True)
class Lds007Packet:
    index: int
    rpm: float
    points: tuple[Lds007Point, Lds007Point, Lds007Point, Lds007Point]


def compute_checksum(pkt22: bytes) -> int:
    """Compute LDS-007 checksum.

    Reference implementation:
      chk = 0
      for i in 0..19: chk = (chk << 1) + data[i]
      return chk & 0x7FFF
    """

    if len(pkt22) != FRAME_LEN:
        raise ValueError(f"Expected {FRAME_LEN} bytes, got {len(pkt22)}")

    chk = 0
    for b in pkt22[:20]:
        chk = ((chk << 1) + b) & 0xFFFFFFFF
    return chk & 0x7FFF


def parse_packet(pkt22: bytes, *, validate_checksum: bool = True) -> Optional[Lds007Packet]:
    if len(pkt22) != FRAME_LEN:
        return None
    if pkt22[0] != FRAME_HEADER:
        return None

    idx = pkt22[1]
    if idx < IDX_MIN or idx > IDX_MAX:
        return None

    checksum_rx = pkt22[20] | (pkt22[21] << 8)
    if validate_checksum:
        checksum_calc = compute_checksum(pkt22)
        if (checksum_rx & 0x7FFF) != checksum_calc:
            return None

    # Motor speed field (XV-11 style): little-endian, unit ~ 1/64 RPM.
    speed_raw = pkt22[2] | (pkt22[3] << 8)
    rpm = speed_raw / 64.0

    block = idx - IDX_MIN
    points: list[Lds007Point] = []

    for i in range(4):
        base = 4 + i * 4
        dist_l = pkt22[base]
        dist_h_flags = pkt22[base + 1]
        intensity_l = pkt22[base + 2]
        intensity_h = pkt22[base + 3]

        invalid = bool(dist_h_flags & 0x80)
        warning = bool(dist_h_flags & 0x40)
        distance_mm = dist_l | ((dist_h_flags & 0x3F) << 8)
        intensity = intensity_l | (intensity_h << 8)

        angle = block * 4 + i
        points.append(
            Lds007Point(
                angle_deg=angle,
                distance_mm=distance_mm,
                intensity=intensity,
                invalid=invalid,
                warning=warning,
            )
        )

    return Lds007Packet(index=idx, rpm=rpm, points=(points[0], points[1], points[2], points[3]))


class Lds007Stream:
    def __init__(
        self,
        port: str,
        baud: int = 115200,
        *,
        start_command: Optional[bytes] = b"startlds$",
        validate_checksum: bool = True,
        read_timeout_s: float = 0.2,
    ) -> None:
        self._ser = serial.Serial(
            port=port,
            baudrate=baud,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=read_timeout_s,
        )
        self._validate_checksum = validate_checksum

        # Some adapters buffer old bytes.
        try:
            self._ser.reset_input_buffer()
        except Exception:
            pass

        if start_command:
            # Give the MCU / sensor time to boot.
            time.sleep(0.2)
            self._ser.write(start_command)
            self._ser.flush()

    def close(self) -> None:
        try:
            self._ser.close()
        except Exception:
            pass

    def packets(self) -> Iterable[Lds007Packet]:
        """Yield decoded packets, resyncing on 0xFA."""
        buf = bytearray()
        while True:
            chunk = self._ser.read(256)
            if not chunk:
                continue
            buf.extend(chunk)

            while True:
                try:
                    start = buf.index(FRAME_HEADER)
                except ValueError:
                    buf.clear()
                    break

                if start > 0:
                    del buf[:start]

                if len(buf) < FRAME_LEN:
                    break

                pkt = bytes(buf[:FRAME_LEN])
                del buf[:FRAME_LEN]

                parsed = parse_packet(pkt, validate_checksum=self._validate_checksum)
                if parsed is None:
                    # If parsing fails, drop one byte and try to resync.
                    if buf:
                        del buf[0:1]
                    continue

                yield parsed
