# AGENTS.md

## Repo Shape

- This repo is a thin `uv`-managed project around the vendored Unitree SDK2 Python package in `packages/unitree_sdk2_python/` plus G1 helper scripts in `scripts/`.

## Network Interface
- Robot-facing commands require the host network interface name, e.g. `enp194s0`; this is machine-specific.
- Use `ip link` or `ip addr` and look for the wired interface on the G1 subnet, commonly `192.168.123.x`.
- More setup/network context is in the README and linked wiki: `https://github.com/MOBILAB-UDESC/wiki`.

## G1/R3-1 Operational Gotchas
- G1 arm actions require `fsm_id` `500`, `501`, or `801`; for `801`, `fsm_mode` must be `0` or `3`.
- Confirmed working state for host-side arm wave: `fsm_id=(0, 801)` and `fsm_mode=(0, 0)`.
- `fsm_id=(0, 1)` is Damp; arm actions will return `7404` in this state.
- On R3-1/newer G1 docs, `L2 + B` is damping/soft emergency stop; do not press it before arm demos unless stopping the robot.
- Controller sequence to leave damping: `L2 + UP` for ready posture, `R2 + A` for motion state, `START` to toggle stand/walk. Keep sticks centered during transitions.

## Scripts
- Current kept scripts are intentionally named `g1_<verb>_<part>.py` or `.sh`:
  `g1_monitor_fsm.py`, `g1_action_arm_wave.py`, `g1_monitor_controller.py`, `g1_monitor_lowstate.py`, `g1_config_env.sh`.
- `g1_monitor_controller.py` reads `LowState.wireless_remote`; if sticks/buttons stay zero, the controller is likely not paired or not received.
- Avoid reintroducing old exploratory script names unless there is a new use case; removed names include `g1_motion_switcher_diag.py`, `g1_loco_diag.py`, `read_g1_lowstate_min.py`, and `probe_g1_lowstate_callback.py`.

## Return Codes Worth Knowing
- `0`: success.
- `3203`: service/API not implemented by current robot firmware.
- `7004`: motion switcher mode change failed or was rejected.
- `7400`: `rt/arm_sdk` is occupied.
- `7401`: arm is holding; send `release arm` or repeat the same action.
- `7402`: invalid arm action ID.
- `7404`: invalid FSM for arm action; check `g1_monitor_fsm.py` before debugging networking.
