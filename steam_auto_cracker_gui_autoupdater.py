import traceback

try: # Handles Python errors to write them to a log file so they can be reported and fixed more easily.
    import requests
    import os
    import subprocess
    import shutil
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
            self.tries += 1
            req = requests.get(self.url, timeout=10)
            if not req.ok:
                if self.tries < RETRY_MAX:
                    # Do another try
                    print(f"- {self.name} request failed, retrying in {RETRY_DELAY}s... ({self.tries}/{RETRY_MAX} tries)")
                    sleep(RETRY_DELAY)
                    self.DoRequest()
                else:
                    print(f"[!] Connection failed after {RETRY_MAX} tries. Are you connected to the Internet? Is GitHub online?")
                    raise Exception(f"SACRequest: Connection failed after {RETRY_MAX} tries")
            else:
                self.req = req
    
    
    print(f"Steam Auto Cracker GUI - Autoupdater v{VERSION}\n")
    
    print("This program will automatically update Steam Auto Cracker GUI, please DO NOT CLOSE IT.\nRetrieving the latest version...")
    req = SACRequest("https://raw.githubusercontent.com/BigBoiCJ/SteamAutoCracker/autoupdater/latestversion.json", "RetrieveLatestVersionJson").req
    data = req.json()
    latestversion = data["version"]
    print(f"Latest version found: {latestversion}")
    
    download_link = data["link"]
    download_link = download_link.replace("[VERSION]", latestversion)
    print(f"Downloading {download_link}")
    req = SACRequest(download_link, "DownloadLatestRelease").req
    
    print(f"Finished downloading the latest release archive!\nExtracting the archive...")
    with zipfile.ZipFile(io.BytesIO(req.content)) as zip:
        folder_name = zip.namelist()[0] # "Steam Auto Cracker GUI (vX.X.X)/"
        zip.extractall()
    # We should now have a new "Steam Auto Cracker GUI (vX.X.X)/" folder. Remove the current SAC installation.
    
    print("Finished extracting the archive!\nRemoving the old installation... (DO NOT CLOSE THE AUTOUPDATER!)\n")
    files = os.listdir()
    for file in files:
        if file in IGNORE_FILES: # Ignore specific files/directories
            continue
        
        skip_file = False
        for ext in IGNORE_EXTS: # Ignore specific file extensions
            if file.endswith(ext):
                skip_file = True
                break
        if skip_file:
            continue
        
        if file == folder_name[:-1]: # Ignore the new installation (without the last "/")
            continue
        
        if os.path.isfile(file): # If file
            os.remove(file)
            print(f"   Removed file {file}")
        else: # If folder/directory
            shutil.rmtree(file)
            print(f"   Removed folder {file} and its content")
    
    print("\nFinished removing the old installation.\nMoving the new installation... (DO NOT CLOSE THE AUTOUPDATER!)")
    files = os.listdir(folder_name)
    for file in files:
        shutil.move(folder_name + file, "./") # Move to the current directory
    os.rmdir(folder_name[:-1]) # Now remove the extracted directory
    
    print("Finished moving the new installation.\n\nUpdate successful! Opening SAC GUI in 3 seconds...")
    sleep(3)
    subprocess.Popen("steam_auto_cracker_gui.exe") # Open SAC GUI
    exit()

except Exception:
    # Handle Python errors
    print("\n[!!!] A Python error occurred! Writing the error to the autoupdater_error.log file.\n---")
    with open("autoupdater_error.log", "w", encoding="utf-8") as errorFile:
        errorFile.write(f"SteamAutoCracker GUI - Autoupdater v{VERSION}\n---\nA Python error occurred!\nPlease report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.\n---\n\n")
        traceback.print_exc(file=errorFile)
    traceback.print_exc()
    print("---\nError written to autoupdater_error.log, please report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.")