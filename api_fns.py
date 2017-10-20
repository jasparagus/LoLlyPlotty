import urllib.request  # import ability to make URL requests
import urllib.error  # import error handler for URL requests
import json  # import ability to parse JSON objects
import time  # import time to allow for use of time.sleep(secs). Prevents excessive API calls
import pathlib  # allows checking for whether or not match_data JSON file exists already


def api_key():
    # gets the API key from a text file called "apikey.txt". Modify this function if that method changes
    try:
        with open("apikey.txt", "r") as file:
            apikey = file.readline()  # Read the first line
        apikey = apikey.replace(" ", "").replace("\n", "")  # strip spaces & newlines
    except:
        print("File \"apikey.txt\", containing api key, not found")
        apikey = ""

    return apikey


def json_from_url(url):
    req = urllib.request.Request(url)  # add the api key header
    req.add_header("X-Riot-Token", api_key())
    try:
        reply = urllib.request.urlopen(req)  # get the reply from the server
        json_data = json.loads(reply.read())  # create a dictionary the data as a JSON object
        _ = api_wait(reply)  # calculate the wait time and wait
    except:
        print("Error opening URL. Check API Key.")
        json_data = {}

    return json_data
# once the above is done, you can use the following as usual:
# xx_reply = urllib.request.urlopen(req)
# xx_data = test.read()


def api_wait(html_reply):
    # Waits an amount of time to avoid excessive API calls determined from the server reply
    wait_time = 0  # only wait if it's necessary
    app = html_reply.info()["X-App-Rate-Limit-Count"].split(",")
    app_lim = html_reply.info()["X-App-Rate-Limit"].split(",")
    method = html_reply.info()["X-Method-Rate-Limit-Count"].split(",")
    method_lim = html_reply.info()["X-Method-Rate-Limit"].split(",")
    retry_after = html_reply.info()["Retry-After"]

    # Check app limit for each timeframe, add wait(s) if necessary
    for ii in range(len(app)):
        att_rem = int(app_lim[ii].split(":")[0])-int(app[ii].split(":")[0])
        timeframe = int(app_lim[ii].split(":")[1])
        # if <2 attempts remain for this timeframe, wait a half-cycle before retrying
        if att_rem <= 2:
            wait_time += int(timeframe)
            print(app)  # for debugging; delete later
            print(app_lim)
            print(method)
            print(method_lim)

    # Check method limit for each timeframe; add wait(s) if necessary
    for ii in range(len(method)):
        att_rem = int(method_lim[ii].split(":")[0]) - int(method[ii].split(":")[0])
        timeframe = int(method_lim[ii].split(":")[1])
        # if <2 attempts remain for this timeframe, wait a half-cycle before retrying
        if att_rem <= 2:
            wait_time += int(timeframe)
            print(app)  # for debugging; delete later
            print(app_lim)
            print(method)
            print(method_lim)

    if retry_after is not None:
        # If you hit a wait limit, give things a good long wait
        print("Retry after was ", retry_after)
        wait_time = int(retry_after) + 1
        print(app)  # for debugging; delete later
        print(app_lim)
        print(method)
        print(method_lim)

    wait_remaining = wait_time
    started_waiting = time.time()
    while wait_remaining > 0:
        wait_remaining = started_waiting + wait_time - time.time()
        print("Wait remaining: " + str(int(wait_remaining)) + "s")
        time.sleep(0.5)
        # popup("Waiting for Riot API rate limit" + str(wait_remaining) + "seconds")

    return wait_time


def config(region, summoner_name):
    """ Take settings info and write a config file. """
    config_info = {}

    # Clean up the summoner name and get the account ID
    summoner_name = summoner_name.replace(" ", "").lower().replace('\n', '')  # strip spaces, caps, and newlines
    account_id = ""
    summoner_id = ""

    # Store the information obtained so far in the configuration dictionary
    config_info["SummonerName"] = summoner_name
    config_info["Region"] = region
    config_info["GameConstants"] = read_game_constants()
    config_info["ChampionDictionary"] = get_champ_dict()

    if (config_info["SummonerName"] is not "" and
            config_info["Region"] in config_info["GameConstants"]["regions.gameconstants"].copy().keys()):
        account_id, summoner_id = summoner_by_name(config_info)  # grab account & summoner IDs from web

    # Write (or overwrite, as applicable) new settings to a configuration dictionary
    config_info["AccountID"] = account_id
    config_info["SummonerID"] = summoner_id

    # Write (or overwrite, as applicable) new settings to a configuration file
    with open("Configuration.json", 'w') as file:
        json.dump(config_info, file)

    return config_info


def summoner_by_name(config_info):
    """ Get summoner ID from summoner name. Summoner name must be lower-case letters only """
    account_id = ""
    summoner_id = ""

    summoner_by_name_url = (
        "https://" +
        config_info["GameConstants"]["regions.gameconstants"][config_info["Region"]] +
        "/lol/summoner/v3/summoners/by-name/" +
        config_info["SummonerName"]
        )

    for attempt in range(5):
        try:
            acct_data_json = json_from_url(summoner_by_name_url)
            account_id = acct_data_json["accountId"]
            account_id = str(account_id)
            summoner_id = acct_data_json["id"]
            summoner_id = str(summoner_id)
            break
        except:
            pass
    return account_id, summoner_id


