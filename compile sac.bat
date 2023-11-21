call .venv\Scripts\activate.bat
pyinstaller --onefile --icon=icon_hashtag.ico sac_files_here\steam_auto_cracker.py
timeout /t 2 /nobreak > NUL
rmdir /S /Q build
del steam_auto_cracker.spec
move dist\steam_auto_cracker.exe "%cd%"
rmdir dist
pause