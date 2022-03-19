# SteamAutoCracker
![GitHub all releases](https://img.shields.io/github/downloads/BigBoiCJ/SteamAutoCracker/total?color=brightgreen&label=Total%20downloads)
![GitHub release (latest by date)](https://img.shields.io/github/downloads/BigBoiCJ/SteamAutoCracker/latest/total?color=green&label=Latest%20version%20downloads)
![GitHub Repo stars](https://img.shields.io/github/stars/BigBoiCJ/SteamAutoCracker?color=yellow&label=Stars)
![GitHub watchers](https://img.shields.io/github/watchers/BigBoiCJ/SteamAutoCracker?label=Watchers)

An open-source script that automatically Cracks (removes DRM from) Steam games

**Setup tip:** you can paste text by using the right click.\
Left clicking will automatically copy the selected text, so don't do that.

## Features
- Automatically cracks your bought or pirated Steam games. You only need to enter the Game Name or AppID.
  - Cracks **Steam API DRM** by applying and configuring **Steam Emulators** automatically
  - Cracks **Steam Stub DRM** by applying **Steamless** on executables automatically
- No Steam account or Steam API key needed
- Configurable to your liking
- Option to only unlock DLCs for your bought Steam games instead of cracking them entirely
- Option to choose your own Steam Emu thanks to a simple config template system (default: ALI213)
- Open source, transparent and privacy focused. No hidden analytics or weird things!

## Screenshots
Screenshots from v1.0.0, they might be a bit outdated.

Setup:
![image](https://user-images.githubusercontent.com/101492671/158049430-d1d7f352-4060-4266-bd9a-5e022c365a29.png)\
Cracking phase 1:
![image](https://user-images.githubusercontent.com/101492671/158049508-20a821c0-22cd-46fe-b6ee-1ef4551cbfc7.png)\
Cracking phase 2:
![image](https://user-images.githubusercontent.com/101492671/158049553-5b41d992-d144-4851-b6cb-ed3eeb528b82.png)

## Requirements
- An internet connection (STA will do requests to `steampowered.com` to retrieve AppIDs and DLCs)
- If you use the compiled .exe:
  - 64 bits Windows
- If you use the python file (source):
  - No requirement. I think Python 3+ is needed.

## Notes about DLCs
Some DLCs in some games requires you to download additional files.\
This tool is not able to download those files, you'll have to get a clean version of them.

You can get clean Steam files for games (and sometimes DLCs) in the [Steam Content Sharing section from cs.rin.ru](https://cs.rin.ru/forum/viewforum.php?f=22)

## Windows Build informations
Compiled using [auto-py-to-exe](https://pypi.org/project/auto-py-to-exe/)

## Privacy
STA will do requests to `steampowered.com` (Steam's official website) to retrieve AppIDs and DLCs.\
It is not bannable, and won't cause you problems.

Nothing is logged by STA.\
You can delete the STA folder at any time and there won't be any leftovers.

## Virus detection
You could get a virus detection on some files. The biggest offender is `sac_emu\game\steam_api.dll`.\
A lot of cracking tools are detected as malware, either because their behavior is suspect (bypass game protections), or because they have been flagged manually (happens with a lot of tools).\
If you're suspicious about the legitimacy of the files, just delete the DLLs and use your owns instead.\
You can discuss with others about the tool in [cs.rin.ru](https://cs.rin.ru/forum/viewtopic.php?f=10&t=120610) or in the GitHub issues.

## Thanks
- Thanks to [atom0s for their Steamless project](https://github.com/atom0s/Steamless)
- Thanks to [oureveryday for their Steamless fork, supporting command-line](https://github.com/oureveryday/Steamless_CLI)
- Thanks to the creators of Steam Emus, speficially those who are included: ALI213 and deadmau5 (creator of CreamAPI)
- Thanks to CS.RIN.RU and their members for being helpful and sharing quality uploads
