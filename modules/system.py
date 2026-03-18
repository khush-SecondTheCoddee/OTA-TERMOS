import os
import sys
import time
import requests

class SystemTools:
    def __init__(self):
        # GitHub Repository Configuration
        self.repo_base = "https://raw.githubusercontent.com/khush-SecondTheCoddee/OTA-TERMOS/main"
        
        # Command Registry for the Help menu
        self.commands = {
            "help": "Displays this help menu",
            "tasklist": "Shows System CPU and RAM usage",
            "update": "Check for and install OTA updates",
            "clear": "Clears the terminal screen",
            "exit": "Safely shut down TermOS"
        }

    def play_boot_animation(self):
        """Displays the ASCII logo and initialization sequence."""
        os.system('clear')
        color = "\033[92m" # Green
        reset = "\033[0m"
        
        logo = f"""{color}
     _________  ____  __  _______  _____
    /_  __/ _ \/ __ \/  |/  / __ \/ ___/
     / / /  __/ /_/ / /|_/ / /_/ /\__ \ 
    /_/  \___/\____/_/  /_/\____/____/  
    {reset}"""
        print(logo)
        
        steps = [
            "Initializing Kernel...",
            "Mounting Virtual Partitions...",
            "Loading System Registry...",
            "Checking Network Status..."
        ]
        
        for step in steps:
            sys.stdout.write(f"  [ WAIT ] {step}")
            sys.stdout.flush()
            time.sleep(0.4)
            sys.stdout.write(f"\r  [  OK  ] {step}\n")
        
        print(f"\nSystem Ready. Type 'help' for commands.\n")

    def display_help(self, all_commands):
        """Prints a formatted list of all registered commands."""
        print("\n" + "="*40)
        print(" TermOS SYSTEM HELP ".center(40, " "))
        print("="*40)
        for cmd, desc in sorted(all_commands.items()):
            print(f"  {cmd:<12} : {desc}")
        print("="*40 + "\n")

    def show_taskmgr(self):
        """Reads real-time data from Android/Linux /proc files."""
        try:
            # RAM Information
            with open('/proc/meminfo', 'r') as f:
                mem = f.readlines()
                total = int(mem[0].split()[1]) // 1024
                free = int(mem[2].split()[1]) // 1024
                used = total - free
            
            # CPU Load (1-minute average)
            with open('/proc/loadavg', 'r') as f:
                load = f.readline().split()[0]

            print(f"\n--- SYSTEM PERFORMANCE ---")
            print(f" CPU LOAD: {load}")
            print(f" RAM:      {used}MB / {total}MB")
            print(f" STATUS:   Optimal")
            print(f"--------------------------\n")
        except Exception as e:
            print(f"Error reading system stats: {e}")

    def run_ota_update(self):
        """Connects to GitHub to refresh all system files."""
        print("\033[93m[ OTA ] Initiating System Update...\033[0m")
        
        # List of files in the modular structure
        files_to_update = [
            "main.py",
            "boot.py",
            "modules/security.py",
            "modules/storage.py",
            "modules/system.py"
        ]
        
        confirm = input("Confirm update from GitHub? (y/n): ").lower()
        if confirm != 'y':
            print("Update cancelled.")
            return

        success_count = 0
        try:
            for file in files_to_update:
                url = f"{self.repo_base}/{file}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # Ensure local directory exists for the module
                local_path = os.path.expanduser(f"~/TERMOS/{file}")
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                with open(local_path, "w") as f:
                    f.write(response.text)
                
                print(f"  > Downloaded: {file}")
                success_count += 1

            if success_count == len(files_to_update):
                print("\n\033[92m[ SUCCESS ] Update complete. Restarting TermOS...\033[0m")
                time.sleep(1)
                sys.exit() # Exit so the user can restart via boot.py
        except Exception as e:
            print(f"\n\033[91m[ ERROR ] Update failed: {e}\033[0m")
