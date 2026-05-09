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

Usage examples (Windows):
  python lds007_uart_reader.py --port COM3
  python lds007_uart_reader.py --port COM3 --csv out.csv
    python lds007_uart_reader.py --port COM3 --plot

Dependencies:
  pip install pyserial
    pip install matplotlib   (only if you use --plot)
"""

from __future__ import annotations

import argparse
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


class RealtimePlot:
    def __init__(self, *, max_mm: int = 6000, update_hz: float = 20.0) -> None:
        try:
            import matplotlib.pyplot as plt  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise SystemExit(
                "Missing dependency: matplotlib. Install with: pip install matplotlib"
            ) from exc

        self._plt = plt
        self._max_mm = max(1, int(max_mm))
        self._min_dt = 1.0 / max(1.0, float(update_hz))
        self._last_update = 0.0

        plt.ion()
        self._fig, self._ax = plt.subplots(figsize=(7, 7))
        self._ax.set_aspect("equal", adjustable="box")
        self._ax.set_title("LDS-007 Realtime Scan")
        self._ax.set_xlabel("x (mm)")
        self._ax.set_ylabel("y (mm)")
        self._ax.grid(True, linewidth=0.5, alpha=0.4)
        lim = self._max_mm
        self._ax.set_xlim(-lim, lim)
        self._ax.set_ylim(-lim, lim)

        # Valid points colored by intensity; invalid points in red.
        self._sc_valid = self._ax.scatter([], [], s=6, c=[], cmap="viridis", vmin=0, vmax=2048)
        self._sc_invalid = self._ax.scatter([], [], s=8, c="red")

        # Draw origin.
        self._ax.scatter([0], [0], s=25, c="white")

        try:
            self._fig.canvas.manager.set_window_title("LDS-007")
        except Exception:
            pass

        plt.show(block=False)

    def update(
        self,
        *,
        distances_mm: list[int],
        intensities: list[int],
        invalids: list[bool],
        warnings: list[bool],
        rpm: float,
    ) -> None:
        now = time.time()
        if now - self._last_update < self._min_dt:
            return
        self._last_update = now

        xs_valid: list[float] = []
        ys_valid: list[float] = []
        cs_valid: list[int] = []

        xs_invalid: list[float] = []
        ys_invalid: list[float] = []

        max_mm = self._max_mm

        # 0 deg along +X axis; increase counter-clockwise.
        for a in range(360):
            d = int(distances_mm[a])
            if d <= 0 or d > max_mm:
                continue

            rad = (a * 3.141592653589793) / 180.0
            x = d * math.cos(rad)
            y = d * math.sin(rad)

            if invalids[a] or warnings[a]:
                xs_invalid.append(x)
                ys_invalid.append(y)
            else:
                xs_valid.append(x)
                ys_valid.append(y)
                cs_valid.append(int(intensities[a]))

        # Build proper Nx2 arrays; matplotlib fails on 1-D empty arrays
        if xs_valid:
            offsets_valid = np.column_stack((np.array(xs_valid, dtype=float), np.array(ys_valid, dtype=float)))
        else:
            offsets_valid = np.empty((0, 2), dtype=float)

        if xs_invalid:
            offsets_invalid = np.column_stack((np.array(xs_invalid, dtype=float), np.array(ys_invalid, dtype=float)))
        else:
            offsets_invalid = np.empty((0, 2), dtype=float)

        self._sc_valid.set_offsets(offsets_valid)
        # ensure color/intensity array matches number of valid points
        if cs_valid:
            self._sc_valid.set_array(np.array(cs_valid, dtype=float))
        else:
            # empty array
            self._sc_valid.set_array(np.array([], dtype=float))

        self._sc_invalid.set_offsets(offsets_invalid)

        self._ax.set_title(f"LDS-007 Realtime Scan | rpm={rpm:.2f} | max={max_mm}mm")

        self._fig.canvas.draw_idle()
        # Allow GUI event loop to process input/paint.
        self._plt.pause(0.001)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Read and decode LDS-007 packets over UART")
    ap.add_argument("--port", required=True, help="Serial port (e.g. COM3, /dev/ttyUSB0)")
    ap.add_argument("--baud", type=int, default=115200, help="Baudrate (default: 115200)")
    ap.add_argument(
        "--no-start-cmd",
        action="store_true",
        help="Do not send start command (default sends 'startlds$')",
    )
    ap.add_argument(
        "--start-cmd",
        default="startlds$",
        help="Start command to send (default: startlds$)",
    )
    ap.add_argument(
        "--no-checksum",
        action="store_true",
        help="Disable checksum validation (useful if your wiring is noisy)",
    )
    ap.add_argument(
        "--partial",
        action="store_true",
        help="Emit output on every packet (default outputs only when a full 360° scan is ready)",
    )
    ap.add_argument(
        "--plot",
        action="store_true",
        help="Show a realtime 2D plot of the scan (requires matplotlib)",
    )
    ap.add_argument(
        "--plot-max-mm",
        type=int,
        default=6000,
        help="Plot range limit in mm (default: 6000)",
    )
    ap.add_argument(
        "--csv",
        default=None,
        help="Write points to CSV file (timestamp, angle_deg, distance_mm, intensity, invalid, warning, rpm)",
    )

    args = ap.parse_args(argv)

    start_cmd: Optional[bytes]
    if args.no_start_cmd:
        start_cmd = None
    else:
        start_cmd = args.start_cmd.encode("ascii", errors="strict")

    stream = Lds007Stream(
        port=args.port,
        baud=args.baud,
        start_command=start_cmd,
        validate_checksum=not args.no_checksum,
    )

    distances = [0] * 360
    intensities = [0] * 360
    invalids = [False] * 360
    warnings = [False] * 360
    received = [False] * 360
    received_count = 0

    plotter: Optional[RealtimePlot] = None
    if args.plot:
        plotter = RealtimePlot(max_mm=args.plot_max_mm, update_hz=20.0)

    csv_file = None
    csv_writer = None
    if args.csv:
        csv_file = open(args.csv, "w", newline="", encoding="utf-8")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(
            [
                "ts_unix",
                "angle_deg",
                "distance_mm",
                "intensity",
                "invalid",
                "warning",
                "rpm",
            ]
        )

    last_print = 0.0

    def emit_scan(rpm: float) -> None:
        nonlocal last_print
        ts = time.time()

        if plotter is not None:
            plotter.update(
                distances_mm=distances,
                intensities=intensities,
                invalids=invalids,
                warnings=warnings,
                rpm=rpm,
            )
        if csv_writer is not None:
            for a in range(360):
                csv_writer.writerow(
                    [
                        f"{ts:.6f}",
                        a,
                        distances[a],
                        intensities[a],
                        int(invalids[a]),
                        int(warnings[a]),
                        f"{rpm:.2f}",
                    ]
                )
            csv_file.flush()
            return

        # Console summary (throttle a bit)
        if ts - last_print < 0.1:
            return
        last_print = ts

        # Show a tiny snapshot
        sample_angles = (0, 90, 180, 270)
        parts = [f"rpm={rpm:.2f}"]
        for a in sample_angles:
            d = distances[a]
            inv = "!" if invalids[a] else ""
            parts.append(f"a{a}:{d}{inv}")
        print(" ".join(parts))

    def emit_plot_only(rpm: float) -> None:
        if plotter is None:
            return
        plotter.update(
            distances_mm=distances,
            intensities=intensities,
            invalids=invalids,
            warnings=warnings,
            rpm=rpm,
        )

    try:
        for pkt in stream.packets():
            for p in pkt.points:
                a = p.angle_deg
                distances[a] = p.distance_mm
                intensities[a] = p.intensity
                invalids[a] = p.invalid
                warnings[a] = p.warning
                if not received[a]:
                    received[a] = True
                    received_count += 1

            # For plotting, update continuously even if we haven't yet received a full 360°.
            # This avoids a blank plot when packets are dropped.
            if plotter is not None:
                emit_plot_only(pkt.rpm)

            if args.partial:
                emit_scan(pkt.rpm)
            elif received_count >= 360:
                emit_scan(pkt.rpm)
                for i in range(360):
                    received[i] = False
                received_count = 0

    except KeyboardInterrupt:
        pass
    finally:
        if csv_file is not None:
            csv_file.close()
        stream.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
