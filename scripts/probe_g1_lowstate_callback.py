#!/usr/bin/env python3

import sys
import time
from collections import defaultdict

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_ as HgLowState

try:
    from unitree_sdk2py.idl.unitree_go.msg.dds_ import LowState_ as GoLowState
except Exception:
    GoLowState = None


hits = defaultdict(int)
last_msg = {}
last_print = 0.0


def make_handler(name):
    def handler(msg):
        hits[name] += 1
        last_msg[name] = msg

    return handler


def print_sample(name, msg):
    print(f"\n--- {name} ---")
    print(f"messages: {hits[name]}")

    for attr in ["mode_machine", "tick"]:
        try:
            print(f"{attr}: {getattr(msg, attr)}")
        except Exception:
            pass

    try:
        print(f"motor[0].q:  {msg.motor_state[0].q}")
        print(f"motor[0].dq: {msg.motor_state[0].dq}")
    except Exception as exc:
        print(f"motor sample failed: {exc}")

    try:
        print(f"imu gyro:  {list(msg.imu_state.gyroscope)}")
        print(f"imu accel: {list(msg.imu_state.accelerometer)}")
    except Exception as exc:
        print(f"imu sample failed: {exc}")


def main():
    global last_print

    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/probe_g1_lowstate_callback.py <iface> [domain]")
        print("Example: uv run python scripts/probe_g1_lowstate_callback.py enp194s0 0")
        raise SystemExit(2)

    iface = sys.argv[1]
    domain = int(sys.argv[2]) if len(sys.argv) >= 3 else 0

    print(f"Initializing DDS domain={domain}, iface={iface}")
    ChannelFactoryInitialize(domain, iface)

    candidates = [
        ("rt/lowstate [hg]", "rt/lowstate", HgLowState),
        ("rt/lf/lowstate [hg]", "rt/lf/lowstate", HgLowState),
    ]

    if GoLowState is not None:
        candidates.extend(
            [
                ("rt/lowstate [go]", "rt/lowstate", GoLowState),
                ("rt/lf/lowstate [go]", "rt/lf/lowstate", GoLowState),
            ]
        )

    subscribers = []

    for name, topic, msg_type in candidates:
        try:
            sub = ChannelSubscriber(topic, msg_type)
            sub.Init(make_handler(name), 10)
            subscribers.append(sub)
            print(f"subscribed: {name}")
        except Exception as exc:
            print(f"failed: {name}: {exc}")

    print("Waiting for callbacks. Read-only. No publishers created.")
    print("Press Ctrl+C to stop.")

    while True:
        now = time.time()

        if now - last_print >= 1.0:
            last_print = now

            if not hits:
                print("no callbacks yet")
            else:
                for name, msg in list(last_msg.items()):
                    print_sample(name, msg)

        time.sleep(0.05)


if __name__ == "__main__":
    main()
