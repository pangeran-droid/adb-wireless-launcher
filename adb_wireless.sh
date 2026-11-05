#!/usr/bin/env bash

# ------------------------------------------
# ADB Wireless & Scrcpy Auto Launcher
# devops by github.com/pangeran-droid
# ------------------------------------------

set -euo pipefail

ADB_PORT=5555
PAIR_MODE=false
SCRCPY_ARGS=()

usage() {
    cat <<'EOF'
Usage: adb_wireless.sh [options] [-- scrcpy options]

Options:
  -h, --help    Show this help and exit
  --pair        Use Android 11+ Wireless Debugging (adb pair), no USB cable needed

Any other argument is passed straight to scrcpy, for example:
  ./adb_wireless.sh --max-size 1280 --stay-awake
EOF
}

while [ $# -gt 0 ]; do
    case "$1" in
        -h|--help) usage; exit 0 ;;
        --pair)    PAIR_MODE=true; shift ;;
        --)        shift; SCRCPY_ARGS+=("$@"); break ;;
        *)         SCRCPY_ARGS+=("$1"); shift ;;
    esac
done


# Package manager helpers
PM=""
for candidate_pm in apt-get pacman dnf zypper brew; do
    if command -v "$candidate_pm" >/dev/null 2>&1; then
        PM="$candidate_pm"
        break
    fi
done

pkg_name() {
    case "$1:$PM" in
        adb:apt-get)                     echo "android-tools-adb" ;;
        adb:pacman|adb:dnf|adb:zypper)   echo "android-tools" ;;
        adb:brew)                        echo "android-platform-tools" ;;
        scrcpy:*)                        echo "scrcpy" ;;
    esac
}

install_pkg() {
    local pkg
    pkg=$(pkg_name "$1")
    case "$PM" in
        apt-get) sudo apt-get update && sudo apt-get install -y "$pkg" ;;
        pacman)  sudo pacman -S --needed "$pkg" ;;
        dnf)     sudo dnf install -y "$pkg" ;;
        zypper)  sudo zypper install -y "$pkg" ;;
        brew)
            if [ "$1" = "adb" ]; then
                brew install --cask "$pkg"
            else
                brew install "$pkg"
            fi
            ;;
        *) return 1 ;;
    esac
}

ensure_tool() {
    local tool="$1" choice

    if command -v "$tool" >/dev/null 2>&1; then
        return 0
    fi

    if [ -z "$PM" ]; then
        echo "[-] Error: '$tool' is not installed and no supported package manager was found."
        echo "    Please install '$tool' manually and run this script again."
        exit 1
    fi

    read -r -p "[?] '$tool' is not found. Install it now with $PM? (y/n): " choice

    if [[ "$choice" =~ ^[Yy]$ ]]; then
        echo "[+] Installing $tool..."
        if ! install_pkg "$tool"; then
            echo "[-] Failed to install '$tool'."
            exit 1
        fi
    else
        echo "[-] '$tool' is required. Exiting."
        exit 1
    fi

    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "[-] '$tool' still not found after installation."
        exit 1
    fi
}

ensure_tool adb

# Packaged scrcpy on some distros (e.g. Ubuntu LTS) is very old.
ensure_tool scrcpy

