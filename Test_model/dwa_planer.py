from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Optional

import numpy as np


@dataclass
class RobotState:
    x_mm: float
    y_mm: float
    yaw_rad: float
    v_mm_s: float = 0.0
    w_rad_s: float = 0.0


@dataclass(frozen=True)
class Obstacle:
    x_mm: float
    y_mm: float
    radius_mm: float = 150.0


class DWAPlanner:
    def __init__(
        self,
        *,
        max_speed_mm_s: float = 500.0,
        max_yaw_rate_rad_s: float = 40.0 * math.pi / 180.0,
        max_accel_mm_s2: float = 800.0,
        max_yaw_accel_rad_s2: float = 80.0 * math.pi / 180.0,
        predict_time_s: float = 3.0,
        dt_s: float = 0.05,
        robot_radius_mm: float = 180.0,
        v_res_mm_s: float = 50.0,
        w_res_rad_s: float = 0.1,
        w_goal: float = 1.0,
        w_clearance: float = 2.0,
        w_speed: float = 0.2,
    ) -> None:
        # Thông số cấu hình robot
        self.max_speed = float(max_speed_mm_s)
        self.max_yaw_rate = float(max_yaw_rate_rad_s)
        self.max_accel = float(max_accel_mm_s2)
        self.max_yaw_accel = float(max_yaw_accel_rad_s2)
        self.predict_time = float(predict_time_s)
        self.dt = float(dt_s)
        self.robot_radius = float(robot_radius_mm)

        self.v_res = float(v_res_mm_s)
        self.w_res = float(w_res_rad_s)

        # Weights cho cost function
        self.w_goal = float(w_goal)
        self.w_clearance = float(w_clearance)
        self.w_speed = float(w_speed)

    def plan(
        self,
        current: RobotState,
        goal_xy_mm: tuple[float, float],
        obstacles: Iterable[Obstacle] = (),
    ) -> Optional[np.ndarray]:
        """Return best trajectory as Nx3 array: [x_mm, y_mm, yaw_rad]."""

        goal_x, goal_y = goal_xy_mm
        obstacles_list = list(obstacles)

        v_min, v_max, w_min, w_max = self.dynamic_window(current)

        best_traj: Optional[np.ndarray] = None
        best_cost = float("inf")

        # Duyệt qua các cặp vận tốc (v, w) có thể có.
        # Dùng linspace để vẫn có nhiều mẫu ngay cả khi dynamic window nhỏ hơn bước lấy mẫu.
        v_values = self._sample_range(v_min, v_max, self.v_res)
        w_values = self._sample_range(w_min, w_max, self.w_res)

        for v in v_values:
            for w in w_values:
                traj = self.predict_trajectory(current, v, w)
                cost = self.calculate_cost(traj, goal_x, goal_y, v, obstacles_list)

                if cost < best_cost:
                    best_cost = cost
                    best_traj = traj

        return best_traj

    @staticmethod
    def _sample_range(min_value: float, max_value: float, resolution: float) -> np.ndarray:
        """Sample a closed interval with at least 2 points when possible."""
        if max_value < min_value:
            return np.array([], dtype=float)

        span = max_value - min_value
        if span <= 1e-9:
            return np.array([min_value], dtype=float)

        steps = max(2, int(math.ceil(span / max(1e-9, resolution))) + 1)
        return np.linspace(min_value, max_value, steps, dtype=float)

    def dynamic_window(self, state: RobotState) -> tuple[float, float, float, float]:
        """Compute [v_min, v_max, w_min, w_max] based on current state and accel limits."""
        v_min = max(0.0, state.v_mm_s - self.max_accel * self.dt)
        v_max = min(self.max_speed, state.v_mm_s + self.max_accel * self.dt)
        w_min = max(-self.max_yaw_rate, state.w_rad_s - self.max_yaw_accel * self.dt)
        w_max = min(self.max_yaw_rate, state.w_rad_s + self.max_yaw_accel * self.dt)
        return v_min, v_max, w_min, w_max

    def predict_trajectory(self, start: RobotState, v_mm_s: float, w_rad_s: float) -> np.ndarray:
        """Simulate unicycle model forward for predict_time.

        Returns Nx3 array [x_mm, y_mm, yaw_rad]. Includes starting pose.
        """
        steps = max(1, int(self.predict_time / self.dt))

        x = float(start.x_mm)
        y = float(start.y_mm)
        yaw = float(start.yaw_rad)

        traj = np.zeros((steps + 1, 3), dtype=float)
        traj[0, :] = (x, y, yaw)

        v = float(v_mm_s)
        w = float(w_rad_s)

        for k in range(1, steps + 1):
            x += v * math.cos(yaw) * self.dt
            y += v * math.sin(yaw) * self.dt
            yaw = self._wrap_pi(yaw + w * self.dt)
            traj[k, :] = (x, y, yaw)

        return traj

    def calculate_cost(
        self,
        traj: np.ndarray,
        goal_x: float,
        goal_y: float,
        v_mm_s: float,
        obstacles: list[Obstacle],
    ) -> float:
        # 1) Goal cost: khoảng cách từ điểm cuối tới goal
        dx = float(traj[-1, 0]) - float(goal_x)
        dy = float(traj[-1, 1]) - float(goal_y)
        goal_cost = math.hypot(dx, dy)

        # 2) Clearance / collision cost
        clearance_cost = self._clearance_cost(traj, obstacles)

        # 3) Speed cost (ưu tiên đi nhanh hơn một chút)
        speed_cost = (self.max_speed - float(v_mm_s)) / max(1.0, self.max_speed)

        return self.w_goal * goal_cost + self.w_clearance * clearance_cost + self.w_speed * speed_cost

    def _clearance_cost(self, traj: np.ndarray, obstacles: list[Obstacle]) -> float:
        if not obstacles:
            return 0.0

        # Tính khoảng cách nhỏ nhất từ mọi điểm trên traj tới mọi obstacle
        # Nếu va chạm: trả về cost cực lớn
        min_dist = float("inf")

        for obs in obstacles:
            ox = obs.x_mm
            oy = obs.y_mm
            safe_r = self.robot_radius + obs.radius_mm

            dx = traj[:, 0] - ox
            dy = traj[:, 1] - oy
            d = np.hypot(dx, dy)
            d_min = float(d.min())

            if d_min <= safe_r:
                return 1e9

            if d_min < min_dist:
                min_dist = d_min

        # Cost càng lớn khi đi sát vật cản (inverse)
        return 1.0 / max(1.0, (min_dist - self.robot_radius))

    @staticmethod
    def _wrap_pi(a: float) -> float:
        while a > math.pi:
            a -= 2.0 * math.pi
        while a < -math.pi:
            a += 2.0 * math.pi
        return a


