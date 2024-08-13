# SteamAutoCracker
![GitHub all releases](https://img.shields.io/github/downloads/BigBoiCJ/SteamAutoCracker/total?color=brightgreen&label=Total%20downloads)
![GitHub release (latest by date)](https://img.shields.io/github/downloads/BigBoiCJ/SteamAutoCracker/latest/total?color=green&label=Latest%20version%20downloads)
![GitHub Repo stars](https://img.shields.io/github/stars/BigBoiCJ/SteamAutoCracker?color=yellow&label=Stars)
![GitHub watchers](https://img.shields.io/github/watchers/BigBoiCJ/SteamAutoCracker?label=Watchers)

An open-source script that automatically Cracks (removes DRM from) Steam games

## How to use (easy way)
- Download the bundled/compiled version by clicking [here](https://github.com/BigBoiCJ/SteamAutoCracker/releases/latest) and downloading the file named `Steam.Auto.Cracker.GUI.vX.X.X.zip`
- Extract the content of the archive (.zip) somewhere on your computer
- Run `steam_auto_cracker_gui.exe`
- Select the folder of your game
- Enter the name of the game to try to crack it! (you can also enter the Steam AppID if you know it)
  - SAC will automatically attempt to find the AppID using the Name you provided. If it can't, please try entering the AppID yourself.
  - You can find the AppID in the URL of the game's Steam page (ex: store.steampowered.com/app/-> ***620980*** <-/Beat_Saber/)

## Features
- Automatically cracks your bought or pirated Steam games. You only need to select the game's folder, and enter the Game Name or AppID.
  - Cracks **Steam API DRM** by applying and configuring **Steam Emulators** automatically
  - Cracks **Steam Stub DRM** by applying **Steamless** on executables automatically
- No Steam account or Steam API key needed
- Configurable to your liking
- Option to only unlock DLCs for your bought Steam games instead of cracking them entirely
- Option to choose your own Steam Emu thanks to a simple list, and simple config template system (default: ALI213)
  - List of Steam emus included by default:
    - ALI213 (Game)
    - Goldberg (Game)
    - CreamAPI (DLC)
- Open source, transparent and privacy focused. No hidden analytics or weird things!
- An opt-in autoupdater and version checker. Opt-in for privacy!

## Screenshots
Screenshots from v2.0.0

<details>
<summary>Images</summary>
<img src="https://github.com/BigBoiCJ/SteamAutoCracker/assets/101492671/6b9cd91e-9ff1-42a2-9efb-09586d41dbd3" width=50% height=50%>
<img src="https://github.com/BigBoiCJ/SteamAutoCracker/assets/101492671/039d5af8-1bad-47ec-b4c0-b164cc0388eb" width=50% height=50%>
<img src="https://github.com/BigBoiCJ/SteamAutoCracker/assets/101492671/25f0c44c-262f-4358-b694-fb0792bbcf52" width=50% height=50%>
</details>

## Requirements
- An internet connection (SAC will do requests to `steampowered.com` to retrieve AppIDs and DLCs)
- If you use the compiled .exe:
  - 64 bits Windows
- If you use the python file (source):
  - The `requests` module. Install with `py -m pip install requests` or `python -m pip install requests` or `python3 -m pip install requests`
  - The `pywin32` module (which contains win32api). Install with `py -m pip install pywin32` or `python -m pip install pywin32` or `python3 -m pip install pywin32`
    - If you have any problem, please check https://pypi.org/project/pywin32/
  - The `tkinter` module, but it should be included in Python by default.
  - As of v2.2.0 GUI, the `tkinterdnd2` module is required as well (v0.4.0+). Install it with `py -m pip install tkinterdnd2`. ([pypi link](https://pypi.org/project/tkinterdnd2/) - [github link](https://github.com/Eliav2/tkinterdnd2))
  - I believe Python 3.7+ is needed.

## Notes about DLCs
Some DLCs in some games requires you to download additional files.\
This tool is not able to download those files, you'll have to get a clean version of them.

You can get clean Steam files for games (and sometimes DLCs) in the [Steam Content Sharing section from cs.rin.ru](https://cs.rin.ru/forum/viewforum.php?f=22)

## Windows Build informations
Compiled using [pyinstaller](https://pypi.org/project/pyinstaller/) and venv\
Was previously compiled using [auto-py-to-exe](https://pypi.org/project/auto-py-to-exe/) (which is just a GUI for pyinstaller)

Instructions on how to compile SAC, as well as useful scripts are available here: https://github.com/BigBoiCJ/SteamAutoCracker/tree/compile-env

## Privacy
SAC will do requests to `steampowered.com` (Steam's official website) to retrieve AppIDs and DLCs.\
It is not bannable, and won't cause you problems.

SAC will do requests to this GitHub repository to check for updates, download the autoupdater and new releases.\
This only happens if you decide to manually click on the "Check for updates" button, and decide to update using the autoupdater. SAC can also automatically check for updates if enabled in the settings (it is disabled by default)

Nothing is logged by SAC.\
You can delete the SAC folder at any time and there won't be any leftovers. *

__* Exception to leftovers:__
- There will be some leftovers if you use the compiled exe. This is due to how PyInstaller / auto-py-to-exe works. An embedded version of Python and the python script itself will be extracted to the temp-folder of your OS. The folder will be named `_MEIxxxxxx`, where xxxxxx is a random number. You can delete the folder at any time after using the program, as it might not correctly delete itself in all cases. Please check the [pyinstaller documentation](https://pyinstaller.org/en/stable/operating-mode.html#how-the-one-file-program-works) for more infos.

## Virus detection
You could get a virus detection on some files. The biggest offender is `sac_emu/game_ali213/files/steam_api.dll`.\
A lot of cracking tools are detected as malware, either because their behavior is suspect (bypass game protections), or because they have been flagged manually (happens with a lot of tools).\
If you're suspicious about the legitimacy of the files, just delete the DLLs and use your owns instead.\
You can discuss with others about the tool in [cs.rin.ru](https://cs.rin.ru/forum/viewtopic.php?f=10&t=120610) or in the GitHub issues.

## Thanks
- Thanks to [atom0s for their Steamless project](https://github.com/atom0s/Steamless)
- Thanks to [oureveryday for their Steamless fork, supporting command-line](https://github.com/oureveryday/Steamless_CLI) (no longer used)
- Thanks to the creators of Steam Emus, specifically those who are included: ALI213, Goldberg and deadmau5 (creator of CreamAPI)
- Thanks to CS.RIN.RU and their members for being helpful and sharing quality uploads
- Thanks to our contributors that propose code, report issues and give suggestions! The most notable ones will be quoted in releases' notes
  - Even if you're not credited, that doesn't mean you didn't help! I thank everyone :heart:
