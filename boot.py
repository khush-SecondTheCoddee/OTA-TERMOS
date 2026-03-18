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

# MANIFEST: Files required for a successful boot
REQUIRED_FILES = [
    "main.py",
    "modules/__init__.py",
    "modules/security.py",
    "modules/storage.py",
    "modules/system.py",
    "modules/dev.py"
]

def get_file_hash(path):
    """Generates SHA-256 hash for integrity verification."""
    sha256_hash = hashlib.sha256()
    try:
        if not os.path.exists(path): return None
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except: return None

def repair_system():
    """Force-syncs missing components from GitHub."""
    print("\033[93m[ REPAIR ] Component mismatch. Syncing with Cloud...\033[0m")
    for file in REQUIRED_FILES:
        local_path = os.path.expanduser(f"~/TERMOS/{file}")
        if not os.path.exists(local_path):
            try:
                print(f"  > Recovering: {file}")
                r = requests.get(f"{REPO_BASE}/{file}", timeout=15)
                r.raise_for_status()
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, "w") as f:
                    f.write(r.text)
            except Exception as e:
                print(f"\033[91m[ FATAL ] Recovery failed for {file}: {e}\033[0m")
                return False
    
    # Re-sign the kernel
    new_sig = get_file_hash(KERNEL)
    os.makedirs(os.path.dirname(SIG_FILE), exist_ok=True)
    with open(SIG_FILE, "w") as f:
        f.write(new_sig)
    return True

def check_for_interrupt(timeout=2):
    """Detects CTRL+@ (ASCII 0) during the boot window."""
    print(f"\n\033[93m[ BOOT ] Hold CTRL+@ within {timeout}s for Safe Mode...\033[0m")
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        i, o, e = select.select([sys.stdin], [], [], timeout)
        if i:
            if sys.stdin.read(1) == chr(0): return True
    except: pass
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return False

def verify_integrity():
    """Checks for missing files and verifies signature."""
    for file in REQUIRED_FILES:
        if not os.path.exists(os.path.expanduser(f"~/TERMOS/{file}")):
            return False, "FILES_MISSING"
    
    current_sig = get_file_hash(KERNEL)
    if not os.path.exists(SIG_FILE): return True, "INIT"

    with open(SIG_FILE, "r") as f:
        stored_sig = f.read().strip()
    
    return (True, "OK") if current_sig == stored_sig else (False, "TAMPER_DETECTED")

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    os.system('clear')
    print("\033[94m" + "="*40 + "\n TermOS SECURE BOOTLOADER v5.4 \n" + "="*40 + "\033[0m")
    
    # Check for manual interrupt
    if check_for_interrupt():
        print("\033[41m [ INTERRUPT ] Safe Mode Entry. \033[0m")
        sys.exit()

    # Self-Healing Logic
    valid, status = verify_integrity()
    if not valid:
        if status == "FILES_MISSING":
            if not repair_system():
                print("\033[91m[ ERROR ] No connection. System locked.\033[0m")
                sys.exit()
        else:
            print("\033[41m[ SECURITY ] Tamper detected. Boot Aborted.\033[0m")
            sys.exit()

    print("\033[92m[ SUCCESS ] Integrity Verified.\033[0m")
    time.sleep(0.5)
    os.chdir(os.path.expanduser("~/TERMOS"))
    os.system("python main.py")
