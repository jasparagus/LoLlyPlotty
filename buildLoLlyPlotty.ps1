# First, clean up old files
Remove-Item .\build -Recurse -Force -Confirm:$false
Remove-Item .\dist -Recurse -Force -Confirm:$false

# Next, do the actual build
$outputName = "LoLlyPlotty.exe"
pyinstaller --icon "icon.ico" --name $outputName --onefile main.py

# Now, copy in the supplemental information
Copy-Item -Path "README.md" -Destination "dist\README.md"
Copy-Item -Path "icon.ico" -Destination "dist\icon.ico"
Copy-Item -Path "license.txt" -Destination "dist\license.txt"
Copy-Item -Path "maps.gameconstants" -Destination "dist\maps.gameconstants"
Copy-Item -Path "queues.gameconstants" -Destination "dist\queues.gameconstants"
Copy-Item -Path "regions.gameconstants" -Destination "dist\regions.gameconstants"
Copy-Item -Path "roles.gameconstants" -Destination "dist\roles.gameconstants"
Copy-Item -Path "seasons.gameconstants" -Destination "dist\seasons.gameconstants"

# Package everything in the "dist" folder into a zip file using 7zip
$timeStamp = Get-Date -Format "yyyyMMdd"
& "C:\Program Files\7-Zip\7z.exe" a ("archive\LoLlyPlotty_" + $timeStamp + ".zip") .\dist\*

Copy-Item -Path ("archive\LoLlyPlotty_" + $timeStamp + ".zip") -Destination ("LoLlyPlotty" + ".zip") -Force

# Clean up the build/dist folders after everything is done
Remove-Item .\build -Recurse -Force -Confirm:$false
Remove-Item .\dist -Recurse -Force -Confirm:$false
Remove-Item ($outputName + ".spec") -Force -Confirm:$false