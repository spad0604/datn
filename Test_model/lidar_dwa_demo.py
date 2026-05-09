"""Real-time LDS-007 LiDAR visualization with DWA planning.

Click on the plot to set a goal, DWA will plan and display the trajectory.
Lidar points update continuously in background.

Usage:
    python lidar_dwa_demo.py --port COM3 --no-checksum
"""

from __future__ import annotations

import argparse
import math
import sys
import threading
import time
from dataclasses import dataclass
from typing import Optional

import numpy as np

try:
    import matplotlib.pyplot as plt  # type: ignore
except ImportError as exc:
    raise SystemExit("Missing dependency: matplotlib. Install with: pip install matplotlib") from exc

# Import LDS reader from lds007_uart_reader
from lds007_uart_reader import Lds007Stream, Lds007Packet

# Import DWA planner
from dwa_planer import DWAPlanner, RobotState, Obstacle


@dataclass
class LidarScan:
    """Snapshot of 360 LiDAR measurements."""
    distances_mm: list[int]
    intensities: list[int]
    invalids: list[bool]
    rpm: float
    timestamp: float


class LidarReader(threading.Thread):
    """Background thread that reads LiDAR packets and updates a shared scan buffer."""

    def __init__(
        self,
        port: str,
        baud: int = 115200,
        validate_checksum: bool = True,
        start_command: Optional[bytes] = b"startlds$",
    ) -> None:
        super().__init__(daemon=True)
        self.port = port
        self.baud = baud
        self.validate_checksum = validate_checksum
        self.start_command = start_command

        self.stream: Optional[Lds007Stream] = None
        self.should_stop = False

        # Shared state
        self.lock = threading.Lock()
        self.distances = [0] * 360
        self.intensities = [0] * 360
        self.invalids = [False] * 360
        self.rpm = 0.0
        self.last_update_time = 0.0

    def run(self) -> None:
        try:
            self.stream = Lds007Stream(
                port=self.port,
                baud=self.baud,
                start_command=self.start_command,
                validate_checksum=self.validate_checksum,
            )

            for pkt in self.stream.packets():
                if self.should_stop:
                    break

                with self.lock:
                    for p in pkt.points:
                        a = p.angle_deg
                        self.distances[a] = p.distance_mm
                        self.intensities[a] = p.intensity
                        self.invalids[a] = p.invalid
                    self.rpm = pkt.rpm
                    self.last_update_time = time.time()

        except Exception as e:
            print(f"LiDAR reader error: {e}", file=sys.stderr)
        finally:
            if self.stream is not None:
                self.stream.close()

    def get_current_scan(self) -> LidarScan:
        with self.lock:
            return LidarScan(
                distances_mm=list(self.distances),
                intensities=list(self.intensities),
                invalids=list(self.invalids),
                rpm=self.rpm,
                timestamp=self.last_update_time,
            )

    def stop(self) -> None:
        self.should_stop = True
        if self.stream is not None:
            self.stream.close()


def scan_to_obstacles(
    scan: LidarScan,
    robot_radius_mm: float = 180.0,
    min_distance_mm: float = 200.0,
    max_distance_mm: float = 5000.0,
    cluster_tolerance_mm: float = 300.0,
) -> list[Obstacle]:
    """Convert LiDAR scan to obstacles (simple point clustering)."""
    points: list[tuple[float, float]] = []

    for a in range(360):
        d = scan.distances_mm[a]
        if d <= min_distance_mm or d > max_distance_mm:
            continue
        if scan.invalids[a]:
            continue

        rad = (a * math.pi) / 180.0
        x = d * math.cos(rad)
        y = d * math.sin(rad)
        points.append((x, y))

    if not points:
        return []

    # Simple clustering by proximity
    obstacles: list[Obstacle] = []
    used = [False] * len(points)

    for i, (px, py) in enumerate(points):
        if used[i]:
            continue

        # Start a new cluster
        cluster_x = [px]
        cluster_y = [py]
        used[i] = True

        # Find nearby points
        for j, (qx, qy) in enumerate(points):
            if used[j]:
                continue
            dist_sq = (px - qx) ** 2 + (py - qy) ** 2
            if dist_sq <= cluster_tolerance_mm**2:
                cluster_x.append(qx)
                cluster_y.append(qy)
                used[j] = True

        # Centroid of cluster
        cx = float(np.mean(cluster_x))
        cy = float(np.mean(cluster_y))
        obstacles.append(
            Obstacle(x_mm=cx, y_mm=cy, radius_mm=robot_radius_mm + 100.0)
        )

    return obstacles


