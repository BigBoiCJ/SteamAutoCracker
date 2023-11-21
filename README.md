# SteamAutoCracker compile environment

**Change the branch to `main` to return to SteamAutoCracker!**

Scripts and files to help you 'compile'/bundle SteamAutoCracker into an .exe by yourself

## Requirements
- An internet connection (if you haven't installed the `requests` and `pywin32` modules)
- 64 bits Windows
- The `requests` and `pywin32` module. Just run `create venv.bat` to create a virtual environment and install those modules on it, but I'll explain this later.
- Python 3.7+ is needed. I'm personally running 3.9, so this version is guaranteed to work.

## Compile instructions for Windows and pyinstaller
Compiled using [pyinstaller](https://pypi.org/project/pyinstaller/) and [venv](https://docs.python.org/3/library/venv.html)

1. Download this branch, and extract the folder in the archive somewhere on your PC
2. Open your windows terminal (cmd) and run `pip install pyinstaller` or `py -m pip install pyinstaller` if pyinstaller isn't already installed.
3. Open the folder and run `create venv.bat`. This is a Windows script file, it might trigger a warning, but allow the file to run anyway. (If you're afraid of it having viruses, you can easily open this file with a text editor and see what's inside)
4. Download the `main` branch of SteamAutoCracker, and put the `steam_auto_cracker.py` file and the `sac_lib` folder inside of `sac_files_here`
5. Run `compile sac.bat`, wait a bit, and you should now have a `steam_auto_cracker.exe` file! Enjoy :)

(The `open venv.bat` file isn't used, but you can run it to access to the virtual environment, install modules and run commands... Modules installed inside the venv won't be installed on your real Python environment.)

## Troubleshooting
- If `py` ins't recognized as a command:
  - Please make sure you installed Python 3.9+ from the official website (not the microsoft store). I can't guarantee the syntax on older versions of Python.
  - Manually edit the .bat scripts and change `py` to your python command.
- If `pyinstaller` isn't recognized as a command:
  - Make sure you installed `pyinstaller` correctly with `py -m pip install pyinstaller`
  - Make sure your Python installation has been correctly added to your Path environment variables. Check online on how to do it. GLHF, that might be a pain to do.
 
## Why does this exist?
For transparency, to share knowledge and to let people fork and/or continue to support SteamAutoCracker by themselves.

Feel free to re-use those scripts for your own projects.
