import os
import sys
import time

try:
    from modules.security import SecurityGate
    from modules.storage import FileSystem
    from modules.system import SystemTools
except ImportError as e:
    print(f"Module Error: {e}")
    sys.exit()

class TermOS:
    def __init__(self):
        self.security = SecurityGate()
        self.storage = FileSystem()
        self.system = SystemTools()
        self.is_running = True

    def boot_sequence(self):
        os.system('clear')
        if not self.security.run_gate():
            sys.exit()
        self.system.play_boot_animation()
        self.run_shell()

    def run_shell(self):
        color = self.security.registry.get("color", "\033[92m")
        while self.is_running:
            prompt = self.storage.get_prompt(color)
            try:
                user_in = input(prompt).strip().split()
            except (EOFError, KeyboardInterrupt):
                break
                
            if not user_in: continue
            cmd = user_in[0].lower()
            args = user_in[1:]

            if cmd == "exit":
                self.is_running = False
            elif cmd == "help":
                self.system.display_help({**self.system.commands, **self.storage.commands})
            elif cmd == "update":
                self.system.run_ota_update()
            elif cmd == "tasklist":
                self.system.show_taskmgr()
            elif cmd in ["ls", "dir"]:
                self.storage.list_dir()
            elif cmd == "cd":
                self.storage.change_dir(args[0] if args else "")
            elif cmd == "switch":
                self.storage.switch_partition(args[0] if args else "C:")
            elif cmd == "clear" or cmd == "cls":
                os.system('clear')
            else:
                print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    os_instance = TermOS()
    os_instance.boot_sequence()