def _demo_click_to_plan() -> None:
    """Demo: click một điểm trên plot để đặt goal, DWA sẽ vẽ trajectory."""
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except ImportError as exc:
        raise SystemExit("Missing dependency: matplotlib. Install with: pip install matplotlib") from exc

    planner = DWAPlanner()
    state = RobotState(x_mm=0.0, y_mm=0.0, yaw_rad=0.0, v_mm_s=0.0, w_rad_s=0.0)

    # Bạn có thể thay obstacles theo map LiDAR của bạn
    obstacles: list[Obstacle] = []

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Click to set goal (DWA)")
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.grid(True, linewidth=0.5, alpha=0.4)

    lim = 4000
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)

    robot_dot = ax.scatter([state.x_mm], [state.y_mm], s=40)
    traj_line, = ax.plot([], [], linewidth=2)
    goal_dot = ax.scatter([], [], s=60)

    def redraw_obstacles() -> None:
        # Clear old obstacle artists (simple approach)
        # Keep the first few known artists only
        # (robot_dot, traj_line, goal_dot) are kept; rest are obstacles.
        while len(ax.patches) > 0:
            ax.patches.pop()
        for obs in obstacles:
            circ = plt.Circle((obs.x_mm, obs.y_mm), obs.radius_mm, fill=False)
            ax.add_patch(circ)

    redraw_obstacles()

    def on_click(event) -> None:
        nonlocal state
        if event.inaxes != ax:
            return
        if event.xdata is None or event.ydata is None:
            return

        goal_x = float(event.xdata)
        goal_y = float(event.ydata)

        goal_dot.set_offsets(np.array([[goal_x, goal_y]], dtype=float))

        best = planner.plan(state, (goal_x, goal_y), obstacles)
        if best is None:
            traj_line.set_data([], [])
            fig.canvas.draw_idle()
            return

        traj_line.set_data(best[:, 0], best[:, 1])
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("button_press_event", on_click)
    plt.show()


if __name__ == "__main__":
    _demo_click_to_plan()