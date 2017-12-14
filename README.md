![LoLlyPlotty](icon.png)
# LoLlyPlotty
## League of Legends Statistics and Plots
### Begun March 2017 by jasparagus, cjc77, and PVisnRT


**IMPORTANT: Requires an API key, obtained for free from [Riot's API Site](https://developer.riotgames.com "Riot API Site"). You must choose "Sign Up Now", then follow the directions. Keys are linked to your Riot account and expire every 24hrs; do not share them.**

Uses Riot Games API to download complete match data for a summoner (normals, ranked, etc.), parses and analyzes that data, and generates plots for data visualization given the user's preferences (e.g. champions played, friends played with, etc.).

## Instructions (.exe for Windows x64)
+ Follow directions above (or click link in-app) to get an API key:
  + Go to https://developer.riotgames.com
  + Choose "SIGN UP NOW"
  + Log in and refresh your API key if necessary
+ Download [LoLlyPlotty_Win_x64_v1.0.zip](LoLlyPlotty_Win_x64_v1.0.zip) directly or download the source code via GitHub and locate it
+ Extract downloaded zip and run "main.exe" (for executable) or "main.py" (for python)
+ Enter summoner info for desired summoner
+ Enter your API key (note that freshly generated API keys may take a few moments to activate)
+ Get your data! Note that this will take a long time on first run
+ Choose your y and x variables, then make a plot from them!
+ If desired, filter to include/exclude specific options (e.g. roles or champions played) and re-make your plot(s)
  + Try Win/Loss vs. Champion to see your wintrate on various champions
  + Try Gold/Min Diff. (0 -> 10 Min) vs. Champion (Lane Opponent's) to see your gold defecit when laning against various champions
+ Note that all data is limited by what the Riot API knows (e.g. sometimes it can't reliably figure out what lane you were in)
  


## Required Python 3 Modules to Run From Source
(See also directions for [installing packages in Python](https://packaging.python.org/tutorials/installing-packages/))
+ [Matplotlib](https://matplotlib.org/)
+ [NumPy](http://www.numpy.org/)


## Notes:
+ Runs in-place to create a (rather large) json data file for each summoner analyzed
+ Riot's API servers have rate limits, so don't be alarmed if it takes a little while to get matches the first time it is run (matches are saved to disk for later use)
+ This is a work in progress, and features will be added over time

## Known Issues:
+ First Blood Assist Doesn't work

## To-Do:
+ Add a Teammate filter (a filter for games that include specific teammate(s)), along the same lines as the Champion filter. This will require identifying "Teammates" on startup or via a button press. Best way will probably be to make a "settings" window and include a "# Games to be considered a 'Teammate'" option on that pane.

+ Add a progress bar beneath the bottom status text for long tasks (e.g. firstrun getting of match data)

+ Add new fractional variables (for histograms): percentage of team's (VARIABLE) that the player did/earned/etc. (e.g. damage or gold)
  + XP
  + Wards placed
  + Kills/Deaths/Assists?

+ Identify starting item(s) on a per-match basis - this requires "timeline" data api calls, which are not currently implemented

+ GUI Update
  + Change resizing to allow for scrollbars
  + Make it not look hideous
  + Switch to ttk for theming
  + Make a menu bar at the top for tabbed navigation (e.g., Options tab)
  + Add a scrollbar for the list of filters (so that many more filters can be added)

+ Implement hist2d in matplotlib - really convenient replacement for scatter plots

## License
LoLlyPlotty: league of legends statistics and plots.
Copyright (C) 2017, league_plots@outlook.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions. See license.txt for details.


## Notes
Thanks to [PVisnRT](https://github.com/PVisnRT) for working together on the original version of this (written in Matlab... lol) and for contributing to adapting this for Python. Thanks to [cjc77](https://github.com/cjc77) for extensive help with Python data structures and tons of Python advice.


## Major Changelog
#### 2017-12-10: First executable version (for Windows x64); made using the excellent [pyinstaller tool](http://www.pyinstaller.org/)
#### 2017-11-30: Updated GUI for resizability
#### 2017-11-21: Implemented fractional plots (e.g. fraction of team damage, etc.)
#### 2017-10-31: Rebuilt plotting to work with custom plots via dropdown
#### 2017-10-26: Updated for Riot API v3 with new filtering method and file format
#### 2017-03-25: Working for Riot API v2