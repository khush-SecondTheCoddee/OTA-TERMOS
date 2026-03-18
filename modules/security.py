import os
import json
import hashlib
import getpass
import time
import requests
import base64

class SecurityGate:
    def __init__(self):
        # Cloud Configuration
        self.token = "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"
        self.repo = "khush-SecondTheCoddee/TERMOS-ACCOUNTS"
        self.api_url = f"https://api.github.com/repos/{self.repo}/contents/users.json"
        
        self.registry_path = os.path.expanduser("~/TERMOS/system/registry.json")
        self.registry = {"color": "\033[92m"}
        self.cloud_users = {}
        self.file_sha = None 

    def _get_headers(self):
        return {"Authorization": f"token {self.token}", "Accept": "application/vnd.github.v3+json"}

    def sync_from_cloud(self):
        """Fetches the user database from the private GitHub repo."""
        try:
            response = requests.get(self.api_url, headers=self._get_headers())
            if response.status_code == 200:
                data = response.json()
                decoded_bytes = base64.b64decode(data['content'])
                self.cloud_users = json.loads(decoded_bytes.decode('utf-8'))
                self.file_sha = data['sha']
                return True
            return False
        except Exception as e:
            print(f"\033[91m[ CLOUD ERR ] {e}\033[0m")
            return False

    def push_to_cloud(self):
        """Saves updated users to the private GitHub repo."""
        content_str = json.dumps(self.cloud_users, indent=4)
        encoded_content = base64.b64encode(content_str.encode()).decode()
        data = {"message": "Update Users", "content": encoded_content, "sha": self.file_sha}
        requests.put(self.api_url, headers=self._get_headers(), json=data)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def signup(self):
        self.sync_from_cloud()
        print("\n--- TermOS CLOUD SIGNUP ---")
        user = input("Username: ").strip()
        if user in self.cloud_users:
            print("Username taken.")
            return
        pwd = getpass.getpass("Password: ")
        self.cloud_users[user] = self.hash_password(pwd)
        self.push_to_cloud()
        print(f"Account {user} created in Cloud.")

    def login(self):
        if not self.sync_from_cloud(): return None
        user = input("TermOS Username: ").strip()
        if user not in self.cloud_users: return None
        pwd = getpass.getpass("Password: ")
        if self.hash_password(pwd) == self.cloud_users[user]:
            return user
        return None
