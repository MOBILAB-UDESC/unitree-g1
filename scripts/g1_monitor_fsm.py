#!/usr/bin/env python3

import argparse
import json
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.loco.g1_loco_api import (
    ROBOT_API_ID_LOCO_GET_BALANCE_MODE,
    ROBOT_API_ID_LOCO_GET_FSM_ID,
    ROBOT_API_ID_LOCO_GET_FSM_MODE,
    ROBOT_API_ID_LOCO_GET_STAND_HEIGHT,
    ROBOT_API_ID_LOCO_GET_SWING_HEIGHT,
)
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient


GETTERS = [
    ("fsm_id", ROBOT_API_ID_LOCO_GET_FSM_ID),
    ("fsm_mode", ROBOT_API_ID_LOCO_GET_FSM_MODE),
    ("balance_mode", ROBOT_API_ID_LOCO_GET_BALANCE_MODE),
    ("swing_height", ROBOT_API_ID_LOCO_GET_SWING_HEIGHT),
    ("stand_height", ROBOT_API_ID_LOCO_GET_STAND_HEIGHT),
]


def call_getter(client, api_id):
    code, data = client._Call(api_id, "{}")
    if code != 0 or not data:
        return code, None, data

    try:
        return code, json.loads(data).get("data"), data
    except json.JSONDecodeError:
        return code, None, data


def read_state(client):
    result = {}
    for name, api_id in GETTERS:
        code, value, raw = call_getter(client, api_id)
        result[name] = {"code": code, "value": value, "raw": raw}
    return result


def print_state(state):
    parts = []
    for name in ["fsm_id", "fsm_mode", "balance_mode", "swing_height", "stand_height"]:
        item = state[name]
        parts.append(f"{name}=({item['code']}, {item['value']})")
    print(" ".join(parts))


def main():
    parser = argparse.ArgumentParser(description="Monitor G1 sport FSM state.")
    parser.add_argument("iface", help="network interface connected to the robot")
    parser.add_argument("--domain", type=int, default=0, help="DDS domain id")
    parser.add_argument("--interval", type=float, default=1.0, help="seconds between polls")
    parser.add_argument("--once", action="store_true", help="print one sample and exit")
    parser.add_argument("--raw", action="store_true", help="print raw JSON responses")
    args = parser.parse_args()

    ChannelFactoryInitialize(args.domain, args.iface)

    client = LocoClient()
    client.SetTimeout(10.0)
    client.Init()

    print("sport server api version:", client.GetServerApiVersion())
    print("Read-only. Arm actions require fsm_id 500, 501, or 801 with fsm_mode 0/3.")

    while True:
        state = read_state(client)
        print_state(state)
        if args.raw:
            for name, item in state.items():
                print(f"  {name}.raw={item['raw']}")

        if args.once:
            return

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
