import os
import sys
import subprocess
import requests
import base64

class DevKit:
    def __init__(self, security_module):
        self.security = security_module
        self.current_user = None
        self.token = "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"
        self.repo = "khush-SecondTheCoddee/TERMOS-APPS"
        self.api_url = f"https://api.github.com/repos/{self.repo}/contents/"
        self.work_dir = os.path.expanduser("~/TERMOS/FILES/C/DEVKIT")
        os.makedirs(self.work_dir, exist_ok=True)

        self.commands = {
            "login": "Login to TermOS Cloud Account",
            "signup": "Create a TermOS Cloud Account",
            "ide": "Create/Edit a Python App",
            "run": "Run a local app (run <name.py>)",
            "publish": "Upload app to TermOS-APPS Store",
            "store": "Browse and download community apps"
        }

    def ide(self):
        if not self.current_user:
            print("Please 'login' first.")
            return
        name = input("App Name: ")
        print("Enter code (type ':q' to save):")
        lines = []
        while True:
            line = input("> ")
            if line == ":q": break
            lines.append(line)
        with open(os.path.join(self.work_dir, name), "w") as f:
            f.write("\n".join(lines))

    def publish(self, name):
        if not self.current_user: return
        path = os.path.join(self.work_dir, name)
        with open(path, "r") as f:
            content = base64.b64encode(f.read().encode()).decode()
        
        headers = {"Authorization": f"token {self.token}"}
        data = {"message": f"Dev: {self.current_user}", "content": content}
        res = requests.put(self.api_url + name, headers=headers, json=data)
        if res.status_code in [200, 201]: print("Published to Store!")

    def browse_store(self):
        res = requests.get(self.api_url, headers={"Authorization": f"token {self.token}"})
        if res.status_code == 200:
            apps = [f['name'] for f in res.json() if f['name'].endswith('.py')]
            for i, a in enumerate(apps): print(f"[{i}] {a}")
            # Simplified: Add download logic here as needed
