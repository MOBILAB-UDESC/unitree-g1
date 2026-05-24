#!/usr/bin/env python3

import argparse
import json
import time

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.g1.arm.g1_arm_action_client import G1ArmActionClient, action_map
from unitree_sdk2py.g1.loco.g1_loco_api import (
    ROBOT_API_ID_LOCO_GET_FSM_ID,
    ROBOT_API_ID_LOCO_GET_FSM_MODE,
)
from unitree_sdk2py.g1.loco.g1_loco_client import LocoClient


ERROR_HINTS = {
    0: "success",
    3104: "client timeout; service/topic may be unreachable",
    3203: "server API not implemented",
    3204: "server rejected parameter",
    7400: "rt/arm_sdk is occupied",
    7401: "arm is holding; send release arm or repeat last action",
    7402: "invalid arm action id",
    7404: "invalid FSM; requires fsm_id 500/501 or 801 with fsm_mode 0/3",
}


def explain(code):
    return ERROR_HINTS.get(code, "unknown")


def get_loco_value(client, api_id):
    code, data = client._Call(api_id, "{}")
    if code != 0 or not data:
        return code, None
    try:
        return code, json.loads(data).get("data")
    except json.JSONDecodeError:
        return code, data


def resolve_action(name_or_id):
    if name_or_id in action_map:
        return action_map[name_or_id], name_or_id

    try:
        action_id = int(name_or_id)
    except ValueError as exc:
        known = ", ".join(sorted(action_map))
        raise SystemExit(f"unknown action {name_or_id!r}. Known names: {known}") from exc

    return action_id, str(action_id)


def main():
    parser = argparse.ArgumentParser(description="Run or diagnose the G1 arm wave action demo.")
    parser.add_argument("iface", help="network interface connected to the robot")
    parser.add_argument("--domain", type=int, default=0, help="DDS domain id")
    parser.add_argument(
        "--action",
        default="high wave",
        help="action name from action_map or numeric action id. Default: high wave",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="execute release arm followed by the selected action",
    )
    parser.add_argument("--no-release", action="store_true", help="do not send release arm first")
    args = parser.parse_args()

    ChannelFactoryInitialize(args.domain, args.iface)

    loco = LocoClient()
    loco.SetTimeout(10.0)
    loco.Init()

    arm = G1ArmActionClient()
    arm.SetTimeout(10.0)
    arm.Init()

    fsm_id = get_loco_value(loco, ROBOT_API_ID_LOCO_GET_FSM_ID)
    fsm_mode = get_loco_value(loco, ROBOT_API_ID_LOCO_GET_FSM_MODE)
    print("sport server api version:", loco.GetServerApiVersion())
    print("arm server api version:", arm.GetServerApiVersion())
    print("fsm_id:", fsm_id)
    print("fsm_mode:", fsm_mode)
    print("action list:", arm.GetActionList())

    action_id, action_label = resolve_action(args.action)
    print(f"selected action: {action_label!r} id={action_id}")
    print("Arm actions require fsm_id 500, 501, or 801 with fsm_mode 0/3.")

    if not args.execute:
        print("Dry run. Pass --execute to send commands.")
        return

    if not args.no_release:
        code = arm.ExecuteAction(action_map["release arm"])
        print(f"release arm: code={code} ({explain(code)})")
        time.sleep(1.0)

    code = arm.ExecuteAction(action_id)
    print(f"{action_label}: code={code} ({explain(code)})")


if __name__ == "__main__":
    main()
