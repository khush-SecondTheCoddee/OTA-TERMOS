import os
import sys
import time
import requests
import hashlib

class SystemTools:
    def __init__(self):
        self.repo_base = "https://raw.githubusercontent.com/khush-SecondTheCoddee/OTA-TERMOS/main"
        self.sig_path = os.path.expanduser("~/TERMOS/system/sig.dat")
        
        self.commands = {
            "help": "Displays this help menu",
            "tasklist": "Shows System CPU and RAM usage",
            "update": "Check for and install OTA updates",
            "clear / cls": "Clears the terminal screen",
            "exit": "Safely shut down TermOS"
        }

    def play_boot_animation(self):
        os.system('clear')
        color = "\033[92m" 
        reset = "\033[0m"
        print(f"{color}--- TermOS KERNEL LOADED ---{reset}\n")
        time.sleep(0.5)

    def display_help(self, all_commands):
        print("\n" + "="*45)
        print(" TermOS SYSTEM COMMANDS ".center(45, " "))
        print("="*45)
        for cmd, desc in sorted(all_commands.items()):
            print(f"  {cmd:<12} : {desc}")
        print("="*45 + "\n")

    def show_taskmgr(self):
        try:
            with open('/proc/meminfo', 'r') as f:
                mem = f.readlines()
                total = int(mem[0].split()[1]) // 1024
                free = int(mem[2].split()[1]) // 1024
                used = total - free
            print(f"\n--- SYSTEM PERFORMANCE ---\n RAM: {used}MB / {total}MB\n STATUS: OPTIMAL\n")
        except:
            print("Error reading system stats.")

    def generate_new_signature(self):
        """Generates a new hash for the updated Kernel."""
        kernel_path = os.path.expanduser("~/TERMOS/main.py")
        sha256_hash = hashlib.sha256()
        try:
            with open(kernel_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            # Save the new hash so the Bootloader trusts it
            os.makedirs(os.path.dirname(self.sig_path), exist_ok=True)
            with open(self.sig_path, "w") as f:
                f.write(sha256_hash.hexdigest())
            print("\033[92m[ SIG ] New System Signature Generated.\033[0m")
        except Exception as e:
            print(f"\033[91m[ ERR ] Could not sign Kernel: {e}\033[0m")

    def run_ota_update(self):
        print("\033[93m[ OTA ] Initiating Secure Update...\033[0m")
        files = ["main.py", "boot.py", "modules/security.py", "modules/storage.py", "modules/system.py"]
        
        try:
            for file in files:
                url = f"{self.repo_base}/{file}"
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                
                local_path = os.path.expanduser(f"~/TERMOS/{file}")
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                with open(local_path, "w") as f:
                    f.write(r.text)
                print(f"  > Updated: {file}")

            # CRITICAL: Re-sign the Kernel after update
            self.generate_new_signature()
            
            print("\n\033[92m[ SUCCESS ] Update complete. Restarting...\033[0m")
            time.sleep(2)
            sys.exit()
        except Exception as e:
            print(f"\n\033[91m[ ERROR ] Update failed: {e}\033[0m")
