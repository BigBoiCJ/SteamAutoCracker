import traceback
import sys

try: # Handles Python errors to write them to a log file so they can be reported and fixed more easily.
    import requests
    import os
    import subprocess
    import shutil
    import tempfile
    from time import sleep
    import zipfile
    import io
    from sys import exit

    VERSION = "1.0.1"

    RETRY_DELAY = 3 # Delay in seconds before retrying a failed request. (default, can be modified in config.ini)
    RETRY_MAX = 5 # Number of failed tries (includes the first try) after which SAC will stop trying and quit. (default, can be modified in config.ini)
    
    IGNORE_FILES = ("steam_auto_cracker_gui_autoupdater.py", "steam_auto_cracker_gui_autoupdater.exe", "applist.txt")
    IGNORE_EXTS = (".ini", ".log")

    class SACRequest:
        def __init__(self, url:str, name:str = "Unnamed"):
            self.url = url
            self.tries = 0
            self.name = name
            self.DoRequest()

        def DoRequest(self):
            # Iterative retry with exception handling (safer for frozen executables)
            while self.tries < RETRY_MAX:
                self.tries += 1
                try:
                    req = requests.get(self.url, timeout=10)
                except requests.exceptions.RequestException:
                    req = None

                if req is None or not getattr(req, 'ok', False):
                    if self.tries < RETRY_MAX:
                        print(f"- {self.name} request failed, retrying in {RETRY_DELAY}s... ({self.tries}/{RETRY_MAX} tries)")
                        sleep(RETRY_DELAY)
                        continue
                    else:
                        print(f"[!] Connection failed after {RETRY_MAX} tries. Are you connected to the Internet? Is GitHub online?")
                        raise Exception(f"SACRequest: Connection failed after {RETRY_MAX} tries")
                else:
                    self.req = req
                    return
    
    
    print(f"Steam Auto Cracker GUI - Autoupdater v{VERSION}\n")
    
    print("This program will automatically update Steam Auto Cracker GUI, please DO NOT CLOSE IT.\nRetrieving the latest version...")
    req = SACRequest("https://raw.githubusercontent.com/SquashyHydra/SteamAutoCracker/autoupdater/latestversion.json", "RetrieveLatestVersionJson").req
    data = req.json()
    latestversion = data["version"]
    print(f"Latest version found: {latestversion}")
    
    download_link = data["link"]
    download_link = download_link.replace("[VERSION]", latestversion)
    print(f"Downloading {download_link}")
    req = SACRequest(download_link, "DownloadLatestRelease").req
    
    print(f"Finished downloading the latest release archive!\nExtracting the archive...")

    # Extract into a temporary directory to avoid issues when running as a frozen executable
    tempdir = tempfile.mkdtemp()
    with zipfile.ZipFile(io.BytesIO(req.content)) as z:
        namelist = z.namelist()
        if not namelist:
            raise Exception("Downloaded archive is empty")

        # Determine if archive has a single top-level folder
        tops = [n.split('/')[0] for n in namelist if n and not n.startswith('/')]
        top_folder = tops[0] if tops and all(t == tops[0] for t in tops) else None

        z.extractall(tempdir)

        print("Finished extracting the archive!\nRemoving the old installation... (DO NOT CLOSE THE AUTOUPDATER!)\n")

        # Determine base directory where the running single-file exe or the script is located
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

    # Remove old installation files/folders in the base directory (be careful!)
    cwd_files = os.listdir(base_dir)
    for file in cwd_files:
        if file in IGNORE_FILES: # Ignore specific files/directories
            continue

        skip_file = False
        for ext in IGNORE_EXTS: # Ignore specific file extensions
            if file.endswith(ext):
                skip_file = True
                break
        if skip_file:
            continue

        path = os.path.join(base_dir, file)

        if os.path.isfile(path): # If file
            os.remove(path)
            print(f"   Removed file {file}")
        else: # If folder/directory
            if os.path.islink(path): # If it's a symlink, remove the link only
                os.unlink(path)
                print(f"   Removed symlink {file}")
            elif os.path.isdir(path):
                shutil.rmtree(path)
                print(f"   Removed folder {file} and its content")

    print("\nFinished removing the old installation.\nMoving the new installation... (DO NOT CLOSE THE AUTOUPDATER!)")

    # Source directory inside tempdir: either the top folder or the tempdir itself
    if top_folder:
        extracted_root = os.path.join(tempdir, top_folder)
    else:
        extracted_root = tempdir

    files = os.listdir(extracted_root)
    for file in files:
        src = os.path.join(extracted_root, file)
        dst = os.path.join(base_dir, file)
        shutil.move(src, dst)
    # Cleanup temporary extraction directory
    try:
        shutil.rmtree(tempdir)
    except Exception:
        pass

    print("Finished moving the new installation.\n\nUpdate successful! Opening SAC GUI in 3 seconds...")
    sleep(3)
    # Open SAC GUI from the base directory
    try:
        subprocess.Popen([os.path.join(base_dir, "steam_auto_cracker_gui.exe")], cwd=base_dir)
    except Exception:
        subprocess.Popen("steam_auto_cracker_gui.exe") # fallback
    exit()

except Exception:
    # Handle Python errors and write log next to the executable/script
    print("\n[!!!] A Python error occurred! Writing the error to the autoupdater_error.log file.\n---")
    try:
        if getattr(sys, 'frozen', False):
            error_dir = os.path.dirname(sys.executable)
        else:
            error_dir = os.path.dirname(os.path.abspath(__file__))
    except Exception:
        error_dir = os.getcwd()

    version = globals().get("VERSION", "unknown")
    log_path = os.path.join(error_dir, "autoupdater_error.log")
    with open(log_path, "w", encoding="utf-8") as errorFile:
        errorFile.write(f"SteamAutoCracker GUI - Autoupdater v{version}\n---\nA Python error occurred!\nPlease report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.\n---\n\n")
        traceback.print_exc(file=errorFile)
    traceback.print_exc()
    print(f"---\nError written to {log_path}, please report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.")