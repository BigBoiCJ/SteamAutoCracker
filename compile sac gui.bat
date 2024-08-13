call .venv\Scripts\activate.bat
pyinstaller --onefile --windowed --icon=icon_hashtag.ico sac_files_here\steam_auto_cracker_gui.py --additional-hooks-dir=./hooks/
timeout /t 2 /nobreak > NUL
rmdir /S /Q build
del steam_auto_cracker_gui.spec
move dist\steam_auto_cracker_gui.exe "%cd%"
rmdir dist
pause
