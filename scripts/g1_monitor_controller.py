#!/usr/bin/env python3

import argparse
import struct
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize, ChannelSubscriber
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_


BUTTONS_1 = ["R1", "L1", "Start", "Select", "R2", "L2", "F1", "F3"]
BUTTONS_2 = ["A", "B", "X", "Y", "Up", "Right", "Down", "Left"]


def parse_remote(data):
    raw = bytes(data)
    if len(raw) < 24:
        raise ValueError(f"wireless_remote has {len(raw)} bytes, expected at least 24")

    buttons = {}
    for i, name in enumerate(BUTTONS_1):
        buttons[name] = (raw[2] >> i) & 1
    for i, name in enumerate(BUTTONS_2):
        buttons[name] = (raw[3] >> i) & 1

    sticks = {
        "Lx": struct.unpack("<f", raw[4:8])[0],
        "Rx": struct.unpack("<f", raw[8:12])[0],
        "Ry": struct.unpack("<f", raw[12:16])[0],
        "Ly": struct.unpack("<f", raw[20:24])[0],
    }

    return sticks, buttons, list(raw)


class TopicState:
    def __init__(self, name):
        self.name = name
        self.count = 0
        self.last_msg = None

    def handler(self, msg):
        self.count += 1
        self.last_msg = msg


def main():
    parser = argparse.ArgumentParser(
        description="Monitor G1 R3-1 controller data from LowState.wireless_remote."
    )
    parser.add_argument("iface", help="network interface connected to the robot")
    parser.add_argument("--domain", type=int, default=0, help="DDS domain id")
    parser.add_argument(
        "--raw",
        action="store_true",
        help="also print the raw 40-byte wireless_remote array",
    )
    parser.add_argument(
        "--topic",
        action="append",
        default=None,
        help="topic to subscribe; may be repeated. Defaults to rt/lowstate and rt/lf/lowstate",
    )
    args = parser.parse_args()

    topics = args.topic or ["rt/lowstate", "rt/lf/lowstate"]

    ChannelFactoryInitialize(args.domain, args.iface)

    states = []
    subscribers = []
    for topic in topics:
        state = TopicState(topic)
        sub = ChannelSubscriber(topic, LowState_)
        sub.Init(state.handler, 10)
        states.append(state)
        subscribers.append(sub)
        print(f"subscribed: {topic}")

    print("Read-only. Press controller buttons/sticks; Ctrl+C to stop.")
    print("If values stay zero, the controller is probably not paired or not received.")

    last_counts = {state.name: 0 for state in states}
    last_time = time.time()

    while True:
        time.sleep(1.0)
        now = time.time()
        elapsed = max(now - last_time, 1e-6)
        last_time = now

        for state in states:
            hz = (state.count - last_counts[state.name]) / elapsed
            last_counts[state.name] = state.count

            if state.last_msg is None:
                print(f"{state.name}: no data yet")
                continue

            sticks, buttons, raw = parse_remote(state.last_msg.wireless_remote)
            pressed = [name for name, value in buttons.items() if value]
            print(
                f"{state.name}: hz={hz:.1f} "
                f"sticks={sticks} pressed={pressed or []}"
            )
            if args.raw:
                print(f"{state.name}: raw={raw}")


if __name__ == "__main__":
    main()
