#!/usr/bin/env bash

# ==========================================
# ADB Wireless & Scrcpy Auto Launcher
# ==========================================

set -euo pipefail

# Ensure ADB is installed before proceeding
if ! command -v adb &> /dev/null; then
    echo "[-] Error: 'adb' is not installed. Please install it first:"
    echo "    sudo apt install android-tools-adb"
    exit 1
fi

echo "=== ADB Wireless & Scrcpy Launcher ==="

# Detect the first connected USB device (must be in 'device' state, not 'unauthorized'/'offline')
echo "[+] Searching for connected Android devices..."
DEVICE_ID=$(adb devices | awk 'NR>1 && $2=="device" {print $1; exit}')

if [ -z "$DEVICE_ID" ]; then
    echo "[-] No authorized device detected via USB."
    echo "    Connect your phone and make sure 'USB debugging' is allowed on it."
    exit 1
fi

echo "[+] Target device found: $DEVICE_ID"

# Switch device to TCP/IP mode on port 5555
echo "[+] Restarting ADB in TCP/IP mode (port 5555)..."
adb -s "$DEVICE_ID" tcpip 5555
sleep 2

# Retrieve device IP address automatically
echo "[+] Fetching device IP address..."
IP_ADDRESS=$(adb -s "$DEVICE_ID" shell ip route 2>/dev/null | awk '/wlan0/ {for(i=1;i<=NF;i++) if ($i=="src") print $(i+1)}' | head -n 1)

# Fallback method if route parsing fails
if [ -z "$IP_ADDRESS" ]; then
    IP_ADDRESS=$(adb -s "$DEVICE_ID" shell ip -f inet addr show wlan0 2>/dev/null | grep inet | awk '{print $2}' | cut -d/ -f1)
fi

# Manual prompt if automatic detection fails entirely
if [ -z "$IP_ADDRESS" ]; then
    echo "[!] Could not detect IP automatically. Please enter it manually:"
    read -r -p "Device IP (e.g., 192.168.1.5): " IP_ADDRESS
else
    echo "[+] IP acquired successfully: $IP_ADDRESS"
fi

if [ -z "$IP_ADDRESS" ]; then
    echo "[-] No IP address provided. Aborting."
    exit 1
fi

# Establish wireless connection
TARGET="$IP_ADDRESS:5555"
echo "[+] Connecting to $TARGET..."
CONNECT_OUTPUT=$(adb connect "$TARGET" 2>&1)
echo "$CONNECT_OUTPUT"

if ! echo "$CONNECT_OUTPUT" | grep -qE "connected to|already connected"; then
    echo "[-] Failed to connect to $TARGET over Wi-Fi."
    echo "    Make sure your phone and computer are on the same network."
    exit 1
fi

echo "-----------------------------------"
adb devices
echo "-----------------------------------"
echo "[+] Success! You can now unplug the USB cable."

# Check if scrcpy is installed
if ! command -v scrcpy &> /dev/null; then
    read -r -p "[?] 'scrcpy' is not found. Do you want to install it now? (y/n): " choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        echo "[+] Installing scrcpy..."
        sudo apt update && sudo apt install -y scrcpy
    else
        echo "[-] Scrcpy installation skipped. Exiting."
        exit 0
    fi
fi

# Launch scrcpy targeting the wireless device explicitly.
# This avoids the "more than one device/emulator" error that happens
# when the USB connection is still active alongside the new TCP/IP one.
echo "[+] Launching scrcpy on $TARGET..."
scrcpy -s "$TARGET"
