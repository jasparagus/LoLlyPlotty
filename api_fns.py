#    LICENSE INFORMATION
#    LoLlyPlotty: league of legends statistics and plots.
#    Copyright (C) 2017 Jasper Cook, league_plots@outlook.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    This program comes with ABSOLUTELY NO WARRANTY.
#    This is free software, and you are welcome to redistribute it
#    under certain conditions. See license.txt for details.

import urllib.request  # import ability to make URL requests
import urllib.error  # import error handler for URL requests
import json  # import ability to parse JSON objects
import time  # import time to allow for use of time.sleep(secs). Prevents excessive API calls
import pathlib  # allows checking for whether or not match_data JSON file exists already

#Todo: add new URLs from (https://developer.riotgames.com/docs/lol)
#    http://static.developer.riotgames.com/docs/lol/seasons.json
#    http://static.developer.riotgames.com/docs/lol/queues.json
#    http://static.developer.riotgames.com/docs/lol/maps.json
#    http://static.developer.riotgames.com/docs/lol/gameModes.json
#    http://static.developer.riotgames.com/docs/lol/gameTypes.json

def get_api_key(write_mode=False, key_in=""):
    # gets the API key from a text file called "apikey.txt". Modify this function if that changes
    try:
        with open("apikey.txt", "r") as file:
            file_contents = file.readlines()  # Read the first line

        key = file_contents[0].replace(" ", "").replace("\n", "")  # strip spaces & newlines

        expiry = str(file_contents[1]).replace(" ", "").replace("\n", "")  # read the 2nd line
        if float(expiry) < float(time.time()):
            key = "API Key Expired. Please Get A New Key"

    except FileNotFoundError:
        key = "API Key Not Found. Please Get A Key"
        expiry = 0

    except (AttributeError, ValueError):
        key = "API Key Error. Please Get A New Key"
        expiry = 0

    if write_mode is True and str(key) != str(key_in):
        # print("in write mode")
        with open("apikey.txt", "w") as file:
            file.write(str(key_in).replace(" ", "").replace("\n", ""))
            file.seek(0, 2)  # seek point 0 characters away from end of file ("2")
            file.write("\n" + str(time.time() + 24 * 60 * 60))

    return key, expiry


def json_from_url(url, status=None):
    # Makes a request to riot servers using API key, and returns the result in json form
    req = urllib.request.Request(url)  # add the api key header
    api_key, _ = get_api_key()
    req.add_header("X-Riot-Token", api_key)
    try:
        reply = urllib.request.urlopen(req)  # get the reply from the server
        json_data = json.loads(reply.read())  # create a dictionary the data as a JSON object
        if status is not None:
            _ = api_wait(reply, status=status)  # calculate the wait time and wait
        else:
            _ = api_wait(reply)
    except urllib.error.HTTPError as e:
        if status is not None:
            status.set(
                "HTTP response code: " + str(e) + ". See https://developer.riotgames.com/response-codes.html")
        print(e, "See https://developer.riotgames.com/response-codes.html for more details. Attempted URL: " + url)
        json_data = {}
    except Exception as e:
        if status is not None:
            status.set("Error opening URL. Check API Key or wait a few moments if it's a new key.")
        print("Non-HTTP error, see below. Also check API Key.")
        print(e)
        print("attempted URL:" + url)
        json_data = {}

    return json_data


def api_wait(html_reply, status=None):
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
            # print(app)  # for debugging; delete later
            # print(app_lim)
            # print(method)
            # print(method_lim)

    # Check method limit for each timeframe; add wait(s) if necessary
    for ii in range(len(method)):
        att_rem = int(method_lim[ii].split(":")[0]) - int(method[ii].split(":")[0])
        timeframe = int(method_lim[ii].split(":")[1])
        # if <2 attempts remain for this timeframe, wait a half-cycle before retrying
        if att_rem <= 2:
            wait_time += int(timeframe)
            # print(app)  # for debugging; delete later
            # print(app_lim)
            # print(method)
            # print(method_lim)

    if retry_after is not None:
        # If you hit a wait limit, give things a good long wait
        # print("Retry after was ", retry_after)
        wait_time = int(retry_after) + 1
        # print(app)  # for debugging; delete later
        # print(app_lim)
        # print(method)
        # print(method_lim)

    wait_remaining = wait_time
    started_waiting = time.time()
    while wait_remaining > 0:
        wait_remaining = started_waiting + wait_time - time.time()
        # print("Wait remaining: " + str(int(wait_remaining)) + "s")
        if status is not None:
            status.set("Waiting to make more API calls: " + str(int(wait_remaining)) + " seconds...")
        time.sleep(0.5)
        # popup("Waiting for Riot API rate limit" + str(wait_remaining) + "seconds")

    return wait_time


