![LoLlyPlotty](icon.png)
# LoLlyPlotty
## League of Legends Statistics and Plots
Uses Riot Games API to download complete match data for a summoner (normals, ranked, etc.), parses and analyzes that data, and generates plots for data visualization given the user's preferences (e.g. champions played, friends played with, etc.).

## Instructions (Installation and Use)
#### Getting an API Key
**IMPORTANT: LoLlyPlotty requires an API key, obtained for free from [Riot's API Site](https://developer.riotgames.com "Riot API Site"). You must choose "Sign Up Now", then follow the directions. Keys are linked to your Riot account and expire every 24hrs; do not share them.**
+ Go to [https://developer.riotgames.com](https://developer.riotgames.com)
+ Choose "SIGN UP NOW" (this is free and very easy to do)
+ Log in and refresh your API key if necessary
+ Copy your API key

#### Running LoLlyPlotty (64-bit Windows)
+ Download the latest [LoLlyPlotty zip file](https://github.com/jasparagus/LoLlyPlotty/raw/master/LoLlyPlotty.zip)
+ Extract downloaded zip (Right-Click > "Extract All")
+ Run "LoLlyPlotty.exe" from the extracted files (tested on Windows 10 64-bit only)
+ IF UPGRADING FROM A PREVIOUS VERSION
  + Move your MatchData files (they end in .json) from the old folder to the new folder, otherwise they will be re-downloaded unnecessarily. If you accidentally begin to re-download match data, you can quit the program, copy over your old files, and re-start the program. It should find your old data without requiring a re-download. 
  + Move your configuration file (Configuration.json) from the old folder to the new folder if desired (not necessary)

*OR*

#### Running LoLlyPlotty from Python Source Code
+ Download the latest version of Python from [python.org](https://www.python.org/downloads/)
+ Check that you have the required modules (see also [Tutorial: Installing Packages in Python](https://packaging.python.org/tutorials/installing-packages/))
  + [Matplotlib](https://matplotlib.org/)
  + [NumPy](http://www.numpy.org/)
+ Download the Python source code from [Github](https://github.com/jasparagus/LoLlyPlotty)
+ Run "main.py"


#### Using LoLlyPlotty
+ Enter summoner info for desired summoner
+ Enter your API key (note that API keys may take a few moments to become active after they are created, so if things fail, try again in a few seconds)
+ Get your data! 
  + Note that this will take a long time on first run (can take >20 min. for 2000+ games; just let it run in the background)
  + Riot's API only allows you to grab ~3 years worth of data, but you can keep your data file and manually merge it if you'd like... instructions to come.
+ Once data is downloaded, choose a Y variable and an X variable (e.g. "Win/Loss" and "Teammate"), then make a plot from them!
  + LoLlyPlotty will choose an appropriate plot type (histogram, bar chart, scatter plot) for the selected data types
  + Try swapping X and Y for a different way to visualize the data
  + If desired, filters may be used to exclude/include specific options (e.g. champions, roles, seasons, ranked, etc.)
  + You may filter by recency (e.g. only games in the last 30 days)
  + You may exclude small sample-size items from your plots (e.g. exclude champions on which you've played fewer than 10 games) using the box at the bottom left
  + Choose the [confidence interval](https://en.wikipedia.org/wiki/Confidence_interval) you'd like shown on the plot (appears as a vertical black "error bar") using the appropriate dropdown; this is estimated from the data using
   [z-scores](https://en.wikipedia.org/wiki/Standard_score) and either the [standard deviation](https://en.wikipedia.org/wiki/Standard_deviation) or the [binomial proportion confidence interval](https://en.wikipedia.org/wiki/Binomial_proportion_confidence_interval), as applicable. Error bars are drawn on bar charts only (for now).
+ Plots to try, to get a feel for how LoLlyPlotty works:
  + "Win/Loss" vs. "Champion": your wintrate on various champions. Try filtering by ranked only, normals only, or ARAMs only and compare the results.
  + "Win/Loss" vs. "Champion (Played by Enemy)": note what champions you often lose against and reconsider your typical bans.
  + "Gold/Min Diff. (0 -> 10 Min)" vs. "Champion (Lane Opponent's)" to see your gold defecit when laning against various champions
  + "Win/Loss" vs. "Fraction of Team Damage (Total, To Champs)": see how your damage shares stack up in wins and losses. Note that "Win/Loss True" is a win and "Win/Loss False" is a loss.
+ Note that data is limited by what the Riot API knows (e.g. sometimes it can't figure out what lane you were in, so that data may be unknown). Not all data is available for all matches (older matches, for example, do not contain "self mitigated damage" data).


## Notes
+ Creates a .json data file for each summoner analyzed. This file is saved in the directory where LoLlyPlotty runs. These may be tens of MB in size. Make sure to copy these files when changing versions so you don't have to re-download them.
+ Riot's API keys have associated rate limits, and I haven't gotten a developer API key, since I don't want to pay for a server :)  
  + It will take a long time to download match data the first time the program is used to analyze a new summoner 
  + Matches are saved to your computer as they download, so you can stop and then resume downloading. 
  + Reloading the program and simply updating with new matches (e.g. adding 10-100 new matches) is fairly quick, since the bulk of the data is already on your computer.
+ LoLlyPlotty is a work in progress, and features will be added over time as laziness permits.
+ If you are experiencing strange issues/behavior, try deleting your Configuration.json file. If that doesn't work, try deleting your MatchData_summonername_REGION.json files (back them up first - this is all of your saved match data!) 


## Known Issues
+ First Blood Assist Doesn't work (Riot always records a 0 for this variable) as of last checking
+ Newly generated API keys do not work immediately. Wait ~5s after creating an API key before trying to use it for an API call. This seems(?) to be on Riot's end upon API key creation.
+ Riot's API sometimes returns an incorrect number of total matches from the MATCH-V3 Matchlist API. This may cause the total number displayed in-app to be incorrect.  This seems(?) to be on Riot's end, but is currently circumvented by grabbing the matchlist sequentially rather than in predefined blocks. 


## To-Do
+ Add Kill Participation, Kill Share generation (and subsequently plotting)
+ Add units to time played, etc.
+ Add a summoner spell filter (a filter for games where summoner spell 1 or 2 was a specific spell, e.g. ignite)
+ Add a progress bar above the bottom status text for long tasks (e.g. firstrun getting of match data)
+ Add new fractional variables (for histograms): percentage of team's (VARIABLE) that the player did/earned/etc. (e.g. damage or gold)
  + XP
  + Wards placed
  + Kills/Deaths/Assists?
+ Identify starting item(s) on a per-match basis - this requires "timeline" data api calls, which are not currently implemented
+ GUI Update
  + Make it not look hideous
  + Switch to ttk for better UI?
  + Switch to tabbed browsing using ttk via a menu bar at the top for tabbed navigation (e.g., Options tab)
+ Implement hist2d in matplotlib - convenient replacement for scatter plots
+ Consider using Pandas for handling (increasingly large) json data files


## Thanks
Thanks to [PVisnRT](https://github.com/PVisnRT) for working together on the original version of this (written in Matlab... no joke) and for contributing to adapting this for Python and working on data visualization methods. Thanks to [cjc77](https://github.com/cjc77) for extensive help with Python data structures and tons of Python advice.


## License
LoLlyPlotty isn’t endorsed by Riot Games and doesn’t reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.

LoLlyPlotty: league of legends statistics and plots. Copyright (C) 2017, league_plots@outlook.com

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
under certain conditions. See [license.txt](license.txt) for details.


## Notice
LoLlyPlotty isn’t endorsed by Riot Games and doesn’t reflect the views or opinions of Riot Games or anyone officially involved in producing or managing League of Legends. League of Legends and Riot Games are trademarks or registered trademarks of Riot Games, Inc. League of Legends © Riot Games, Inc.


## Changelog
+ 2019-07-27: Version 1.4: updated API calls for riot API v4. Implementing improved error handling on urllib calls. 
+ 2017-12-22: Version 1.2: broke out GUI (now a module). Added theming (manually via config file) Various bugfixes throughout.
+ 2017-12-16: Version 1.1: major GUI overhaul (color scheme, added frames everywhere).
+ 2017-12-10: Version 1.0: first executable version (for Windows x64); made using the excellent [pyinstaller tool](http://www.pyinstaller.org/)
+ 2017-11-30: Updated GUI for resizability
+ 2017-11-21: Implemented fractional plots (e.g. fraction of team damage, etc.)
+ 2017-10-31: Rebuilt plotting to work with custom plots via dropdown
+ 2017-10-26: Updated for Riot API v3 with new filtering method and file format
+ 2017-03-25: Working for Riot API v2 in Python with help from cjc77 and PVisnRT
+ 2016-October: Initial Matlab script by jasparagus and PVisnRT for Riot API v2.