echo ""
echo -e "\033[0;37m                       ▄\033[0;97m▄█\033[0;37m   \033[0;97m█▄\033[0;37m▄        \033[0m"
echo -e "\033[0;37m                      \033[0;97m████\033[0;37m   \033[0;97m████\033[0;37m       \033[0m"
echo -e "\033[0;37m                      \033[0;97m█\033[0;97;47m▓▓\033[0;97m█\033[0;37m   \033[0;97m█\033[0;97;47m▓▓\033[0;37m█\033[0;37m       \033[0m Wireless & Scrcpy Launcher"
echo -e "\033[0;37m  \033[0;97m▄▄\033[0;97;47m█▓\033[0;97m██\033[0;97;47m▓█\033[0;97m▄▄\033[0;37m      \033[0;97m▄▄▄\033[0;37m \033[0;97;47m▒▒▓▓\033[0;97m▄\033[0;37m \033[0;97m▄\033[0;97;47m▓▓▒▒\033[0;37m \033[0;97m▄▄▄\033[0;37m   \033[0m"
echo -e "\033[0;37m \033[0;97;47m▓\033[0;37m▀\033[0;97;47m▓▓\033[0;37m▀  ▀\033[0;97;47m▓▓\033[0;97m█\033[0;97;47m▓\033[0;37m   \033[0;97m▄\033[0;97;47m▒▓\033[0;97m█▀▀\033[0;37m█\033[0;97;47m░▒\033[0;97m▀\033[0;37m   \033[0;97m▀\033[0;97;47m▒░\033[0;37m█\033[0;97m▀▀█\033[0;97;47m▓▒\033[0;37m▄ \033[0m"
echo -e "\033[0;97;47m▒▒░░\033[0;37m      \033[0;97;47m░░▒▒\033[0;37m ▄\033[0;97;47m░░▒\033[0;37m   ██\033[0;97;47m░▒\033[0;37m   \033[0;97;47m▒░\033[0;37m██   \033[0;97;47m▒░░\033[0;37m▄\033[0m"
echo -e "\033[0;37m▀\033[0;97;47m░░\033[0;37m█▄    ▄█\033[0;97;47m░░\033[0;37m█ ▀██\033[0;97;47m░\033[0;37m   ███\033[0;97;47m░\033[0;37m   \033[0;97;47m░\033[0;37m███   \033[0;97;47m░\033[0;37m██▀\033[0m"
echo -e "\033[0;37m  ▀███▄▄██████  ▀██▌ ▐████   ████▌ ▐██▀ \033[0m"
echo -e "\033[0;37m    ▀▀▀▀▀▀ ▀▀▀    ▀███▀ ▀█   █▀ ▀███▀   \033[0m"
echo ""


# Helpers
# List authorized devices. $1 = wireless | usb
list_devices() {
    adb devices | awk -v kind="$1" '
        NR > 1 && $2 == "device" {
            w = ($1 ~ /:/ || $1 ~ /_adb-tls-/)
            if ((kind == "wireless" && w) || (kind == "usb" && !w)) print $1
        }
    '
}

valid_ip() {
    local ip="$1" o
    local IFS=.
    [[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]] || return 1
    for o in $ip; do
        [ "$((10#$o))" -le 255 ] || return 1
    done
    return 0
}

