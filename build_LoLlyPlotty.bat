RMDIR /S /Q build
RMDIR /S /Q dist
pyinstaller --icon "icon.ico" --onefile main.py
copy README.md dist\README.md
copy license.txt dist\license.txt
copy icon.ico dist\icon.ico
copy maps.gameconstants dist\maps.gameconstants
copy queues.gameconstants dist\queues.gameconstants
copy regions.gameconstants dist\regions.gameconstants
copy roles.gameconstants dist\roles.gameconstants
copy seasons.gameconstants dist\seasons.gameconstants

"C:\Program Files\7-Zip\7z.exe" a LoLlyPlotty.zip .\dist\*



rem Following is previous method of building that does not use the "onefile" method
rem pyinstaller ^
rem --icon "icon.ico"^
rem  --add-data "README.md;."^
rem  --add-data "license.txt;."^
rem  --add-data "icon.png;."^
rem  --add-data "icon.ico;."^
rem  --add-data "maps.gameconstants;."^
rem  --add-data "queues.gameconstants;."^
rem  --add-data "regions.gameconstants;."^
rem  --add-data "roles.gameconstants;."^
rem  --add-data "seasons.gameconstants;."^
rem  main.py