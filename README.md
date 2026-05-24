# Unitree G1 python SDK 2 environment and scripts

## Setup

This repository uses `uv` for Python environment management.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv python install 3.10
uv sync
uv pip install -e packages/unitree_sdk2_python
```

## Verify

Run a quick import check:

```bash
uv run python -c "import cyclonedds, numpy, cv2, unitree_sdk2py; print('ok')"
```

## Find The Robot Network Interface

Most commands need the network interface connected to the robot. In these examples that value is `enp194s0`, but it is machine-specific.

List network interfaces:

```bash
ip link
```

Or show interface addresses:

```bash
ip addr
```

Look for the wired interface connected to the G1 network. It often has an address in the robot subnet, such as `192.168.123.x`. Use that interface name in the scripts:

```bash
uv run python scripts/g1_monitor_fsm.py <interface-name>
```

Example:

```bash
uv run python scripts/g1_monitor_fsm.py enp194s0
```

More setup and network details are documented in the [wiki](https://github.com/MOBILAB-UDESC/wiki).

## Quick Demo: Monitor State And Wave

Replace `enp194s0` with the network interface connected to the robot.

This is the main workflow for running a simple host-side arm action demo:

1. Put the robot in the right state using the paired R3-1 controller.
2. Monitor the robot state from the host.
3. Execute the arm action demo from the host.

### 1. Put G1 In The Right State

Use this sequence when the R3-1 controller is already paired and the robot is currently in damping or a zero-torque-safe posture.

Start the FSM monitor in terminal A before using the controller:

```bash
uv run python scripts/g1_monitor_fsm.py enp194s0
```

Confirm the controller link before changing state. The remote should be powered on, and the right `DL` indicator should be on. The G1 manual says this means the remote is connected to the robot data transmission module.

Keep both joysticks centered while switching states. Do not touch the sticks during state transitions.

Have one person near the robot, ready to support it at the shoulders. Use the safety rope or support frame if available.

Do not press `L2 + B` again unless needed. On R3-1/newer G1 docs, `L2 + B` is damping mode, the soft emergency stop. Use it only if the robot becomes unstable or enters an unexpected state.

Enter ready state:

```text
Hold L2.
Tap UP.
Release both.
```

Expected result: the robot should move into a neutral ready posture. Newer G1 control docs describe this as `L2 + UP` to enter ready state after damping/unlock.

Enter motion state:

```text
Press R2 + A.
```

Expected result: the control program starts, and G1 transitions from ready state to motion state. Newer G1 docs list `R2 + A` for this step.

Toggle stand/walk:

```text
Press START once.
```

Expected result: `START` switches between standing and walking states.

Test motion minimally:

- Left stick: tiny forward/back or lateral input
- Right stick: tiny yaw input
- Release sticks immediately and verify the robot stops

State sequence:

```text
Zero torque / booted
        |
        |  L2 + B only if needed to enter damping/unlock
        v
Damping
        |
        |  L2 + UP
        v
Ready / neutral posture
        |
        |  R2 + A
        v
Motion state
        |
        |  START
        v
Stand <-> walk toggle
```

For arm actions from the host, the confirmed working state was:

```text
fsm_id=(0, 801) fsm_mode=(0, 0)
```

Other valid arm-action states are `fsm_id` `500`, `501`, or `801` with `fsm_mode` `0` or `3`. If the monitor shows `fsm_id=(0, 1)`, the robot is in Damp and arm actions will be rejected with `7404`.

### 2. Run The Host Demo

Keep the FSM monitor running in terminal A:

```bash
uv run python scripts/g1_monitor_fsm.py enp194s0
```

When terminal A shows a valid arm-action state, run the demo in terminal B:

```bash
uv run python scripts/g1_action_arm_wave.py enp194s0 --execute
```

This command prints the sport service version, arm service version, current FSM, available arm actions, then sends `release arm` followed by `high wave`.

Expected successful return codes:

```text
release arm: code=0
high wave: code=0
```

If the command returns `7404`, go back to terminal A and check the FSM. The robot is not in `500`, `501`, or valid `801`.

## Running SDK Examples

Replace `enp2s0` with the network interface connected to the robot.

```bash
uv run python packages/unitree_sdk2_python/example/high_level/read_highstate.py enp2s0
```

If `cyclonedds` fails to build on your machine, install system build tools first:

```bash
sudo apt update
sudo apt install -y build-essential cmake git
```

Full setup documentation in the [wiki](https://github.com/MOBILAB-UDESC/wiki)

## G1 Debug Scripts Reference

Replace `enp194s0` with the network interface connected to the robot.

All scripts are intended for diagnosis or controlled demos. `g1_monitor_controller.py`, `g1_monitor_fsm.py`, and `g1_monitor_lowstate.py` are read-only. `g1_action_arm_wave.py` is read-only unless it is run with `--execute`.

### Controller Data

Use this to verify whether an R3-1 controller is paired and its data reaches the robot:

```bash
uv run python scripts/g1_monitor_controller.py enp194s0
```

Press controller buttons and move sticks. If `pressed=[]` and all stick values stay near zero, the controller is probably not paired or not received by the robot.

Print raw `wireless_remote` bytes too:

```bash
uv run python scripts/g1_monitor_controller.py enp194s0 --raw
```

The R3-1/G1 manual says first-time remote binding is done in the Unitree Explore App under `Settings -> Remote Control Settings` by entering the remote control code. The SDK and PC2 shell can verify controller data, but no public SDK2 pairing API was found.

### FSM State

Use this to monitor the G1 sport FSM:

```bash
uv run python scripts/g1_monitor_fsm.py enp194s0
```

Print one sample and exit:

```bash
uv run python scripts/g1_monitor_fsm.py enp194s0 --once
```

For preset arm actions, the arm service requires `fsm_id` `500`, `501`, or `801`. If `fsm_id` is `801`, `fsm_mode` must be `0` or `3`. If the robot stays at `fsm_id=1`, it is in Damp and arm actions will be rejected.

### Arm Action Diagnostics

Inspect the arm service, current FSM, and available actions without moving the robot:

```bash
uv run python scripts/g1_action_arm_wave.py enp194s0
```

Execute `release arm`, then `high wave`:

```bash
uv run python scripts/g1_action_arm_wave.py enp194s0 --execute
```

Execute a different action by name or ID:

```bash
uv run python scripts/g1_action_arm_wave.py enp194s0 --action "face wave" --execute
uv run python scripts/g1_action_arm_wave.py enp194s0 --action 26 --execute
```

Common return codes seen during debugging:

- `0`: success
- `3203`: API not implemented by the robot firmware/service
- `7004`: motion switcher mode change failed or was rejected
- `7400`: `rt/arm_sdk` is occupied
- `7401`: arm is holding; send `release arm` or repeat the same action
- `7402`: invalid arm action ID
- `7404`: invalid FSM for arm action; use `g1_monitor_fsm.py` and get to `fsm_id` `500`, `501`, or valid `801`

### LowState Monitor

Read the low-level state topic for message rate, `mode_machine`, one motor sample, and IMU acceleration:

```bash
uv run python scripts/g1_monitor_lowstate.py enp194s0
```
