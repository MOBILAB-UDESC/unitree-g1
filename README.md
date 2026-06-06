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
uv run python scripts/g1_monitor_fsm.py enp194s0
```

Replace `enp194s0` with the network interface connected to the robot.
More setup and network details are documented in the [wiki](https://github.com/MOBILAB-UDESC/wiki).

## Quick Demo: Monitor State And Wave

This is the main workflow for running a simple host-side arm action demo:

### 1. Put G1 In The Right State

Use this sequence when the R3-1 controller is already paired and the robot is currently in damping or a zero-torque-safe posture.

- `L2 + B` to put it in damping
- `L2 + UP` to make it ready
- `R2 + A` to put it in the motion state
- `Start` to toggle stand/walk

Start the FSM monitor in terminal A before using the controller:

```bash
uv run python scripts/g1_monitor_fsm.py enp194s0
```

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

### 2. Run The Host Demo

When terminal A shows a valid arm-action state, run the demo in terminal B:

```bash
uv run python scripts/g1_action_arm_wave.py enp194s0 --execute
```

This command sends `release arm` followed by `high wave`.

Expected successful return codes:

```text
release arm: code=0
high wave: code=0
```

If the command returns `7404`, go back to terminal A and check the FSM. The robot is not in `500`, `501`, or valid `801`.

## Running SDK Examples

```bash
uv run python packages/unitree_sdk2_python/example/high_level/read_highstate.py enp194s0
```

If `cyclonedds` fails to build on your machine, install system build tools first:

```bash
sudo apt update
sudo apt install -y build-essential cmake git
```

Full setup documentation in the [wiki](https://github.com/MOBILAB-UDESC/wiki)

## G1 Debug Scripts Reference

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
