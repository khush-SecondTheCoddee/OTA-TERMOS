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

def get_file_hash(path):
    """Generates a SHA-256 hash of the Kernel file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return None

def sys_health():
    """Checks Disk and Network status."""
    print("\033[94m[ HEALTH ] Scanning Hardware...")
    _, _, free = shutil.disk_usage("/")
    free_gb = free // (2**30)
    
    status = "OK" if free_gb > 1 else "LOW STORAGE"
    print(f"  > Disk Space: {free_gb}GB Free [{status}]")
    
    try:
        requests.get("https://github.com", timeout=2)
        print("  > Network: Connected [ONLINE]\033[0m")
    except:
        print("  > Network: Offline [OFFLINE]\033[0m")

def safe_mode():
    """Emergency recovery menu if integrity fails."""
    os.system('clear')
    print("\033[41m\033[97m === TermOS SAFE MODE === \033[0m")
    print("\n1. Full System Repair (Force OTA)")
    print("2. Reset Registry (Wipe Password)")
    print("3. Exit to Termux")
    
    choice = input("\nSelect Option: ")
    if choice == "1":
        print("Initiating Repair...")
        # This would normally call a repair function
        return False 
    elif choice == "2":
        reg = os.path.expanduser("~/TERMOS/system/registry.json")
        if os.path.exists(reg): os.remove(reg)
        print("Registry Wiped. Rebooting...")
        time.sleep(2)
        return False
    else:
        sys.exit()

def verify_integrity():
    """Checks if the Kernel matches the last recorded signature."""
    if not os.path.exists(KERNEL):
        return False
    
    if not os.path.exists(SIG_FILE):
        print("\033[93m[ SIG ] Initializing Master Signature...\033[0m")
        with open(SIG_FILE, "w") as f:
            f.write(get_file_hash(KERNEL))
        return True

    with open(SIG_FILE, "r") as f:
        stored_sig = f.read().strip()
    
    if get_file_hash(KERNEL) != stored_sig:
        print("\033[41m[ ALERT ] KERNEL INTEGRITY FAILURE!\033[0m")
        return False
    
    print("\033[92m[ SIG ] Kernel Verified: Authentic\033[0m")
    return True

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_IGN) # Disable Ctrl+C
    os.system('clear')
    print("\033[94mTermOS Secure Bootloader Loading...\033[0m")
    
    sys_health()
    time.sleep(1)
    
    if not verify_integrity():
        safe_mode()
        sys.exit()

    print("\033[94mHanding over to Kernel...\033[0m")
    os.chdir(os.path.expanduser("~/TERMOS"))
    os.system("python main.py")
