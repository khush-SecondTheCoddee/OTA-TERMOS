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
            "color": "\033[92m", # Green
            "last_login": "Never"
        }
        
        self.load_registry()

    def load_registry(self):
        """Loads user settings from the JSON registry file."""
        if os.path.exists(self.reg_path):
            try:
                with open(self.reg_path, "r") as f:
                    self.registry.update(json.load(f))
            except:
                pass
        else:
            self.save_registry()

    def save_registry(self):
        """Saves current settings to the JSON registry file."""
        os.makedirs(os.path.dirname(self.reg_path), exist_ok=True)
        with open(self.reg_path, "w") as f:
            json.dump(self.registry, f, indent=4)

    def hash_password(self, password):
        """Standard SHA-256 hashing for security."""
        return hashlib.sha256(password.encode()).hexdigest()

    def run_gate(self):
        """The login challenge presented at boot."""
        color = self.registry["color"]
        reset = "\033[0m"
        
        print(f"{color}--- TermOS SECURITY SYSTEM ---{reset}")
        
        # Initial Setup (First time running the OS)
        if self.registry["password_hash"] is None:
            print("No system password detected. Starting First-Time Setup...")
            user = input("Choose a Username: ").strip() or "Admin"
            pwd = getpass.getpass("Create System Password: ")
            
            self.registry["username"] = user
            self.registry["password_hash"] = self.hash_password(pwd)
            self.save_registry()
            
            print(f"\n{color}[ SUCCESS ] Identity Created. Rebooting...{reset}")
            time.sleep(1.5)
            return True

        # Standard Login Challenge
        attempts = 3
        while attempts > 0:
            entry = getpass.getpass(f"Password for {self.registry['username']}: ")
            if self.hash_password(entry) == self.registry["password_hash"]:
                print(f"{color}ACCESS GRANTED. Welcome, {self.registry['username']}.{reset}")
                self.registry["last_login"] = time.ctime()
                self.save_registry()
                time.sleep(0.5)
                return True
            else:
                attempts -= 1
                print(f"\033[91mACCESS DENIED. {attempts} attempts remaining.\033[0m")
        
        return False