def config(region, summoner_name, status=None):
    """ Take settings info and write a config file. """
    if status is not None:
        status.set("Updating configuration file")
    config_info = {}

    # Clean up the summoner name and get the account ID
    summoner_name = summoner_name.replace(" ", "").lower().replace('\n', '')  # strip spaces, caps, and newlines
    account_id = ""
    summoner_id = ""

    # Store the information obtained so far in the configuration dictionary
    config_info["SummonerName"] = summoner_name
    config_info["Region"] = region
    config_info = add_game_constants(config_info, status=status)
    config_info = add_static_data(config_info, status=status)

    if (config_info["SummonerName"] is not "" and
            config_info["Region"] in config_info["regions.gameconstants"].copy().keys()):
        account_id, summoner_id = summoner_by_name(config_info, status=status)  # grab account & summoner IDs from web
    # Write (or overwrite, as applicable) new settings to a configuration dictionary
    config_info["AccountID"] = account_id
    config_info["SummonerID"] = summoner_id

    # Write (or overwrite, as applicable) new settings to a configuration file
    with open("Configuration.json", 'w') as file:
        json.dump(config_info, file)

    return config_info


def config_overwrite(config_info):

    with open("Configuration.json", 'w') as file:
        json.dump(config_info, file)

    return config_info


def summoner_by_name(config_info, status=None):
    """ Get summoner ID from summoner name. Summoner name must be lower-case letters only """
    if status is not None:
        status.set("Getting summoner info")
    account_id = ""
    summoner_id = ""

    summoner_by_name_url = (
        "https://" +
        config_info["regions.gameconstants"][config_info["Region"]] +
        "/lol/summoner/v4/summoners/by-name/" +
        config_info["SummonerName"]
        )

    for attempt in range(3):
        try:
            acct_data_json = json_from_url(summoner_by_name_url, status=status)
            account_id = acct_data_json["accountId"]
            account_id = str(account_id)
            summoner_id = acct_data_json["id"]
            summoner_id = str(summoner_id)
            break
        except KeyError:
            pass
    return account_id, summoner_id


def get_matchlist(config_info, begin_index, status=None):
    """
    Asks for 50 matches starting with begin_index (inclusive) and older
    :param config_info: program configuration information
    :param begin_index: index of newest match to grab; starts at 0
    :return: matchlist, an array of strings of gameIds; total_games, the number of games Riot has available.
    Games are returned in chronological order (e.g. first game in "matchlist" is oldest).
    """
    if status is not None:
        status.set("Getting matchlist from riot servers. Found " + str(begin_index) + " matches.")
    end_index = "0"
    total_games = "0"
    matchlist = []

    matchlist_url = (
        "https://" +
        config_info["regions.gameconstants"][config_info["Region"]] +
        "/lol/match/v4/matchlists/by-account/" +
        config_info["AccountID"] +
        "?beginIndex=" + str(begin_index)
    )

    # Ask for the matchlist up to 5 times, returning an empty matchlist if failed
    for attempt in range(3):
        try:
            matchlist_json = json_from_url(matchlist_url, status=status)  # make the matchlist call
            total_games = str(matchlist_json["totalGames"])  # check the total number of games - isn't always correct
            end_index = str(matchlist_json["endIndex"])  # the last index retrieved, not inclusive
            n_matches = len(matchlist_json["matches"])  # check how many matches were returned
            for match_index in range(n_matches):
                # new_matches =
                matchlist.append(str(matchlist_json["matches"][match_index]["gameId"]))
            break
        except Exception as e:
            print("Error with:", e, "\nMatchlist was:", matchlist)
            if status is not None:
                status.set("Unexpected error:" + str(e))
    return matchlist, end_index, total_games


