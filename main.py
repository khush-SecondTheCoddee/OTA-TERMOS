import os
import sys
import time

# --- SUBSYSTEM INITIALIZATION ---
try:
    from modules.security import SecurityGate
    from modules.storage import FileSystem
    from modules.system import SystemTools
    from modules.dev import DevKit
except ImportError as e:
    print(f"\033[91m[ KERNEL PANIC ] Critical Module Missing: {e}\033[0m")
    sys.exit()

class TermOS:
    def __init__(self):
        # Initialize Core Subsystems
        self.security = SecurityGate()
        self.storage = FileSystem()
        self.system = SystemTools()
        
        # Link Security to DevKit for Cloud Permissions
        self.dev = DevKit(self.security)
        
        self.is_running = True

    def boot_sequence(self):
        """Pre-shell login challenge and hardware check."""
        os.system('clear')
        self.system.play_boot_animation()
        
        print("\033[94m[ AUTH ] Connecting to TermOS Cloud Gateway...\033[0m")
        time.sleep(1)
        
        # Force Cloud Login
        user = self.security.login()
        if user:
            self.dev.current_user = user
            print(f"\033[92m[ SUCCESS ] Session started for {user}.\033[0m")
        else:
            print("\033[93m[ WARN ] Authentication Failed. Entering Guest Mode.\033[0m")
            time.sleep(1.5)
        
        self.run_shell()

    def run_shell(self):
        """The main Operating Loop."""
        color = self.security.registry.get("color", "\033[92m")
        reset = "\033[0m"

        while self.is_running:
            user_display = self.dev.current_user if self.dev.current_user else "Guest"
            prompt_str = f"{color}{self.storage.current_drive}\\{user_display}>{reset} "
            
            try:
                user_input = input(prompt_str).strip().split()
            except (EOFError, KeyboardInterrupt):
                print("\nUse 'exit' to shut down safely.")
                continue
                
            if not user_input: continue
            
            cmd = user_input[0].lower()
            args = user_input[1:]

            # --- ROUTING TABLE ---
            if cmd == "login":
                user = self.security.login()
                if user: self.dev.current_user = user
            
            elif cmd == "signup":
                self.security.signup()

            elif cmd == "ide":
                self.dev.ide()
            
            elif cmd == "publish":
                self.dev.publish_to_github(args[0] if args else "")

            elif cmd == "store":
                self.dev.browse_store()

            elif cmd in ["ls", "dir"]:
                self.storage.list_dir()
                
            elif cmd == "cd":
                self.storage.change_dir(args[0] if args else "")
                
            elif cmd == "help":
                all_cmds = {**self.system.commands, **self.storage.commands, **self.dev.commands}
                self.system.display_help(all_cmds)
                
            elif cmd == "update":
                self.system.run_ota_update()

            elif cmd == "clear" or cmd == "cls":
                os.system('clear')

            elif cmd == "exit":
                print(f"{color}TermOS: Shutting down...{reset}")
                self.is_running = False

            else:
                print(f"'{cmd}' is not recognized as an internal or external command.")

if __name__ == "__main__":
    kernel = TermOS()
    try:
        kernel.boot_sequence()
    except Exception as e:
        print(f"\033[91m[ KERNEL PANIC ] {e}\033[0m")
        time.sleep(3)
        sys.exit()
