import os
import shutil

class FileSystem:
    def __init__(self):
        # Define the root of the Virtual OS
        self.os_root = os.path.expanduser("~/TERMOS/FILES")
        self.partitions = {
            "C:": os.path.join(self.os_root, "C"),
            "D:": os.path.join(self.os_root, "D")
        }
        
        # Ensure base directories exist
        for path in self.partitions.values():
            os.makedirs(path, exist_ok=True)
            
        self.current_drive = "C:"
        self.current_path = self.partitions["C:"]
        
        self.commands = {
            "ls / dir": "List files in the current directory",
            "cd": "Change directory (e.g., cd DEVKIT)",
            "switch": "Switch partition (switch D:)",
            "mkdir": "Create a new folder",
            "rm": "Delete a file or folder"
        }

    def get_relative_path(self):
        """Returns the path relative to the partition root for the prompt."""
        rel = os.path.relpath(self.current_path, self.partitions[self.current_drive])
        return "" if rel == "." else rel

    def list_dir(self):
        """Displays files with size and type info."""
        print(f"\n Directory of {self.current_drive}\\{self.get_relative_path()}")
        print("-" * 30)
        try:
            items = os.listdir(self.current_path)
            if not items:
                print("  (Empty Folder)")
            for item in items:
                full_path = os.path.join(self.current_path, item)
                suffix = "/" if os.path.isdir(full_path) else ""
                size = os.path.getsize(full_path)
                print(f"  {size:8} bytes | {item}{suffix}")
        except Exception as e:
            print(f"Error reading directory: {e}")
        print("")

    def change_dir(self, target):
        """Changes directory while preventing escapes from the sandbox."""
        if not target or target == "~":
            self.current_path = self.partitions[self.current_drive]
            return

        new_path = os.path.abspath(os.path.join(self.current_path, target))
        
        # Security Check: Ensure the new path is still inside the current partition
        if new_path.startswith(self.partitions[self.current_drive]):
            if os.path.exists(new_path) and os.path.isdir(new_path):
                self.current_path = new_path
            else:
                print("\033[91mDirectory not found.\033[0m")
        else:
            print("\033[91mAccess Denied: Cannot escape partition root.\033[0m")

    def switch_partition(self, drive_letter):
        """Switches between C: and D: drives."""
        drive_letter = drive_letter.upper()
        if not drive_letter.endswith(":"):
            drive_letter += ":"
            
        if drive_letter in self.partitions:
            self.current_drive = drive_letter
            self.current_path = self.partitions[drive_letter]
            print(f"Switched to {drive_letter}")
        else:
            print(f"\033[91mDrive {drive_letter} does not exist.\033[0m")

    def make_directory(self, name):
        if not name: return
        try:
            os.makedirs(os.path.join(self.current_path, name), exist_ok=True)
            print(f"Folder '{name}' created.")
        except Exception as e:
            print(f"Error: {e}")

    def delete_item(self, name):
        if not name: return
        target = os.path.join(self.current_path, name)
        try:
            if os.path.isfile(target):
                os.remove(target)
                print(f"File '{name}' deleted.")
            elif os.path.isdir(target):
                shutil.rmtree(target)
                print(f"Folder '{name}' deleted.")
        except Exception as e:
            print(f"Deletion failed: {e}")
