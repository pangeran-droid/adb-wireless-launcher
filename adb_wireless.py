#!/usr/bin/env python3
"""
ADB Wireless & Scrcpy Auto Launcher (cross-platform: Windows, macOS, Linux)
devops by github.com/pangeran-droid

Needs only Python 3.7+ and the standard library.

Usage:
    python adb_wireless.py [options] [scrcpy options]

Options:
    -h, --help       Show this help and exit
    --pair           Use Android 11+ Wireless Debugging (adb pair), no USB cable
    --adb-port N     TCP port used for adb over Wi-Fi (default 5555)

Every other argument is passed straight to scrcpy, for example:
    python adb_wireless.py --max-size 1280 --stay-awake
"""

import glob
import ipaddress
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time

SYSTEM = platform.system()  # "Windows", "Darwin" or "Linux"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

ADB = "adb"
SCRCPY = "scrcpy"

# ------------------------------------------
# Output helpers
# ------------------------------------------
ANSI_RE = re.compile(r"\033\[[0-9;]*m")
USE_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def setup_console():
    if os.name == "nt":
        os.system("")  # enables ANSI escape sequences on Windows 10+
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def out(text=""):
    if not USE_COLOR:
        text = ANSI_RE.sub("", text)
    print(text, flush=True)


def info(msg):
    out("[+] " + msg)


def warn(msg):
    out("[!] " + msg)


def fail(msg, code=1):
    out("[-] " + msg)
    sys.exit(code)


