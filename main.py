import os
import time
import json
import sys
import hashlib
import shutil
import getpass
import requests

class TermOS:
    def __init__(self):
        # Path Configuration
        self.root = os.path.expanduser("~/TERMOS")
        self.files_path = os.path.join(self.root, "FILES")
        self.reg_path = os.path.join(self.root, "system/registry.json")
        self.partitions = ["C:", "D:", "E:"]
        
        # Default System Registry
        self.registry = {
            "username": "Admin",
            "password_hash": None,
            "color": "\033[92m", # Green
            "boot_speed": 0.03
        }
        
        self.current_drive = "C:"
        self.current_dir = ""
        self.is_running = True
        
        self._setup_system()
        self.load_registry()

    def _setup_system(self):
        """Creates the physical folder structure in Termux."""
        os.makedirs(os.path.join(self.root, "system"), exist_ok=True)
        for d in self.partitions:
            os.makedirs(os.path.join(self.files_path, d.replace(":", "")), exist_ok=True)
        if not os.path.exists(self.reg_path):
            self.save_registry()

    def load_registry(self):
        try:
            with open(self.reg_path, "r") as f:
                self.registry.update(json.load(f))
        except: pass

    def save_registry(self):
        with open(self.reg_path, "w") as f:
            json.dump(self.registry, f, indent=4)

    def hash_pwd(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def get_real_path(self):
        """Translates Virtual Path to Real Termux Path."""
        return os.path.join(self.files_path, self.current_drive.replace(":", ""), self.current_dir)

    # --- SYSTEM SERVICES ---

    def security_gate(self):
        os.system('clear')
        color = self.registry["color"]
        print(f"{color}--- TermOS SECURITY GATE --- \033[0m")
        
        if self.registry["password_hash"] is None:
            print("No Admin password set.")
            new_pwd = getpass.getpass("Create New Password: ")
            self.registry["password_hash"] = self.hash_pwd(new_pwd)
            self.save_registry()
            print("\033[93mPassword encrypted. Rebooting...\033[0m")
            time.sleep(1)
            return True

        for i in range(3, 0, -1):
            pwd = getpass.getpass(f"Password for {self.registry['username']}: ")
            if self.hash_pwd(pwd) == self.registry["password_hash"]:
                return True
            print(f"\033[91mAccess Denied. {i-1} attempts left.\033[0m")
        
        print("System Locked.")
        sys.exit()

    def boot_animation(self):
        os.system('clear')
        c = self.registry["color"]
        logo = f"""{c}
     _________  ____  __  _______  _____
    /_  __/ _ \/ __ \/  |/  / __ \/ ___/
     / / /  __/ /_/ / /|_/ / /_/ /\__ \ 
    /_/  \___/\____/_/  /_/\____/____/  
    \033[0m"""
        print(logo)
        steps = ["Loading Kernel...", "Mounting VFS...", "Starting Services...", "Registry Sync..."]
        for step in steps:
            sys.stdout.write(f"  > {step}")
            sys.stdout.flush()
            time.sleep(0.4)
            print(" [ OK ]")
        time.sleep(0.5)

    # --- COMMANDS ---

    def list_files(self):
        items = os.listdir(self.get_real_path())
        print(f"\n Directory of {self.current_drive}\\{self.current_dir}\n")
        for item in items:
            print(f"  {item}")

    def task_manager(self):
        with open('/proc/meminfo', 'r') as f:
            mem = f.readlines()
            total = int(mem[0].split()[1]) // 1024
            free = int(mem[2].split()[1]) // 1024
        print(f"\n--- TASK MANAGER ---")
        print(f"RAM: {total - free}MB / {total}MB")
        print(f"DRIVE {self.current_drive}: ONLINE")

    def notepad(self, filename):
        print(f"Entering Notepad (Type ':save' to exit)")
        lines = []
        while True:
            line = input()
            if line.lower() == ":save": break
            lines.append(line)
        with open(os.path.join(self.get_real_path(), filename), "w") as f:
            f.write("\n".join(lines))

    def update_system(self):
        url = "https://raw.githubusercontent.com/khush-SecondTheCoddee/OTA-TERMOS/main/main.py"
        print("Checking for OTA updates...")
        try:
            r = requests.get(url, timeout=5)
            with open(__file__, "w") as f:
                f.write(r.text)
            print("Update complete. Restarting...")
            sys.exit()
        except: print("Update failed. Check connection.")

    def run_shell(self):
        c = self.registry["color"]
        while self.is_running:
            prompt = f"{c}{self.current_drive}\\{self.current_dir}> \033[0m"
            user_in = input(prompt).strip().split()
            if not user_in: continue
            
            cmd = user_in[0].lower()
            args = user_in[1:]

            if cmd == "exit": self.is_running = False
            elif cmd in ["ls", "dir"]: self.list_files()
            elif cmd == "cd":
                target = args[0] if args else ""
                new_path = os.path.join(self.get_real_path(), target)
                if os.path.isdir(new_path): self.current_dir = target
            elif cmd == "switch": self.current_drive = args[0].upper() if args else "C:"
            elif cmd == "tasklist": self.task_manager()
            elif cmd == "notepad": self.notepad(args[0] if args else "new_file.txt")
            elif cmd == "update": self.update_system()
            elif cmd == "clear": os.system('clear')
            else: print(f"'{cmd}' is not recognized.")

if __name__ == "__main__":
    os_sys = TermOS()
    if os_sys.security_gate():
        os_sys.boot_animation()
        os_sys.run_shell()