def get_full_matchlist(config_info, status=None):
    begin_index = "0"
    full_matchlist = []

    while True:
        # Get the matchlist for this iteration
        partial_matchlist, end_index, _ = get_matchlist(config_info, begin_index, status=status)

        full_matchlist += partial_matchlist

        if str(begin_index) == str(end_index):  # see if you have reached the end of the matchlist
            break
        else:  # if not, the next iteration should start where this one ended
            begin_index = str(end_index)

    # Remove any duplicates and sorth the whole matchlist by gameId
    full_matchlist = sorted(list(set(full_matchlist)))
    len_full_matchlist = len(full_matchlist)

    return full_matchlist, len_full_matchlist


def get_match(config_info, game_id, status=None):
    """
    Gets match data for the given match id
    :param config_info: configuration settings for application
    :param game_id: match ID (string or int) for desired match
    :param status: status string object (tkinter StrinkVar for holding status information)
    :return: returns match as a dict
    """
    match = {}

    match_url = (
        "https://" +
        config_info["regions.gameconstants"][config_info["Region"]] +
        "/lol/match/v4/matches/" +
        str(game_id)
    )

    # Ask for the match data
    for attempt in range(3):
        try:
            match = json_from_url(match_url, status=status)
            break
        except Exception:
            if status is not None:
                status.set("Unable to get game with matchId = " + str(game_id))
            pass
    return match


def append_match(config_info, match, match_key, status=None):
    """
    Appends the match data from "match" to the match data file
    :param config_info: configuration dictionary
    :param match: dictionary containing match data
    :param match_key: key to which the match will be linked in the file, e.g. the gameId for a game
    :param status: status string object (tkinter StrinkVar for holding status information)
    """
    if status is not None:
        status.set("Appending match \"" + str(match_key) + "\" to file")

    fp = "MatchData_" + str(config_info["SummonerName"]) + "_" + str(config_info["Region"]) + ".json"

    if pathlib.Path(fp).is_file():
        with open(fp, mode="r+") as file:
            file.seek(0, 2)  # find the end of the file
            position = file.tell() - 1  # find the position of the 2nd-to-last character
            file.seek(position)  # go to the 2nd-to-last character
            file.write(", \"" + str(match_key) + "\": " + json.dumps(match) + "}")
    else:
        with open(fp, "w") as file:
            json.dump({str(match_key): match}, file)
    return


def verify_matches(config_info, match_data, status=None):
    game_ids = list(match_data.copy().keys())

    for game_id in game_ids:
        try:
            # See if the match has a gameId in its data; if so, assume it's OK. This could be improved.
            # TODO: figure out a better way to check if a match's data is correct than its gameId field
            if str(match_data[game_id]["gameId"]) != str(game_id):
                # If you find the entry but its gameId is wrong, raise an exception
                raise Exception
            timestamp = match_data[game_id]["gameCreation"]  # Check that the match has a timestamp
            length = match_data[game_id]["gameDuration"]  # check that match has a length
            float(timestamp)  # check that timestamp can be a number
            float(length)  # check that length can be a number
        except (Exception, ValueError, NameError, KeyError):
            # if there was an issue with the match, remove it from the dictionary and overwrite the data file
            print("Match file had an error with match " + str(game_id) + ". Removing it and updating file.")
            if status is not None:
                status.set("Match file had an error with match " + str(game_id) + ". Removing it and updating file.")
            match_data.pop(game_id, None)
            # Overwrite the entire file with the corrected file
            fp = "MatchData_" + str(config_info["SummonerName"]) + "_" + str(config_info["Region"]) + ".json"
            with open(fp, "w") as file:
                json.dump(match_data, file)

    return match_data


