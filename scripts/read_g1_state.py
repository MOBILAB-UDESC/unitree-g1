#!/usr/bin/env python3

import sys
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_


state = None
count = 0


def handler(msg: LowState_):
    global state, count
    state = msg
    count += 1


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/read_g1_state.py <iface>")
        raise SystemExit(2)

    iface = sys.argv[1]

    ChannelFactoryInitialize(0, iface)

    sub = ChannelSubscriber("rt/lowstate", LowState_)
    sub.Init(handler, 10)

    print("Reading G1 rt/lowstate. Read-only. Ctrl+C to stop.")

    last_count = 0
    last_time = time.time()

    while True:
        time.sleep(1.0)

        if state is None:
            print("No state received yet")
            continue

        now = time.time()
        hz = (count - last_count) / (now - last_time)
        last_count = count
        last_time = now

        print(
            f"hz={hz:.1f} "
            f"tick={state.tick} "
            f"mode_machine={state.mode_machine} "
            f"q0={state.motor_state[0].q:.4f} "
            f"dq0={state.motor_state[0].dq:.4f} "
            f"imu_accel={list(state.imu_state.accelerometer)}"
        )


if __name__ == "__main__":
    main()
