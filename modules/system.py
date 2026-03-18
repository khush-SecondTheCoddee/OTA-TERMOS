import os
import sys
import time
import requests
import hashlib

class SystemTools:
    def __init__(self):
        # GitHub Repository for OTA Updates
        self.repo_base = "https://raw.githubusercontent.com/khush-SecondTheCoddee/OTA-TERMOS/main"
        self.sig_path = os.path.expanduser("~/TERMOS/system/sig.dat")
        
        # Manifest of all System Files
        self.files_to_update = [
            "main.py", 
            "boot.py", 
            "modules/__init__.py", 
            "modules/security.py", 
            "modules/storage.py", 
            "modules/system.py",
            "modules/dev.py"
        ]
        
        self.commands = {
            "help": "Displays the Master Command List",
            "update": "Syncs all system files with the GitHub Main Branch",
            "tasklist": "Shows System Memory and Storage stats",
            "clear": "Clears the terminal screen",
            "exit": "Safely shuts down the TermOS Kernel"
        }

    def play_boot_animation(self):
        """Classic terminal boot sequence."""
        os.system('clear')
        print("\033[92m" + "="*40)
        print(" TermOS KERNEL v5.4 - STABLE RELEASE ".center(40, " "))
        print("="*40 + "\033[0m")
        time.sleep(0.3)
        print("[ OK ] Loading Subsystems...")
        time.sleep(0.3)
        print("[ OK ] Mounting Virtual Partitions...")
        time.sleep(0.3)

    def display_help(self, all_commands):
        print("\n" + "\033[94m="*45)
        print(" TermOS COMMAND CENTER ".center(45, " "))
        print("="*45 + "\033[0m")
        for cmd, desc in sorted(all_commands.items()):
            print(f"  \033[92m{cmd:<12}\033[0m : {desc}")
        print("\033[94m="*45 + "\n\033[0m")

    def show_taskmgr(self):
        """Displays storage and simulated RAM usage."""
        try:
            total, used, free = shutil.disk_usage("/")
            print(f"\n\033[94m[ SYSTEM MONITOR ]\033[0m")
            print(f" STORAGE: {used // (2**30)}GB Used / {total // (2**30)}GB Total")
            print(f" STATUS : STABLE\n")
        except:
            # Fallback for systems where shutil.disk_usage is restricted
            print("\n\033[94m[ SYSTEM MONITOR ]\033[0m\n STATUS: ONLINE\n")

    def generate_new_signature(self):
        """Creates a new SHA-256 fingerprint for the Kernel."""
        kernel_path = os.path.expanduser("~/TERMOS/main.py")
        sha256_hash = hashlib.sha256()
        try:
            with open(kernel_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            os.makedirs(os.path.dirname(self.sig_path), exist_ok=True)
            with open(self.sig_path, "w") as f:
                f.write(sha256_hash.hexdigest())
            print("\033[92m[ SIG ] System Signature Re-Validated.\033[0m")
        except Exception as e:
            print(f"\033[91m[ ERR ] Integrity Signing Failed: {e}\033[0m")

    def run_ota_update(self):
        """Downloads latest files and restarts the OS."""
        print("\033[93m[ OTA ] Checking for system updates...\033[0m")
        
        try:
            for file in self.files_to_update:
                url = f"{self.repo_base}/{file}"
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                
                local_path = os.path.expanduser(f"~/TERMOS/{file}")
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                with open(local_path, "w") as f:
                    f.write(r.text)
                print(f"  > Pulled: {file}")

            # Re-sign the kernel to prevent bootloader lockout
            self.generate_new_signature()
            
            print("\n\033[92m[ SUCCESS ] Update Complete. Restarting...\033[0m")
            time.sleep(2)
            sys.exit()
        except Exception as e:
            print(f"\n\033[91m[ FATAL ] Update Interrupted: {e}\033[0m")
