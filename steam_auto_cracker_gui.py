import traceback

try: # Handles Python errors to write them to a log file so they can be reported and fixed more easily.
    import tkinter as tk
    from tkinter import ttk, filedialog, font
    from tkinterdnd2 import DND_FILES, TkinterDnD

    import requests
    import configparser
    import json
    import os
    import subprocess
    from sac_lib.get_file_version import GetFileVersion
    import shutil
    from time import sleep
    from sys import exit

    VERSION = "2.2.2"

    RETRY_DELAY = 15 # Delay in seconds before retrying a failed request. (default, can be modified in config.ini)
    RETRY_MAX = 30 # Number of failed tries (includes the first try) after which SAC will stop trying and quit. (default, can be modified in config.ini)

    HIGH_DLC_WARNING = 125

    folder_path = ""
    appID = 0
    gameSearchDone = False

    STATE_FindingInAppList = False
    STATE_UpdatingAppList = False

    EXTS_TO_REPLACE = (".txt", ".ini", ".cfg")

    GITHUB_LATESTVERSIONJSON = "https://raw.githubusercontent.com/BigBoiCJ/SteamAutoCracker/autoupdater/latestversion.json"
    GITHUB_AUTOUPDATER = "https://raw.githubusercontent.com/BigBoiCJ/SteamAutoCracker/autoupdater/steam_auto_cracker_gui_autoupdater.exe"

    def OnTkinterError(exc, val, tb):
        # Handle Tkinter Python errors
        print("\n[!!!] A Tkinter Python error occurred! Writing the error to the error_tkinter.log file.\n---")
        with open("error_tkinter.log", "w", encoding="utf-8") as errorFile:
            errorFile.write(f"SteamAutoCracker GUI v{VERSION}\n---\nA Tkinter Python error occurred!\nPlease report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.\nNOTE: '_tkinter.TclError: invalid command name' errors are normal if you closed the window while SAC was busy. In that case, you should not report the issue and just ignore it.\n---\n\n")
            traceback.print_exc(file=errorFile)
        traceback.print_exc()
        print("---\nError written to error_tkinter.log, please report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.")

        try:
            update_logs("[!!!] A Tkinter Python error occurred! The error has written to error_tkinter.log, please report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.")
        except Exception:
            pass

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
                if self.tries < int(config["Advanced"]["RetryMax"]):
                    # Do another try
                    update_logs("- " + self.name + " request failed, retrying in " + config["Advanced"]["RetryDelay"] + "s... (" + str(self.tries) + "/" + config["Advanced"]["RetryMax"] + " tries)")
                    root.update()
                    sleep(int(config["Advanced"]["RetryDelay"]))
                    self.DoRequest()
                else:
                    update_logs("[!] Connection failed after " + config["Advanced"]["RetryMax"] + " tries. Are you connected to the Internet? Is Steam online?\nIf you being rate limited (too many DLCs), you should try increasing retrydelay and retrymax in the config")
                    raise Exception(f"SACRequest: Connection failed after {config['Advanced']['RetryMax']} tries")
            else:
                self.req = req

    def handle_folder_selection(event=None):
        global folder_path
        global last_selected_folder
        last_selected_folder = config["Preferences"].get("last_selected_folder", "")
        # Reset and hide UI elements related to folder selection and game cracking
        def reset_folder_selection_ui():
            selectedFolderLabel.config(text="")
            selectedFolderLabel.pack_forget()
            frameGame2.pack_forget()
            frameCrack2.pack_forget() # Hide the crack frame

        # Determine the folder path based on the event type
        if event:  # Handling drag and drop
            folder_path_temp = event.data.strip("{}").replace("\\", "/") # Returns the directory with no "/" at the end
        else:  # Handling button click
            initial_dir = "/"
            if last_selected_folder != "" and os.path.isdir(last_selected_folder):
                initial_dir = last_selected_folder
            folder_path_temp = filedialog.askdirectory(initialdir=initial_dir) # Returns the directory with no "/" at the end

            # Fix to work on Linux: Tkinter: tuple → string
            if isinstance(folder_path_temp, tuple):
                folder_path_temp = folder_path_temp[0]


        if os.path.isdir(folder_path_temp):
            folder_path = folder_path_temp
            # Update the last dropped folder for future use
            last_selected_folder = os.path.dirname(folder_path) # If no "/" at the end, returns the parent directory
            config["Preferences"]["last_selected_folder"] = last_selected_folder
            UpdateConfig()
            folder_name = os.path.basename(folder_path) # Gets the name of the folder ("C:/Something/Games/Hello" will return "Hello")

            # Update UI elements with the selected folder information
            update_logs(f"\nSelected folder: {folder_path}")
            selectedFolderLabel.config(text=f"Selected folder:\n{folder_path}")
            selectedFolderLabel.pack()
            frameGame2.pack()

            # Update the game name entry with the folder name
            gameNameEntry.delete(0, tk.END) # Removes the content of the Entry element starting from index 0 to the end
            gameNameEntry.insert(0, folder_name) # Inserts the name of the folder in the Entry element at the start of it (index 0)

            # Show crack frame if game search is done
            if gameSearchDone:
                frameCrack2.pack()
        else:
            # Handle invalid folder selection
            update_logs("\nNo valid folder selected")
            folder_path = ""
            reset_folder_selection_ui()

    def update_logs(log_message):
        # Get current content
        current_logs = logs_text.get("1.0", tk.END)

        logs_text.config(state=tk.NORMAL)  # Enables modification (needed to add content)
        # Delete the current content
        logs_text.delete("1.0", tk.END)

        # Insert the new message at the end with a linebreak
        logs_text.insert(tk.END, current_logs + log_message)

        # Scroll the widget to the bottom
        logs_text.yview_moveto(1.0)

        # Focus on the end
        logs_text.see(tk.END)
        logs_text.config(state=tk.DISABLED)  # Disables modification (prevents the user from writing inside the field)

    def search_game():
        searchGameButton.config(state=tk.DISABLED) # Prevents the user from starting multiple searches at the same time
        frameCrack2.pack_forget() # Hide the crack frame
        global gameSearchDone
        gameSearchDone = False

        gameFoundStatus.config(text=f"")
        # Disable the ability to change the selected folder
        selectFolderButton.config(state=tk.DISABLED)
        updateAppListButton.grid_forget()
        root.update()

        global appID
        appID = 0
        if gameNameEntry.get() == "":
            update_logs("\n[!] Please enter a valid Name or AppID")
            searchGameButton.config(state=tk.NORMAL)  # Re-enable the ability to search the game
            selectFolderButton.config(state=tk.NORMAL) # Re-enable the ability to change the selected folder
            return

        try:
            appID = int(gameNameEntry.get())
        except:
            appID = FindInAppList(gameNameEntry.get())

        if appID != 0 and RetrieveGame(): # On success
            # We are now on step 3
            gameSearchDone = True
            frameCrack2.pack() # Show the crack frame
            searchGameButton.config(state=tk.NORMAL) # Re-enable the ability to search the game
            selectFolderButton.config(state=tk.NORMAL) # Re-enable the ability to change the selected folder
        else:
            searchGameButton.config(state=tk.NORMAL) # Re-enable the ability to search the game
            selectFolderButton.config(state=tk.NORMAL) # Re-enable the ability to change the selected folder

    def FindInAppList(appName):
        update_logs("\nImporting and searching the App List, this could take a few seconds if your computer isn't powerful enough.")
        gameFoundStatus.config(text=f"Searching in the App List...")
        root.update() # Update the window now
        try:
            with open("applist.txt", "r", encoding="utf-8") as file:
                data = json.load(file)
        except:
            update_logs("The App List isn't downloaded on your computer, downloading it...")
            UpdateAppList()
            return FindInAppList(appName) # Re launch this funtion

        for elem in data["applist"]["apps"]:
            if elem["name"].lower() != appName.lower():
                continue

            return elem["appid"]

        update_logs("[!] The App was not found, make sure you entered EXACTLY the Steam Game's name (watch it on Steam)")
        update_logs("If you typed it properly, you can try to update the App List. Alternatively, you can try entering the AppID.")
        gameFoundStatus.config(text=f"App not found!")

        updateAppListButton.grid(row=0, column=2, padx=(10, 0))
        return 0

    def UpdateAppList():
        updateAppListButton.grid_forget()
        update_logs("\nUpdating the App List, this could take a few seconds to up to a minute, depending on your internet connection.")
        gameFoundStatus.config(text=f"Updating the App List...")
        root.update()
        try:
            req = SACRequest("https://api.steampowered.com/ISteamApps/GetAppList/v2/", "UpdateAppList").req
        except Exception:
            gameFoundStatus.config(text=f"An error has occurred")
            return

        with open("applist.txt", "w", encoding="utf-8") as file:
            file.write(req.text)
        update_logs("App List updated!")
        gameFoundStatus.config(text=f"App List updated!")

    def RetrieveAppName(appID: int) -> str:
        try:
            req = SACRequest("https://store.steampowered.com/api/appdetails?appids=" + str(appID) + "&filters=basic", "RetrieveAppName").req
        except Exception:
            return "error"

        data = req.json()
        data = data[str(appID)]
        if (not "data" in data) or (not "name" in data["data"]):
            return "error"
        return data["data"]["name"]

    def RetrieveGame() -> bool:
        global appID
        global gameName
        global dlcIDs
        global dlcNames

        dlcIDs = []
        dlcNames = []

        update_logs("\n[1/2] Retrieving game informations from Steam...")
        gameFoundStatus.config(text=f"[1/2] Retrieving game informations from Steam...")
        root.update()
        # https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI#appdetails
        try:
            req = SACRequest("https://store.steampowered.com/api/appdetails?appids=" + str(appID) + "&filters=basic", "RetrieveGame").req
        except Exception:
            gameFoundStatus.config(text=f"An error has occurred")
            return False
        data = req.json()
        data = data[str(appID)]
        if not data["success"]:
            update_logs(f"\n[!] AppID {appID} not found.")
            gameFoundStatus.config(text=f"AppID {appID} not found.")
            appID = 0
            return False
        if config["Advanced"]["BypassGameVerification"] != "1" and data["data"]["type"] != "game":
            update_logs(f"\n[!] AppID {appID} is not a game. You can bypass this verification in the Advanced settings.")
            gameFoundStatus.config(text=f"AppID {appID} is not a game.")
            appID = 0
            return False

        gameName = data["data"]["name"]
        appID = data["data"]["steam_appid"]
        update_logs(f"- Game found! Name: {gameName} - AppID: {appID}")

        update_logs("\n[2/2] Retrieving DLCs...")
        gameFoundStatus.config(text=f"[2/2] Retrieving DLCs...")
        root.update()

        # Optional config check
        option = "0"
        try:
            option = config["Developer"]["RetrieveDLCOption"]
        except:
            pass

        if option == "1":
            # Old retrieve option
            update_logs("Using the old retrieve option (RetrieveDLCOption is set to 1)")

            if "dlc" in data["data"]:
                dlcIDs = data["data"]["dlc"]
                dlcIDsLen = len(dlcIDs)

                if dlcIDsLen >= HIGH_DLC_WARNING:
                    update_logs(f"/!\\ WARNING: This game has more than {HIGH_DLC_WARNING} DLCs. Requests may fail due to Steam rate limiting. If it does, just give it time, it'll eventually manage to retrieve all DLCs.")

                # Get DLCs names
                for i in range(dlcIDsLen):
                    appName = RetrieveAppName(dlcIDs[i])
                    if appName == "error":
                        update_logs(f"[!] Error! No App Name found for AppID {dlcIDs[i]}")
                        gameFoundStatus.config(text=f"[!] Error! No App Name found for AppID {dlcIDs[i]}")
                        appID = 0
                        return False
                    dlcNames.append(appName)
                    update_logs("- Found DLC " + str(i+1) + "/" + str(dlcIDsLen) + ": " + appName + " (" + str(dlcIDs[i]) + ")")
                    gameFoundStatus.config(text=f"[2/2] Retrieving DLCs... ({i+1}/{dlcIDsLen})")
                    root.update()
            else:
                update_logs("- No DLC found for this game!")
        else:
            # Default retrieve option

            try:
                req2 = SACRequest("https://store.steampowered.com/dlc/" + str(appID) +"/random/ajaxgetfilteredrecommendations/?query&count=10000", "RetrieveDLC").req
            except Exception:
                gameFoundStatus.config(text=f"An error has occurred")
                return False
            data2 = req2.json()
            if not data2["success"]:
                update_logs("[!] Retrieve DLC request failed!")
                gameFoundStatus.config(text=f"Retrieve DLC request failed!")
                appID = 0
                return False

            if data2["total_count"] == 0:
                update_logs("- No DLC found for this game!")
            else:
                if data2["total_count"] >= HIGH_DLC_WARNING:
                    update_logs(f"/!\\ WARNING: This game has more than {HIGH_DLC_WARNING} DLCs. Requests may fail due to Steam rate limiting. If it does, just give it time, it'll eventually manage to retrieve all DLCs.")

                resultsIndex = 0

                # format: data-ds-appid="1812883"
                i = -1
                while i + 1 < data2["total_count"]:
                    i += 1

                    resultsStr = ""
                    resultsIndex = data2["results_html"].find("data-ds-appid=\"", resultsIndex)
                    resultsIndex += len("data-ds-appid=\"")

                    while data2["results_html"][resultsIndex] != "\"":
                        resultsStr += data2["results_html"][resultsIndex]
                        resultsIndex += 1

                    dlcID = int(resultsStr)
                    if dlcID in dlcIDs: # data-ds-appid is present 2 times for each AppID currently. This will allow us to not include it if it is already.
                        i -= 1
                        continue
                    dlcIDs.append(int(resultsStr))

                    # Retrieve DLC name
                    appName = RetrieveAppName(dlcIDs[i])
                    if appName == "error":
                        update_logs(f"[!] Error! No App Name found for AppID {dlcIDs[i]}")
                        gameFoundStatus.config(text=f"Error! No App Name found for AppID {dlcIDs[i]}")
                        appID = 0
                        return False
                    dlcNames.append(appName)
                    update_logs("- Found DLC " + str(i+1) + "/" + str(data2["total_count"]) + ": " + appName + " (" + str(dlcIDs[i]) + ")")
                    gameFoundStatus.config(text=f"[2/2] Retrieving DLCs... ({i+1}/{data2['total_count']})")
                    root.update()

        update_logs(f"Finished retrieving all the details about the game {gameName} (appID: {appID})")
        gameFoundStatus.config(text=f"All details retrieved for {gameName}!")
        return True # Retrieved game and DLCs successfully

    def CrackGame():
        global appID

        # Prevents the user from searching a game or selecting a folder or re-clicking the crack game button
        selectFolderButton.config(state=tk.DISABLED)
        searchGameButton.config(state=tk.DISABLED)
        selectCrackButton.config(state=tk.DISABLED)
        crackGameButton.config(state=tk.DISABLED)

        update_logs("\nSearching Steam API DLLs and cracking them...")
        cracked = False

        if config["Crack"]["SelectedCrack"][:3] == "dlc" and len(dlcIDs) == 0: # If a dlc only crack has been selected, but the game has no DLC
            update_logs("-----\nNo DLC is available, and you selected a DLC only crack. Aborting the cracking process.")
            EndCrack()
            return

        configDir = os.path.join(os.getcwd(), "sac_emu\\" + config["Crack"]["SelectedCrack"]) # "sac_emu/game_ali213" for example
        try:
            config.read(configDir + "\\config_override.ini")
        except Exception:
            pass

        configDir = os.path.join(configDir, "files") # "sac_emu/game_ali213/files" for example

        # Check if some custom Steamless options have been set up
        steamlessOptions = ""
        try:
            steamlessOptions = config["Developer"]["SteamlessOptions"] + " "
        except:
            pass

        root.update()

        dllLocations = []
        for root_dir, dirs, files in os.walk(folder_path):
            apiFile = ""

            # Use Steamless if configured
            if config["Preferences"]["Steamless"] == "1" and crackListSteamless[config["Crack"]["SelectedCrack"]]:
                # Run Steamless on every .exe file. If it's not under DRM or not the wrong file, no problem!
                for fileName in files:
                    if not fileName.endswith(".exe"):
                        continue
                    update_logs(f"- Attempting to run Steamless on {fileName}")
                    root.update()
                    #update_logs("\n[[[ Steamless logs ]]]")
                    fileLocation = root_dir + "/" + fileName
                    shutil.move(fileLocation, fileName) # Move the file to our location
                    subprocess.call("Steamless_CLI\\Steamless.CLI.exe " + steamlessOptions + "\"" + fileName + "\"", shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE) # Run Steamless on the game
                    #update_logs("[[[ -------------- ]]]\n")

                    # Check if the game was NOT unpacked
                    if not os.path.isfile(fileName + ".unpacked.exe"):
                        # Move back the original game's exe since it didn't change
                        update_logs("- Couldn't run Steamless on " + fileName + ", it is probably not under DRM.")
                        shutil.move(fileName, fileLocation)
                        root.update()
                        continue

                    update_logs(f"- Removed Steam Stub DRM from {fileName}")
                    if config["FileNames"]["GameEXE"] != "":
                        # Rename and move back the original game's exe
                        shutil.move(fileName, fileLocation + config["FileNames"]["GameEXE"])
                    else:
                        # Delete the original game's exe
                        os.remove(fileName)
                    # Rename and move the unpacked exe to the game's directory
                    shutil.move(fileName + ".unpacked.exe", fileLocation)
                    root.update()

            if "steam_api.dll" in files:
                if config["FileNames"]["SteamAPI"] in files:
                    update_logs("[!] Seems like a file named " + config["FileNames"]["SteamAPI"] + " is present. This could indicate that steam_api.dll has already been cracked! Overwriting steam_api.dll. No backup of the previous steam_api.dll could be created, and the file has been deleted. " + config["FileNames"]["SteamAPI"] + " has been restored.")
                    os.remove(root_dir + "/steam_api.dll")
                    shutil.move(root_dir + "/" + config["FileNames"]["SteamAPI"], root_dir + "/steam_api.dll")

                apiFile = root_dir + "/steam_api.dll"
                try:
                    apiFileVersion = GetFileVersion(apiFile)
                except Exception:
                    update_logs("[!] steam_api.dll: could not retrieve the file version! Seems like the steam_api.dll file has already been cracked! Aborting...")
                    EndCrack()
                    return

                update_logs(f"- Found steam_api.dll in {root_dir}, planning crack application")

            if "steam_api64.dll" in files:
                if config["FileNames"]["SteamAPI64"] in files:
                    update_logs("[!] Seems like a file named " + config["FileNames"]["SteamAPI64"] + " is present. This could indicate that steam_api64.dll has already been cracked! Overwriting steam_api64.dll. No backup of the previous steam_api64.dll could be created, and the file has been deleted. " + config["FileNames"]["SteamAPI64"] + " has been restored.")
                    os.remove(root_dir + "/steam_api64.dll")
                    shutil.move(root_dir + "/" + config["FileNames"]["SteamAPI64"], root_dir + "/steam_api64.dll")

                apiFile = root_dir + "/steam_api64.dll"
                try:
                    apiFileVersion = GetFileVersion(apiFile)
                except Exception:
                    update_logs("[!] steam_api64.dll: could not retrieve the file version! Seems like the steam_api64.dll file has already been cracked! Aborting...")
                    EndCrack()
                    return

                update_logs(f"- Found steam_api64.dll in {root_dir}, planning crack application")

            if apiFile != "":
                if root_dir not in dllLocations:
                    dllLocations.append(root_dir)

                cracked = True
                root.update()

        for dllCurrentLocation in dllLocations:
            for root_dir, dirs, files in os.walk(configDir):
                relativeRootDir = root_dir[len(configDir) + 1:]
                dllAbsoluteRelativeLocation = os.path.join(dllCurrentLocation, relativeRootDir)

                # To make it look right, add a "\" at the end of relativeRootDir if it is not empty
                if len(relativeRootDir) > 0:
                    relativeRootDir += "\\"

                # Create all missing directories
                for dir in dirs:
                    if not os.path.isdir(os.path.join(dllAbsoluteRelativeLocation, dir)):
                        os.mkdir(os.path.join(dllAbsoluteRelativeLocation, dir))
                        update_logs("Created new directory " + relativeRootDir + dir)
                        root.update()

                # Create all files
                for fileName in files:
                    root.update()
                    if os.path.isfile(os.path.join(dllAbsoluteRelativeLocation, fileName)): # The file already exists in the game, rename it to .bak
                        newName = fileName + config["FileNames"]["BakSuffix"]
                        if fileName == "steam_api.dll" or fileName == "steam_api64.dll":
                            if config["Preferences"]["CrackOption"] != "0": # Only create config
                                update_logs("Ignoring " + relativeRootDir + fileName + " because of the set crack approach")
                                continue

                            if fileName == "steam_api.dll":
                                newName = config["FileNames"]["SteamAPI"]
                            else:
                                newName = config["FileNames"]["SteamAPI64"]

                        if newName == "": # Don't keep a backup of the steam_api(64).dll file
                            os.remove(os.path.join(dllAbsoluteRelativeLocation, fileName))
                            update_logs("Removed old " + relativeRootDir + fileName + " file because no backup file name is set")
                        elif os.path.isfile(os.path.join(dllAbsoluteRelativeLocation, newName)): # A backup of this file already exists, the game might already be cracked, abort!
                            update_logs("[!] Seems like the backup of " + relativeRootDir + fileName + " file already exists! This could indicate that the game has already been cracked. Overwriting it. No backup of " + relativeRootDir + fileName + " could be created, and the file has been deleted.")
                            os.remove(os.path.join(dllAbsoluteRelativeLocation, fileName))
                        else:
                            shutil.move(os.path.join(dllAbsoluteRelativeLocation, fileName), os.path.join(dllAbsoluteRelativeLocation, newName))
                            update_logs("Backupped old file " + relativeRootDir + fileName + " -> " + newName)
                    elif fileName == "steam_api.dll" or fileName == "steam_api64.dll": # No existing file, and this file is the steam_api(64).dll one
                        continue # Ignore this file

                    shutil.copyfile(os.path.join(root_dir, fileName), os.path.join(dllAbsoluteRelativeLocation, fileName))

                    # Check if ends with a specific extension, so we can replace the presets inside
                    if any(fileName.endswith(extension) for extension in EXTS_TO_REPLACE):
                        # Read the file's content
                        with open(os.path.join(dllAbsoluteRelativeLocation, fileName), "r", encoding="utf-8") as file:
                            fileContent = file.read()

                        # Replace the presets if any
                        fileContent = fileContent.replace("SAC_AppID", str(appID))
                        fileContent = fileContent.replace("SAC_APIVersion", apiFileVersion)
                        buffer = ""
                        for i in range(len(dlcIDs)):
                            buffer += str(dlcIDs[i]) + " = " + dlcNames[i] + "\n"
                        fileContent = fileContent.replace("SAC_DLC", buffer)
                        buffer = ""
                        for i in range(len(dlcIDs)):
                            buffer += str(dlcIDs[i]) + "=" + dlcNames[i] + "\n"
                        fileContent = fileContent.replace("SAC_NoSpaceDLC", buffer)

                        # Write the changes
                        with open(os.path.join(dllAbsoluteRelativeLocation, fileName), "w", encoding="utf-8") as file:
                            file.write(fileContent)

                    update_logs("Created new file " + relativeRootDir + fileName)


        update_logs("\n-----\nFinished cracking the game!")
        if not cracked:
            update_logs("[!] No Steam API DLL was found in the game!")
        else:
            update_logs("The game has been cracked successfully! (If you attempt to crack if again, SAC will try its best to make it work, but will let some leftovers of old cracks.)")

        EndCrack()

    def EndCrack():
        # Cracking process done!
        ReloadConfig() # Reload the config to remove the overwritten config from config_override.ini

        # Now let's remove locks
        selectFolderButton.config(state=tk.NORMAL)
        searchGameButton.config(state=tk.NORMAL)
        selectCrackButton.config(state=tk.NORMAL)
        crackGameButton.config(state=tk.NORMAL)

    # ----- Settings -----

    def SettingsButton():
        top = tk.Toplevel(root)
        #top.geometry("750x250")
        top.title(f"SteamAutoCracker GUI v{VERSION} - Settings")
        top.resizable(False, False) # Prevents resizing the window's width and height
        biggerFont = DEFAULT_FONT.copy()
        biggerFont.config(size=10)
        ttk.Label(top, text= "Settings", font=FONT2).pack(padx=200, pady=(10,10), anchor="center")

        ttk.Button(top, text="Reset to default", padding=0, command=ResetSettingsButton).pack(pady=(0,0), anchor="center")

        # Handle scrolling
        scrollCanvas = tk.Canvas(top, width=600, height=450, highlightthickness=0)
        scrollCanvas.pack(pady=(5, 0), side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollFrame = ttk.Frame(scrollCanvas)
        scrollCanvas.create_window((0,0), window=scrollFrame, anchor="nw")

        # Damn don't ask me how all of this works. It just does :D
        scrollbar = tk.Scrollbar(top, command=scrollCanvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        scrollCanvas.config(yscrollcommand=scrollbar.set)

        def on_mousewheel(event):
            scrollCanvas.yview_scroll(int(-1*(event.delta/120)), "units") # Some magic I guess. Huge thanks to LLM who probably stole this code from someone.

        top.bind("<MouseWheel>", on_mousewheel)

        def configure_canvas(event):
            scrollCanvas.config(scrollregion=scrollCanvas.bbox("all"))

        scrollFrame.bind("<Configure>", configure_canvas)
        # Finished handling scrolling

        # Update options (UpdateOption)
        ttk.Label(scrollFrame, text="Updates:", font=FONT3, padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        ttk.Label(scrollFrame, text="This will search the latest version on GitHub.\nIf you're afraid of leaking your IP to GitHub, use a VPN and/or disable auto updating.", font=FONT4, padding=0, foreground="#575757", wraplength=600).pack(padx=(6, 0), pady=(0,0), anchor="w")
        settings_frame_updates = ttk.Frame(scrollFrame)
        settings_frame_updates.pack(padx=(15, 0), pady=(0, 0), anchor="w")

        ## Radio
        global UpdateOption_var
        UpdateOption_var = tk.StringVar()
        UpdateOption_var.set(config["Preferences"]["UpdateOption"])
        ttk.Radiobutton(settings_frame_updates, text="Don't automatically check for updates (RECOMMENDED FOR PRIVACY)", variable=UpdateOption_var, value="0", command=lambda: UpdateConfigKey("Preferences", "UpdateOption", UpdateOption_var.get())).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(settings_frame_updates, text="Automatically check for updates on SAC start (RECOMMENDED FOR CONVENIENCE)", variable=UpdateOption_var, value="1", command=lambda: UpdateConfigKey("Preferences", "UpdateOption", UpdateOption_var.get())).grid(row=1, column=0, sticky="w")

        # Crack approach (CrackOption)
        ttk.Label(scrollFrame, text="Crack approach:", font=FONT3, padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        settings_frame1 = ttk.Frame(scrollFrame)
        settings_frame1.pack(padx=(15, 0), pady=(0, 0), anchor="w")

        ## Radio
        global CrackOption_var
        CrackOption_var = tk.StringVar()
        CrackOption_var.set(config["Preferences"]["CrackOption"])
        ttk.Radiobutton(settings_frame1, text="Crack the game automatically (RECOMMENDED)", variable=CrackOption_var, value="0", command=lambda: UpdateConfigKey("Preferences", "CrackOption", CrackOption_var.get())).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(settings_frame1, text="Only create the crack config, and put it in the same directory as steam_api(64).dll", variable=CrackOption_var, value="1", command=lambda: UpdateConfigKey("Preferences", "CrackOption", CrackOption_var.get())).grid(row=1, column=0, sticky="w")
        ttk.Radiobutton(settings_frame1, text="Only create the crack config, and put it in the same directory as the Steam Auto Cracker tool\n(currently bugged, doesn't work!)", variable=CrackOption_var, value="2", command=lambda: UpdateConfigKey("Preferences", "CrackOption", CrackOption_var.get())).grid(row=2, column=0, sticky="w")

        # Steamless (Steamless)
        ttk.Label(scrollFrame, text="Steamless:", font=FONT3, padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        ttk.Label(scrollFrame, text="This will allow SAC to bypass the SteamStub DRM if it is used.", font=FONT4, padding=0, foreground="#575757", wraplength=600).pack(padx=(6, 0), pady=(0,0), anchor="w")

        settings_frame2 = ttk.Frame(scrollFrame)
        settings_frame2.pack(padx=(15, 0), pady=(0, 10), anchor="w")

        ## Radio
        global Steamless_var
        Steamless_var = tk.StringVar()
        Steamless_var.set(config["Preferences"]["Steamless"])
        ttk.Radiobutton(settings_frame2, text="Don't attempt to use Steamless", variable=Steamless_var, value="0", command=lambda: UpdateConfigKey("Preferences", "Steamless", Steamless_var.get())).grid(row=0, column=0, sticky="w")
        ttk.Radiobutton(settings_frame2, text="Attempt to use Steamless (RECOMMENDED)", variable=Steamless_var, value="1", command=lambda: UpdateConfigKey("Preferences", "Steamless", Steamless_var.get())).grid(row=1, column=0, sticky="w")

        # FileNames
        ttk.Label(scrollFrame, text="File names:", font=FONT3, padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        ttk.Label(scrollFrame, text="You can enter the name the different files will have.\nIt is recommended to keep the default ones.", font=FONT4, padding=0, foreground="#575757", wraplength=600).pack(padx=(6, 0), pady=(0,0), anchor="w")

        fileNamesFrame = ttk.Frame(scrollFrame)
        fileNamesFrame.pack(padx=(15, 0), pady=(0, 10), anchor="w")

        tk.Label(fileNamesFrame, text="steam_api.dll backup name:").grid(row=0, column=0)
        global SteamApi_var
        SteamApi_var = tk.StringVar()
        steamApiEntry = tk.Entry(fileNamesFrame, width=35, textvariable=SteamApi_var)
        steamApiEntry.grid(row=0, column=1, ipadx=10, ipady=3)
        SteamApi_var.set(config["FileNames"]["SteamAPI"])
        ttk.Button(fileNamesFrame, text="Save", padding=3, command=lambda: UpdateFileName("SteamAPI", SteamApi_var)).grid(row=0, column=2, ipadx=10)

        tk.Label(fileNamesFrame, text="steam_api64.dll backup name:").grid(row=1, column=0)
        global SteamApi64_var
        SteamApi64_var = tk.StringVar()
        steamApiEntry = tk.Entry(fileNamesFrame, width=35, textvariable=SteamApi64_var)
        steamApiEntry.grid(row=1, column=1, ipadx=10, ipady=3)
        SteamApi64_var.set(config["FileNames"]["SteamAPI64"])
        ttk.Button(fileNamesFrame, text="Save", padding=3, command=lambda: UpdateFileName("SteamAPI64", SteamApi64_var)).grid(row=1, column=2, ipadx=10)

        tk.Label(fileNamesFrame, text="Game EXE backup suffix:").grid(row=2, column=0)
        global GameEXE_var
        GameEXE_var = tk.StringVar()
        steamApiEntry = tk.Entry(fileNamesFrame, width=35, textvariable=GameEXE_var)
        steamApiEntry.grid(row=2, column=1, ipadx=10, ipady=3)
        GameEXE_var.set(config["FileNames"]["GameEXE"])
        ttk.Button(fileNamesFrame, text="Save", padding=3, command=lambda: UpdateFileName("GameEXE", GameEXE_var)).grid(row=2, column=2, ipadx=10)

        tk.Label(fileNamesFrame, text="Other files backup suffix:").grid(row=3, column=0)
        global BakSuffix_var
        BakSuffix_var = tk.StringVar()
        steamApiEntry = tk.Entry(fileNamesFrame, width=35, textvariable=BakSuffix_var)
        steamApiEntry.grid(row=3, column=1, ipadx=10, ipady=3)
        BakSuffix_var.set(config["FileNames"]["BakSuffix"])
        ttk.Button(fileNamesFrame, text="Save", padding=3, command=lambda: UpdateFileName("BakSuffix", BakSuffix_var)).grid(row=3, column=2, ipadx=10)

        # Advanced
        ttk.Label(scrollFrame, text="Advanced:", font=FONT3, padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        ttk.Label(scrollFrame, text="Advanced settings, don't modify unless you know what you're doing.", font=FONT4, padding=0, foreground="#575757", wraplength=600).pack(padx=(6, 0), pady=(0,0), anchor="w")

        advTextFrame = ttk.Frame(scrollFrame)
        advTextFrame.pack(padx=(15, 0), pady=(0, 10), anchor="w")

        tk.Label(advTextFrame, text="RetryDelay:").grid(row=0, column=0)
        global RetryDelay_var
        RetryDelay_var = tk.StringVar()
        steamApiEntry = tk.Entry(advTextFrame, width=35, textvariable=RetryDelay_var)
        steamApiEntry.grid(row=0, column=1, ipadx=10, ipady=3)
        RetryDelay_var.set(config["Advanced"]["RetryDelay"])
        ttk.Button(advTextFrame, text="Save", padding=3, command=lambda: UpdateAdvanced("RetryDelay", RetryDelay_var)).grid(row=0, column=2, ipadx=10)

        tk.Label(advTextFrame, text="RetryMax:").grid(row=1, column=0)
        global RetryMax_var
        RetryMax_var = tk.StringVar()
        steamApiEntry = tk.Entry(advTextFrame, width=35, textvariable=RetryMax_var)
        steamApiEntry.grid(row=1, column=1, ipadx=10, ipady=3)
        RetryMax_var.set(config["Advanced"]["RetryMax"])
        ttk.Button(advTextFrame, text="Save", padding=3, command=lambda: UpdateAdvanced("RetryMax", RetryMax_var)).grid(row=1, column=2, ipadx=10)

        global BypassGameVerification_var
        BypassGameVerification_var = tk.StringVar()
        BypassGameVerification_var.set(config["Advanced"]["BypassGameVerification"])
        advBypassGameVerification = ttk.Checkbutton(scrollFrame, text="Bypass the game verification, allows to crack AppIDs not recognized as games", variable=BypassGameVerification_var, command=lambda: UpdateAdvanced("BypassGameVerification", BypassGameVerification_var))
        advBypassGameVerification.pack(padx=(15, 0), pady=(0, 10), anchor="w")

        top.grab_set() # Catches all interactions, prevents the user from interacting with the root window

    def UpdateFileName(key, strVar):
        value = strVar.get().strip()
        strVar.set(value)
        UpdateConfigKey("FileNames", key, value)

    def UpdateAdvanced(key, strVar):
        value = strVar.get().strip()
        try:
            int(value)
        except:
            strVar.set(config["Advanced"][key])
        else: # If no error
            strVar.set(value)
            UpdateConfigKey("Advanced", key, value)

    def ResetSettingsButton():
        ResetConfig(1)

        # Update the radio buttons values
        UpdateOption_var.set(config["Preferences"]["UpdateOption"])
        CrackOption_var.set(config["Preferences"]["CrackOption"])
        Steamless_var.set(config["Preferences"]["Steamless"])
        SteamApi_var.set(config["FileNames"]["SteamAPI"])
        SteamApi64_var.set(config["FileNames"]["SteamAPI64"])
        GameEXE_var.set(config["FileNames"]["GameEXE"])
        BakSuffix_var.set(config["FileNames"]["BakSuffix"])
        RetryDelay_var.set(config["Advanced"]["RetryDelay"])
        RetryMax_var.set(config["Advanced"]["RetryMax"])
        BypassGameVerification_var.set(config["Advanced"]["BypassGameVerification"])

    # ----- Crack List -----

    crackList = { # A list of all selectable cracks
        "game_ali213": ["ALI213 (Game)", "The ALI213 crack is simple and can crack a full game. It will unlock all DLCs and will also prevent the game from connecting to the internet.\nThe game folder can then freely be shared with others as the crack is contained inside the game folder.\nIf it doesn't work, consider using Goldberg instead."],
        "game_goldberg": ["Goldberg (Game)", "The Goldberg (experimental) crack is similar to ALI213's one.\nIt is open-source, which is better, but might not work with older games, due to SAC's current partial support.\nThis crack will however work better for recent games, where ALI213 could fail.\nInternet connection is blocked, but LAN is enabled."],
        "dlc_creamapi": ["CreamAPI (DLC)", "The CreamAPI crack will unlock all DLCs but will not crack the main game. It is meant to be used with bought copies of a game, with your real Steam account.\nOnly use this is you have purchased the game on Steam and want to unlock its DLCs.\nWill not work for most online games, but might exceptionally work with some like Beat Saber."]
    }

    crackListSteamless = { # Whether to use Steamless with a specific crack. True = use Steamless
        "game_ali213": True,
        "game_goldberg": True,
        "dlc_creamapi": False
    }

    def DisplayCrackList():
        top = tk.Toplevel(root)
        top.title(f"SteamAutoCracker GUI v{VERSION} - Crack List")
        top.resizable(False, False) # Prevents resizing the window's width and height
        biggerFont = DEFAULT_FONT.copy()
        biggerFont.config(size=10)
        ttk.Label(top, text= "Crack List", font=FONT2).pack(padx=200, pady=(10,10), anchor="center")

        ttk.Button(top, text="Reset to default", padding=0, command=ResetCrackListButton).pack(pady=(0,0), anchor="center")

        # Selected crack (SelectedCrack)
        ttk.Label(top, text="Selected crack:", font=FONT3, padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        settings_frame1 = ttk.Frame(top)
        settings_frame1.pack(padx=(15, 0), pady=(0, 0), anchor="w")

        ## Radio
        global SelectedCrack_var
        SelectedCrack_var = tk.StringVar()
        SelectedCrack_var.set(config["Crack"]["SelectedCrack"])
        rowNum = 0
        for k, v in crackList.items():
            ttk.Radiobutton(settings_frame1, text=v[0], variable=SelectedCrack_var, value=k, command=lambda: UpdateSelectedCrack()).grid(row=rowNum, column=0, sticky="w")
            rowNum += 1
            if len(v) > 1: # Contains a description
                tk.Label(settings_frame1, text=v[1], font=FONT4, foreground="#575757", wraplength=700, justify="left").grid(row=rowNum, column=0, sticky="w", ipadx=20)
                rowNum += 1

        # Spacer
        tk.Label(top, text="").pack()

        top.grab_set() # Catches all interactions, prevents the user from interacting with the root window

    def UpdateSelectedCrack():
        value = SelectedCrack_var.get()
        UpdateConfigKey("Crack", "SelectedCrack", value)
        UpdateSelectedCrackDisplay()

    def UpdateSelectedCrackDisplay():
        selectCrackButton.config(text=crackList[config["Crack"]["SelectedCrack"]][0]) # Display the name of the selected crack on the select crack button in the root window

    def ResetCrackListButton():
        ResetConfig(2)

        # Update the radio buttons values
        SelectedCrack_var.set(config["Crack"]["SelectedCrack"])

        # Update the root button's text
        UpdateSelectedCrackDisplay()

    # ---------------------------------------

    def UpdateConfig():
        with open("config.ini", "w", encoding="utf-8") as configFile:
            config.write(configFile)

    def UpdateConfigKey(section: str, key: str, value: str):
        config[section][key] = value
        UpdateConfig()

    def ResetConfig(resetLevel = 0, customConfig=None):
        """resetLevel values:
        0 = Everything
        1 = Main settings only (Preferences, FileNames, Advanced)
        2 = Crack selection settings only (Crack)
        """
        if customConfig:
            currentConfig = customConfig
        else:
            currentConfig = config

        if resetLevel == 0 or resetLevel == 1:
            currentConfig["Preferences"] = {}
            currentConfig["Preferences"]["UpdateOption"] = "0"
            currentConfig["Preferences"]["CrackOption"] = "0"
            currentConfig["Preferences"]["Steamless"] = "1"
            currentConfig["Preferences"]["last_selected_folder"] = ""

            currentConfig["FileNames"] = {}
            currentConfig["FileNames"]["GameEXE"] = ".bak"
            currentConfig["FileNames"]["BakSuffix"] = ".bak"
            currentConfig["FileNames"]["SteamAPI"] = "steam_api.dll.bak"
            currentConfig["FileNames"]["SteamAPI64"] = "steam_api64.dll.bak"

            currentConfig["Advanced"] = {}
            currentConfig["Advanced"]["RetryDelay"] = str(RETRY_DELAY)
            currentConfig["Advanced"]["RetryMax"] = str(RETRY_MAX)
            currentConfig["Advanced"]["BypassGameVerification"] = "0"
        if resetLevel == 0 or resetLevel == 2:
            currentConfig["Crack"] = {}
            currentConfig["Crack"]["SelectedCrack"] = "game_ali213"

        if not customConfig:
            UpdateConfig()

    def FillConfig(currentConfig, configDefault):
        changed = False
        for k, v in configDefault.items():
            if k not in currentConfig:
                currentConfig[k] = v
                print("Updated", k, "->", v)
                changed = True
            if type(v) == configparser.SectionProxy:
                if FillConfig(currentConfig[k], v):
                    changed = True

        return changed

    def ReloadConfig():
        global config
        config = configparser.ConfigParser()

        if config.read("config.ini") == []:
            # Config doesn't exist, create it
            ResetConfig()
        else:
            # Create a config with default values
            configDefault = configparser.ConfigParser()
            ResetConfig(0, configDefault)

            # Check if the config is complete. If not, complete it.
            changed = FillConfig(config, configDefault)
            if changed:
                print("[SAC] config.ini has been updated, missing entries have been created")
                UpdateConfig()

    ReloadConfig()

    # ---------------------------------------

    def CheckUpdates():
        updatesButton.config(text="Searching for updates...", state=tk.DISABLED)
        root.update()

        req = SACRequest(GITHUB_LATESTVERSIONJSON, "RetrieveLatestVersionJson").req
        data = req.json()
        global latestversion
        latestversion = data["version"]
        if latestversion == VERSION: # The latest stable version is the one we're running
            updatesButton.config(text="SAC is up to date!", state=tk.NORMAL)
            return

        global release_link
        release_link = data["release"]
        release_link = release_link.replace("[VERSION]", latestversion)

        updatesButton.config(text="SAC is outdated!", state=tk.NORMAL)
        DisplayUpdate()

    def DisplayUpdate():
        top = tk.Toplevel(root)
        top.title(f"SteamAutoCracker GUI v{VERSION} - Update")
        top.resizable(False, False) # Prevents resizing the window's width and height
        biggerFont = DEFAULT_FONT.copy()
        biggerFont.config(size=10)
        ttk.Label(top, text= "Update", font=FONT2).pack(padx=200, pady=(10,10), anchor="center")
        ttk.Label(top, text="A new update for Steam Auto Cracker GUI is available.\nDo you want to download it automatically?", font=biggerFont, padding=0).pack(padx=(6, 0), pady=(10,0), anchor="w")
        ttk.Label(top, text=f"Current version: {VERSION}", font=biggerFont, padding=0).pack(padx=(6, 0), pady=(15,0), anchor="w")
        ttk.Label(top, text=f"Latest version: {latestversion}", font=biggerFont, padding=0).pack(padx=(6, 0), pady=(0,10), anchor="w")

        updateDisplayButtonsFrame = ttk.Frame(top)
        updateDisplayButtonsFrame.pack(pady=(5,20))

        global updateDisplayButtonUpdate
        updateDisplayButtonUpdate = ttk.Button(updateDisplayButtonsFrame, text="Update now", command=UpdateSAC, padding=3)
        updateDisplayButtonUpdate.grid(row=0, column=0)

        global updateDisplayButtonCopy
        updateDisplayButtonCopy = ttk.Button(updateDisplayButtonsFrame, text="Copy the release URL", command=CopyReleaseURL, padding=3)
        updateDisplayButtonCopy.grid(row=0, column=1, padx=(50,0))

        global updateDisplayButtonClose
        updateDisplayButtonClose = ttk.Button(updateDisplayButtonsFrame, text="Don't update yet", command=top.destroy, padding=3)
        updateDisplayButtonClose.grid(row=0, column=2, padx=(50,0))

        global updateDisplayStatusLabel
        updateDisplayStatusLabel = ttk.Label(top, text="", font=biggerFont, padding=0)

        top.grab_set() # Catches all interactions, prevents the user from interacting with the root window

        global updateDisplayTop
        updateDisplayTop = top

    def UpdateSAC():
        updateDisplayButtonUpdate.config(state=tk.DISABLED)
        updateDisplayButtonCopy.config(state=tk.DISABLED)
        updateDisplayButtonClose.config(state=tk.DISABLED)

        updateDisplayStatusLabel.pack(pady=(0,20), anchor="center")
        updateDisplayStatusLabel.config(text="Downloading the autoupdater, please wait...\nThis might take some time depending on your internet connection speed...")
        root.update()

        # Check for the existence of a leftover autoupdater
        if os.path.isfile("steam_auto_cracker_gui_autoupdater.exe"):
            try:
                os.remove("steam_auto_cracker_gui_autoupdater.exe")
            except Exception: # In case the file is locked for example
                updateDisplayButtonUpdate.config(state=tk.NORMAL)
                updateDisplayButtonCopy.config(state=tk.NORMAL)
                updateDisplayButtonClose.config(state=tk.NORMAL)
                updateDisplayStatusLabel.config(text="An error occurred. The autoupdater (steam_auto_cracker_gui_autoupdater.exe) already exists.\nSAC couldn't delete the autoupdater. Please try to remove it yourself, or try again.")
                root.update()
                return
            print("Removed leftover autoupdater")

        # Override RetryDelay and RetryMax
        config["Advanced"]["RetryDelay"] = "3"
        config["Advanced"]["RetryMax"] = "5"

        req = SACRequest(GITHUB_AUTOUPDATER, "DownloadAutoupdater").req

        updateDisplayStatusLabel.config(text="Writing the autoupdater, please wait...")
        root.update()

        with open("steam_auto_cracker_gui_autoupdater.exe", mode="wb") as file:
            file.write(req.content)

        updateDisplayStatusLabel.config(text="Autoupdater installed!\nStarting it in 3 seconds...")
        root.update()

        sleep(3)
        subprocess.Popen("steam_auto_cracker_gui_autoupdater.exe") # Open SAC GUI Autoupdater
        exit()

    def CopyReleaseURL():
        root.clipboard_clear()
        root.clipboard_append(release_link)

    # ---------------------------------------


    # Let's now create the main window
    root = TkinterDnD.Tk()
    root.resizable(False, False) # Prevents resizing the window's width and height
    root.title(f"SteamAutoCracker GUI v{VERSION}")
    root.drop_target_register(DND_FILES) # Register the drop target
    root.dnd_bind("<<Drop>>", lambda event: handle_folder_selection(event=event)) # Bind the drop target

    DEFAULT_FONT = font.nametofont('TkTextFont')
    FONT2 = DEFAULT_FONT.copy()
    FONT2.config(size=15)
    FONT3 = DEFAULT_FONT.copy()
    FONT3.config(size=12)
    FONT4 = DEFAULT_FONT.copy()
    FONT4.config(size=8)
    FONT_APP_ENTRY = DEFAULT_FONT.copy()
    FONT_APP_ENTRY.config(size=10)

    # Style ttk
    style = ttk.Style()
    style.configure("TFrame", padding=0)
    style.configure("TLabel", padding=6)
    style.configure("TRadiobutton", padding=6)
    style.configure("TButton", padding=10)
    style.configure("TText", padding=6)

    ttk.Label(root, text=f"SteamAutoCracker GUI v{VERSION}", font=FONT2, padding=0).pack(pady=(10, 0), anchor="center")
    ttk.Label(root, text="by BigBoiCJ", padding=0).pack(pady=(0, 0), anchor="center")

    updatesFrame = tk.Frame(root)
    updatesButton = ttk.Button(updatesFrame, text="Check for updates", command=CheckUpdates, padding=0)
    updatesButton.grid(row=0, column=0)
    updatesFrame.pack(pady=(0, 20))

    ttk.Button(root, text="Settings", command=SettingsButton, padding=8).pack(pady=(0, 20), anchor="center")

    """
    frame4 = ttk.Frame(root)
    frame4.pack(pady=(5, 0), padx=10, anchor="center")"""

    ttk.Separator(root, orient='horizontal').pack(fill="x", padx=220)

    # Select folder fields
    tk.Label(root, text="Select where your game is installed :",).pack(pady=(20, 5), anchor="center")
    selectFolderButton = ttk.Button(root, text="Select a folder", command=lambda: handle_folder_selection())
    selectFolderButton.pack(pady=(0, 10))

    selectedFolderFrame = tk.Frame(root) # This frame will contain the label. This is so we can resize the root window properly when the text is empty.
    selectedFolderFrame.pack()
    tk.Frame(selectedFolderFrame, width=1, height=1).pack() # 1x1 frame, else selectedFolderFrame will not update its size after it is emptied (by selectedFolderLabel.pack_forget)
    selectedFolderLabel = tk.Label(selectedFolderFrame, text="", wraplength=700)
    selectedFolderLabel.pack()
    selectedFolderLabel.pack_forget()

    # Enter game name or appID fields
    frameGame = ttk.Frame(root) # Main frame for the game
    frameGame.pack(pady=(5, 0), anchor="center")

    tk.Frame(frameGame, width=1, height=1).pack() # 1x1 frame, else frameGame will not update its size after it is emptied (by frameGame2.pack_forget)
    frameGame2 = ttk.Frame(frameGame) # The elements will be inside this one. This is so we can call pack_forget and still preserve the location of frameGame.
    frameGame2.pack()
    ttk.Separator(frameGame2, orient='horizontal').pack(fill="x", padx=50, pady=(15, 0))
    ttk.Label(frameGame2, text="Enter the Name or AppID of the game you want to Crack:").pack(pady=(15, 0), anchor="center")

    frame4 = ttk.Frame(frameGame2)
    frame4.pack(pady=(5, 0), anchor="center")
    gameNameEntry = tk.Entry(frame4, width=35, font=FONT_APP_ENTRY)
    gameNameEntry.grid(row=0, column=0, ipady=5)
    searchGameButton = ttk.Button(frame4, text="Search", padding=5, command=search_game)
    searchGameButton.grid(row=0, column=1, padx=(10, 0))
    updateAppListButton = ttk.Button(frame4, text="Update the App List", padding=0, command=UpdateAppList)

    gameFoundStatus = ttk.Label(frameGame2, text="")
    gameFoundStatus.pack(pady=(5, 0), anchor="center")

    frameGame2.pack_forget() # Hide the elements, but preserves their location thanks to frameGame still being packed but empty

    # Crack fields
    frameCrack = ttk.Frame(root)
    frameCrack.pack(pady=(15, 0), anchor="center")
    tk.Frame(frameCrack, width=1, height=1).pack() # 1x1 frame
    frameCrack2 = ttk.Frame(frameCrack)
    frameCrack2.pack()
    ttk.Separator(frameCrack2, orient='horizontal').pack(fill="x", padx=0, pady=(0, 15))
    selectedCrackFrame = ttk.Frame(frameCrack2)
    selectedCrackFrame.pack()
    tk.Label(selectedCrackFrame, text="Selected crack:").grid(row=0, column=0)
    selectCrackButton = ttk.Button(selectedCrackFrame, text="None", padding=5, command=DisplayCrackList)
    selectCrackButton.grid(row=0, column=1, padx=(10, 0))
    UpdateSelectedCrackDisplay() # Updates the text of selectCrackButton
    crackGameButton = ttk.Button(frameCrack2, text="Crack the game", padding=8, command=CrackGame)
    crackGameButton.pack(pady=(10, 0))

    frameCrack2.pack_forget() # Hide the elements, but preserves their location thanks to frameCrack still being packed but empty

    # Spacer
    #tk.Label(root, text="").pack()

    # Logs scroll text widget
    logs_text = tk.Text(root, height=15, width=100)
    logs_text.pack(pady=10, padx=10)

    text = f"SteamAutoCracker GUI v{VERSION} by BigBoiCJ"
    buf = ""
    for i in range(len(text)):
        buf += "-"

    logs_text.insert("1.0", f"{buf}\n{text}\n{buf}")
    logs_text.config(state=tk.DISABLED) # Prevents users from editing the text inside logs_text

    # Handle errors to log them while tkinter is running
    root.report_callback_exception = OnTkinterError

    # Check for the existence of a leftover autoupdater
    if os.path.isfile("steam_auto_cracker_gui_autoupdater.exe"):
        try:
            os.remove("steam_auto_cracker_gui_autoupdater.exe")
        except Exception: # In case the file is locked for example
            pass

    # Check for updates
    if config["Preferences"]["UpdateOption"] == "1":
        CheckUpdates()

    # Start main loop
    root.mainloop()

except Exception:
    # Handle Python errors
    print("\n[!!!] A Python error occurred! Writing the error to the error.log file.\n---")
    with open("error.log", "w", encoding="utf-8") as errorFile:
        errorFile.write(f"SteamAutoCracker GUI v{VERSION}\n---\nA Python error occurred!\nPlease report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.\n---\n\n")
        traceback.print_exc(file=errorFile)
    traceback.print_exc()
    print("---\nError written to error.log, please report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.")
