import urllib.request  # import ability to make URL requests
import urllib.error  # import error handler for URL requests
import json  # import ability to parse JSON objects
import time  # import time to allow for use of time.sleep(secs). Prevents excessive api calls


def update_match_data(config_info, matchlist, n_matches):
    """
    Pulls down list of matches, checks against saved data, grabs missing data, saves everything.
    Currently being deprecated in favor of 2 separate functions
    """
    match_data_loaded = {}
    match_data = {}
    new_matches = []
    if n_matches != 0:
        try:
            with open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "r") as file:
                match_data_loaded = json.loads(file.read())
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
            match_call = (
                "https://na.api.pvp.net/api/lol/" + config_info["Settings"]["Region"]
                + "/v2.2/match/" + mid + "?"
                + "api_key=" + config_info["Settings"]["APIKey"]
            )
            for attempt in range(5):
                try:
                    print("Getting match " + mid
                          + "(" + str(mm+1) + " of " + str(n_nm) + ")"
                          + ", attempt #" + str(attempt + 1) + "/5")
                    time.sleep(1.4)  # wait a sec to avoid excessive API calls with repeated retries
                    match_data[str(n_loaded+mm)] = json.loads(urllib.request.urlopen(match_call).read())
                    with open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "w") as file:
                        json.dump(match_data, file)
                    print("Got match " + mid)
                    break
                except:
                    match_data[str(n_loaded+mm)] = {}
    print("Done getting match data.")
    return match_data


def get_matchlist(config_info):
    """
    Pulls down list of matches and returns them as matchlist
    IN PROCESS OF BEING DEPRECATED
    """
    matchlist = {}
    n_matches = 0
    matchlist_call = (
        "https://na.api.pvp.net/api/lol/" + config_info["Settings"]["Region"]
        + "/v2.2/matchlist/by-summoner/" + config_info["Settings"]["SID"] + "?"
        + "rankedQueues="
    )

    for queue in config_info["RankedQueues"]:
        matchlist_call = matchlist_call + queue + ","
    matchlist_call = matchlist_call[:-1] + "&" + "api_key=" + config_info["Settings"]["APIKey"]

    for attempt in range(5):
        print("Getting list of all ranked matches (newest first), attempt #" + str(attempt+1) + "/5")
        time.sleep(1.4)  # wait a sec to avoid excessive API calls with repeated retries
        try:
            matchlist = json.loads(urllib.request.urlopen(matchlist_call).read())
            with open(config_info["Settings"]["SummonerName"] + "_MatchList.json", "w") as file:
                json.dump(matchlist, file)
            n_matches = len(matchlist["matches"])
            print("Matchlist downloaded")
            break
        except:
            pass

    return matchlist, n_matches


def get_match_list(config_info):
    """
    Pulls down list of matches.
    Returns a list of match IDs as strings(match_list)
    """
    match_list = []

    match_list_call = (
        "https://na.api.pvp.net/api/lol/" + config_info["Settings"]["Region"]
        + "/v2.2/matchlist/by-summoner/" + config_info["Settings"]["SID"] + "?"
        + "rankedQueues="
    )

    # Prepare a list of ranked queues from which to ask for matches
    for queue in config_info["RankedQueues"]:
        match_list_call = match_list_call + queue + ","

    match_list_call = match_list_call[:-1] + "&" + "api_key=" + config_info["Settings"]["APIKey"]

    # Ask for the matchlist up to 5 times, retunring an empty match_list when failed
    for attempt in range(5):
        # print("Getting list of all ranked matches (newest first), attempt #" + str(attempt+1) + "/5")
        time.sleep(1.4)  # wait a sec to avoid excessive API calls with repeated retries
        try:
            match_list_reply = json.loads(urllib.request.urlopen(match_list_call).read())
            n_matches = len(match_list_reply["matches"])
            for match in range(n_matches):
                match_list.append(str(match_list_reply["matches"][match]["matchId"]))
            match_list = match_list[::-1]
            break
        except:
            match_list = []

    return match_list


def get_match(config_info, match_list, match_data, match_id):
    """
    Checks matchlist for match "match_id"
    Gets the match if it's new
    match, puts in the corresponding key of "match_data", and saves the whole thing
    """
    try:
        # Find the match "index" for the new match
        match_idx = match_list.index(str(match_id))

        # Prepare the API call
        match_call = (
            "https://na.api.pvp.net/api/lol/" + config_info["Settings"]["Region"]
            + "/v2.2/match/" + str(match_id) + "?"
            + "api_key=" + config_info["Settings"]["APIKey"]
        )

        # Do the api call
        for attempt in range(5):
            try:
                time.sleep(1.4)  # wait a sec to avoid excessive API calls with repeated retries
                match_data[str(match_idx)] = json.loads(urllib.request.urlopen(match_call).read())
                with open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "w") as file:
                    json.dump(match_data, file)
                break
            except:
                match_data[str(match_idx)] = {}
        # print(
        #     "Got match " + str(match_id)
        #     + "(" + str(match_idx+1) + " of " + str(len(match_list)) + ")"
        # )
    except:
        pass
    return match_data


"""
import urllib.request  # import ability to make URL requests
import urllib.error  # import error handler for URL requests
import json  # import ability to parse JSON objects
import time  # import time to allow for use of time.sleep(secs). Prevents excessive api calls
config_info = json.loads(open("Configuration.LoHConfig", "r").read())
match_data = json.loads(open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "r").read())

"""