import os
import json
import hashlib
import getpass
import time
import requests
import base64

class SecurityGate:
    def __init__(self):
        # --- CONFIGURATION ---
        self.token = "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"
        self.repo = "khush-SecondTheCoddee/TERMOS-ACCOUNTS"
        # We add 'ref=main' to explicitly tell GitHub which branch to use
        self.api_url = f"https://api.github.com/repos/{self.repo}/contents/users.json?ref=main"
        
        self.registry = {"color": "\033[92m"}
        self.cloud_users = {}
        self.file_sha = None 

    def _get_headers(self):
        """Standardized headers for Private Repo Access."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    def sync_from_cloud(self):
        """Fetches the latest user database and its SHA ID."""
        try:
            print(f"\033[94m[ CLOUD ] Syncing with {self.repo}...\033[0m")
            response = requests.get(self.api_url, headers=self._get_headers())
            
            if response.status_code == 200:
                data = response.json()
                # GitHub returns content as base64 with newlines; we must strip them
                clean_content = data['content'].replace("\n", "")
                decoded_bytes = base64.b64decode(clean_content)
                self.cloud_users = json.loads(decoded_bytes.decode('utf-8'))
                self.file_sha = data['sha'] 
                return True
            elif response.status_code == 404:
                print("\033[93m[ WARN ] users.json not found. Creating new registry...\033[0m")
                self.cloud_users = {}
                return True
            else:
                print(f"\033[91m[ SYNC FAILED ] HTTP {response.status_code}\033[0m")
                print(f"Error: {response.json().get('message')}")
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
            "content": encoded_content
        }
        
        # If the file already exists, we MUST provide the SHA to update it
        if self.file_sha:
            data["sha"] = self.file_sha
        
        # Note: We use the URL without the '?ref=main' parameter for PUT requests
        put_url = self.api_url.split('?')[0]
        response = requests.put(put_url, headers=self._get_headers(), json=data)
        
        if response.status_code in [200, 201]:
            print("\033[92m[ SUCCESS ] Cloud Database Updated.\033[0m")
            self.file_sha = response.json()['content']['sha']
        else:
            print(f"\033[91m[ PUSH FAILED ] GitHub Error {response.status_code}\033[0m")
            print(f"Details: {response.json().get('message')}")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def signup(self):
        print("\n--- TermOS CLOUD SIGNUP ---")
        if not self.sync_from_cloud(): return
        
        user = input("Choose Username: ").strip()
        if user in self.cloud_users:
            print("\033[91mError: Username already exists.\033[0m")
            return
        
        pwd = getpass.getpass("Create Password: ")
        conf = getpass.getpass("Confirm Password: ")
        
        if pwd == conf and len(pwd) >= 4:
            self.cloud_users[user] = self.hash_password(pwd)
            self.push_to_cloud()
        else:
            print("\033[91mSignup failed. Check password length/match.\033[0m")

    def login(self):
        if not self.sync_from_cloud(): return None
        user = input("TermOS Username: ").strip()
        if user not in self.cloud_users:
            print("\033[91mUser not found.\033[0m")
            return None
        pwd = getpass.getpass("Password: ")
        if self.hash_password(pwd) == self.cloud_users[user]:
            return user
        print("\033[91mInvalid Password.\033[0m")
        return None
