import subprocess
import requests
import time
import os
import re

from backend.utils.constants import NGROK_API_URL, NGROK_CONFIG_PATH, VITE_CONFIG_PATH, CONSTANTS_PATH, ENV_PATH

def start_ngrok():
    ngrok_path = get_ngrok_path()
    if ngrok_path :
        subprocess.Popen([ngrok_path, "start", "--all", "--config", NGROK_CONFIG_PATH])
        print("Starting ngrok...")
        time.sleep(5)  # Wait for tunnels to be up
    else :
        raise FileExistsError(f"Ngrok file not found")

def get_ngrok_urls():
    resp = requests.get(NGROK_API_URL).json()
    urls = {}
    for tunnel in resp["tunnels"]:
        name = tunnel["name"]
        public_url = tunnel["public_url"]
        urls[name] = public_url
    return urls

def update_constants_py(backend_url):
    with open(CONSTANTS_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(CONSTANTS_PATH, "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith("BASE_URL"):
                f.write(f'BASE_URL = "{backend_url}"\n')
            else:
                f.write(line)

def update_vite_config(frontend_url):
    with open(VITE_CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract hostname from the public URL
    import urllib.parse
    hostname = urllib.parse.urlparse(frontend_url).hostname

    # Update proxy target
    content = re.sub(
        r'(target:\s*")[^"]+(")',
        rf'\1{frontend_url}\2',
        content,
        flags=re.DOTALL
    )
    # Update allowedHosts
    content = re.sub(
        r'(allowedHosts:\s*)\[[^\]]*\]',
        rf'\1["{hostname}"]',
        content
    )

    with open(VITE_CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(content)

def update_env_file(backend_url):
    lines = []
    found = False

    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("VITE_API_BASE="):
                    lines.append(f"VITE_API_BASE={backend_url}\n")
                    found = True
                else:
                    lines.append(line)

    if not found:
        lines.append(f"VITE_API_BASE={backend_url}\n")

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

def run_servers():
    subprocess.Popen(
        ["cmd", "/c", "start", "cmd", "/k", "uvicorn backend.main:app --reload"],
        shell=True
    )

    subprocess.Popen(
        ["cmd", "/c", "start", "cmd", "/k", "npm run dev"],
        cwd="frontend",
        shell=True
    )

def get_ngrok_path():
    """
    Returns the full path to ngrok.exe if it exists in the default npm global path.
    Otherwise returns None.
    """
    appdata = os.getenv("APPDATA")  # C:\Users\<User>\AppData\Roaming
    if not appdata:
        return None  # Shouldn't happen on Windows, but safe check

    ngrok_path = os.path.join(appdata, "npm", "ngrok.cmd")

    if os.path.isfile(ngrok_path):
        return ngrok_path
    return None

def booting_servers():
    start_ngrok()
    urls = get_ngrok_urls()

    backend_url = urls.get("backend")
    frontend_url = urls.get("frontend")

    if backend_url:
        update_constants_py(backend_url)
        update_env_file(backend_url)
    if frontend_url:
        update_vite_config(frontend_url)
    time.sleep(1) # Make sure config files are updatd before launching servers
    run_servers()

if __name__ == "__main__":
    booting_servers()