# Print the device IP that is directly reachable from this machine (same subnet).
detect_ip() {
    local dev="$1" candidates cand route

    candidates=$(adb -s "$dev" shell ip -o -4 addr show 2>/dev/null |
        tr -d '\r' |
        awk '
            $2 != "lo" {
                split($4, addr, "/")
                ip = addr[1]
                if (ip !~ /^127\./ && ip !~ /^169\.254\./) print ip
            }
        ') || true

    if [ -z "$candidates" ]; then
        return 0
    fi

    # Host without iproute2 (e.g. macOS): cannot verify subnet, take the first candidate.
    if ! command -v ip >/dev/null 2>&1; then
        printf '%s\n' "$candidates" | sed -n '1p'
        return 0
    fi

    while read -r cand; do
        route=$(ip -4 route get "$cand" 2>/dev/null | head -n 1) || true
        if [ -n "$route" ] && [[ "$route" != *" via "* ]]; then
            echo "$cand"
            return 0
        fi
    done <<< "$candidates"

    return 0
}

connect_with_retry() {
    local target="$1" out i

    for i in 1 2 3 4 5 6; do
        out=$(adb connect "$target" 2>&1 || true)
        if echo "$out" | grep -qE "connected to|already connected"; then
            echo "$out"
            return 0
        fi
        sleep 1
    done

    echo "$out"
    return 1
}


# Establish connection
TARGET=""
USB_DEVICE_ID=""
USED_TCPIP=false

if [ "$PAIR_MODE" = true ]; then

    echo "[+] Wireless Debugging mode (Android 11+)"
    echo "    On the phone: Developer options > Wireless debugging > Pair device with pairing code"
    echo ""

    read -r -p "[?] Pairing address (IP:PORT): " PAIR_ADDR
    adb pair "$PAIR_ADDR"

    read -r -p "[?] Connect address (IP:PORT from the main Wireless debugging screen): " TARGET

    echo "[+] Connecting to $TARGET..."
    if ! connect_with_retry "$TARGET"; then
        echo "[-] Failed to connect to $TARGET."
        exit 1
    fi

else

    echo "[+] Searching for connected Android devices..."

    if adb devices | awk 'NR > 1 && $2 == "unauthorized" { f = 1 } END { exit !f }'; then
        echo "[!] A device is 'unauthorized'. Unlock the phone and accept the USB debugging prompt."
    fi

    WIRELESS_DEVICE=$(list_devices wireless | sed -n '1p')

    if [ -n "$WIRELESS_DEVICE" ]; then

        TARGET="$WIRELESS_DEVICE"
        echo "[+] Existing wireless device found: $TARGET"
        echo "[+] Reusing existing wireless connection."

    else

        USB_DEVICES=()
        while IFS= read -r line; do
            if [ -n "$line" ]; then
                USB_DEVICES+=("$line")
            fi
        done < <(list_devices usb)

        if [ "${#USB_DEVICES[@]}" -eq 0 ]; then
            echo "[-] No authorized USB or wireless device detected."
            echo "    - Enable USB debugging and plug in the cable, or"
            echo "    - Run with --pair to use Wireless Debugging (Android 11+)."
            exit 1
        fi

        if [ "${#USB_DEVICES[@]}" -eq 1 ]; then
            USB_DEVICE_ID="${USB_DEVICES[0]}"
        else
            echo "[!] Multiple USB devices detected:"
            idx=1
            for d in "${USB_DEVICES[@]}"; do
                model=$(adb -s "$d" shell getprop ro.product.model 2>/dev/null | tr -d '\r') || true
                echo "    $idx) $d  ${model:-unknown model}"
                idx=$((idx + 1))
            done

            while true; do
                read -r -p "[?] Select device [1-${#USB_DEVICES[@]}]: " pick
                if [[ "$pick" =~ ^[0-9]+$ ]] && [ "$pick" -ge 1 ] && [ "$pick" -le "${#USB_DEVICES[@]}" ]; then
                    USB_DEVICE_ID="${USB_DEVICES[$((pick - 1))]}"
                    break
                fi
                echo "[-] Invalid choice."
            done
        fi

        echo "[+] Using USB device: $USB_DEVICE_ID"

        # Retrieve Android IP address automatically
        echo "[+] Fetching device IP address..."
        IP_ADDRESS=$(detect_ip "$USB_DEVICE_ID")

        # Manual fallback
        if [ -z "$IP_ADDRESS" ]; then
            echo "[!] Could not detect IP automatically."

            while true; do
                read -r -p "[?] Enter Android device IP manually: " IP_ADDRESS
                if valid_ip "$IP_ADDRESS"; then
                    break
                fi
                echo "[-] Invalid IP address."
            done
        else
            echo "[+] IP acquired successfully: $IP_ADDRESS"
        fi

        # Enable ADB TCP/IP
        echo "[+] Restarting ADB in TCP/IP mode (port $ADB_PORT)..."
        adb -s "$USB_DEVICE_ID" tcpip "$ADB_PORT"
        USED_TCPIP=true

        TARGET="$IP_ADDRESS:$ADB_PORT"

        echo "[+] Connecting to $TARGET..."
        if ! connect_with_retry "$TARGET"; then
            echo "[-] Failed to connect to $TARGET over Wi-Fi."
            echo "    Make sure the phone and this computer are on the same network."
            exit 1
        fi
    fi
fi


# Verify connection
echo "-----------------------------------"
adb devices
echo "-----------------------------------"

echo "[+] Wireless ADB ready!"
echo "[+] Target: $TARGET"
if [ -n "$USB_DEVICE_ID" ]; then
    echo "[+] You can unplug the USB cable."
fi


# Launch scrcpy
echo "[+] Launching scrcpy on $TARGET..."

set +e
scrcpy -s "$TARGET" ${SCRCPY_ARGS[@]+"${SCRCPY_ARGS[@]}"}
SCRCPY_STATUS=$?
set -e


# Cleanup
echo ""
echo "[!] An open ADB port on a shared Wi-Fi network is a security risk."
read -r -p "[?] Disconnect wireless ADB now? (Y/n): " cleanup_choice

if [[ ! "$cleanup_choice" =~ ^[Nn]$ ]]; then
    if [ "$USED_TCPIP" = true ]; then
        echo "[+] Switching phone back to USB mode..."
        adb -s "$TARGET" usb >/dev/null 2>&1 || true
        sleep 1
    fi
    adb disconnect "$TARGET" >/dev/null 2>&1 || true
    echo "[+] Disconnected from $TARGET."
else
    echo "[+] Connection left open. Run 'adb disconnect $TARGET' when you are done."
fi

exit "$SCRCPY_STATUS"