#!/usr/bin/env python3
"""Small CLI to test BE WebSocket/STOMP connection from robot side.

This script uses the `ServerService` class and exposes simple commands to send a single
location update, run periodic updates, or subscribe to order topic.

Usage examples:
  python robot_ws_test.py once --lat 21.0285 --lon 105.8542
  python robot_ws_test.py periodic --interval 5
  python robot_ws_test.py listen
"""
from __future__ import annotations

import argparse
import os
import sys
from typing import Any

from ws_client import ServerService, run_periodic_location_update
from config_ws import DEFAULT_WS_URL, DEFAULT_API_BASE_URL, DEFAULT_SECRET, DEFAULT_ROBOT_ID


def cmd_once(args: argparse.Namespace) -> int:
    client = ServerService(
        ws_url=args.ws_url or DEFAULT_WS_URL,
        api_base_url=args.api_url or DEFAULT_API_BASE_URL,
        robot_id=args.robot_id or DEFAULT_ROBOT_ID,
        secret_key=args.secret or DEFAULT_SECRET,
    )

    lat = float(args.lat)
    lon = float(args.lon)
    ok = client.update_robot_location(lat, lon)
    print(f"update_robot_location -> {ok}")
    return 0 if ok else 2


def cmd_periodic(args: argparse.Namespace) -> int:
    client = ServerService(
        ws_url=args.ws_url or DEFAULT_WS_URL,
        api_base_url=args.api_url or DEFAULT_API_BASE_URL,
        robot_id=args.robot_id or DEFAULT_ROBOT_ID,
        secret_key=args.secret or DEFAULT_SECRET,
    )

    try:
        run_periodic_location_update(
            client,
            interval_seconds=int(args.interval),
            max_distance_meters=float(args.max_distance),
            initial_lat=float(args.lat) if args.lat is not None else None,
            initial_lon=float(args.lon) if args.lon is not None else None,
        )
    except KeyboardInterrupt:
        print("Stopped by user")
    return 0


def cmd_listen(args: argparse.Namespace) -> int:
    client = ServerService(
        ws_url=args.ws_url or DEFAULT_WS_URL,
        api_base_url=args.api_url or DEFAULT_API_BASE_URL,
        robot_id=args.robot_id or DEFAULT_ROBOT_ID,
        secret_key=args.secret or DEFAULT_SECRET,
    )

    def on_change(orders, payload, event_type: str) -> None:
        print(f"[EVENT:{event_type}] payload={payload}")
        print(f"Orders count: {len(orders)}")

    def on_error(exc: Exception) -> None:
        print(f"Listen error: {exc}")

    print("Subscribing to order topic. Press Ctrl+C to stop.")
    client.listen_orders(on_change=on_change, on_error=on_error)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Robot WS/STOMP test launcher")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--ws-url", default=os.getenv("ROBOT_WS_URL", DEFAULT_WS_URL), help="WebSocket URL (overrides auto)")
    common.add_argument("--api-url", default=os.getenv("ROBOT_API_BASE_URL", DEFAULT_API_BASE_URL), help="API base URL for REST snapshot")
    common.add_argument("--robot-id", default=int(os.getenv("ROBOT_ID", str(DEFAULT_ROBOT_ID))), type=int, help="Robot ID")
    common.add_argument("--secret", default=os.getenv("ROBOT_SHARED_SECRET", DEFAULT_SECRET), help="Robot shared secret")

    p_once = sub.add_parser("once", parents=[common], help="Send one location update")
    p_once.add_argument("--lat", required=True, help="Latitude")
    p_once.add_argument("--lon", "--lng", dest="lon", required=True, help="Longitude")

    p_periodic = sub.add_parser("periodic", parents=[common], help="Send periodic location updates")
    p_periodic.add_argument("--interval", default=10, help="Seconds between updates")
    p_periodic.add_argument("--max-distance", default=200.0, help="Max move distance (meters)")
    p_periodic.add_argument("--lat", required=False, help="Initial latitude (optional)")
    p_periodic.add_argument("--lon", "--lng", dest="lon", required=False, help="Initial longitude (optional)")

    p_listen = sub.add_parser("listen", parents=[common], help="Subscribe to order topic")

    return p


def main(argv: Any | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # If ws or api url not provided, allow ServerService to resolve defaults
    if args.cmd == "once":
        return cmd_once(args)
    if args.cmd == "periodic":
        return cmd_periodic(args)
    if args.cmd == "listen":
        return cmd_listen(args)
    print("Unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
