import os
import sys
import time

# Attempt to import the modular package
try:
    from modules.security import SecurityGate
    from modules.storage import FileSystem
    from modules.system import SystemTools
except ImportError as e:
    print(f"\033[91m[ KERNEL ERROR ] Critical Module Missing: {e}\033[0m")
    print("Please run boot.py to repair the system.")
    sys.exit()

class TermOS:
    def __init__(self):
        # Initialize Module instances
        self.security = SecurityGate()
        self.storage = FileSystem()
        self.system = SystemTools()
        self.is_running = True

    def boot_sequence(self):
        """Final internal checks before showing the prompt."""
        os.system('clear')
        
        # 1. Run Security Gate
        if not self.security.run_gate():
            print("\033[91mAuthentication Failed. Shutdown.\033[0m")
            sys.exit()
            
        # 2. Show Boot Animation
        self.system.play_boot_animation()
        
        # 3. Enter the Shell
        self.run_shell()

    def run_shell(self):
        """The main User Interface loop."""
        while self.is_running:
            # Get the dynamic prompt from the Storage module
            prompt_str = self.storage.get_prompt()
            
            try:
                user_input = input(prompt_str).strip().split()
            except EOFError:
                break
                
            if not user_input:
                continue
            
            cmd = user_input[0].lower()
            args = user_input[1:]

            # --- COMMAND ROUTING ---
            
            # Internal Kernel Commands
            if cmd == "exit":
                print("Shutting down TermOS...")
                self.is_running = False
                
            elif cmd == "clear":
                os.system('clear')

            # System Module Commands
            elif cmd == "help":
                # Combine help strings from all modules
                all_help = {**self.system.commands, **self.storage.commands}
                self.system.display_help(all_help)
                
            elif cmd == "tasklist":
                self.system.show_taskmgr()
                
            elif cmd == "update":
                self.system.run_ota_update()

            # Storage Module Commands
            elif cmd in ["ls", "dir"]:
                self.storage.list_dir()
                
            elif cmd == "cd":
                self.storage.change_dir(args[0] if args else "")
                
            elif cmd == "switch":
                self.storage.switch_partition(args[0] if args else "C:")
                
            elif cmd == "mkdir":
                self.storage.make_directory(args[0] if args else "")

            elif cmd == "notepad":
                self.storage.notepad(args[0] if args else "new_file.txt")

            else:
                print(f"Error: '{cmd}' is not a recognized command.")

if __name__ == "__main__":
    # Create the OS instance and start
    kernel = TermOS()
    try:
        kernel.boot_sequence()
    except KeyboardInterrupt:
        print("\n\033[93m[ SYSTEM ] Kernel Interrupted. Exiting...\033[0m")
        sys.exit()
