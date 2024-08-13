call .venv\Scripts\activate.bat
pyinstaller --onefile --icon=icon_hashtag.ico sac_files_here\steam_auto_cracker_gui_autoupdater.py
timeout /t 2 /nobreak > NUL
rmdir /S /Q build
del steam_auto_cracker_gui_autoupdater.spec
move dist\steam_auto_cracker_gui_autoupdater.exe "%cd%"
rmdir dist
pause