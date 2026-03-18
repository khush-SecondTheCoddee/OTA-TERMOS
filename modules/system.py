import os
import sys
import time
import requests

class SystemTools:
    def __init__(self):
        # GitHub Repository Configuration (Matches your URL)
        self.repo_base = "https://raw.githubusercontent.com/khush-SecondTheCoddee/OTA-TERMOS/main"
        
        # Command Registry for the Help menu
        self.commands = {
            "help": "Displays this help menu",
            "tasklist": "Shows System CPU and RAM usage",
            "update": "Check for and install OTA updates",
            "clear / cls": "Clears the terminal screen",
            "exit": "Safely shut down TermOS"
        }

    def play_boot_animation(self):
        """Displays the ASCII logo and initialization sequence."""
        os.system('clear')
        # We use a default green here; main.py handles the registry color
        color = "\033[92m" 
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
            "Checking Module Integrity...",
            "Mounting File System...",
            "Synchronizing Registry..."
        ]
        
        for step in steps:
            sys.stdout.write(f"  [ WAIT ] {step}")
            sys.stdout.flush()
            time.sleep(0.3)
            sys.stdout.write(f"\r  [  OK  ] {step}\n")
        
        print(f"\nSystem Online. Welcome to TermOS.\n")

    def display_help(self, all_commands):
        """Prints a formatted list of all registered commands from all modules."""
        print("\n" + "="*45)
        print(" TermOS SYSTEM COMMANDS ".center(45, " "))
        print("="*45)
        # Sort commands alphabetically for easy reading
        for cmd, desc in sorted(all_commands.items()):
            print(f"  {cmd:<12} : {desc}")
        print("="*45 + "\n")

    def show_taskmgr(self):
        """Reads real-time data from Android/Linux system files."""
        try:
            # RAM Information from /proc/meminfo
            with open('/proc/meminfo', 'r') as f:
                mem = f.readlines()
                total = int(mem[0].split()[1]) // 1024
                free = int(mem[2].split()[1]) // 1024
                used = total - free
            
            # CPU Load (1-minute average) from /proc/loadavg
            with open('/proc/loadavg', 'r') as f:
                load = f.readline().split()[0]

            print(f"\n--- PERFORMANCE MONITOR ---")
            print(f" CPU LOAD (1m): {load}")
            print(f" RAM USAGE:     {used}MB / {total}MB")
            print(f" OS STATUS:     STABLE")
            print(f"---------------------------\n")
        except Exception as e:
            print(f"\033[91m[ ERROR ] Could not read system stats: {e}\033[0m")

    def run_ota_update(self):
        """Connects to GitHub to refresh all system files and modules."""
        print("\033[93m[ OTA ] Contacting Update Server...\033[0m")
        
        # List of all files in your modular architecture
        files_to_update = [
            "main.py",
            "boot.py",
            "modules/__init__.py",
            "modules/security.py",
            "modules/storage.py",
            "modules/system.py"
        ]
        
        confirm = input("Confirm system-wide update from GitHub? (y/n): ").lower()
        if confirm != 'y':
            print("Update aborted.")
            return

        success_count = 0
        try:
            for file in files_to_update:
                url = f"{self.repo_base}/{file}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # Determine local path and ensure directory exists
                local_path = os.path.expanduser(f"~/TERMOS/{file}")
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                with open(local_path, "w") as f:
                    f.write(response.text)
                
                print(f"  > Successfully updated: {file}")
                success_count += 1

            if success_count == len(files_to_update):
                print("\n\033[92m[ SUCCESS ] All modules updated. System rebooting...\033[0m")
                time.sleep(2)
                sys.exit() # Exit so the user restarts through boot.py
        except Exception as e:
            print(f"\n\033[91m[ FATAL ] Update failed: {e}\033[0m")
