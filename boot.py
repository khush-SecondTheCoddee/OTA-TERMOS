import os
import sys
import time
import hashlib
import requests
import shutil
import signal
import select
import tty
import termios

# --- CONFIGURATION ---
REPO_BASE = "https://raw.githubusercontent.com/khush-SecondTheCoddee/OTA-TERMOS/main"
SIG_FILE = os.path.expanduser("~/TERMOS/system/sig.dat")
KERNEL = os.path.expanduser("~/TERMOS/main.py")
FILES_DIR = os.path.expanduser("~/TERMOS/FILES")

# Manifest for Self-Healing
REQUIRED_FILES = [
    "main.py",
    "modules/__init__.py",
    "modules/security.py",
    "modules/storage.py",
    "modules/system.py",
    "modules/dev.py"
]

def get_file_hash(path):
    sha256_hash = hashlib.sha256()
    try:
        if not os.path.exists(path): return None
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None

def repair_system():
    """Automatically downloads missing files from GitHub."""
    print("\033[93m[ REPAIR ] Missing components detected. Downloading...\033[0m")
    for file in REQUIRED_FILES:
        local_path = os.path.expanduser(f"~/TERMOS/{file}")
        if not os.path.exists(local_path):
            try:
                print(f"  > Fetching: {file}")
                r = requests.get(f"{REPO_BASE}/{file}", timeout=10)
                r.raise_for_status()
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, "w") as f:
                    f.write(r.text)
            except Exception as e:
                print(f"\033[91m[ FATAL ] Network Error: {e}\033[0m")
                return False
    
    # Update signature after repair to ensure a smooth boot
    current_sig = get_file_hash(KERNEL)
    with open(SIG_FILE, "w") as f:
        f.write(current_sig)
    return True

def sys_health():
    print("\033[94m[ HEALTH ] Scanning Hardware Environment...")
    # ... (Disk and Network checks as before) ...
    try:
        _, _, free = shutil.disk_usage("/")
        print(f"  > Storage: {free // (2**30)}GB Free")
        requests.get("https://github.com", timeout=2)
        print("  > Cloud Network: \033[92mCONNECTED\033[94m")
    except:
        print("  > Cloud Network: \033[91mOFFLINE\033[94m")

def check_for_interrupt(timeout=2):
    print(f"\n\033[93m[ BOOT ] Hold CTRL+@ within {timeout}s for Safe Mode...\033[0m")
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        start_time = time.time()
        while time.time() - start_time < timeout:
            if select.select([sys.stdin], [], [], 0.1)[0]:
                char = sys.stdin.read(1)
                if char == chr(0): return True
    except Exception: pass
    finally: termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return False

def verify_integrity():
    """Checks if all files exist and the Kernel is authentic."""
    # Check for missing files first
    for file in REQUIRED_FILES:
        if not os.path.exists(os.path.expanduser(f"~/TERMOS/{file}")):
            return False, "MISSING_FILES"
    
    # Check Kernel signature
    current_sig = get_file_hash(KERNEL)
    if not os.path.exists(SIG_FILE):
        os.makedirs(os.path.dirname(SIG_FILE), exist_ok=True)
        with open(SIG_FILE, "w") as f: f.write(current_sig)
        return True, "INIT"

    with open(SIG_FILE, "r") as f:
        stored_sig = f.read().strip()
    
    if current_sig != stored_sig:
        return False, "TAMPER_DETECTED"
    
    return True, "OK"

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    os.system('clear')
    print("\033[94m" + "="*40 + "\n TermOS SECURE BOOTLOADER v5.3 \n" + "="*40 + "\033[0m")
    
    sys_health()
    
    if check_for_interrupt(timeout=2):
        from modules.system import SystemTools # Fallback if needed
        # Safe Mode logic as before
        sys.exit()

    # AUTO-REPAIR LOGIC
    valid, status_msg = verify_integrity()
    if status_msg == "MISSING_FILES":
        if not repair_system():
            print("\033[91m[ ERROR ] Self-Repair failed. Check Internet.\033[0m")
            time.sleep(3)
            sys.exit()
    elif status_msg == "TAMPER_DETECTED":
        print("\033[41m[ ALERT ] KERNEL TAMPERED!\033[0m")
        # Go to Safe Mode
        sys.exit()

    print("\033[92m[ OK ] System Integrity Verified.\033[0m")
    time.sleep(0.5)
    os.chdir(os.path.expanduser("~/TERMOS"))
    os.system("python main.py")
    sys.exit()
