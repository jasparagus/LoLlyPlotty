# LeagueOfHistograms
## League of legends statistics analyzer
### Begun 2017-03-07 for League API v2
### By jasparagus, cjc77, and PVisnRT
![LeagueOfHistograms](https://github.com/jasparagus/LeagueOfHistograms/blob/master/icon.png "LeagueOfHistograms")

**Requires an API key, obtained for free from:**
[https://developer.riotgames.com/api-keys.html]

Uses Riot Games API to download complete match data for a summoner (normals, ranked, etc.), parses and analyzes that data, and generates plots for data visualization given the user's preferences (e.g. champions played, friends played with, etc.).


## Required Modules:
+ matplotlib
+ urllib3


## Notes:
+ Will run in-place (wherever the master file is located) to create a (rather large) json data file for each summoner
+ Riot's API servers have rate limits, so don't be alarmed if it takes a little while to get matches the first time it is run (matches are saved to disk for later use)
+ This is a work in progress, and features will be added over time


## To-Do:
+ Re-implement fractional variables (for histograms): percentage of team's (VARIABLE) that the player did/earned/etc. (e.g. damage or gold)
  2. Damage stats
  3. Gold stats
  4. XP stats
  5. Wards placed
  6. Kills/Deaths/Assists?
  
+ Identify starting item(s) on a per-match basis - this may require "timeline" data api calls, which are not currently implemented

+ GUI Update
  0. Make it not look hideous
  1. Switch to ttk for theming
  2. Add tabbed navigation? Or a scrollbar for more filters
  
+ Add mean/median to histograms?

+ Incorporate KDA somehow (probably through a histogram)

+ Switch GUI filter panes to trade entries rather than reproducing them
  1. read queues, etc. as dictionaries
  2. add them to the appropriate filtering dropdowns
  3. Replace the dropdowns with multiselect boxes
  
+ Add CS and CS differential data

+ Winrate by lane opponent's champion

+ Winrate for when every champion is on the enemy or on your team (not including when you play them); use overlaid red(enemy team)/green(ally team) bars with winrates, with n_games printed below each bar