import urllib.request # import ability to make URL requests
import urllib.error # import error handler for URL requests
import json # import ability to parse JSON objects
import time # import time to allow for use of time.sleep(secs). Prevents excessive api calls


def update_match_data(config_info, matchlist, n_matches):
    """ Pulls down list of matches, checks against saved data, grabs missing data, saves everything. """
    match_data_loaded = {}
    match_data = {}
    new_matches = []
    if n_matches != 0:
        try:
            match_data_loaded = open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "r")
            match_data_loaded = json.loads(match_data_loaded.read())
            n_loaded = len(match_data_loaded)
            for mm in range(n_matches):
                mid = str(matchlist["matches"][mm]["matchId"])
                if str(n_matches-1-mm) in match_data_loaded.keys():
                    print(mid, "found in file")
                else:
                    print(mid, "(match ",  mm, ") is new")
                    new_matches.append(mid)
            print("Found ", len(new_matches), " new matches")
        except:
            print("Saved match data not found, downloading all matches")
            n_loaded = 0
            for mm in range(n_matches):
                mid = str(matchlist["matches"][mm]["matchId"])
                new_matches.append(mid)
        n_nm = len(new_matches)

        # reverse the order to grab oldest missing match first, then append in chronological order
        new_matches = new_matches[::-1]
        match_data = match_data_loaded
        for mm in range(n_nm):
            mid = str(new_matches[mm])
            BaseURL = "https://na.api.pvp.net/api/lol/"
            match_call = (BaseURL + config_info["Settings"]["Region"]
                          + "/v2.2/match/"
                          + mid
                          + "?api_key="
                          + config_info["Settings"]["APIKey"]
                          )
            for attempt in range(5):
                try:
                    print("Getting match " + mid
                          + "(" + str(mm+1) + " of " + str(n_nm) + ")"
                          + ", attempt #" + str(attempt + 1) + "/5")
                    time.sleep(2)  # wait a sec to avoid excessive API calls with repeated retries
                    match_data[str(n_loaded+mm)] = json.loads(urllib.request.urlopen(match_call).read())
                    with open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "w") as match_data_file:
                        json.dump(match_data, match_data_file)
                    print("Got match " + mid)
                    break
                except:
                    match_data[str(n_loaded+mm)] = {}
    print("Done getting match data.")
    return match_data


def get_matchlist(config_info):
    """ Pulls down list of matches and returns them as matchlist """
    matchlist = {}
    n_matches = 0
    BaseURL = "https://na.api.pvp.net/api/lol/"
    matchlist_call = (BaseURL + config_info["Settings"]["Region"]
                     + "/v2.2/matchlist/by-summoner/"
                     + config_info["Settings"]["SID"]
                     + "?api_key="
                     + config_info["Settings"]["APIKey"])
    for attempt in range(5):
        print("Getting list of all ranked matches (newest first), attempt #" + str(attempt+1) + "/5")
        time.sleep(2)  # wait a sec to avoid excessive API calls with repeated retries
        try:
            matchlist = json.loads(urllib.request.urlopen(matchlist_call).read())
            with open(config_info["Settings"]["SummonerName"] + "_MatchList.json", "w") as matchlist_file:
                json.dump(matchlist, matchlist_file)
            n_matches = len(matchlist["matches"])
            print("Matchlist downloaded")
            break
        except:
            n_matches = 0
    return matchlist, n_matches