def get_matchlist(config_info, begin_index):
    """
    Asks for 50 matches starting with begin_index (inclusive) and older
    :param config_info: program configuration information
    :param begin_index: index of newest match to grab; starts at 0
    :return: matchlist, an array of strings of gameIds; total_games, the number of games Riot has available.
    Games are returned in chronological order (e.g. first game in "matchlist" is oldest).
    """
    total_games = 0
    matchlist = []

    matchlist_url = (
        "https://" +
        config_info["GameConstants"]["regions.gameconstants"][config_info["Region"]] +
        "/lol/match/v3/matchlists/by-account/" +
        config_info["AccountID"] +
        "?beginIndex=" + str(begin_index)
    )

    # Ask for the matchlist up to 5 times, returning an empty matchlist if failed
    for attempt in range(5):
        try:
            matchlist_json = json_from_url(matchlist_url)  # make the matchlist call
            total_games = matchlist_json["totalGames"]  # check the total number of games played
            n_matches = len(matchlist_json["matches"])  # check how many matches were returned
            for match_index in range(n_matches):
                # new_matches =
                matchlist.append(str(matchlist_json["matches"][match_index]["gameId"]))
            break
        except:
            print(matchlist)
    return matchlist, total_games


def get_full_matchlist(config_info):
    begin_index = 0
    full_matchlist = {}

    matchlist_tmp, total_games = get_matchlist(config_info, begin_index)

    # Figure out how many partial matchlists will need to be retrieved
    num_times = total_games/len(matchlist_tmp)  # this may be a non-integer...
    if int(num_times) < num_times:
        num_times += 1  # if there's anything that got truncated, account for it before final truncation
    num_times = int(num_times)

    for ii in range(num_times):
        # Get the matchlist for this iteration
        matchlist_tmp, total_games = get_matchlist(config_info, begin_index)

        # For each partial matchlist, get the match index and match IDs
        for jj in range(len(matchlist_tmp)):
            match_index = total_games - (begin_index + jj)
            match_id = matchlist_tmp[jj]
            full_matchlist[match_index] = match_id

        # compute the next begin index
        begin_index += len(matchlist_tmp)

    len_full_matchlist = len(full_matchlist)

    return full_matchlist, len_full_matchlist


def get_match(config_info, match_id):
    """
    Gets match data for the given match id
    :param config_info: configuration settings for application
    :param match_id: match ID (string or int) for desired match
    :return: returns match as a dict
    """
    match = {}

    match_url = (
        "https://" +
        config_info["GameConstants"]["regions.gameconstants"][config_info["Region"]] +
        "/lol/match/v3/matches/" +
        str(match_id)
    )

    # Ask for the match data
    for attempt in range(5):
        try:
            match = json_from_url(match_url)
            break
        except:
            pass
    return match


def append_match(config_info, match, match_index):
    """
    Appends the match data from "match" to the match data file
    :param config_info: configuration dictionary
    :param match: dictionary containing match data
    :param match_index: index of the match
    """
    f_path = config_info["SummonerName"] + "_MatchData.json"

    if pathlib.Path(f_path).is_file():
        with open(f_path, mode="r+") as file:
            file.seek(0, 2)  # find the end of the file
            position = file.tell() - 1  # find the position of the 2nd-to-last character
            file.seek(position)  # go to the 2nd-to-last character
            file.write(", \"" + str(match_index) + "\": " + json.dumps(match) + "}")
    else:
        with open(f_path, "w") as file:
            json.dump({str(match_index):match}, file)
    return


def verify_matches(match_data):
    for match_index in range(len(match_data)):
        match_number = str(match_index + 1)
        try:
            # See if the match has a gameId
            match_data[match_number]["gameId"]
        except:
            # if you can't find the gameId, delete the match from the match list
            match_data.pop(match_number, None)
    return match_data


def get_champ_dict():
    """
    Creates a champion lookup table using Riot's Data Dragon web service or locally if that fails
    """
    try:
        time.sleep(0.1)
        realms_url = "http://ddragon.leagueoflegends.com/realms/na.json"
        dd_version = json.loads(urllib.request.urlopen(realms_url).read())
        champ_version = str(dd_version["n"]["champion"])

        time.sleep(0.1)
        champ_url = "http://ddragon.leagueoflegends.com/cdn/" + champ_version + "/data/en_US/champion.json"
        champ_data = json.loads(urllib.request.urlopen(champ_url).read())

        champ_IDs = champ_data["data"].copy().keys()
        champ_dict = {}

        for name in champ_IDs:
            champ_dict[champ_data["data"][name]["key"]] = champ_data["data"][name]["name"]
    except:
        # If data dragon isn't working, try to load the local file
        try:
            with open("Configuration.json","r") as file:
                config_info = json.loads(file.read())
                champ_dict = config_info["ChampionDictionary"]
        except:
            champ_dict = {}
            print("Couldn't connect to data dragon or load champion list... sorry :(")

    return champ_dict


def champ_name(champ_dict, cId):
    """ Returns a champion name from its champion ID using the lookup table pulled from Data Dragon. """
    try:
        cName = champ_dict[str(cId)]
    except:
        cName = "MissingNo"
    return cName


def read_game_constants():
    """
    Loads up all game constant files, which are not available through Riot's API.
    Files are tab-delimited with each entry on a new line.
     Each line should consist of "code \t value"; following content is ignored (e.g. trailing \n, subsequent \t, etc.)
    :return: Dictionary of game constants, allowing lookup of, e.g., maps by mapId.
    """

    game_constants = {}
    game_constants_files = [str(p) for p in pathlib.Path(".").iterdir() if "gameconstants" in str(p)]

    for ii in game_constants_files:
        try:
            with open(ii) as file:
                rows = (line.split("\t") for line in file)
                game_constants[ii] = {row[0]: row[1].replace("\n", "") for row in rows}
        except:
            print("Unable to load/open file: " + ii)
            game_constants[ii] = {}
            pass

    return game_constants
