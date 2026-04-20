# Steam Game Utility Manager

![GitHub all releases](https://img.shields.io/github/downloads/BigBoiCJ/SteamAutoCracker/total?color=brightgreen&label=Total%20downloads)
![GitHub release (latest by date)](https://img.shields.io/github/downloads/BigBoiCJ/SteamAutoCracker/latest/total?color=green&label=Latest%20version%20downloads)
![GitHub Repo stars](https://img.shields.io/github/stars/BigBoiCJ/SteamAutoCracker?color=yellow&label=Stars)
![GitHub watchers](https://img.shields.io/github/watchers/BigBoiCJ/SteamAutoCracker?label=Watchers)

---

## Project Intent

This application is a **desktop utility for managing and automating local Steam game configuration workflows**.

It is designed to help users:
- Organize and manage installed Steam game folders
- Apply compatibility or configuration adjustments for local game setups
- Automate repetitive setup tasks for installed games
- Retrieve game metadata (such as AppIDs) from Steam’s public store pages

This tool does **not modify Steam services**, does **not interact with Steam accounts**, and does **not distribute game content**.

---

## How to use (easy way)

- Download the latest release from:  
  https://github.com/BigBoiCJ/SteamAutoCracker/releases/latest

- Extract the `.zip` archive to a folder on your computer

- Run:

- Select your installed game folder

- Enter the game name or Steam AppID
- The tool will attempt to resolve the AppID automatically if a name is provided
- You can find the AppID in the Steam store URL  
  Example: `store.steampowered.com/app/620980/Beat_Saber/`

---

## Features

- Automates local configuration tasks for Steam game directories
- Supports modular workflow plugins for different game setup processes
- No Steam account or API key required
- Lightweight and configurable design
- Optional metadata lookup using Steam public store pages
- Plugin-based architecture for extensibility
- No analytics or user tracking

---

## Screenshots

Screenshots from v2.0.0

<details>
<summary>Images</summary>

<img src="https://github.com/BigBoiCJ/SteamAutoCracker/assets/101492671/6b9cd91e-9ff1-42a2-9efb-09586d41dbd3" width=50% height=50%>
<img src="https://github.com/BigBoiCJ/SteamAutoCracker/assets/101492671/039d5af8-1bad-47ec-b4c0-b164cc0388eb" width=50% height=50%>
<img src="https://github.com/BigBoiCJ/SteamAutoCracker/assets/101492671/25f0c44c-262f-4358-b694-fb0792bbcf52" width=50% height=50%>

</details>

---

## Requirements

- Internet connection (used only for retrieving public Steam store metadata)
- If using compiled version:
- Windows 64-bit
- If using source:
- Python 3.7+
- requests
- pywin32
- tkinter (usually included)
- tkinterdnd2

---

## Notes about DLCs

Some DLCs in certain games may require additional content files depending on the user’s setup.  
This tool does not handle external game content downloads.

Users are responsible for ensuring they have legitimate access to any game or DLC files they use with this tool.

---

## Windows Build Information

Compiled using [PyInstaller](https://pypi.org/project/pyinstaller/) and venv.  
Was previously compiled using [auto-py-to-exe](https://pypi.org/project/auto-py-to-exe/) (a GUI wrapper for PyInstaller).

Instructions on how to compile the project, as well as useful development scripts, are available here:  
https://github.com/BigBoiCJ/SteamAutoCracker/tree/compile-env

---

## Privacy

This tool may make requests to `steampowered.com` (Steam’s official website) to retrieve public metadata such as AppIDs and DLC listings.

It may also check this GitHub repository for updates when update functionality is enabled by the user.

No analytics, telemetry, or user tracking is performed.

Temporary files created during execution or packaging (e.g., PyInstaller builds) may be stored in the system’s temporary directory and removed automatically by the operating system.

---

## Antivirus / False Positives

Some antivirus software may flag executables created with packaging tools such as PyInstaller.  
This is a common false positive for many Python applications and does not necessarily indicate malicious behavior.

If desired, users can run the application directly from source.

---

## Thanks

- Thanks to all contributors, testers, and users who provide feedback and improvements
- Thanks to open-source tooling communities that make this project possible
