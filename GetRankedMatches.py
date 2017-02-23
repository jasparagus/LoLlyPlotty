# GET LIST OF RANKED MATCHES, SAVE, GET MATCH DATA, SAVE


import urllib.request # import ability to make URL requests
import urllib.error # import error handler for URL requests
import json # import ability to parse JSON objects
import time # import time to allow for use of time.sleep(secs). Prevents excessive api calls


def get_matches(config,APIKey):
    print(config,APIKey)
    matches = 1
    return matches


BaseURL = "https://na.api.pvp.net/api/lol/na/"
MatchlistCall = BaseURL + "v2.2/matchlist/by-summoner/" + SID + "?api_key=" + APIKey


TimesTried = 0
while TimesTried < 10:
    TimesTried = TimesTried+1 # increment loop variable
    print("Getting list of all ranked matches (newest first). Attempt #",TimesTried)
    time.sleep(2) # wait a sec to avoid excessive API calls
    try:
        MatchlistReply = urllib.request.urlopen(MatchlistCall)
        MatchlistData = MatchlistReply.read()
        MatchlistJSONData = json.loads(MatchlistData)
        print("Matchlist Retrieved. Found",len(MatchlistJSONData["matches"]),"matches.")
        break
    except urllib.error.URLError as MatchlistReply:
        print("Error getting matchlist. Oops.")

# CHECK FOR EXISTING MATCHLIST FILE, COMPARE IT TO NEW MATCHLIST
MatchlistFileLoaded = open(SummonerName + '_Matchlist.json', 'r')
MatchlistJSONDataLoaded = json.loads(MatchlistFileLoaded.read())
for mm in range(len(MatchlistJSONData["matches"])):
    if MatchlistJSONData["matches"][mm]["matchId"] == MatchlistJSONDataLoaded["matches"][0]["matchId"]:
        print("Found", mm, "new matches")

# SAVE UPDATED MATCHLIST TO FILE
with open(SummonerName + "_Matchlist.json", "w") as MatchlistFile:
    json.dump(MatchlistJSONData, MatchlistFile)

# LOAD EXISTING MATCH DATA, GET NEW MATCH DATA, APPEND DATA, SAVE EVERYTHING -------- IN PROGRESS 2017-02-21
for mm in range(len(MatchlistJSONData["matches"])): # for each match found
    print("Grabbing info from match", mm+1,"/",len(MatchlistJSONData["matches"]))
    # MatchlistJSONData["matches"][mm]["matchId"]
    # MatchlistJSONData["matches"][mm]["champion"]
    # MatchlistJSONData["matches"][mm]["lane"]