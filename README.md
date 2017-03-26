# LeagueOfHistograms
## League of legends statistics analyzer
### Initial version 2017-03-07: jasparagus, cjc77, PVisnRT
![LeagueOfHistograms](https://github.com/jasparagus/LeagueOfHistograms/blob/master/icon.png "LeagueOfHistograms")

**Requires an API key, obtained for free from:**
[https://developer.riotgames.com/docs/api-keys]

Uses Riot Games API to obtain match data, parses and analyzes that data according to a set of filters, and generates plots for data visualization.


## Required Modules:
numpy
matplotlib
urllib3


## Notes:
1. Will run in-place and create a set of json files containing player data
2. It takes about 1.5s per match to download matches due to API rate limit, so on first-run you may need to give it a while
3. Match data is saved to your hard drive, and data is saved locally (it does not have to be re-downloaded each time the program is started)


## To-Do:
1. Damage Share Histograms
  -X-axis: percentage share of champion damage dealt, structure damage dealt, damage tanked in blocks of ~10%
  -Y-axis, plot 1: Percentage/fraction of wins per category or number of wins per category (both are identical except for normalization)
  -Y-axis, plot 2:  Winrate per category

2. Gold and XP leads histograms
  
3. Starting item winrates (useful when filtering by a specific champion)

4. Secondary plot options (entry boxes for things like number of matches to be considered a "teammate")

5. Require/Exclude mode for all filters

6. Update Filtering
  -Replace season, champion, queue type, and role with multiselection listboxes
  -Create enable/disable toggle for all options to be looped over
  -Update filter to loop over selected rather than a long list of if/then statements
  
  
7. GUI Update
  -Fix colors in general (expecially background)
  -Add graphics
  -Add explanation of 90% CI

8. Add mean/median/mode to histograms
9. Encorporate KDA somehow (probably through a histogram)
10. Add kill participation graph(s) (e.g. % KP by champion/role/win or histogram of wins)
