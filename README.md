# LeagueOfHistograms
## League of legends statistics analyzer
### Begun 2017-03-07 for League API v2
### By jasparagus, cjc77, and PVisnRT
![LeagueOfHistograms](https://github.com/jasparagus/LeagueOfHistograms/blob/master/icon.png "LeagueOfHistograms")

**Requires an API key, obtained for free from:**
[https://developer.riotgames.com/api-keys.html]

Uses Riot Games API to download complete match data for a summoner (normals, ranked, etc.), parses and analyzes that data, and generates plots for data visualization given the user's preferences (e.g. champions played, friends played with, etc.).


## Required Modules:
numpy
matplotlib
urllib3


## Notes:
1. Will run in-place (wherever the master file is located) and creates a (someimes large) json file of data for each summoner
2. Riot's API servers have rate limits, so don't be alarmed if it takes a little while to get matches at first
3. Match data is saved to your hard drive (it does not have to be re-downloaded each time the program is started)


## To-Do:
+ Fix plot generation code to use the new parsed_data format (for the match data once it has been parsed)

+ Damage Share Histograms
  1. X-axis: percentage share of champion damage dealt, structure damage dealt, damage tanked in blocks of ~10%
  2. Y-axis, plot 1: Percentage/fraction of wins per category or number of wins per category (both are identical except for normalization)
  3. Y-axis, plot 2:  Winrate per category

+ Gold and XP leads histograms
  
+ Starting item winrates (useful when filtering by a specific champion)

+ Secondary plot options (entry boxes for things like number of matches to be considered a "teammate")

+ Replace season, champion, queue type, and role with multiselection listboxes
  1. Update filter to loop over selected options
  2. 
  
+ GUI Update
  1. Add background colors
  2. Modify font sizes/styles to improve look
  3. Break out into multiple panes instead of one giant thing to make the formatting nicer.
  
+ Add mean/median/mode to histograms

+ Incorporate KDA somehow (probably through a histogram)

+ Read in a dictionary for the appropriate game constants and populate dropdowns
  1. read queues, etc. as dictionaries
  2. add them to the appropriate filtering dropdowns
  3. Replace the dropdowns with multiselect boxes
  
+ Add CS and CS differential data

+ Winrate by lane opponent's champion

+ Winrate for when every champion is on the enemy or on your team (not including when you play them); use overlaid red(enemy team)/green(ally team) bars with winrates, with n_games printed below each bar