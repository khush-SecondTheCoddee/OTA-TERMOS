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
    """Performs pre-boot hardware diagnostics."""
    print("\033[94m[ HEALTH ] Scanning Hardware Environment...")
    try:
        _, _, free = shutil.disk_usage("/")
        free_gb = free // (2**30)
        status = "\033[92mOK\033[94m" if free_gb > 1 else "\033[91mLOW\033[94m"
        print(f"  > Storage: {free_gb}GB Free [{status}]")
    except:
        print("  > Storage: Unknown")
    
    try:
        # Check connection to your auth server
        requests.get("https://github.com", timeout=2)
        print("  > Cloud Network: \033[92mCONNECTED\033[94m")
    except:
        print("  > Cloud Network: \033[93mOFFLINE\033[94m")

def check_for_interrupt(timeout=2):
    """Detects CTRL+@ (ASCII 0) using Raw Mode."""
    print(f"\n\033[93m[ BOOT ] Hold CTRL+@ within {timeout}s for Safe Mode...\033[0m")
    
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        # Switch to Raw Mode to catch keys without 'Enter'
        tty.setraw(sys.stdin.fileno())
        start_time = time.time()
        while time.time() - start_time < timeout:
            if select.select([sys.stdin], [], [], 0.1)[0]:
                char = sys.stdin.read(1)
                # chr(0) is the value for CTRL+@ or CTRL+Space
                if char == chr(0):
                    return True
    except Exception:
        pass
    finally:
        # Restore terminal to normal mode
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return False

def factory_reset():
    """Wipes all partitions and system settings."""
    print("\n\033[41m\033[97m !!! WARNING: DESTRUCTIVE ACTION !!! \033[0m")
    confirm = input("Type 'CONFIRM' to wipe all data and passwords: ")
    
    if confirm == "CONFIRM":
        print("\033[93m[ WIPE ] Formatting System...")
        to_delete = [os.path.dirname(SIG_FILE), FILES_DIR]
        for path in to_delete:
            if os.path.exists(path):
                shutil.rmtree(path)
        print("\033[92m[ SUCCESS ] System Reset. Exiting...\033[0m")
        time.sleep(2)
        sys.exit()
    else:
        print("Reset Aborted.")

def safe_mode(reason):
    """Emergency maintenance menu."""
    os.system('clear')
    print(f"\033[41m\033[97m === TermOS SAFE MODE: {reason} === \033[0m")
    print("\n1. Repair System (Force OTA Update)")
    print("2. Factory Reset (Wipe Everything)")
    print("3. Emergency Shell (Bypass Security)")
    print("4. Shutdown")
    
    choice = input("\nSelect Option: ")
    if choice == "1":
        print("Run 'update' inside the OS or refresh via GitHub.")
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
    """Verifies SHA-256 Kernel Signature."""
    if not os.path.exists(KERNEL):
        return False, "KERNEL MISSING"
    
    current_sig = get_file_hash(KERNEL)
    
    if not os.path.exists(SIG_FILE):
        os.makedirs(os.path.dirname(SIG_FILE), exist_ok=True)
        with open(SIG_FILE, "w") as f:
            f.write(current_sig)
        return True, "OK"

    with open(SIG_FILE, "r") as f:
        stored_sig = f.read().strip()
    
    if current_sig != stored_sig:
        return False, "TAMPER DETECTED"
    
    print("\033[92m[ SIG ] Kernel Verified: Authentic\033[0m")
    return True, "OK"

if __name__ == "__main__":
    # Ignore Ctrl+C
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    os.system('clear')
    print("\033[94m" + "="*40)
    print(" TermOS SECURE BOOTLOADER v5.2 ".center(40, " "))
    print("="*40 + "\033[0m")
    
    sys_health()
    
    # Check for manual CTRL+@ trigger
    if check_for_interrupt(timeout=2):
        if not safe_mode("SECURE INTERRUPT"):
            sys.exit()
    else:
        # Standard integrity check
        valid, status_msg = verify_integrity()
        if not valid:
            if not safe_mode(status_msg):
                sys.exit()

    print("\033[94m[ BOOT ] Launching Kernel...\033[0m")
    time.sleep(0.5)
    
    # Switch directory and launch main.py
    os.chdir(os.path.expanduser("~/TERMOS"))
    os.system("python main.py")
    
    # Close Termux session after Kernel exit
    sys.exit()
