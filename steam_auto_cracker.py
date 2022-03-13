import requests
import configparser
import json
import os
import sys
from sac_lib.get_file_version import GetFileVersion
from itertools import combinations
import shutil

VERSION = "1.0.0"

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
    req = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")

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
        exit()

def FindGameDirectory(gameName: str, configName: str, attemptCombos=True) -> str:
    gameName = gameName.lower()
    gameNameList = [gameName]

    # Create a list with all the combinations of name possible
    characters = [" ", ":", "-", "'"]
    for combo in combinations(characters, len(characters)):
        # This will remove all possible combinations of characters that are often not included in folder names
        buffer = gameName
        for char in combo:
            buffer.replace(char, "")
        gameNameList.append(buffer)

    for folder in os.listdir(config["Locations"][configName]):
        if folder.lower() in gameNameList:
            return folder
    return "error"

def RetrieveAppName(appID: int) -> str:
    req = requests.get("https://store.steampowered.com/api/appdetails?appids=" + str(appID) + "&filters=basic")
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

    print("[1/4] Retrieving game informations from Steam...")
    # https://wiki.teamfortress.com/wiki/User:RJackson/StorefrontAPI#appdetails
    req = requests.get("https://store.steampowered.com/api/appdetails?appids=" + str(appID) + "&filters=basic")
    data = req.json()
    data = data[str(appID)]
    if data["success"] == "false":
        print("- AppID " + str(appID) + " not found.")
        input("Press enter to exit")
        exit()
    if data["data"]["type"] != "game":
        print("- AppID " + str(appID) + " is not a game.")
        input("Press enter to exit")
        exit()

    gameName = data["data"]["name"]
    appID = data["data"]["steam_appid"]
    print("- Game found! Name:", gameName, "- AppID:", appID)

    print("[2/4] Retrieving DLCs...")

    if "dlc" in data["data"]:
        dlcIDs = data["data"]["dlc"]
        dlcIDsLen = len(dlcIDs)

        # Get DLCs names
        for i in range(dlcIDsLen):
            appName = RetrieveAppName(dlcIDs[i])
            if appName == "error":
                print("- Error! No App Name found for AppID", dlcIDs[i])
                input("Press enter to exit")
                exit()
            dlcNames.append(appName)
            print("- Found DLC " + str(i+1) + "/" + str(dlcIDsLen) + ": " + appName + " (" + str(dlcIDs[i]) + ")")
    else:
        print("- No DLC found for this game!")

# Other

print("Steam Auto Cracker (v" + VERSION + ") by BigBoiCJ")
print("-----")

# Config

config = configparser.ConfigParser()
if config.read("config.ini") == []:
    # Config doesn't exist, create it
    config["Locations"] = {}

    print("Since this is the first time you start the Steam Auto Crack tool (or you removed the config file), you'll need to specify the location of your Steam games")
    print("Example: D:/Games/Steam/SteamApps/common/")
    print("Note: anti-slashes \\ will be converted to slashes /")
    print("If you do not have Steam or you do not plan to auto-unlock DLCs for your BOUGHT Steam games, don't write anything")

    loc = input("Steam Games location: ")
    loc = FixFolderFormatting(loc)
    config["Locations"]["Steam"] = loc

    print("----------")
    print("Specify the location of your NON-LEGAL/Pirated Steam Games. This will allow the tool to automatically crack the game for you. Sadly, Steamless can't be automated, so we won't be able to remove Steam Stub.")
    print("Example: D:\\Games\\Pirated\\")
    print("Note: anti-slashes \\ will be converted to slashes /")
    print("If you do not have Pirated Games or you do not plan to auto-crack games and/or auto-unlock DLCs, don't write anything")

    loc = input("Pirated Games location: ")
    loc = FixFolderFormatting(loc)
    config["Locations"]["Pirated"] = loc

    config["Preferences"] = {}

    print("----------")
    print("Now, please decide wether or not we should directly crack the game, or if we should only create the crack config instead:")
    print("0 - Crack the game automatically")
    print("1 - Only create the crack config, and put it in the same directory as steam_api(64).dll")
    print("2 - Only create the crack config, and put it in the same directory as the Steam Auto Crack tool")
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

    print("----------")
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

    config["FileNames"] = {}

    print("----------")
    print("Should we keep the default steam_api.dll file?")
    print("empty = don't keep it, delete it")
    print("anything else = new file name (including the extension)")
    choice = input("New file name for steam_api.dll: ")
    config["FileNames"]["SteamAPI"] = str(choice)

    print("----------")
    print("Should we keep the default steam_api64.dll file?")
    print("empty = don't keep it, delete it")
    print("anything else = new file name (including the extension)")
    choice = input("New file name for steam_api64.dll: ")
    config["FileNames"]["SteamAPI64"] = str(choice)

    with open("config.ini", "w", encoding="utf-8") as configFile:
        config.write(configFile)

    print("----------")
    print("Setup finished!")
    print("-----=====-----")

# Script

gameName = input("Enter the Name or AppID of the game you want to Crack: ")
appID = 0
dlcIDs = []
dlcNames = []

try:
    appID = int(gameName)
except:
    appID = FindInAppList(gameName)

RetrieveGame()

print("[3/4] Searching the game folder...")

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
print("[4/4] Searching Steam API DLLs and cracking them...")

cracked = False

if platform == "Steam" and config["Preferences"]["CrackOwnedGames"] == "0":
    configDir = "sac_emu/dlc/"
else:
    configDir = "sac_emu/game/"
config.read(configDir + "config_override.ini")

for root, dirs, files in os.walk(config["Locations"][platform] + gameDir):
    apiFile = ""

    if "steam_api.dll" in files:
        apiFile = root + "/steam_api.dll"
        apiFileVersion = GetFileVersion(apiFile)

        if config["Preferences"]["CrackOption"] == "0":
            if config["FileNames"]["SteamAPI"] == "":
                os.remove(apiFile)
            else:
                os.rename(apiFile, root + "/" + config["FileNames"]["SteamAPI"])
            shutil.copyfile(configDir + "steam_api.dll", apiFile)

    if "steam_api64.dll" in files:
        apiFile = root + "/steam_api64.dll"
        apiFileVersion = GetFileVersion(apiFile)

        if config["Preferences"]["CrackOption"] == "0":
            if config["FileNames"]["SteamAPI64"] == "":
                os.remove(apiFile)
            else:
                os.rename(apiFile, root + "/" + config["FileNames"]["SteamAPI64"])
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

print("-----\nFinished cracking the game!")
if not cracked:
    print("[!] No Steam API DLL was found in the game!")
else:
    print("Remember to use Steamless on the game if needed!")

input("Press enter to exit")