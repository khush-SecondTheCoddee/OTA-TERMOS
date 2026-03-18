import os
import sys
import subprocess
import requests
import tarfile
import lzma

# --- CONFIGURATION ---
OTA_REPO = "khush-SecondTheCoddee/OTA-TERMOS"
# The official bootstrap image you provided
BOOTSTRAP_URL = "https://github.com/termux/proot-distro/releases/download/v4.29.0/debian-trixie-aarch64-pd-v4.29.0.tar.xz"

ROOT_DIR = os.path.expanduser("~/termos_root")
VERSION_FILE = os.path.join(ROOT_DIR, ".version")

def setup_system():
    print("📥 Termos: Initializing First-Run Bootstrap...")
    os.makedirs(ROOT_DIR, exist_ok=True)
    
    print(f"📡 Downloading Core Engine from: {BOOTSTRAP_URL}")
    r = requests.get(BOOTSTRAP_URL, stream=True)
    archive = os.path.join(ROOT_DIR, "bootstrap.tar.xz")
    
    with open(archive, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            f.write(chunk)
            print("..", end="", flush=True)

    print("\n🏗️  Unpacking System Layers (XZ)...")
    with lzma.open(archive) as f:
        with tarfile.open(fileobj=f) as tar:
            tar.extractall(path=ROOT_DIR)
    
    # Initialize versioning
    with open(VERSION_FILE, "w") as v:
        v.write("v4.29.0-base")
    
    os.remove(archive)
    print("✅ Bootstrap Complete.")

def check_ota():
    print("🛰️  Checking OTA-TERMOS for updates...")
    try:
        api_url = f"https://api.github.com/repos/{OTA_REPO}/releases/latest"
        r = requests.get(api_url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            remote_ver = data['tag_name']
            with open(VERSION_FILE, "r") as f:
                local_ver = f.read().strip()
            
            if remote_ver != local_ver:
                print(f"✨ Update Found: {remote_ver}! Run 'termos --update' to apply.")
    except:
        pass # Skip if offline or repo empty

def boot():
    print("🚀 Booting Termos OS...")
    # Proot environment variables and execution
    proot_cmd = [
        "proot", "-0", "-r", ROOT_DIR,
        "-b", "/dev", "-b", "/proc", "-b", "/sys",
        "-b", "/data/data/com.termux/files/home:/home",
        "-w", "/root",
        "/usr/bin/env", "-i",
        "HOME=/root", "TERM=xterm-256color",
        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "/bin/bash", "--login"
    ]
    subprocess.run(proot_cmd)

if __name__ == "__main__":
    if not os.path.exists(VERSION_FILE):
        setup_system()
    else:
        check_ota()
    boot()
