import os
import shutil

class FileSystem:
    def __init__(self):
        # Physical root for all OS data
        self.base_path = os.path.expanduser("~/TERMOS/FILES")
        # Partitions defined but access will be restricted
        self.partitions = ["C:", "D:", "E:"]
        self.current_drive = "C:"
        self.current_dir = "" 
        
        # Command Registry for the Help menu
        self.commands = {
            "ls / dir": "List files and folders",
            "cd": "Change directory",
            "switch": "Change partition (RESTRICTED)",
            "mkdir": "Create a new folder",
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

    def get_prompt(self, color_code):
        """Returns the classic Windows-style prompt string with the system theme."""
        return f"{color_code}{self.current_drive}\\{self.current_dir}>{0}\033[0m ".format("\033[0m")

    def list_dir(self):
        path = self.get_real_path()
        print(f"\n Directory of {self.current_drive}\\{self.current_dir}\n")
        try:
            items = os.listdir(path)
            if not items:
                print("  (Empty)")
            for item in items:
                suffix = "/" if os.path.isdir(os.path.join(path, item)) else ""
                print(f"  {item}{suffix}")
        except FileNotFoundError:
            print("  [ ERROR ] Current directory path is invalid.")
        print("")

    def change_dir(self, target):
        if target == "..":
            self.current_dir = os.path.dirname(self.current_dir)
        elif target == "\\" or target == "/":
            self.current_dir = ""
        else:
            new_rel_path = os.path.join(self.current_dir, target).strip("/")
            full_path = os.path.join(self.base_path, self.current_drive.replace(":", ""), new_rel_path)
            if os.path.isdir(full_path):
                self.current_dir = new_rel_path
            else:
                print(f"Path not found: {target}")

    def switch_partition(self, drive_letter):
        """Logic to block unauthorized partition switching."""
        drive_letter = drive_letter.upper().replace(":", "")
        
        # Security Restriction: Only allow switching to C:
        if drive_letter == "C":
            self.current_drive = "C:"
            self.current_dir = ""
            print("[ SYSTEM ] Switched to Primary Partition (C:)")
        else:
            print(f"\033[91m[ ACCESS DENIED ] Partition {drive_letter}: is LOCKED by System Administrator.\033[0m")
            print("Contact your developer for 'Level 2' clearance.")

    def make_directory(self, name):
        if not name:
            print("Usage: mkdir [name]")
            return
        path = os.path.join(self.get_real_path(), name)
        os.makedirs(path, exist_ok=True)
        print(f"Directory '{name}' created.")

    def delete_item(self, target):
        if not target:
            print("Usage: rm [filename/folder]")
            return
        path = os.path.join(self.get_real_path(), target)
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            print(f"Deleted: {target}")
        else:
            print("File or folder not found.")

    def notepad(self, filename):
        print(f"--- TermOS Notepad: {filename} ---")
        print("Enter text. Type ':save' on a new line to finish.")
        content = []
        while True:
            try:
                line = input()
                if line.strip().lower() == ":save":
                    break
                content.append(line)
            except EOFError:
                break
        
        full_path = os.path.join(self.get_real_path(), filename)
        with open(full_path, "w") as f:
            f.write("\n".join(content))
        print(f"File '{filename}' saved to {self.current_drive}.")
