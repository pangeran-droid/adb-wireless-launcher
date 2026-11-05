<p align="center">
  <img src="https://raw.githubusercontent.com/pangeran-droid/adb-wireless-launcher/refs/heads/main/.github/image/logo.svg" alt="ADB Wireless Launcher logo" width="600"/>
</p>

<h1 align="center">ADB Wireless & Scrcpy Auto Launcher</h1>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-informational" alt="Platform: Windows, macOS, Linux">
  <img src="https://img.shields.io/badge/python-3.7%2B-3776AB?logo=python&logoColor=white" alt="Python 3.7+">
  <img src="https://img.shields.io/badge/requires-adb%20%7C%20scrcpy-blue" alt="Requires adb and scrcpy">
  <a href="https://github.com/pangeran-droid/adb-wireless-launcher/stargazers"><img src="https://img.shields.io/github/stars/pangeran-droid/adb-wireless-launcher?style=flat" alt="GitHub stars"></a>
  <a href="https://github.com/pangeran-droid/adb-wireless-launcher/issues"><img src="https://img.shields.io/github/issues/pangeran-droid/adb-wireless-launcher" alt="GitHub issues"></a>
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</p>

A lightweight, dependency-free launcher that automates **Android Wireless Debugging (ADB)** setup and instantly starts **Scrcpy** for screen mirroring. It runs on **Windows, macOS and Linux** using a single Python file (standard library only). A Bash version for Linux/macOS is also included.

## Features
- **Cross-platform:** one Python script for Windows, macOS and Linux. No `pip install` needed.
- **Auto-Detect:** finds your connected Android device via USB, with a selection menu when several are plugged in.
- **TCP/IP Switch:** restarts ADB into TCP/IP mode on port `5555` (configurable with `--adb-port`).
- **Smart IP Detection:** reads the phone's IPs and picks the one on the same subnet as your computer (so mobile-data addresses are ignored). Falls back to a manual prompt, showing the IPs the phone reported.
- **Wireless Debugging (Android 11+):** `--pair` pairs and connects without any USB cable.
- **Connection Verification:** retries `adb connect` and only continues once it really succeeded.
- **Reuses Existing Connections:** if a wireless device is already connected, it skips the setup.
- **Dependency Check:** finds `adb` and `scrcpy` (including common Windows/macOS install folders) and offers to install them with `winget`/`scoop`/`choco`, `brew`, `apt`, `pacman`, `dnf` or `zypper`.
- **Scrcpy Options Pass-through:** any extra flag goes straight to scrcpy (`--max-size 1280`, `--stay-awake`, ...).
- **Safe Cleanup:** after scrcpy closes, it offers to switch the phone back to USB mode and disconnect, so port `5555` is not left open on shared Wi-Fi.

## Example
```bash
ubuntu@ubuntu:~/adb-wireless-launcher$ python3 adb_wireless.py
[!] scrcpy 1.25 is quite old. Newer versions are faster and have more features:
[!] https://github.com/Genymobile/scrcpy/releases

▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄  ▄▄  ▄▄▄▄▄▄▄▄
▒▒░░░░░░░░░▒▒░░░░ ▄▄░░▒ ▄▄░░░░░░░ Wireless & Scrcpy Launcher
▓▀▄▄░▄ ▄▄░█▓▀▄▄░▄ ░  █▓ ░  ▄   ▀█
░ ░  ▒ ░  ▒░ ░  ▒    ▒░ ░  ▒ ▄▄░▒
▒    ▓    ▓▒    ▓    ▓▒    ▓ ░  ▓
▀▄▄▄▄▀▄▄▄▄▀▀▄▄▄▄▀▄▄▄▄▀▀▄▄▄▄▀▄▄▄▄▀
 ▒██▓ ██▓░  ▒██▓ ██▓░  ▒██▓ ██▓░ 
  ▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀ ▀▀▀▀▀▀▀▀  

[+] Searching for connected Android devices...
[+] Using USB device: LFDIXXXXXXXXXXXX
[+] Fetching device IP address...
[+] IP acquired successfully: 192.168.x.x
[+] Restarting ADB in TCP/IP mode (port 5555)...
restarting in TCP mode port: 5555
[+] Connecting to 192.168.x.x:5555...
connected to 192.168.x.x:5555
-----------------------------------
List of devices attached
192.168.x.x:5555	device
-----------------------------------
[+] Wireless ADB ready!
[+] Target: 192.168.x.x:5555
[+] You can unplug the USB cable.
[+] Launching scrcpy on 192.168.x.x:5555...
scrcpy 1.25 <https://github.com/Genymobile/scrcpy>
/usr/share/scrcpy/scrcpy-server: 1 file pushed, 0 skipped. 15.4 MB/s (41650 bytes in 0.003s)
[server] INFO: Device: Samsung (Android 10)
INFO: Renderer: opengl
INFO: OpenGL version: 4.x (Compatibility Profile) Mesa 25.x.x-0ubuntu0.26.x.x
INFO: Trilinear filtering enabled
INFO: Initial texture: 720x1560

[!] An open ADB port on a shared Wi-Fi network is a security risk.
[?] Disconnect wireless ADB now? (Y/n): n
[+] Connection left open. Run 'adb disconnect 192.168.x.x:5555' when you are done.
ubuntu@ubuntu:~/adb-wireless-launcher$
```

