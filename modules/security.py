import os
import json
import hashlib
import getpass
import time

class SecurityGate:
    def __init__(self):
        # Paths for system configuration
        self.root = os.path.expanduser("~/TERMOS")
        self.reg_path = os.path.join(self.root, "system/registry.json")
        
        # Default Registry Settings
        self.registry = {
            "username": "Admin",
            "password_hash": None,
            "color": "\033[92m", # Green (Default)
            "last_login": "Never",
            "access_level": 1
        }
        
        self.load_registry()

    def load_registry(self):
        """Loads user settings from the JSON registry file."""
        if os.path.exists(self.reg_path):
            try:
                with open(self.reg_path, "r") as f:
                    data = json.load(f)
                    self.registry.update(data)
            except Exception:
                # If file is corrupted, we keep defaults
                pass
        else:
            self._ensure_dir()
            self.save_registry()

    def _ensure_dir(self):
        """Creates the system directory if it's missing."""
        os.makedirs(os.path.dirname(self.reg_path), exist_ok=True)

    def save_registry(self):
        """Saves current settings to the JSON registry file."""
        self._ensure_dir()
        with open(self.reg_path, "w") as f:
            json.dump(self.registry, f, indent=4)

    def hash_password(self, password):
        """Standard SHA-256 hashing."""
        return hashlib.sha256(password.encode()).hexdigest()

    def run_gate(self):
        """The authentication challenge presented at boot."""
        color = self.registry.get("color", "\033[92m")
        reset = "\033[0m"
        
        print(f"{color}--- TermOS SECURITY GATEWAY ---{reset}")
        
        # --- FIRST TIME SETUP ---
        if self.registry["password_hash"] is None:
            print("\033[93m[ ! ] No Admin password detected. Starting Setup...\033[0m")
            user = input("Set Username: ").strip() or "Admin"
            
            while True:
                pwd = getpass.getpass("Create System Password: ")
                confirm = getpass.getpass("Confirm Password: ")
                
                if pwd == confirm and len(pwd) > 0:
                    self.registry["username"] = user
                    self.registry["password_hash"] = self.hash_password(pwd)
                    self.save_registry()
                    print(f"\n{color}[ SUCCESS ] Credentials Encrypted. Rebooting...{reset}")
                    time.sleep(1.5)
                    return True
                else:
                    print("\033[91mPasswords do not match or are empty. Try again.\033[0m")

        # --- STANDARD LOGIN ---
        attempts = 3
        while attempts > 0:
            try:
                entry = getpass.getpass(f"Password for {self.registry['username']}: ")
                if self.hash_password(entry) == self.registry["password_hash"]:
                    print(f"{color}[ ACCESS GRANTED ] Welcome back, {self.registry['username']}.{reset}")
                    self.registry["last_login"] = time.ctime()
                    self.save_registry()
                    time.sleep(0.5)
                    return True
                else:
                    attempts -= 1
                    print(f"\033[91m[ ERROR ] Invalid Password. {attempts} attempts left.\033[0m")
            except KeyboardInterrupt:
                # Bootloader will catch the exit if interrupts are ignored there
                print("\nLogin Aborted.")
                return False
        
        return False

    def change_theme(self, color_name):
        """Optional feature to change OS colors via command."""
        themes = {
            "green": "\033[92m",
            "blue": "\033[94m",
            "red": "\033[91m",
            "yellow": "\033[93m",
            "cyan": "\033[96m",
            "white": "\033[97m"
        }
        if color_name in themes:
            self.registry["color"] = themes[color_name]
            self.save_registry()
            print(f"Theme updated to {color_name}. Restart required.")
        else:
            print(f"Available themes: {', '.join(themes.keys())}")
