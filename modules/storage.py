import os
import shutil

class FileSystem:
    def __init__(self):
        # Physical root for all OS data
        self.base_path = os.path.expanduser("~/TERMOS/FILES")
        self.partitions = ["C:", "D:", "E:"]
        self.current_drive = "C:"
        self.current_dir = "" # Relative to the partition root
        
        # Command Registry for the Help menu
        self.commands = {
            "ls / dir": "List files and folders",
            "cd": "Change directory (e.g., cd system)",
            "switch": "Change partition (e.g., switch D:)",
            "mkdir": "Create a new directory",
            "notepad": "Create/Edit a text file",
            "rm": "Delete a file or folder"
        }
        self._ensure_partitions()

    def _ensure_partitions(self):
        """Creates physical folders for C, D, and E if missing."""
        for drive in self.partitions:
            path = os.path.join(self.base_path, drive.replace(":", ""))
            os.makedirs(path, exist_ok=True)

    def get_real_path(self):
        """Translates the virtual path to a real Termux path."""
        drive_letter = self.current_drive.replace(":", "")
        return os.path.join(self.base_path, drive_letter, self.current_dir)

    def get_prompt(self):
        """Returns the classic Windows-style prompt string."""
        return f"\033[92m{self.current_drive}\\{self.current_dir}>\033[0m "

    def list_dir(self):
        path = self.get_real_path()
        print(f"\n Directory of {self.current_drive}\\{self.current_dir}\n")
        items = os.listdir(path)
        if not items:
            print("  (Empty)")
        for item in items:
            suffix = "/" if os.path.isdir(os.path.join(path, item)) else ""
            print(f"  {item}{suffix}")
        print("")

    def change_dir(self, target):
        if target == "..":
            # Go back one level
            self.current_dir = os.path.dirname(self.current_dir)
        elif target == "\\":
            self.current_dir = ""
        else:
            new_rel_path = os.path.join(self.current_dir, target).strip("/")
            full_path = os.path.join(self.base_path, self.current_drive.replace(":", ""), new_rel_path)
            if os.path.isdir(full_path):
                self.current_dir = new_rel_path
            else:
                print(f"Path not found: {target}")

    def switch_partition(self, drive_letter):
        drive_letter = drive_letter.upper()
        if ":" not in drive_letter:
            drive_letter += ":"
            
        if drive_letter in self.partitions:
            self.current_drive = drive_letter
            self.current_dir = ""
            print(f"Switched to drive {drive_letter}")
        else:
            print(f"Error: Drive {drive_letter} does not exist.")

    def make_directory(self, name):
        if not name:
            print("Usage: mkdir [name]")
            return
        path = os.path.join(self.get_real_path(), name)
        os.makedirs(path, exist_ok=True)
        print(f"Directory '{name}' created.")

    def notepad(self, filename):
        print(f"--- TermOS Notepad: {filename} ---")
        print("Enter text. Type ':save' on a new line to finish.")
        content = []
        while True:
            line = input()
            if line.strip().lower() == ":save":
                break
            content.append(line)
        
        full_path = os.path.join(self.get_real_path(), filename)
        with open(full_path, "w") as f:
            f.write("\n".join(content))
        print(f"File '{filename}' saved.")
