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
            "color": "\033[92m", # Default Green
            "last_login": "Never",
            "access_level": 1
        }
        
        self.load_registry()

    def load_registry(self):
        """Loads user settings from the JSON registry file."""
        if os.path.exists(self.reg_path):
            try:
                with open(self.reg_path, "r") as f:
                    self.registry.update(json.load(f))
            except Exception:
                # If corrupted, keep defaults to prevent boot crash
                pass
        else:
            self.save_registry()

    def save_registry(self):
        """Saves current settings to the JSON registry file."""
        os.makedirs(os.path.dirname(self.reg_path), exist_ok=True)
        with open(self.reg_path, "w") as f:
            json.dump(self.registry, f, indent=4)

    def hash_password(self, password):
        """Standard SHA-256 hashing for credential security."""
        return hashlib.sha256(password.encode()).hexdigest()

    def run_gate(self):
        """The authentication challenge presented at boot."""
        color = self.registry.get("color", "\033[92m")
        reset = "\033[0m"
        
        print(f"{color}--- TermOS SECURITY GATEWAY ---{reset}")
        
        # --- FIRST TIME SETUP ---
        if self.registry["password_hash"] is None:
            print("\033[93m[ ! ] No Admin detected. Starting Identity Setup...\033[0m")
            user = input("Choose Username: ").strip() or "Admin"
            
            while True:
                pwd = getpass.getpass("Create System Password: ")
                conf = getpass.getpass("Confirm Password: ")
                
                if pwd == conf and len(pwd) > 0:
                    self.registry["username"] = user
                    self.registry["password_hash"] = self.hash_password(pwd)
                    self.save_registry()
                    print(f"\n{color}[ SUCCESS ] Identity Encrypted. Rebooting Kernel...{reset}")
                    time.sleep(1.5)
                    return True
                else:
                    print("\033[91mPasswords do not match. Try again.\033[0m")

        # --- LOGIN CHALLENGE ---
        attempts = 3
        while attempts > 0:
            try:
                entry = getpass.getpass(f"Password for {self.registry['username']}: ")
                if self.hash_password(entry) == self.registry["password_hash"]:
                    print(f"{color}[ ACCESS GRANTED ] Welcome, {self.registry['username']}.{reset}")
                    self.registry["last_login"] = time.ctime()
                    self.save_registry()
                    time.sleep(0.5)
                    return True
                else:
                    attempts -= 1
                    print(f"\033[91m[ DENIED ] Invalid Password. {attempts} left.\033[0m")
            except KeyboardInterrupt:
                return False
        
        return False

    def update_theme(self, color_name):
        """Changes the OS theme color in the registry."""
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
            print(f"Theme updated to {color_name}. Changes will apply on next command.")
        else:
            print(f"Available: {', '.join(themes.keys())}")