def add_static_data(config_info, status=None):
    """
    Creates a spell lookup table using Riot's Data Dragon web service or locally if that fails
    """
    if status is not None:
        status.set("Getting static data from data dragon")
    # Create a dictionary to hold the lookup tables (keys are Riot-determined names for the variables of interest)
    static_data_list = ["champion",  "summoner", "item"]
    for kk in static_data_list:
        config_info[kk] = {}

    try:
        realms_url = "http://ddragon.leagueoflegends.com/realms/na.json"
        dd_version = json.loads(urllib.request.urlopen(realms_url).read())["n"]

        url = ("http://ddragon.leagueoflegends.com/cdn/" + str(dd_version["champion"]) + "/data/en_US/champion.json")
        reply = json.loads(urllib.request.urlopen(url).read())
        lookup_keys = reply["data"].copy().keys()

        for lk in list(lookup_keys):
            config_info["champion"][reply["data"][lk]["key"]] = reply["data"][lk]["name"]

        url = ("http://ddragon.leagueoflegends.com/cdn/" + str(dd_version["summoner"]) + "/data/en_US/summoner.json")
        reply = json.loads(urllib.request.urlopen(url).read())
        lookup_keys = reply["data"].copy().keys()

        for lk in list(lookup_keys):
            config_info["summoner"][reply["data"][lk]["key"]] = reply["data"][lk]["name"]

        url = ("http://ddragon.leagueoflegends.com/cdn/" + str(dd_version["item"]) + "/data/en_US/item.json")
        reply = json.loads(urllib.request.urlopen(url).read())
        lookup_keys = reply["data"].copy().keys()

        for lk in list(lookup_keys):
            config_info["item"][lk] = reply["data"][lk]["name"]

    except Exception as e:
        if status is not None:
            status.set("Couldn't get data from data dragon. Trying to load it from file.")
        # print("Error with:", e)
        # If data dragon isn't working, try to load the local file
        try:
            with open("Configuration.json", "r") as file:
                loaded_config = json.loads(file.read())
                for kk in static_data_list:
                    config_info[kk] = loaded_config[kk]
        except (FileNotFoundError, KeyError):
            if status is not None:
                status.set("Couldn't get data from data dragon or load it from file")
    if status is not None:
        status.set("Got static data")
    return config_info


def add_game_constants(config_info, status=None):
    """
    Loads up all game constant files, which are not available through Riot's API.
    Files are tab-delimited with each entry on a new line.
     Each line should consist of "code \t value"; following content is ignored (e.g. trailing \n, subsequent \t, etc.)
    :return: Dictionary of game constants, allowing lookup of, e.g., maps by mapId.
    """
    if status is not None:
        status.set("Getting game constants...")

    constants = {
        'maps': 'http://static.developer.riotgames.com/docs/lol/maps.json',
        'queues': 'http://static.developer.riotgames.com/docs/lol/gameModes.json',
        'gameTypes': 'http://static.developer.riotgames.com/docs/lol/gameTypes.json',
        'seasons': 'http://static.developer.riotgames.com/docs/lol/seasons.json'
    }

    for constant in constants:
        config_info[constant] = {}
        reply = json.loads(urllib.request.urlopen(constants[constant]).read())

    game_constants_files = [str(p) for p in pathlib.Path(".").iterdir() if "gameconstants" in str(p)]

    for constant in game_constants_files:
        config_info[constant] = {}
        # config_info[constant+"_lookup"] = {}
        try:
            with open(constant) as file:
                rows = (line.split("\t") for line in file)
                # config_info[constant] = {str(row[0]): str(row[1]).replace("\n", "") for row in rows}
                for row in rows:
                    # config_info[constant][str(row[0])] = str(row[1]).replace("\n", "")
                    # config_info[constant+"_lookup"][str(row[1]).replace("\n", "")] = str(row[0])
                    config_info[constant][str(row[0])] = str(row[1]).replace("\n", "")
        except FileNotFoundError:
            if status is not None:
                status.set("Unable to load " + constant + " from file")
            print("Unable to load/open file: " + constant)
            config_info[constant] = {}
            # config_info[constant+"_lookup"] = {}
            pass

    return config_info
