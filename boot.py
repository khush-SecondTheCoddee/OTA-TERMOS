import os
import sys
import time
import hashlib
import requests
import shutil
import signal

# --- CONFIGURATION ---
REPO_BASE = "https://raw.githubusercontent.com/khush-SecondTheCoddee/OTA-TERMOS/main"
SIG_FILE = os.path.expanduser("~/TERMOS/system/sig.dat")
KERNEL = os.path.expanduser("~/TERMOS/main.py")
REGISTRY = os.path.expanduser("~/TERMOS/system/registry.json")
FILES_DIR = os.path.expanduser("~/TERMOS/FILES")

def get_file_hash(path):
    """Generates a SHA-256 hash of the Kernel file."""
    sha256_hash = hashlib.sha256()
    try:
        if not os.path.exists(path): return None
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception:
        return None

def sys_health():
    """Performs pre-boot hardware and network diagnostics."""
    print("\033[94m[ HEALTH ] Scanning Hardware Environment...")
    try:
        _, _, free = shutil.disk_usage("/")
        free_gb = free // (2**30)
        status = "\033[92mOK\033[94m" if free_gb > 1 else "\033[91mLOW\033[94m"
        print(f"  > Storage: {free_gb}GB Free [{status}]")
    except:
        print("  > Storage: Unknown")
    
    try:
        requests.get("https://github.com", timeout=2)
        print("  > Network: \033[92mCONNECTED\033[94m")
    except:
        print("  > Network: \033[93mOFFLINE (Updates Disabled)\033[94m")
    print("\033[0m")

def factory_reset():
    """Wipes all partitions and user credentials."""
    print("\n\033[41m\033[97m !!! WARNING: DESTRUCTIVE ACTION !!! \033[0m")
    confirm = input("Type 'CONFIRM' to wipe all data and passwords: ")
    
    if confirm == "CONFIRM":
        print("\033[93m[ WIPE ] Formatting System...")
        to_delete = [os.path.dirname(SIG_FILE), FILES_DIR]
        for path in to_delete:
            if os.path.exists(path):
                shutil.rmtree(path)
                print(f"  > Deleted: {os.path.basename(path)}")
        print("\033[92m[ SUCCESS ] System Reset. Exiting...\033[0m")
        time.sleep(2)
        sys.exit()
    else:
        print("Reset Aborted.")

def safe_mode(reason):
    """Emergency maintenance menu triggered on integrity failure."""
    os.system('clear')
    print(f"\033[41m\033[97m === TermOS SAFE MODE: {reason} === \033[0m")
    print("\n1. Repair System (Force OTA Update)")
    print("2. Factory Reset (Wipe Everything)")
    print("3. Emergency Shell (Bypass Security)")
    print("4. Shutdown")
    
    choice = input("\nSelect Option: ")
    if choice == "1":
        print("Please run the update manually or re-download boot.py.")
        time.sleep(2)
        return False
    elif choice == "2":
        factory_reset()
    elif choice == "3":
        print("\033[93m[ WARN ] Integrity Bypassed. Launching...\033[0m")
        return True
    else:
        sys.exit()

def verify_integrity():
    """Verifies that the Kernel hasn't been tampered with."""
    if not os.path.exists(KERNEL):
        return False, "KERNEL MISSING"
    
    if not os.path.exists(SIG_FILE):
        print("\033[93m[ SIG ] New System: Generating Signature...\033[0m")
        os.makedirs(os.path.dirname(SIG_FILE), exist_ok=True)
        with open(SIG_FILE, "w") as f:
            f.write(get_file_hash(KERNEL))
        return True, "INIT"

    with open(SIG_FILE, "r") as f:
        stored_sig = f.read().strip()
    
    current_sig = get_file_hash(KERNEL)
    if current_sig != stored_sig:
        return False, "TAMPER DETECTED"
    
    print("\033[92m[ SIG ] Kernel Verified: Authentic\033[0m")
    return True, "OK"

if __name__ == "__main__":
    # Disable Ctrl+C during boot
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    os.system('clear')
    print("\033[94m" + "="*40)
    print(" TermOS SECURE BOOTLOADER v5.0 ".center(40, " "))
    print("="*40 + "\033[0m")
    
    sys_health()
    time.sleep(0.5)
    
    valid, status_msg = verify_integrity()
    
    if not valid:
        if not safe_mode(status_msg):
            sys.exit()

    print("\033[94m[ BOOT ] Handing over to Kernel...\033[0m")
    time.sleep(0.5)
    
    # Execute Kernel
    os.chdir(os.path.expanduser("~/TERMOS"))
    os.system("python main.py")
    
    # Ensure Termux closes if Kernel exits
    sys.exit()
