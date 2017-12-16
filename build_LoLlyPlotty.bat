pyinstaller ^
--icon "icon.ico"^
 --add-data "icon.png;."^
 --add-data "icon.ico;."^
 --add-data "seasons.gameconstants;."^
 --add-data "roles.gameconstants;."^
 --add-data "regions.gameconstants;."^
 --add-data "queues.gameconstants;."^
 --add-data "maps.gameconstants;."^
 --add-data "README.md;."^
 --add-data "license.txt;."^
 main.py