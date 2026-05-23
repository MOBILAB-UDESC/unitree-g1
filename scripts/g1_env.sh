#!/usr/bin/env bash
set -e

export G1_IFACE=enp194s0
export G1_HOST_IP=192.168.123.99
export G1_MCU_IP=192.168.123.161
export G1_PC2_IP=192.168.123.164

export CYCLONEDDS_URI='<CycloneDDS><Domain><General><Interfaces><NetworkInterface name="enp194s0" priority="default" multicast="default" /></Interfaces><AllowMulticast>true</AllowMulticast></General></Domain></CycloneDDS>'
