import os
import sys
import time
import requests
import signal

# --- SYSTEM CONFIGURATION ---
REPO_BASE = "https://raw.githubusercontent.com/khush-SecondTheCoddee/OTA-TERMOS/main"
CORE_FILES = ["main.py"]
MODULE_FILES = ["__init__.py", "security.py", "storage.py", "system.py"]

def disable_interrupts():
    """Prevents the user from stopping the boot process with Ctrl+C."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)

def clear():
    os.system('clear')

def check_structure():
    """Ensures necessary OS directories exist."""
    paths = ["system", "FILES/C", "modules"]
    for p in paths:
        full_path = os.path.expanduser(f"~/TERMOS/{p}")
        if not os.path.exists(full_path):
            os.makedirs(full_path, exist_ok=True)

def fetch_file(filepath):
    """Emergency OTA recovery if a system file is missing."""
    url = f"{REPO_BASE}/{filepath}"
    local_path = os.path.expanduser(f"~/TERMOS/{filepath}")
    try:
        print(f"\033[93m[ RECOVERY ] Downloading {filepath}...\033[0m")
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        with open(local_path, "w") as f:
            f.write(r.text)
        return True
    except Exception:
        return False

def run_boot():
    clear()
    print("\033[94m" + "="*40)
    print(" TermOS SECURE BOOT v4.0 ".center(40, " "))
    print("="*40 + "\033[0m")
    
    check_structure()
    
    # 1. Integrity Check: Core & Modules
    all_files = CORE_FILES + [f"modules/{m}" for m in MODULE_FILES]
    for file in all_files:
        if not os.path.exists(os.path.expanduser(f"~/TERMOS/{file}")):
            print(f"\033[91m[ ! ] System Corrupted: {file} missing.\033[0m")
            if not fetch_file(file):
                print("\033[91m[ FATAL ] OTA Recovery Failed. Check Network.\033[0m")
                time.sleep(3)
                sys.exit()

    print("\033[92m[ OK ] System Integrity Verified.")
    print("[ OK ] Bootloader Locked.\033[0m")
    time.sleep(1)

    # 2. Handoff to Kernel
    # We change directory to ensure imports work correctly
    os.chdir(os.path.expanduser("~/TERMOS"))
    
    # Execute main.py. If main.py exits, the script ends.
    os.system("python main.py")

if __name__ == "__main__":
    # Lock the environment
    disable_interrupts()
    
    try:
        run_boot()
    except Exception as e:
        print(f"Boot Error: {e}")
        time.sleep(2)
    
    # Critical: This prevents the user from reaching the Termux prompt 
    # if you've added this script to your .bashrc
    sys.exit()
