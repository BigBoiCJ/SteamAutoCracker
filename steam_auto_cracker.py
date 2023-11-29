import traceback

try: # Handles Python errors to write them to a log file so they can be reported and fixed more easily.
    import requests
    import configparser
    import json
    import os
    import sys
    from sac_lib.get_file_version import GetFileVersion
    from itertools import combinations
    import shutil
    from time import sleep


    VERSION = "1.2.11"

    RETRY_DELAY = 15 # Delay in seconds before retrying a failed request. (default, can be modified in config.ini)
    RETRY_MAX = 30 # Number of failed tries (includes the first try) after which SAC will stop trying and quit. (default, can be modified in config.ini)

    HIGH_DLC_WARNING = 125


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
                    print("- " + self.name + " request failed, retrying in " + str(RETRY_DELAY) + "s... (" + str(self.tries) + "/" + str(RETRY_MAX) + " tries)")
                    sleep(RETRY_DELAY)
                    self.DoRequest()
                else:
                    print("[!] Connection failed after " + str(RETRY_MAX) + " tries. Are you connected to the Internet? Is Steam online?\nIf you being rate limited (too many DLCs), you should try increasing retry_delay and retry_max in config.ini")
                    input("Press enter to exit")
                    sys.exit()
            else:
                self.req = req

    # Functions

    def FixFolderFormatting(loc: str):
        if len(loc) != 0:
            # Fix potential formatting mistakes
            loc = loc.replace("\\", "/")
            if loc[-1] != "/":
                loc += "/"
        return loc

    def UpdateAppList():
        print("- Updating the App List, this could take a few seconds to up to a minute, depending on your internet connection.")
        req = SACRequest("https://api.steampowered.com/ISteamApps/GetAppList/v2/", "UpdateAppList").req

        with open("applist.txt", "w", encoding="utf-8") as file:
            file.write(req.text)
        print("Updated the App List!")

    def FindInAppList(appName):
        print("- Importing and searching the App List, this could take a few seconds if your computer isn't powerful enough.")
        try:
            with open("applist.txt", "r", encoding="utf-8") as file:
                data = json.load(file)
        except:
            print("- The App List isn't downloaded on your computer, downloading it...")
            UpdateAppList()
            return FindInAppList(appName) # Re launch this funtion

        for elem in data["applist"]["apps"]:
            if elem["name"].lower() != appName.lower():
                continue
            return elem["appid"]

        print("The App was not found, make sure you entered EXACTLY the Steam Game's name (watch it on Steam)")
        print("If you typed it properly, you can try to update the App List:")
        choice = input("Update the App List (Y/N): ")
        if choice.upper() == "Y":
            UpdateAppList()
            return FindInAppList(appName) # Re launch this funtion
        else:
            sys.exit()

    def FindGameDirectory(gameName: str, configName: str, attemptCombos=True) -> str:
        # Banned characters (can't be used in folder names in Windows)
        banned_characters = ("\\", "/", ":", "*", "?", "\"", "<", ">", "|")
        for char in banned_characters:
            gameName = gameName.replace(char, "")

        gameName = gameName.lower()
        gameNameList = [gameName]

        # Create a list with all the combinations of name possible
        characters = (" ", "-", "'", "&")
        for i in range(len(characters)):
            for combo in combinations(characters, i + 1):
                # This will remove all possible combinations of characters that are often not included in folder names
                buffer = gameName

                for char in combo:
                    buffer = buffer.replace(char, "")

                if not buffer in gameNameList:
                    gameNameList.append(buffer)

                # Try changing double spaces "  " to single spaces " "
                buffer2 = buffer.replace("  ", " ")
                if (buffer2 != buffer) and (not buffer2 in gameNameList):
                    gameNameList.append(buffer2)

        for folder in os.listdir(config["Locations"][configName]):
            if folder.lower() in gameNameList:
                return folder
        return "error"

    def RetrieveAppName(appID: int) -> str:
        req = SACRequest("https://store.steampowered.com/api/appdetails?appids=" + str(appID) + "&filters=basic", "RetrieveAppName").req

        data = req.json()
        data = data[str(appID)]
        if (not "data" in data) or (not "name" in data["data"]):
            return "error"
        return data["data"]["name"]

    def RetrieveGame():
        global appID
        global gameName
        global dlcIDs
        global dlcNames

        print("\n[1/4] Retrieving game informations from Steam...")
        # https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI#appdetails
        req = SACRequest("https://store.steampowered.com/api/appdetails?appids=" + str(appID) + "&filters=basic", "RetrieveGame").req
        data = req.json()
        data = data[str(appID)]
        if not data["success"]:
            print("[!] AppID " + str(appID) + " not found.")
            input("Press enter to exit")
            sys.exit()
        if data["data"]["type"] != "game":
            print("[!] AppID " + str(appID) + " is not a game.")
            input("Press enter to exit")
            sys.exit()

        gameName = data["data"]["name"]
        appID = data["data"]["steam_appid"]
        print("- Game found! Name:", gameName, "- AppID:", appID)

        print("\n[2/4] Retrieving DLCs...")

        # Optional config check
        option = "0"
        try:
            option = config["Developer"]["RetrieveDLCOption"]
        except:
            pass

        if option == "1":
            # Old retrieve option
            print("Using the old retrieve option (RetrieveDLCOption is set to 1)")

            if "dlc" in data["data"]:
                dlcIDs = data["data"]["dlc"]
                dlcIDsLen = len(dlcIDs)

                if dlcIDsLen >= HIGH_DLC_WARNING:
                    print(f"/!\\ WARNING: This game has more than {HIGH_DLC_WARNING} DLCs. Requests may fail due to Steam rate limiting. If it does, just give it time, it'll eventually manage to retrieve all DLCs.")

                # Get DLCs names
                for i in range(dlcIDsLen):
                    appName = RetrieveAppName(dlcIDs[i])
                    if appName == "error":
                        print("[!] Error! No App Name found for AppID", dlcIDs[i])
                        input("Press enter to exit")
                        sys.exit()
                    dlcNames.append(appName)
                    print("- Found DLC " + str(i+1) + "/" + str(dlcIDsLen) + ": " + appName + " (" + str(dlcIDs[i]) + ")")
            else:
                print("- No DLC found for this game!")
        else:
            # Default retrieve option

            req2 = SACRequest("https://store.steampowered.com/dlc/" + str(appID) +"/random/ajaxgetfilteredrecommendations/?query&count=10000", "RetrieveDLC").req
            data2 = req2.json()
            if not data2["success"]:
                print("[!] Retrieve DLC request failed!")
                input("Press enter to exit")
                sys.exit()

            if data2["total_count"] == 0:
                print("- No DLC found for this game!")
            else:
                if data2["total_count"] >= HIGH_DLC_WARNING:
                    print(f"/!\\ WARNING: This game has more than {HIGH_DLC_WARNING} DLCs. Requests may fail due to Steam rate limiting. If it does, just give it time, it'll eventually manage to retrieve all DLCs.")

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
                        print("[!] Error! No App Name found for AppID", dlcIDs[i])
                        input("Press enter to exit")
                        sys.exit()
                    dlcNames.append(appName)
                    print("- Found DLC " + str(i+1) + "/" + str(data2["total_count"]) + ": " + appName + " (" + str(dlcIDs[i]) + ")")

    # Other

    print(f"Steam Auto Cracker (v{VERSION}) by BigBoiCJ")
    print("-----")

    # Config

    config = configparser.ConfigParser()
    if config.read("config.ini") == []:
        # Config doesn't exist, create it
        config["Locations"] = {}

        print("Since this is the first time you start the Steam Auto Cracker tool (or you removed the config file), you'll need to specify the location of your Steam games")
        print("Example: D:/Games/Steam/SteamApps/common/")
        print("Note: anti-slashes \\ will be converted to slashes /")
        print("If you do not have Steam or you do not plan to auto-unlock DLCs for your BOUGHT Steam games, don't write anything")

        loc = input("Steam Games location: ")
        loc = FixFolderFormatting(loc)
        config["Locations"]["Steam"] = loc

        print("\n----------")
        print("Specify the location of your NON-LEGAL/Pirated Steam Games. This will allow the tool to automatically crack the game for you.")
        print("Example: D:/Games/Pirated/")
        print("Note: anti-slashes \\ will be converted to slashes /")
        print("If you do not have Pirated Games or you do not plan to auto-crack games and/or auto-unlock DLCs, don't write anything")

        loc = input("Pirated Games location: ")
        loc = FixFolderFormatting(loc)
        config["Locations"]["Pirated"] = loc

        config["Preferences"] = {}

        print("\n----------")
        print("Now, please decide whether or not we should directly crack the game, or if we should only create the crack config instead:")
        print("0 - Crack the game automatically")
        print("1 - Only create the crack config, and put it in the same directory as steam_api(64).dll")
        print("2 - Only create the crack config, and put it in the same directory as the Steam Auto Cracker tool")
        while True:
            choice = input("Choice: ")
            try:
                choice = int(choice)
            except:
                print("You did not enter a correct value")
                continue

            if not 0 <= choice <= 2:
                print("You did not enter a correct value")
                continue
            break

        config["Preferences"]["CrackOption"] = str(choice)

        print("\n----------")
        print("Should we also crack Owned/BOUGHT Steam games (not the DLCs, but the base game)?")
        print("There shouldn't be any point to that for the regular user, but if you want to remove DRMs from your owned games or if you want to publish the cracked version of your game, you can enable that.")
        print("0 - Don't attempt to crack BOUGHT games")
        print("1 - Crack bought games")
        while True:
            choice = input("Choice: ")
            try:
                choice = int(choice)
            except:
                print("You did not enter a correct value")
                continue

            if not 0 <= choice <= 1:
                print("You did not enter a correct value")
                continue
            break

        config["Preferences"]["CrackOwnedGames"] = str(choice)

        print("\n----------")
        print("Should we attempt to use Steamless on the game's .exe file?")
        print("This will allow us to bypass the SteamStub DRM if it is used.")
        print("0 - Don't attempt to use Steamless")
        print("1 - Attempt to use Steamless (recommended)")
        while True:
            choice = input("Choice: ")
            try:
                choice = int(choice)
            except:
                print("You did not enter a correct value")
                continue

            if not 0 <= choice <= 1:
                print("You did not enter a correct value")
                continue
            break

        config["Preferences"]["Steamless"] = str(choice)

        config["FileNames"] = {}

        if config["Preferences"]["Steamless"] == "1":
            print("\n----------")
            print("Should we keep the default game's .exe file if cracked by Steamless?")
            print("empty = don't keep it, delete it")
            print("anything else = suffix for the default game's executable")
            choice = input("Suffix for the default game's exe: ")
            config["FileNames"]["GameEXE"] = str(choice)
        else:
            config["FileNames"]["GameEXE"] = ""

        print("\n----------")
        print("Should we keep the default steam_api.dll file?")
        print("empty = don't keep it, delete it")
        print("anything else = new file name (including the extension)")
        choice = input("New file name for steam_api.dll: ")
        config["FileNames"]["SteamAPI"] = str(choice)

        print("\n----------")
        print("Should we keep the default steam_api64.dll file?")
        print("empty = don't keep it, delete it")
        print("anything else = new file name (including the extension)")
        choice = input("New file name for steam_api64.dll: ")
        config["FileNames"]["SteamAPI64"] = str(choice)

        config["Advanced"] = {}
        config["Advanced"]["RetryDelay"] = str(RETRY_DELAY)
        config["Advanced"]["RetryMax"] = str(RETRY_MAX)


        with open("config.ini", "w", encoding="utf-8") as configFile:
            config.write(configFile)

        print("\n-----=====-----")
        print("Setup finished!")
        print("-----=====-----")

    # Script

    # Load config retry variables
    RETRY_DELAY = int(config["Advanced"]["RetryDelay"])
    RETRY_MAX = int(config["Advanced"]["RetryMax"])

    if len(sys.argv) > 1:
        gameName = sys.argv[1]
    else:
        gameName = input("Enter the Name or AppID of the game you want to Crack: ")
    appID = 0
    dlcIDs = []
    dlcNames = []

    try:
        appID = int(gameName)
    except:
        appID = FindInAppList(gameName)

    RetrieveGame()

    print("\n[3/4] Searching the game folder...")

    gameDir = "error"
    gameNameBuffer = gameName
    platform = ""
    while True:
        if gameDir == "error" and config["Locations"]["Pirated"] != "":
            platform = "Pirated"
            gameDir = FindGameDirectory(gameNameBuffer, platform)
        if gameDir == "error" and config["Locations"]["Steam"] != "":
            platform = "Steam"
            gameDir = FindGameDirectory(gameNameBuffer, platform)

        if gameDir == "error":
            if gameNameBuffer == gameName:
                print("Couldn't automatically find the folder name of the game")
            else:
                print("Couldn't find the folder", gameNameBuffer, "anywhere. Did you set-up your Steam and/or Pirated games location properly?")
            print ("Please write the folder name (in SteamApps/common/ or in your pirated games folder)")
            gameNameBuffer = input("Folder name: ")
        else:
            break

    print("- Found the game folder on your computer:", config["Locations"][platform] + gameDir)

    # Found the folder name: gameDir
    # Loop through all folders and files to find steam_api.dll and steam_api64.dll
    print("\n[4/4] Searching Steam API DLLs and cracking them...")

    cracked = False

    if platform == "Steam" and config["Preferences"]["CrackOwnedGames"] == "0":
        # Only crack DLCs
        if len(dlcIDs) == 0:
            # No DLC is available
            print("-----\nNo DLC is available, and you asked to NOT crack owned games. Aborting the cracking process.")
            input("Press enter to exit")
            sys.exit()
        configDir = "sac_emu/dlc/"
    else:
        configDir = "sac_emu/game/"
    config.read(configDir + "config_override.ini")

    # Optional config check
    steamlessOptions = ""
    try:
        steamlessOptions = config["Developer"]["SteamlessOptions"] + " "
    except:
        pass

    for root, dirs, files in os.walk(config["Locations"][platform] + gameDir):
        apiFile = ""

        if config["Preferences"]["Steamless"] == "1" and (platform != "Steam" or config["Preferences"]["CrackOwnedGames"] == "1"):
            # Run Steamless on every .exe file. If it's not under DRM or not the wrong file, no problem!
            for fileName in files:
                if not fileName.endswith(".exe"):
                    continue
                print("- Attempting to run Steamless on", fileName)
                print("\n[[[ Steamless logs ]]]")
                fileLocation = root + "/" + fileName
                shutil.move(fileLocation, fileName) # Move the file to our location
                os.system("Steamless_CLI\\Steamless.CLI.exe " + steamlessOptions + "\"" + fileName + "\"") # Run Steamless on the game
                print("[[[ -------------- ]]]\n")

                # Check if the game was NOT unpacked
                if not os.path.isfile(fileName + ".unpacked.exe"):
                    # Move back the original game's exe since it didn't change
                    print("- Couldn't run Steamless on " + fileName + ", it is probably not under DRM.")
                    shutil.move(fileName, fileLocation)
                    continue

                print("- Removed Steam Stub DRM from", fileName)
                if config["FileNames"]["GameEXE"] != "":
                    # Rename and move back the original game's exe
                    shutil.move(fileName, fileLocation + config["FileNames"]["GameEXE"])
                else:
                    # Delete the original game's exe
                    os.remove(fileName)
                # Rename and move the unpacked exe to the game's directory
                shutil.move(fileName + ".unpacked.exe", fileLocation)

        if "steam_api.dll" in files:
            apiFile = root + "/steam_api.dll"
            apiFileVersion = GetFileVersion(apiFile)

            if config["Preferences"]["CrackOption"] == "0":
                if config["FileNames"]["SteamAPI"] == "":
                    os.remove(apiFile)
                else:
                    shutil.move(apiFile, root + "/" + config["FileNames"]["SteamAPI"])
                shutil.copyfile(configDir + "steam_api.dll", apiFile)

        if "steam_api64.dll" in files:
            apiFile = root + "/steam_api64.dll"
            apiFileVersion = GetFileVersion(apiFile)

            if config["Preferences"]["CrackOption"] == "0":
                if config["FileNames"]["SteamAPI64"] == "":
                    os.remove(apiFile)
                else:
                    shutil.move(apiFile, root + "/" + config["FileNames"]["SteamAPI64"])
                shutil.copyfile(configDir + "steam_api64.dll", apiFile)

        if apiFile != "":
            # Prepare the crack config file
            with open(configDir + "EmuConfigTemplate.ini", "r", encoding="utf-8") as template:
                fileContent = template.read()
            fileContent = fileContent.replace("SAC_AppID", str(appID))
            fileContent = fileContent.replace("SAC_APIVersion", apiFileVersion)
            buffer = ""
            for i in range(len(dlcIDs)):
                buffer += str(dlcIDs[i]) + " = " + dlcNames[i] + "\n"
            fileContent = fileContent.replace("SAC_DLC", buffer)

            # Create the crack config file
            fileLocation = ""
            if config["Preferences"]["CrackOption"] == "0" or config["Preferences"]["CrackOption"] == "1":
                fileLocation = root + "/" + config["FileNames"]["EmuConfig"]
            else:
                fileLocation = config["FileNames"]["EmuConfig"]

            with open(fileLocation, "w", encoding="utf-8") as file:
                file.write(fileContent)

            print("- Found Steam API DLL(s) in", root, "and cracked them successfully")
            cracked = True

    print("\n-----\nFinished cracking the game!")
    if not cracked:
        print("[!] No Steam API DLL was found in the game!")

    input("Press enter to exit")

except Exception:
    # Handle Python errors
    print("\n[!!!] A Python error occurred! Writing the error to the error.log file.\n---")
    with open("error.log", "w", encoding="utf-8") as errorFile:
        traceback.print_exc(file=errorFile)
    traceback.print_exc()
    print("---\nError written to error.log, please report it on GitHub or cs.rin.ru\nMake sure to blank any personal detail.")
    input("Press enter to exit")
