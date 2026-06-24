#!/usr/bin/env python3
# ╔══════════════════════════════════════════════╗
# ║       MAHIR_CODEX - Smart Installer         ║
# ║       VPS Panel - Auto Dependency Fix        ║
# ╚══════════════════════════════════════════════╝

import subprocess
import sys
import os

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def pip_install(pkg, fallback=None, skip_on_fail=False):
    print(f"{CYAN}  ➤ Installing: {pkg}{RESET}")
    code, out, err = run(f"{sys.executable} -m pip install {pkg} --quiet --no-warn-script-location")
    if code == 0:
        print(f"{GREEN}  ✔ OK: {pkg}{RESET}")
        return True
    else:
        if fallback:
            print(f"{YELLOW}  ⚠ Failed with version, trying fallback: {fallback}{RESET}")
            code2, _, _ = run(f"{sys.executable} -m pip install {fallback} --quiet --no-warn-script-location")
            if code2 == 0:
                print(f"{GREEN}  ✔ OK (fallback): {fallback}{RESET}")
                return True
        if skip_on_fail:
            print(f"{YELLOW}  ⚠ Skipped (not critical): {pkg}{RESET}")
            return False
        print(f"{RED}  ✘ FAILED: {pkg}{RESET}")
        return False

def main():
    print(f"\n{BOLD}{CYAN}{'='*50}{RESET}")
    print(f"{BOLD}{CYAN}   MAHIR_CODEX — VPS Panel Installer{RESET}")
    print(f"{BOLD}{CYAN}{'='*50}{RESET}\n")

    # Step 1: Upgrade pip
    print(f"{YELLOW}[1/5] Upgrading pip...{RESET}")
    run(f"{sys.executable} -m pip install --upgrade pip --quiet")
    print(f"{GREEN}  ✔ pip upgraded{RESET}\n")

    # Step 2: Install build tools (Termux specific)
    print(f"{YELLOW}[2/5] Installing build dependencies (Termux)...{RESET}")
    is_termux = os.path.exists("/data/data/com.termux")
    if is_termux:
        run("pkg install -y python python-pip build-essential libffi openssl rust clang 2>/dev/null")
        run("pkg install -y p7zip 2>/dev/null")  # system-level 7z support
        print(f"{GREEN}  ✔ Termux build tools ready{RESET}")
    else:
        print(f"{YELLOW}  ℹ Not Termux, skipping pkg install{RESET}")
    print()

    # Step 3: Core packages
    print(f"{YELLOW}[3/5] Installing core packages...{RESET}")
    core = [
        ("Flask==3.0.0", "Flask"),
        ("gunicorn", None),
        ("requests", None),
        ("httpx", None),
        ("aiohttp", None),
        ("urllib3", None),
        ("psutil", None),
        ("pytz", None),
        ("PyJWT", None),
        ("pycryptodome", None),
        ("colorama", None),
        ("rich", None),
        ("loguru", None),
        ("cachetools", None),
        ("flask_cors", None),
    ]
    for pkg, fb in core:
        pip_install(pkg, fb)
    print()

    # Step 4: Telegram & API packages
    print(f"{YELLOW}[4/5] Installing Telegram & API packages...{RESET}")
    
    # protobuf - version sensitive
    pip_install("protobuf>=3.20.0,<5.0.0", "protobuf")
    pip_install("protobuf-decoder", None, skip_on_fail=True)

    # python-telegram-bot - has dependency conflicts with pyTelegramBotAPI
    pip_install("python-telegram-bot==20.7", "python-telegram-bot", skip_on_fail=True)
    pip_install("pyTelegramBotAPI", None, skip_on_fail=True)
    # telebot is same as pyTelegramBotAPI, skip duplicate
    pip_install("aiogram", None, skip_on_fail=True)

    # google packages
    pip_install("google", None, skip_on_fail=True)
    pip_install("google_play_scraper", None, skip_on_fail=True)

    # pyngrok
    pip_install("pyngrok", None, skip_on_fail=True)

    # cfonts - may not exist on PyPI (JS package), skip
    code, _, _ = run(f"{sys.executable} -m pip install cfonts --quiet")
    if code != 0:
        print(f"{YELLOW}  ⚠ Skipped 'cfonts' — not available for Python (it's a Node.js package){RESET}")
    else:
        print(f"{GREEN}  ✔ OK: cfonts{RESET}")
    print()

    # Step 5: py7zr - special handling
    print(f"{YELLOW}[5/5] Installing py7zr (7zip support)...{RESET}")
    # Try normal install first
    code, out, err = run(f"{sys.executable} -m pip install py7zr --quiet")
    if code == 0:
        print(f"{GREEN}  ✔ OK: py7zr{RESET}")
    else:
        print(f"{YELLOW}  ⚠ py7zr failed via pip. Trying alternatives...{RESET}")
        # Try older version
        code2, _, _ = run(f"{sys.executable} -m pip install 'py7zr==0.20.8' --quiet")
        if code2 == 0:
            print(f"{GREEN}  ✔ OK: py7zr==0.20.8{RESET}")
        else:
            # Try with --no-build-isolation
            code3, _, _ = run(f"{sys.executable} -m pip install py7zr --no-build-isolation --quiet")
            if code3 == 0:
                print(f"{GREEN}  ✔ OK: py7zr (no-build-isolation){RESET}")
            else:
                print(f"{RED}  ✘ py7zr install failed.{RESET}")
                print(f"{YELLOW}  ℹ main.py তে py7zr import আছে কিন্তু comment করা।{RESET}")
                print(f"{YELLOW}  ℹ Termux-এ: pkg install p7zip দিয়ে system-level support নিন।{RESET}")
                print(f"{YELLOW}  ℹ অথবা main.py-র line 8 এ 'import py7zr' টা comment করে রাখুন।{RESET}")
    print()

    # Final check
    print(f"{BOLD}{CYAN}{'='*50}{RESET}")
    print(f"{BOLD}{GREEN}  ✅ Installation Complete!{RESET}")
    print(f"{BOLD}{CYAN}{'='*50}{RESET}")
    print(f"\n{CYAN}এখন চালান:{RESET}")
    print(f"  {BOLD}python main.py{RESET}\n")

if __name__ == "__main__":
    main()
    