def ask(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        fail("No input available (non-interactive session). Exiting.")


def confirm(prompt, default_yes):
    suffix = "(Y/n)" if default_yes else "(y/n)"
    answer = ask("[?] %s %s: " % (prompt, suffix)).lower()
    if not answer:
        return default_yes
    return answer.startswith("y")


BANNER = [
    "\033[0;37m▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄  ▄▄  ▄▄▄▄▄▄▄▄\033[0m",
    "\033[0;97;47m▒▒░░░░░░░░░▒▒░░░░\033[0;37m \033[0;94m▄\033[0;34m▄░\033[0;97;47m░▒\033[0;37m \033[0;94m▄\033[0;34m▄░\033[0;97;47m░░░░░░\033[0m Wireless & Scrcpy Launcher",
    "\033[0;37m▓▀\033[0;94m▄\033[0;34m▄░\033[0;37m▄ \033[0;94m▄\033[0;34m▄░\033[0;37m█▓▀\033[0;94m▄\033[0;34m▄░\033[0;37m▄ \033[0;34m░\033[0;37m  █▓ \033[0;34m░\033[0;37m  ▄   ▀█\033[0m",
    "\033[0;90;47m░\033[0;37m \033[0;34m░\033[0;37m  \033[0;90;47m▒\033[0;37m \033[0;34m░\033[0;37m  \033[0;90;47m▒░\033[0;37m \033[0;34m░\033[0;37m  \033[0;90;47m▒\033[0;37m    \033[0;90;47m▒░\033[0;37m \033[0;34m░\033[0;37m  \033[0;90;47m▒\033[0;37m \033[0;94m▄\033[0;34m▄░\033[0;90;47m▒\033[0m",
    "\033[0;90;47m▒\033[0;37m    \033[0;90;47m▓\033[0;37m    \033[0;90;47m▓▒\033[0;37m    \033[0;90;47m▓\033[0;37m    \033[0;90;47m▓▒\033[0;37m    \033[0;90;47m▓\033[0;37m \033[0;34m░\033[0;37m  \033[0;90;47m▓\033[0m",
    "\033[0;90m▀\033[0;36m▄▄▄▄\033[0;90m▀\033[0;36m▄▄▄▄\033[0;90m▀▀\033[0;36m▄▄▄▄\033[0;90m▀\033[0;36m▄▄▄▄\033[0;90m▀▀\033[0;36m▄▄▄▄\033[0;90m▀\033[0;36m▄▄▄▄\033[0;90m▀\033[0m",
    "\033[0;37m \033[0;96;46m▒\033[0;91;46m██\033[0;37;46m▓\033[0;37m \033[0;36m█\033[0;91;46m█▓░\033[0;37m  \033[0;96;46m▒\033[0;91;46m██\033[0;37;46m▓\033[0;37m \033[0;36m█\033[0;91;46m█▓░\033[0;37m  \033[0;96;46m▒\033[0;91;46m██\033[0;37;46m▓\033[0;37m \033[0;36m█\033[0;91;46m█▓░\033[0;37m \033[0m",
    "\033[0;37m  \033[0;96m▀\033[0;36m▀▀▀▀▀▀▀▀\033[0;37m  \033[0;96m▀\033[0;36m▀▀▀▀▀▀▀▀\033[0;37m \033[0;36m▀\033[0;96m▀\033[0;36m▀▀▀▀▀▀\033[0;37m  \033[0m",
]


def show_banner():
    out()
    for line in BANNER:
        out(line)
    out()


# ------------------------------------------
# Finding / installing adb and scrcpy
# ------------------------------------------
def extra_search_dirs():
    dirs = [SCRIPT_DIR]
    if SYSTEM == "Windows":
        local = os.environ.get("LOCALAPPDATA", "")
        program_data = os.environ.get("ProgramData", "C:\\ProgramData")
        home = os.path.expanduser("~")
        dirs += [
            os.path.join(local, "Microsoft", "WinGet", "Links"),
            os.path.join(home, "scoop", "shims"),
            os.path.join(program_data, "chocolatey", "bin"),
        ]
        pkgs = os.path.join(local, "Microsoft", "WinGet", "Packages")
        dirs += glob.glob(os.path.join(pkgs, "Genymobile.scrcpy*"))
        dirs += glob.glob(os.path.join(pkgs, "Genymobile.scrcpy*", "scrcpy-*"))
        dirs += glob.glob(os.path.join(pkgs, "Google.PlatformTools*", "platform-tools"))
    elif SYSTEM == "Darwin":
        dirs += ["/opt/homebrew/bin", "/usr/local/bin"]
    else:
        dirs += ["/snap/bin", "/usr/local/bin", os.path.expanduser("~/.local/bin")]
    return [d for d in dirs if d and os.path.isdir(d)]


def find_tool(name):
    path = shutil.which(name)
    if path:
        return path
    return shutil.which(name, path=os.pathsep.join(extra_search_dirs()))


def detect_pm():
    if SYSTEM == "Windows":
        order = ["winget", "scoop", "choco"]
    elif SYSTEM == "Darwin":
        order = ["brew"]
    else:
        order = ["apt-get", "pacman", "dnf", "zypper", "brew"]
    for pm in order:
        if shutil.which(pm):
            return pm
    return None


def install_commands(pm, tool):
    """Return the list of commands that install `tool` with package manager `pm`."""
    sudo = []
    if hasattr(os, "geteuid") and os.geteuid() != 0 and pm in ("apt-get", "pacman", "dnf", "zypper"):
        sudo = ["sudo"]

    if pm == "apt-get":
        pkg = "android-tools-adb" if tool == "adb" else "scrcpy"
        return [sudo + ["apt-get", "update"], sudo + ["apt-get", "install", "-y", pkg]]
    if pm == "pacman":
        pkg = "android-tools" if tool == "adb" else "scrcpy"
        return [sudo + ["pacman", "-S", "--needed", pkg]]
    if pm == "dnf":
        pkg = "android-tools" if tool == "adb" else "scrcpy"
        return [sudo + ["dnf", "install", "-y", pkg]]
    if pm == "zypper":
        pkg = "android-tools" if tool == "adb" else "scrcpy"
        return [sudo + ["zypper", "install", "-y", pkg]]
    if pm == "brew":
        if tool == "adb":
            return [["brew", "install", "--cask", "android-platform-tools"]]
        return [["brew", "install", "scrcpy"]]
    # On Windows the scrcpy package already bundles adb.
    if pm == "winget":
        return [["winget", "install", "--id", "Genymobile.scrcpy", "-e",
                 "--accept-package-agreements", "--accept-source-agreements"]]
    if pm == "scoop":
        return [["scoop", "install", "scrcpy"]]
    if pm == "choco":
        return [["choco", "install", "scrcpy", "-y"]]
    return []


def ensure_tool(tool):
    path = find_tool(tool)
    if path:
        return path

    pm = detect_pm()
    if not pm:
        fail("'%s' is not installed and no supported package manager was found.\n"
             "    Install it manually (scrcpy releases bundle adb for Windows/macOS/Linux):\n"
             "    https://github.com/Genymobile/scrcpy/releases" % tool)

    if not confirm("'%s' is not found. Install it now with %s?" % (tool, pm), False):
        fail("'%s' is required. Exiting." % tool)

    info("Installing %s..." % tool)
    for cmd in install_commands(pm, tool):
        try:
            code = subprocess.call(cmd)
        except OSError as exc:
            fail("Could not run %s: %s" % (cmd[0], exc))
        if code != 0:
            fail("Failed to install '%s' (command: %s)." % (tool, " ".join(cmd)))

    path = find_tool(tool)
    if not path:
        fail("'%s' was installed but is not visible yet. "
             "Open a new terminal and run this script again." % tool)
    return path


def check_scrcpy_version():
    try:
        proc = subprocess.run([SCRCPY, "--version"], stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, universal_newlines=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return
    match = re.search(r"scrcpy\s+(\d+)\.(\d+)", proc.stdout or "")
    if match and int(match.group(1)) < 2:
        warn("scrcpy %s.%s is quite old. Newer versions are faster and have more features:"
             % (match.group(1), match.group(2)))
        warn("https://github.com/Genymobile/scrcpy/releases")


# ------------------------------------------
# adb helpers
# ------------------------------------------
def run_adb(*args, **kwargs):
    """Run adb and return (returncode, combined text output). Never raises on failure."""
    serial = kwargs.get("serial")
    timeout = kwargs.get("timeout", 30)
    cmd = [ADB]
    if serial:
        cmd += ["-s", serial]
    cmd += list(args)
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True, errors="replace", timeout=timeout)
        return proc.returncode, (proc.stdout or "").replace("\r", "")
    except subprocess.TimeoutExpired:
        return 124, "adb timed out"
    except OSError as exc:
        return 127, str(exc)


def is_wireless(serial):
    return ":" in serial or "_adb-tls-" in serial


def list_devices():
    """Return a list of (serial, state) from `adb devices`."""
    code, text = run_adb("devices")
    if code != 0:
        fail("`adb devices` failed:\n" + text.strip())
    devices = []
    for line in text.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and not line.startswith("*"):
            devices.append((parts[0], parts[1]))
    return devices


def device_model(serial):
    code, text = run_adb("shell", "getprop", "ro.product.model", serial=serial, timeout=10)
    return text.strip() if code == 0 and text.strip() else "unknown model"


def choose_device(serials, label):
    if len(serials) == 1:
        return serials[0]
    warn("Multiple %s devices detected:" % label)
    for i, serial in enumerate(serials, 1):
        out("    %d) %s  %s" % (i, serial, device_model(serial)))
    while True:
        pick = ask("[?] Select device [1-%d]: " % len(serials))
        if pick.isdigit() and 1 <= int(pick) <= len(serials):
            return serials[int(pick) - 1]
        out("[-] Invalid choice.")


def valid_ip(text):
    if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", text):
        return False
    return all(int(part) <= 255 for part in text.split("."))


def host_ip_towards(ip):
    """Local source address this computer would use to reach `ip` (sends no packet)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect((ip, 9))
        return sock.getsockname()[0]
    except OSError:
        return None
    finally:
        sock.close()


def device_ipv4_interfaces(serial):
    """IPv4 interfaces of the phone, without loopback and link-local ones."""
    code, text = run_adb("shell", "ip", "-o", "-4", "addr", "show", serial=serial, timeout=15)
    found = []
    if code != 0:
        return found
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 4 or parts[1] == "lo":
            continue
        try:
            iface = ipaddress.ip_interface(parts[3])
        except ValueError:
            continue
        if iface.ip.is_loopback or iface.ip.is_link_local:
            continue
        found.append(iface)
    return found


def detect_ip(serial):
    """Return (ip_on_same_subnet_or_empty, all_candidate_ips)."""
    interfaces = device_ipv4_interfaces(serial)
    for iface in interfaces:
        local = host_ip_towards(str(iface.ip))
        if not local:
            continue
        try:
            if ipaddress.ip_address(local) in iface.network:
                return str(iface.ip), [str(i.ip) for i in interfaces]
        except ValueError:
            continue
    return "", [str(i.ip) for i in interfaces]


def connect_with_retry(target, attempts=6):
    text = ""
    for _ in range(attempts):
        _, text = run_adb("connect", target, timeout=15)
        if re.search(r"connected to|already connected", text):
            out(text.strip())
            return True
        time.sleep(1)
    out(text.strip())
    return False


# ------------------------------------------
# Argument parsing
# ------------------------------------------
def parse_args(argv):
    pair = False
    port = 5555
    scrcpy_args = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("-h", "--help"):
            print(__doc__.strip())
            sys.exit(0)
        elif arg == "--pair":
            pair = True
        elif arg == "--adb-port":
            i += 1
            if i >= len(argv) or not argv[i].isdigit() or not 1 <= int(argv[i]) <= 65535:
                fail("--adb-port needs a port number (1-65535).", 2)
            port = int(argv[i])
        elif arg == "--":
            scrcpy_args += argv[i + 1:]
            break
        else:
            scrcpy_args.append(arg)
        i += 1
    return pair, port, scrcpy_args


# ------------------------------------------
# Main flow
# ------------------------------------------
def connect_pair_mode():
    info("Wireless Debugging mode (Android 11+)")
    out("    On the phone: Developer options > Wireless debugging > Pair device with pairing code")
    out()
    pair_addr = ask("[?] Pairing address (IP:PORT): ")
    # `adb pair` asks for the pairing code itself, so it must keep our terminal.
    subprocess.call([ADB, "pair", pair_addr])

    target = ask("[?] Connect address (IP:PORT from the main Wireless debugging screen): ")
    info("Connecting to %s..." % target)
    if not connect_with_retry(target):
        fail("Failed to connect to %s." % target)
    return target


def connect_auto_mode(adb_port):
    """Return (target, usb_serial_or_empty, used_tcpip)."""
    info("Searching for connected Android devices...")
    devices = list_devices()

    if any(state == "unauthorized" for _, state in devices):
        warn("A device is 'unauthorized'. Unlock the phone and accept the USB debugging prompt.")
    if any(state == "offline" for _, state in devices):
        warn("A device is 'offline'. Replug the cable or run: adb kill-server")

    wireless = [s for s, state in devices if state == "device" and is_wireless(s)]
    usb = [s for s, state in devices if state == "device" and not is_wireless(s)]

    if wireless:
        target = choose_device(wireless, "wireless")
        info("Existing wireless device found: %s" % target)
        info("Reusing existing wireless connection.")
        return target, "", False

    if not usb:
        out("[-] No authorized USB or wireless device detected.")
        out("    - Enable USB debugging and plug in the cable, or")
        out("    - Run with --pair to use Wireless Debugging (Android 11+).")
        sys.exit(1)

    usb_serial = choose_device(usb, "USB")
    info("Using USB device: %s" % usb_serial)

    info("Fetching device IP address...")
    ip_address, candidates = detect_ip(usb_serial)
    if ip_address:
        info("IP acquired successfully: %s" % ip_address)
    else:
        warn("Could not detect an IP on the same network as this computer.")
        if candidates:
            warn("The phone reports: %s" % ", ".join(candidates))
        while True:
            ip_address = ask("[?] Enter Android device IP manually: ")
            if valid_ip(ip_address):
                break
            out("[-] Invalid IP address.")

    info("Restarting ADB in TCP/IP mode (port %d)..." % adb_port)
    code, text = run_adb("tcpip", str(adb_port), serial=usb_serial)
    out(text.strip())
    if code != 0:
        fail("`adb tcpip` failed.")

    target = "%s:%d" % (ip_address, adb_port)
    info("Connecting to %s..." % target)
    if not connect_with_retry(target):
        out("[-] Failed to connect to %s over Wi-Fi." % target)
        out("    Make sure the phone and this computer are on the same network.")
        sys.exit(1)
    return target, usb_serial, True


def cleanup(target, used_tcpip):
    out()
    warn("An open ADB port on a shared Wi-Fi network is a security risk.")
    if confirm("Disconnect wireless ADB now?", True):
        if used_tcpip:
            info("Switching phone back to USB mode...")
            run_adb("usb", serial=target, timeout=10)
            time.sleep(1)
        run_adb("disconnect", target, timeout=10)
        info("Disconnected from %s." % target)
    else:
        info("Connection left open. Run 'adb disconnect %s' when you are done." % target)


def main():
    global ADB, SCRCPY

    setup_console()
    pair_mode, adb_port, scrcpy_args = parse_args(sys.argv[1:])

    ADB = ensure_tool("adb")
    SCRCPY = ensure_tool("scrcpy")
    os.environ["ADB"] = ADB  # make scrcpy use the very same adb binary
    check_scrcpy_version()

    show_banner()

    try:
        if pair_mode:
            target, usb_serial, used_tcpip = connect_pair_mode(), "", False
        else:
            target, usb_serial, used_tcpip = connect_auto_mode(adb_port)
    except KeyboardInterrupt:
        out()
        fail("Cancelled.", 130)

    out("-----------------------------------")
    _, text = run_adb("devices")
    out(text.strip())
    out("-----------------------------------")

    info("Wireless ADB ready!")
    info("Target: %s" % target)
    if usb_serial:
        info("You can unplug the USB cable.")

    info("Launching scrcpy on %s..." % target)
    try:
        status = subprocess.call([SCRCPY, "-s", target] + scrcpy_args)
    except KeyboardInterrupt:
        status = 130
    except OSError as exc:
        out("[-] Could not start scrcpy: %s" % exc)
        status = 1

    try:
        cleanup(target, used_tcpip)
    except KeyboardInterrupt:
        out()
    return status


if __name__ == "__main__":
    sys.exit(main())