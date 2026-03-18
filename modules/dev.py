import os
import sys
import subprocess
import requests
import base64

class DevKit:
    def __init__(self, security_module):
        self.security = security_module
        self.current_user = None
        
        # GitHub Configuration for Apps Store
        self.token = "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"
        self.repo = "khush-SecondTheCoddee/TERMOS-APPS"
        self.api_url = f"https://api.github.com/repos/{self.repo}/contents/"
        
        # Local Workspace
        self.work_dir = os.path.expanduser("~/TERMOS/FILES/C/DEVKIT")
        os.makedirs(self.work_dir, exist_ok=True)

        self.commands = {
            "ide": "Open the code editor to create an app",
            "run": "Execute a local script (run <file.py>)",
            "publish": "Upload an app to the GitHub Store",
            "store": "Browse and download community apps",
            "apps": "List all apps in your DEVKIT folder"
        }

    def ide(self):
        """TermOS Internal Code Editor."""
        if not self.current_user:
            print("\033[91m[ ! ] Login required to use the IDE.\033[0m")
            return
            
        filename = input("App Name (e.g. hello.py): ").strip()
        if not filename.endswith(".py"): filename += ".py"
        
        print(f"\n--- TermOS IDE: {filename} ---")
        print("Enter your Python code. Type ':q' on a new line to save.")
        
        code_lines = []
        while True:
            line = input(">>> ")
            if line.strip() == ":q": break
            code_lines.append(line)
        
        with open(os.path.join(self.work_dir, filename), "w") as f:
            f.write("\n".join(code_lines))
        print(f"\033[92m[ SAVED ] {filename} stored in C:\\DEVKIT\033[0m")

    def run_app(self, filename):
        """Executes the Python script within the OS context."""
        path = os.path.join(self.work_dir, filename)
        if os.path.exists(path):
            print(f"\033[94m[ EXEC ] Starting {filename}...\033[0m\n")
            try:
                subprocess.run([sys.executable, path])
                print(f"\n\033[94m[ DONE ] {filename} terminated.\033[0m")
            except Exception as e:
                print(f"\033[91m[ RUNTIME ERROR ] {e}\033[0m")
        else:
            print(f"\033[91mFile {filename} not found in DEVKIT.\033[0m")

    def publish_to_github(self, filename):
        """Pushes the local file to the TERMOS-APPS repository."""
        if not self.current_user:
            print("\033[91m[ ! ] Login required to publish apps.\033[0m")
            return

        path = os.path.join(self.work_dir, filename)
        if not os.path.exists(path):
            print("\033[91mFile not found in DEVKIT.\033[0m")
            return

        with open(path, "r") as f:
            content = f.read()

        encoded_content = base64.b64encode(content.encode()).decode()
        
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Commit message includes the developer's cloud username
        data = {
            "message": f"App Deployment: {filename} by Dev:{self.current_user}",
            "content": encoded_content
        }

        print(f"\033[93m[ UPLOAD ] Publishing {filename} to Store...\033[0m")
        response = requests.put(self.api_url + filename, headers=headers, json=data)

        if response.status_code in [201, 200]:
            print(f"\033[92m[ SUCCESS ] {filename} is now LIVE on GitHub!\033[0m")
        else:
            print(f"\033[91m[ FAIL ] Upload rejected: {response.status_code}\033[0m")

    def browse_store(self):
        """Lists and downloads apps from the public repository."""
        print("\n--- TermOS APP STORE ---")
        try:
            headers = {"Authorization": f"token {self.token}"}
            response = requests.get(self.api_url, headers=headers)
            if response.status_code == 200:
                files = response.json()
                apps = [f['name'] for f in files if f['name'].endswith('.py')]
                for i, app in enumerate(apps):
                    print(f" [{i}] {app}")
                
                choice = input("\nEnter Number to download (or 'q'): ")
                if choice.isdigit() and int(choice) < len(apps):
                    self.download_app(apps[int(choice)])
            else:
                print("\033[91mCould not reach Store server.\033[0m")
        except Exception as e:
            print(f"Store Error: {e}")

    def download_app(self, app_name):
        headers = {"Authorization": f"token {self.token}"}
        response = requests.get(self.api_url + app_name, headers=headers)
        if response.status_code == 200:
            content = base64.b64decode(response.json()['content']).decode()
            with open(os.path.join(self.work_dir, app_name), "w") as f:
                f.write(content)
            print(f"\033[92m[ OK ] Installed {app_name} to C:\\DEVKIT\033[0m")

    def list_apps(self):
        apps = [f for f in os.listdir(self.work_dir) if f.endswith(".py")]
        print(f"\nLocal Apps in C:\\DEVKIT:")
        for app in apps:
            print(f"  > {app}")
