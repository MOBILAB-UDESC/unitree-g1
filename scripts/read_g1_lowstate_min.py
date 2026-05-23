#!/usr/bin/env python3

import sys
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/read_g1_lowstate_min.py <iface>")
        print("Example: uv run python scripts/read_g1_lowstate_min.py enp194s0")
        raise SystemExit(2)

    iface = sys.argv[1]

    print(f"Init DDS domain=0 iface={iface}")
    ChannelFactoryInitialize(0)

    sub = ChannelSubscriber("rt/lowstate", LowState_)
    sub.Init()

    print("Subscribed to rt/lowstate as unitree_hg LowState_")
    print("Waiting... Ctrl+C to stop.")

    count = 0
    last = time.time()

    while True:
        msg = sub.Read()

        if msg is None:
            time.sleep(0.002)
            continue

        count += 1
        now = time.time()

        if now - last >= 1.0:
            last = now
            print("\n--- got lowstate ---")
            print(f"count: {count}")

            try:
                print(f"mode_machine: {msg.mode_machine}")
            except Exception as e:
                print(f"mode_machine read failed: {e}")

            try:
                print(f"motor[0].q:  {msg.motor_state[0].q}")
                print(f"motor[0].dq: {msg.motor_state[0].dq}")
            except Exception as e:
                print(f"motor read failed: {e}")

            try:
                print(f"imu gyro:  {list(msg.imu_state.gyroscope)}")
                print(f"imu accel: {list(msg.imu_state.accelerometer)}")
            except Exception as e:
                print(f"imu read failed: {e}")


if __name__ == "__main__":
    main()