## Prerequisites
- **Python 3.7 or newer** (for the Python launcher).
- **adb** and **scrcpy**. If they are missing, the launcher offers to install them for you. To install manually:

| OS | Command |
|----|---------|
| Windows | `winget install Genymobile.scrcpy` (already includes adb) |
| macOS | `brew install scrcpy` and `brew install --cask android-platform-tools` |
| Debian/Ubuntu | `sudo apt install android-tools-adb scrcpy` |
| Arch | `sudo pacman -S android-tools scrcpy` |
| Fedora | `sudo dnf install android-tools scrcpy` |

> The `scrcpy` package in Ubuntu/Debian LTS repositories is often very old (1.x). For the latest version, install from [snap](https://snapcraft.io/scrcpy) or the [GitHub releases](https://github.com/Genymobile/scrcpy/releases).

## Installation & Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/pangeran-droid/adb-wireless-launcher.git
   cd adb-wireless-launcher
   ```

2. Enable **Developer options** and **USB debugging** on your Android device, then connect it via USB for the initial setup.

3. Run the launcher:
   ```bash
   # Linux / macOS
   python3 adb_wireless.py

   # Windows (PowerShell or CMD)
   python adb_wireless.py
   ```

4. Once connected, you can safely unplug your USB cable and enjoy wireless debugging along with instant screen mirroring!

### Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help and exit |
| `--pair` | Use Android 11+ Wireless Debugging (`adb pair`), no USB cable needed |
| `--adb-port N` | TCP port for ADB over Wi-Fi (default `5555`) |
| *anything else* | Passed straight to scrcpy |

```bash
# Limit resolution and keep the phone awake
python3 adb_wireless.py --max-size 1280 --stay-awake

# Pair over Wi-Fi without a cable (Android 11+)
python3 adb_wireless.py --pair
```

For `--pair`, open **Developer options > Wireless debugging > Pair device with pairing code** on the phone. Enter the pairing address and code when asked, then the connect address shown on the main Wireless debugging screen.

### Bash version (Linux / macOS)

The original shell script is still available and supports the same options:
```bash
chmod +x adb_wireless.sh
./adb_wireless.sh --max-size 1280
```

## Optional: Make it a Global Command (Shortcut)

**Linux / macOS**
```bash
chmod +x adb_wireless.py
sudo ln -s /path/to/adb-wireless-launcher/adb_wireless.py /usr/local/bin/wsadb
```
Now you can just type `wsadb` anywhere!

**Windows (PowerShell)**: add a function to your profile (`notepad $PROFILE`):
```powershell
function wsadb { python C:\path\to\adb-wireless-launcher\adb_wireless.py @args }
```

## Troubleshooting

- **`unauthorized` device:** unlock the phone and accept the "Allow USB debugging" prompt.
- **IP is not detected:** the phone and computer must be on the same Wi-Fi network. Otherwise type the IP manually when asked, or use `--pair`.
- **`Permission denial ... WRITE_SECURE_SETTINGS` when using `--stay-awake`:** some vendors (e.g. Realme/ColorOS, Xiaomi/MIUI) block this setting. Enable **"USB debugging (Security settings)"** in Developer options, or simply run without `--stay-awake`.
- **Windows: "adb/scrcpy installed but not visible":** open a new terminal so the updated `PATH` is loaded, then run the script again.
- **Port `5555` left open:** run `adb disconnect <ip>:5555`, or answer `Y` to the cleanup prompt next time.

## Platform Status

| Platform | Status |
|----------|--------|
| Linux | Tested |
| macOS | Supported, feedback welcome |
| Windows | Supported, feedback welcome |

If something does not work on your system, please [open an issue](https://github.com/pangeran-droid/adb-wireless-launcher/issues) and include the full terminal output.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request on this repository.

## License

This project is open-source and available under the MIT License.