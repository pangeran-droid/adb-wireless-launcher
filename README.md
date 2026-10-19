<p align="center">
  <img src=".github/image/logo.svg" alt="ADB Wireless Launcher logo" width="600"/>
</p>

<h1 align="center">ADB Wireless & Scrcpy Auto Launcher</h1>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/platform-Linux-informational" alt="Platform: Linux">
  <img src="https://img.shields.io/badge/shell-Bash-4EAA25?logo=gnubash&logoColor=white" alt="Shell: Bash">
  <img src="https://img.shields.io/badge/requires-adb%20%7C%20scrcpy-blue" alt="Requires adb and scrcpy">
  <a href="https://github.com/pangeran-droid/adb-wireless-launcher/stargazers"><img src="https://img.shields.io/github/stars/pangeran-droid/adb-wireless-launcher?style=flat" alt="GitHub stars"></a>
  <a href="https://github.com/pangeran-droid/adb-wireless-launcher/issues"><img src="https://img.shields.io/github/issues/pangeran-droid/adb-wireless-launcher" alt="GitHub issues"></a>
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</p>

A lightweight bash script to automate **Android Wireless Debugging (ADB)** setup and instantly launch **Scrcpy** for screen mirroring on Linux (Ubuntu/Debian-based).

## Features
- **Auto-Detect:** Automatically finds your connected Android device via USB.
- **TCP/IP Switch:** Seamlessly restarts ADB into TCP/IP mode on port `5555`.
- **Auto-IP Fetching:** Pulls your device's local network IP address automatically (with a manual fallback prompt just in case).
- **Connection Verification:** Confirms the wireless `adb connect` actually succeeded before continuing.
- **Dependency Check:** Verifies and offers to install `scrcpy` automatically if it's missing.
- **One-Command Setup:** Connects wirelessly and opens screen mirroring in a single run, correctly targeting the wireless device even if USB is still plugged in.

## Prerequisites
Make sure you have `adb` installed on your system:
```bash
sudo apt install android-tools-adb
```

## Installation & Usage

1. Clone the repository:
   ```bash
   git clone https://github.com/pangeran-droid/adb-wireless-launcher.git
   cd adb-wireless-launcher
   ```

2. Connect your phone via USB for the initial setup (ensure USB Debugging is enabled on your Android device).

3. Give execution permission to the script:
   ```bash
   chmod +x wireless-adb.sh
   ```

4. Run the script:
   ```bash
   ./wireless-adb.sh
   ```

5. Once connected, you can safely unplug your USB cable and enjoy wireless debugging along with instant screen mirroring!

## Optional: Make it a Global Command (Shortcut)

If you want to run this script from anywhere in your terminal without typing the path, create a symlink:
```bash
sudo ln -s /path/to/adb-wireless-launcher/wireless-adb.sh /usr/local/bin/wsadb
```

Now you can just type `wsadb` anywhere!

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to open an issue or submit a pull request on this repository.

## License

This project is open-source and available under the MIT License.
