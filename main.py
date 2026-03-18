import os
import sys
import time

# --- MODULE IMPORT GATE ---
try:
    # We import the classes from your /modules folder
    from modules.security import SecurityGate
    from modules.storage import FileSystem
    from modules.system import SystemTools
except ImportError as e:
    print(f"\033[91m[ KERNEL ERROR ] Critical Subsystem Missing: {e}\033[0m")
    print("Please run boot.py to repair the OS structure.")
    sys.exit()

class TermOS:
    def __init__(self):
        # Initialize the subsystems
        self.security = SecurityGate()
        self.storage = FileSystem()
        self.system = SystemTools()
        self.is_running = True

    def boot_sequence(self):
        """Final internal checks and authentication."""
        os.system('clear')
        
        # 1. Identity Verification (Managed by security.py)
        if not self.security.run_gate():
            print("\033[91m[ LOCKOUT ] Unauthorized Access Detected. Shutting down.\033[0m")
            time.sleep(2)
            sys.exit()
            
        # 2. UI Initialization (Managed by system.py)
        self.system.play_boot_animation()
        
        # 3. Enter the Shell Environment
        self.run_shell()

    def run_shell(self):
        """The Main Operating Loop."""
        # Get the theme color from the registry
        color = self.security.registry.get("color", "\033[92m")
        reset = "\033[0m"

        while self.is_running:
            # Generate the dynamic prompt: C:\Users>
            prompt_str = self.storage.get_prompt(color)
            
            try:
                user_input = input(prompt_str).strip().split()
            except EOFError: # Handles Ctrl+D
                break
            except KeyboardInterrupt: # Handles Ctrl+C inside the shell
                print("\nType 'exit' to shut down properly.")
                continue
                
            if not user_input:
                continue
            
            cmd = user_input[0].lower()
            args = user_input[1:]

            # --- COMMAND ROUTING SYSTEM ---
            
            # KERNEL COMMANDS
            if cmd == "exit":
                print(f"{color}TermOS: Saving session and shutting down...{reset}")
                self.is_running = False
                
            elif cmd == "clear" or cmd == "cls":
                os.system('clear')

            # SYSTEM MODULE COMMANDS
            elif cmd == "help":
                # Merge help dictionaries from all modules for a full menu
                combined_help = {**self.system.commands, **self.storage.commands}
                self.system.display_help(combined_help)
                
            elif cmd == "tasklist":
                self.system.show_taskmgr()
                
            elif cmd == "update":
                # This triggers the OTA download from your GitHub
                self.system.run_ota_update()

            # STORAGE MODULE COMMANDS
            elif cmd in ["ls", "dir"]:
                self.storage.list_dir()
                
            elif cmd == "cd":
                self.storage.change_dir(args[0] if args else "")
                
            elif cmd == "switch":
                # This is where your 'Disabled Switch' logic lives
                self.storage.switch_partition(args[0] if args else "C:")
                
            elif cmd == "mkdir":
                self.storage.make_directory(args[0] if args else "")

            elif cmd == "notepad":
                # Built-in text editor
                self.storage.notepad(args[0] if args else "new_file.txt")

            elif cmd == "rm" or cmd == "del":
                self.storage.delete_item(args[0] if args else None)

            else:
                print(f"'{cmd}' is not recognized as an internal or external command.")

if __name__ == "__main__":
    # Create the OS instance
    kernel = TermOS()
    try:
        kernel.boot_sequence()
    except Exception as e:
        print(f"\033[91m[ KERNEL PANIC ] A critical error occurred: {e}\033[0m")
        time.sleep(3)
        sys.exit()
