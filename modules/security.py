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
        
        self.registry = {"color": "\033[92m"}
        self.cloud_users = {}
        self.file_sha = None 

    def _get_headers(self):
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def sync_from_cloud(self):
        """Fetches the latest user database and its SHA ID."""
        try:
            response = requests.get(self.api_url, headers=self._get_headers())
            if response.status_code == 200:
                data = response.json()
                decoded_bytes = base64.b64decode(data['content'])
                self.cloud_users = json.loads(decoded_bytes.decode('utf-8'))
                self.file_sha = data['sha'] # REQUIRED for updates
                return True
            elif response.status_code == 404:
                print("\033[93m[ WARN ] Cloud Registry not found. Initializing...\033[0m")
                self.cloud_users = {}
                return True
            return False
        except Exception as e:
            print(f"\033[91m[ CLOUD ERR ] {e}\033[0m")
            return False

    def push_to_cloud(self):
        """Saves updated users to GitHub using the mandatory SHA ID."""
        content_str = json.dumps(self.cloud_users, indent=4)
        encoded_content = base64.b64encode(content_str.encode()).decode()
        
        data = {
            "message": f"TermOS Account Sync: {time.ctime()}",
            "content": encoded_content,
            "sha": self.file_sha # Tells GitHub which version to replace
        }
        
        response = requests.put(self.api_url, headers=self._get_headers(), json=data)
        
        if response.status_code in [200, 201]:
            print("\033[92m[ SUCCESS ] Cloud Database Updated.\033[0m")
            self.file_sha = response.json()['content']['sha']
        else:
            print(f"\033[91m[ PUSH FAILED ] GitHub Error {response.status_code}\033[0m")
            print(f"Details: {response.json().get('message')}")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def signup(self):
        """Cloud-based user registration."""
        print("\n--- TermOS CLOUD SIGNUP ---")
        self.sync_from_cloud()
        
        user = input("Choose Username: ").strip()
        if user in self.cloud_users:
            print("\033[91mError: Username already exists in Cloud.\033[0m")
            return
        
        pwd = getpass.getpass("Create Password: ")
        conf = getpass.getpass("Confirm Password: ")
        
        if pwd == conf and len(pwd) >= 4:
            self.cloud_users[user] = self.hash_password(pwd)
            self.push_to_cloud()
        else:
            print("\033[91mSignup failed. Passwords mismatch or too short.\033[0m")

    def login(self):
        """Authenticates session against GitHub Cloud."""
        if not self.sync_from_cloud():
            return None
            
        user = input("TermOS Username: ").strip()
        if user not in self.cloud_users:
            print("\033[91mUser not found.\033[0m")
            return None
        
        pwd = getpass.getpass("Password: ")
        if self.hash_password(pwd) == self.cloud_users[user]:
            return user
        
        print("\033[91mInvalid Password.\033[0m")
        return None
