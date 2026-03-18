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
        # Initialize Subsystems
        self.security = SecurityGate()
        self.storage = FileSystem()
        self.system = SystemTools()
        
        # Pass the security instance to DevKit for Cloud Login access
        self.dev = DevKit(self.security)
        
        self.is_running = True

    def boot_sequence(self):
        """Final environment prep before the shell opens."""
        os.system('clear')
        
        # Verify Identity (Cloud Login)
        print("\033[94m[ SYSTEM ] Initializing Cloud Gateway...\033[0m")
        # Optional: Force login at boot, or allow guest mode
        # user = self.security.login()
        # if user: self.dev.current_user = user
        
        self.system.play_boot_animation()
        self.run_shell()

    def run_shell(self):
        """The Main Operating Loop."""
        # Get theme from registry (defaults to green)
        color = self.security.registry.get("color", "\033[92m")
        reset = "\033[0m"

        while self.is_running:
            # Generate the dynamic prompt: C:\Users\Admin>
            user_display = self.dev.current_user if self.dev.current_user else "Guest"
            prompt_str = f"{color}{self.storage.current_drive}\\{user_display}>{reset} "
            
            try:
                user_input = input(prompt_str).strip().split()
            except (EOFError, KeyboardInterrupt):
                print("\nUse 'exit' to shut down safely.")
                continue
                
            if not user_input:
                continue
            
            cmd = user_input[0].lower()
            args = user_input[1:]

            # --- COMMAND ROUTING ---

            # 1. ACCOUNT & AUTH COMMANDS
            if cmd == "login":
                user = self.security.login()
                if user:
                    self.dev.current_user = user
            
            elif cmd == "signup":
                self.security.signup()

            elif cmd == "whoami":
                status = f"Logged in as: {self.dev.current_user}" if self.dev.current_user else "Logged in as: Guest"
                print(status)

            # 2. APP DEVELOPMENT (ADK) COMMANDS
            elif cmd == "ide":
                self.dev.ide()
            
            elif cmd == "run":
                self.dev.run_app(args[0] if args else "")
                
            elif cmd == "publish":
                self.dev.publish_to_github(args[0] if args else "")

            elif cmd == "store":
                self.dev.browse_store()

            elif cmd == "apps":
                self.dev.list_apps()

            # 3. FILE SYSTEM COMMANDS
            elif cmd in ["ls", "dir"]:
                self.storage.list_dir()
                
            elif cmd == "cd":
                self.storage.change_dir(args[0] if args else "")
                
            elif cmd == "switch":
                self.storage.switch_partition(args[0] if args else "C:")
                
            elif cmd == "mkdir":
                self.storage.make_directory(args[0] if args else "")

            elif cmd == "rm" or cmd == "del":
                self.storage.delete_item(args[0] if args else None)

            # 4. SYSTEM COMMANDS
            elif cmd == "help":
                # Combine help menus from all modules
                all_cmds = {**self.system.commands, **self.storage.commands, **self.dev.commands}
                self.system.display_help(all_cmds)
                
            elif cmd == "update":
                self.system.run_ota_update()
                
            elif cmd == "tasklist":
                self.system.show_taskmgr()

            elif cmd == "clear" or cmd == "cls":
                os.system('clear')

            elif cmd == "exit":
                print(f"{color}TermOS: Shutting down subsystems...{reset}")
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
