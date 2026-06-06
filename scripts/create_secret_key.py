"""
GitHub(Getea)にSecretを登録するスクリプト

Example:
    `set -a; source .env.deploy; set +a; python scripts/create_secret_key.py`
"""

import os
import sys
import json
import urllib.request


def must_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if value is None:
        print(f"Error: {var_name} is not set.")
        sys.exit(1)
    return value


GIT_API_URL = os.getenv("GIT_API_URL", "https://api.github.com")
GIT_API_TOKEN = must_env("GIT_API_TOKEN")
OWNER_NAME = must_env("OWNER_NAME")
REPO_NAME = must_env("REPO_NAME")


def create_secret(secret_name: str, secret_value: str):
    url = f"{GIT_API_URL}/repos/{OWNER_NAME}/{REPO_NAME}/actions/secrets/{secret_name}"
    data = {"data": secret_value}
    headers = {
        "Authorization": f"token {GIT_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = json.dumps(data).encode()
    req = urllib.request.Request(url, data=payload, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Secret '{secret_name}' {response.status} successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")


def main():
    if os.getenv("SSH_HOST"):
        create_secret("SSH_HOST", must_env("SSH_HOST"))
        create_secret("SSH_USER", os.getenv("SSH_USER", "deploy"))
    if os.getenv("PR_GITEA_TOKEN"):
        create_secret("PR_GITEA_TOKEN", must_env("PR_GITEA_TOKEN"))
    if os.getenv("OPENAI_API_KEY"):
        create_secret("OPENAI_API_KEY", must_env("OPENAI_API_KEY"))
    if os.getenv("SSH_PRIVATE_KEY"):
        private_key = ""
        with open("deploy.key", "r") as f:
            private_key = f.read()
        print(private_key[:50])
        if private_key:
            create_secret("SSH_PRIVATE_KEY", private_key)


if __name__ == "__main__":
    main()
