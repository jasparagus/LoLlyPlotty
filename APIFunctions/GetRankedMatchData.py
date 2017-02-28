import urllib.request # import ability to make URL requests
import urllib.error # import error handler for URL requests
import json # import ability to parse JSON objects
import time # import time to allow for use of time.sleep(secs). Prevents excessive api calls


# config_file = open("Configuration.LoHConfig", "r")
# config_info = json.loads(config_file.read())
# matchlist = open(config_info["Settings"]["SummonerName"] + "_MatchList.json", "r")
# matchlist = json.loads(matchlist.read())
# from APIFunctions import GetRankedMatchData


def update_matchdata(config_info):
    """ Pulls down list of matches, checks against saved data, grabs missing data, saves everything. """
    match_data_loaded = {}
    n_loaded = 0
    match_data_all = {}
    match_data = {}
    new_matches = []
    BaseURL = "https://na.api.pvp.net/api/lol/"
    matchlist_call = (BaseURL + config_info["Settings"]["Region"]
                     + "/v2.2/matchlist/by-summoner/"
                     + config_info["Settings"]["SID"]
                     + "?api_key="
                     + config_info["Settings"]["APIKey"])
    attempt = 0
    while attempt < 10:
        print("Getting list of all ranked matches (newest first). Attempt #" + str(attempt+1) + "/10")
        time.sleep(2)  # wait a sec to avoid excessive API calls with repeated retries
        try:
            matchlist_reply = urllib.request.urlopen(matchlist_call)
            matchlist_reply = matchlist_reply.read()
            matchlist = json.loads(matchlist_reply)
            print("Matchlist retrieved. Found", len(matchlist["matches"]), "matches.")
            with open(config_info["Settings"]["SummonerName"] + "_MatchList.json", "w") as matchlist_file:
                json.dump(matchlist, matchlist_file)
            n_matches = len(matchlist["matches"])
            print("Matchlist saved.")
            print("Matchlist")
            # stop iterating if things work
            attempt = 999
        except:
            attempt += 1
            print("Error getting matchlist. No matches found. Exiting.")
            n_matches = 0
        if n_matches !=0:
            try:
                print("Checking saved match data against matchlist.")
                match_data_loaded = open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "r")
                match_data_loaded = json.loads(match_data_loaded.read())
                n_loaded = len(match_data_loaded)
                for mm in range(n_matches):
                    mid = str(matchlist["matches"][mm]["matchId"])
                    if str(n_matches-1-mm) in match_data_loaded.keys():
                        print(mid, "found in file.")
                    else:
                        print(mid, "(match ",  mm, ") is new")
                        new_matches.append(mid)
                print("Found ", len(new_matches), " New Matches")
            except:
                print("Saved match data not found. Downloading all matches instead.")
                n_loaded = 0
                for mm in range(n_matches):
                    mid = str(matchlist["matches"][mm]["matchId"])
                    new_matches.append(mid)
            n_nm = len(new_matches)
            # prepare to compile all match data in match_data variable
            # reverse the order to grab oldest first before prepending them.
            new_matches = new_matches[::-1]
            match_data_all = match_data_loaded
            for mm in range(n_nm):
                print("preparing to pull down a new match")
                mid = str(new_matches[mm])
                BaseURL = "https://na.api.pvp.net/api/lol/"
                match_call = (BaseURL + config_info["Settings"]["Region"]
                              + "/v2.2/match/"
                              + mid
                              + "?api_key="
                              + config_info["Settings"]["APIKey"]
                              )
                attempt = 0
                for attempt in range(10):
                    try:
                        print("Trying to get match " + mid + ", Attempt #" + str(attempt + 1) + "/10")
                        time.sleep(2)  # wait a sec to avoid excessive API calls with repeated retries
                        match_data = urllib.request.urlopen(match_call)
                        match_data = match_data.read()
                        match_data = json.loads(match_data)
                        match_data_all[n_loaded+mm] = match_data
                        print("Succeeded - saving to file.")
                        with open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "w") as match_data_file:
                            json.dump(match_data_all, match_data_file)
                        attempt = 999
                        break
                    except:
                        attempt += 1
                        print("Failed to get match. Retrying up to 10 times.")
                        match_data = {}
                        match_data_all[mid] = match_data
        print("Done getting match data.")
    return match_data_all