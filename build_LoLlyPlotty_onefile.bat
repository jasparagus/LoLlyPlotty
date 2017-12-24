pyinstaller --icon "icon.ico" --onefile main.py
copy license.txt dist\license.txt
copy README.md dist\README.md
copy icon.ico dist\icon.ico
copy maps.gameconstants dist\maps.gameconstants
copy queues.gameconstants dist\queues.gameconstants
copy regions.gameconstants dist\regions.gameconstants
copy roles.gameconstants dist\roles.gameconstants
copy seasons.gameconstants dist\seasons.gameconstants
