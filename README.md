# Unitree G1 python SDK 2 environment and scripts

## Setup

This repository uses `uv` for Python environment management.

`bash
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

## Running examples

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
