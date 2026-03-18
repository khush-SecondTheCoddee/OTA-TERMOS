import os
import sys
import time
import requests
import hashlib

class SystemTools:
    def __init__(self):
        # GitHub Repository Configuration
        self.repo_base = "https://raw.githubusercontent.com/khush-SecondTheCoddee/OTA-TERMOS/main"
        self.sig_path = os.path.expanduser("~/TERMOS/system/sig.dat")
        
        # Command Registry
        self.commands = {
            "help": "Displays this help menu",
            "tasklist": "Shows System CPU and RAM usage",
            "update": "Check for and install OTA updates (Includes DevKit)",
            "clear / cls": "Clears the terminal screen",
            "exit": "Safely shut down TermOS"
        }

    def play_boot_animation(self):
        os.system('clear')
        print("\033[92m--- TermOS KERNEL v5.2 ONLINE ---\033[0m\n")
        time.sleep(0.5)

    def display_help(self, all_commands):
        print("\n" + "="*45)
        print(" TermOS MASTER COMMAND LIST ".center(45, " "))
        print("="*45)
        for cmd, desc in sorted(all_commands.items()):
            print(f"  {cmd:<12} : {desc}")
        print("="*45 + "\n")

    def show_taskmgr(self):
        try:
            with open('/proc/meminfo', 'r') as f:
                mem = f.readlines()
                total = int(mem[0].split()[1]) // 1024
                used = total - (int(mem[2].split()[1]) // 1024)
            print(f"\n[ SYSTEM MONITOR ]\n RAM: {used}MB / {total}MB\n CPU: STABLE\n")
        except:
            print("Error reading hardware stats.")

    def generate_new_signature(self):
        """Re-signs the Kernel after an update to prevent 'Tamper' alerts."""
        kernel_path = os.path.expanduser("~/TERMOS/main.py")
        sha256_hash = hashlib.sha256()
        try:
            with open(kernel_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            os.makedirs(os.path.dirname(self.sig_path), exist_ok=True)
            with open(self.sig_path, "w") as f:
                f.write(sha256_hash.hexdigest())
            print("\033[92m[ SIG ] Kernel Signature Verified & Updated.\033[0m")
        except Exception as e:
            print(f"\033[91m[ ERR ] Could not sign Kernel: {e}\033[0m")

    def run_ota_update(self):
        """The OTA Manifest - Now includes dev.py"""
        print("\033[93m[ OTA ] Contacting Update Server...\033[0m")
        
        # ADDED dev.py TO THIS LIST
        files_to_update = [
            "main.py", 
            "boot.py", 
            "modules/__init__.py", 
            "modules/security.py", 
            "modules/storage.py", 
            "modules/system.py",
            "modules/dev.py" 
        ]
        
        try:
            for file in files_to_update:
                url = f"{self.repo_base}/{file}"
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                
                local_path = os.path.expanduser(f"~/TERMOS/{file}")
                # Ensure the modules directory exists locally
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                with open(local_path, "w") as f:
                    f.write(r.text)
                print(f"  > Successfully Pulled: {file}")

            # Re-generate the signature so boot.py doesn't block the next start
            self.generate_new_signature()
            
            print("\n\033[92m[ SUCCESS ] System Upgraded. Restarting for changes...\033[0m")
            time.sleep(2)
            sys.exit()
        except Exception as e:
            print(f"\n\033[91m[ FATAL ] Update Failed: {e}\033[0m")