class InteractiveLidarDWAPlot:
    """Interactive plot showing LiDAR scan + DWA trajectory planning."""

    def __init__(
        self,
        lidar_reader: LidarReader,
        robot_start_x: float = 0.0,
        robot_start_y: float = 0.0,
        plot_range_mm: float = 4000.0,
    ) -> None:
        self.lidar_reader = lidar_reader
        self.robot_state = RobotState(
            x_mm=float(robot_start_x),
            y_mm=float(robot_start_y),
            yaw_rad=0.0,
            v_mm_s=0.0,
            w_rad_s=0.0,
        )
        self.plot_range = float(plot_range_mm)
        self.planner = DWAPlanner()

        # Current goal (if any)
        self.goal_xy: Optional[tuple[float, float]] = None
        self.last_trajectory: Optional[np.ndarray] = None

        # Figure setup
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_title("LiDAR + DWA Planning (click to set goal)")
        self.ax.set_xlabel("x (mm)")
        self.ax.set_ylabel("y (mm)")
        self.ax.grid(True, linewidth=0.5, alpha=0.3)
        self.ax.set_xlim(-self.plot_range, self.plot_range)
        self.ax.set_ylim(-self.plot_range, self.plot_range)

        # Plot artists
        self.lidar_scatter = self.ax.scatter(
            [], [], s=4, c="blue", alpha=0.6, label="LiDAR points"
        )
        self.obstacle_scatter = self.ax.scatter(
            [], [], s=80, c="red", alpha=0.6, marker="x", label="Obstacles"
        )
        self.robot_dot = self.ax.scatter(
            [self.robot_state.x_mm],
            [self.robot_state.y_mm],
            s=50,
            c="green",
            marker="o",
            label="Robot",
        )
        self.goal_dot = self.ax.scatter([], [], s=100, c="orange", marker="*", label="Goal")
        self.traj_line, = self.ax.plot([], [], "g-", linewidth=2, label="Trajectory")
        self.obstacle_circles = []

        self.ax.legend(loc="upper right")

        # Connect click event
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)

        # Animation loop
        self.animation_timer = self.fig.canvas.new_timer()
        self.animation_timer.interval = 100  # 100 ms
        self.animation_timer.single_shot = False
        self.animation_timer.callbacks.append((self.update_plot, (), {}))
        self.animation_timer.start()

    def update_plot(self) -> None:
        """Update lidar points, obstacles, and trajectory."""
        scan = self.lidar_reader.get_current_scan()

        # Extract valid points
        xs_lidar = []
        ys_lidar = []
        for a in range(360):
            d = scan.distances_mm[a]
            if d <= 100 or d > 5000:
                continue
            if scan.invalids[a]:
                continue
            rad = (a * math.pi) / 180.0
            x = d * math.cos(rad)
            y = d * math.sin(rad)
            xs_lidar.append(x)
            ys_lidar.append(y)

        if xs_lidar:
            self.lidar_scatter.set_offsets(
                np.column_stack((np.array(xs_lidar), np.array(ys_lidar)))
            )
        else:
            self.lidar_scatter.set_offsets(np.empty((0, 2)))

        # Obstacles
        obstacles = scan_to_obstacles(scan)

        xs_obs = [obs.x_mm for obs in obstacles]
        ys_obs = [obs.y_mm for obs in obstacles]

        if xs_obs:
            self.obstacle_scatter.set_offsets(
                np.column_stack((np.array(xs_obs), np.array(ys_obs)))
            )
        else:
            self.obstacle_scatter.set_offsets(np.empty((0, 2)))

        # Redraw obstacle circles
        for circle in self.obstacle_circles:
            circle.remove()
        self.obstacle_circles.clear()
        for obs in obstacles:
            circ = plt.Circle(
                (obs.x_mm, obs.y_mm), obs.radius_mm, fill=False, color="red", alpha=0.3
            )
            self.ax.add_patch(circ)
            self.obstacle_circles.append(circ)

        # Title with RPM
        self.ax.set_title(f"LiDAR + DWA (rpm={scan.rpm:.1f})")

        self.fig.canvas.draw_idle()

    def on_click(self, event) -> None:
        """Handle mouse click to set goal."""
        if event.inaxes != self.ax:
            return
        if event.xdata is None or event.ydata is None:
            return

        goal_x = float(event.xdata)
        goal_y = float(event.ydata)
        self.goal_xy = (goal_x, goal_y)

        self.goal_dot.set_offsets(np.array([[goal_x, goal_y]]))

        # Re-plan
        scan = self.lidar_reader.get_current_scan()
        obstacles = scan_to_obstacles(scan)

        best = self.planner.plan(self.robot_state, self.goal_xy, obstacles)
        if best is not None:
            self.last_trajectory = best
            self.traj_line.set_data(best[:, 0], best[:, 1])

        self.fig.canvas.draw_idle()

    def show(self) -> None:
        """Display the plot."""
        plt.show()


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(
        description="Real-time LiDAR visualization with DWA planning"
    )
    ap.add_argument("--port", required=True, help="Serial port (e.g. COM3, /dev/ttyUSB0)")
    ap.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    ap.add_argument(
        "--no-checksum",
        action="store_true",
        help="Disable checksum validation",
    )
    ap.add_argument(
        "--no-start-cmd",
        action="store_true",
        help="Do not send start command",
    )

    args = ap.parse_args(argv)

    start_cmd: Optional[bytes] = None if args.no_start_cmd else b"startlds$"

    print(f"Connecting to {args.port} at {args.baud} baud...")
    reader = LidarReader(
        port=args.port,
        baud=args.baud,
        validate_checksum=not args.no_checksum,
        start_command=start_cmd,
    )
    reader.start()

    # Give reader time to connect
    time.sleep(0.5)

    print("Starting interactive plot...")
    print("Click on the plot to set a goal. DWA will plan a trajectory.")
    print("Close the plot window to exit.")

    plotter = InteractiveLidarDWAPlot(reader)
    try:
        plotter.show()
    finally:
        reader.stop()
        reader.join(timeout=2.0)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
