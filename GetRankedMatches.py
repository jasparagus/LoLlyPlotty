# GET LIST OF RANKED MATCHES, SAVE, GET MATCH DATA, SAVE


import urllib.request # import ability to make URL requests
import urllib.error # import error handler for URL requests
import json # import ability to parse JSON objects
import time # import time to allow for use of time.sleep(secs). Prevents excessive api calls


# CONTENTS OF config_info REPRODUCED HERE FOR REFERENCE
# config_info["settings"]["APIKey"]
# config_info["settings"]["Region"]
# config_info["settings"]["SummonerName"]
# config_info["settings"]["SID"]

def get_matchlist(config_info):
    BaseURL = "https://na.api.pvp.net/api/lol/"
    matchlist_call = (BaseURL + config_info["Settings"]["Region"]
                     + "/v2.2/matchlist/by-summoner/"
                     + config_info["Settings"]["SID"]
                     + "?api_key="
                     + config_info["Settings"]["APIKey"])

    TimesTried = 0 # prepare to retry a few times if needed
    while TimesTried < 10:
        TimesTried += 1  # increment loop variable
        print("Getting list of all ranked matches (newest first). Attempt #", TimesTried)
        time.sleep(2)  # wait a sec to avoid excessive API calls with repeated retries
        try:
            matchlist_reply = urllib.request.urlopen(matchlist_call)
            matchlist_data = matchlist_reply.read()
            matchlist_JSON_data = json.loads(matchlist_data)
            print("Matchlist Retrieved. Found", len(matchlist_JSON_data["matches"]), "matches.")
            break
        except urllib.error.URLError as MatchlistReply:
            print("Error getting matchlist. Oops.")
            matchlist_JSON_data = {}

    # # CHECK FOR EXISTING MATCHLIST FILE, COMPARE IT TO NEW MATCHLIST
    # MatchlistFileLoaded = open(SummonerName + "_Matchlist.json", "r")  # open matchlist
    # MatchlistJSONDataLoaded = json.loads(MatchlistFileLoaded.read())
    # for mm in range(len(matchlist_JSON_data["matches"])):
    #     if matchlist_JSON_data["matches"][mm]["matchId"] == MatchlistJSONDataLoaded["matches"][0]["matchId"]:
    #         print("Found", mm, "new matches")
    #
    # # SAVE UPDATED MATCHLIST TO FILE
    # with open(SummonerName + "_Matchlist.json", "w") as MatchlistFile:
    #     json.dump(matchlist_JSON_data, MatchlistFile)
    return matchlist_JSON_data





def get_matchinfo(config_info, matchid):
    print("You called get_matchinfo. Function isn't done yet.")
    print(matchid)
    print(config_info)
    matchinfo = 0
    return matchinfo



# LOAD EXISTING MATCH DATA, GET NEW MATCH DATA, APPEND DATA, SAVE EVERYTHING -------- IN PROGRESS 2017-02-21
# for mm in range(len(MatchlistJSONData["matches"])): # for each match found
#     print("Grabbing info from match", mm+1,"/",len(MatchlistJSONData["matches"]))
    # MatchlistJSONData["matches"][mm]["matchId"]
    # MatchlistJSONData["matches"][mm]["champion"]
    # MatchlistJSONData["matches"][mm]["lane"]