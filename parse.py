import time


def parse_variable(match_data, parsed_data, variable_name, key_list):
    """
    Creates an entry in the parsed_match_data dictionary under key "var_name" for the property at "json_path"   :param config_info:
    :param match_data: match_data dictionary
    :param variable_name: key name to use for the new
    :param key_list: list of keys, in order, where the data is located in the match_data dictionary
    :return:
    """
    # variable_name = variable_name.replace(" ","_")
    value = match_data.copy()

    # Extract the nested value from the list of keys
    try:
        for key in key_list:
            value = value[key]
    except:
        value = "Unknown"

    # Load the old variable list or create it if this is the first time it's been called
    try:
        parse_variable = parsed_data[variable_name]
    except:
        parse_variable = []

    # Append the new value to the list and place it in the parsed_data dictionary
    parse_variable.append(value)
    parsed_data[variable_name] = parse_variable

    return parsed_data


def find_player_id(config_info, match_data, game_id, parsed_data):
    player_id = 999
    teamId = 999
    opponent_id = "UNKNOWN"
    player_lane = "UNKNOWN"
    player_role = "UNKNOWN"
    n_players = len(match_data[str(game_id)]["participantIdentities"])
    ally_stats = {}
    enemy_stats = {}

    for ii in range(n_players):
        if (str(match_data[str(game_id)]["participantIdentities"][ii]["player"]["accountId"]) ==
                str(config_info["AccountID"])):
            player_id = ii
            teamId = match_data[str(game_id)]["participants"][ii]["teamId"]
            player_lane = match_data[str(game_id)]["participants"][ii]["timeline"]["lane"]
            player_role = match_data[str(game_id)]["participants"][ii]["timeline"]["role"]

    ally_stats["names"] = []
    ally_stats["gold_earned"] = 0
    ally_stats["damage_total"] = 0
    ally_stats["damage_champs"] = 0
    ally_stats["damage_taken"] = 0
    ally_stats["damage_mitigated"] = 0

    enemy_stats["names"] = []
    enemy_stats["gold_earned"] = 0
    enemy_stats["damage_total"] = 0
    enemy_stats["damage_champs"] = 0
    enemy_stats["damage_taken"] = 0
    enemy_stats["damage_mitigated"] = 0
    enemy_stats["lane_opponent_damage_total"] = 0
    enemy_stats["lane_opponent_gold"] = 0
    enemy_stats["lane_opponent_damage_champs"] = 0
    enemy_stats["lane_opponent_rank"] = ""

    player_ids = list(range(n_players))
    player_ids.remove(player_id)
    for ii in range(n_players):
        # Find ally players
        if teamId == match_data[str(game_id)]["participants"][ii]["teamId"] and ii != player_id:
            # If the participant was on your team, stick their info in ally stats
            ally_stats["names"].append(
                match_data[str(game_id)]["participantIdentities"][ii]["player"]["summonerName"])
            ally_stats["gold_earned"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "goldEarned"]
            ally_stats["damage_total"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "totalDamageDealt"]
            ally_stats["damage_champs"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "totalDamageDealtToChampions"]
            ally_stats["damage_taken"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "totalDamageTaken"]
            ally_stats["damage_mitigated"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "damageSelfMitigated"]

        # Find enemy players
        elif ii != player_id:
            enemy_stats["names"].append(
                match_data[str(game_id)]["participantIdentities"][ii]["player"]["summonerName"])
            enemy_stats["gold_earned"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "goldEarned"]
            enemy_stats["damage_total"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "totalDamageDealt"]
            enemy_stats["damage_champs"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "totalDamageDealtToChampions"]
            enemy_stats["damage_taken"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "totalDamageTaken"]
            enemy_stats["damage_mitigated"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "damageSelfMitigated"]

        # Find the player's lane opponent
        if (str(match_data[str(game_id)]["participants"][ii]["timeline"]["lane"]) == str(player_lane) and
            str(match_data[str(game_id)]["participants"][ii]["timeline"]["role"]) == str(player_role) and
            ii != player_id):
            opponent_id = ii

    return player_id, parsed_data, ally_stats, enemy_stats, opponent_id


def parse_data(config_info, match_data):
    parsed_data = {}
    parsed_data["n_matches"] = 0
    parsed_data["ally_stats"] = []
    parsed_data["enemy_stats"] = []

    game_ids = list(match_data.copy().keys())  # list of strings of match numbers (e.g. "1") from the match data

    for game_id in game_ids:
        # Get information for allies and enemeis, as well as the player's ID for the given match
        pid, parsed_data, ally_stats, enemy_stats, oid = find_player_id(config_info, match_data, game_id, parsed_data)

        parsed_data["ally_stats"].append(ally_stats)
        parsed_data["enemy_stats"].append(enemy_stats)

        parse_variable(match_data, parsed_data, "game_id", [game_id, "gameId"])
        parse_variable(match_data, parsed_data, "season", [game_id, "seasonId"])
        parse_variable(match_data, parsed_data, "timestamp", [game_id, "gameCreation"])
        parse_variable(match_data, parsed_data, "match_length", [game_id, "gameDuration"])
        parse_variable(match_data, parsed_data, "queue_type", [game_id, "queueId"])
        parse_variable(match_data, parsed_data, "map_id", [game_id, "mapId"])
        parse_variable(match_data, parsed_data, "game_mode", [game_id, "gameMode"])

        # Grab things from the player ID list entry
        parse_variable(match_data, parsed_data, "team", [game_id, "participants", pid,
                                                         "teamId"])
        parse_variable(match_data, parsed_data, "champion", [game_id, "participants", pid,
                                                             "championId"])
        parse_variable(match_data, parsed_data, "Your Rank", [game_id, "participants", pid,
                                                              "highestAchievedSeasonTier"])
        parse_variable(match_data, parsed_data, "summoner_spell_1", [game_id, "participants", pid,
                                                                     "spell1Id"])
        parse_variable(match_data, parsed_data, "summoner_spell_2", [game_id, "participants", pid,
                                                                     "spell2Id"])

        # Grab stats that are from the "timeline" block
        parse_variable(match_data, parsed_data, "role", [game_id, "participants", pid, "timeline",
                                                         "role"])
        parse_variable(match_data, parsed_data, "lane", [game_id, "participants", pid, "timeline",
                                                         "lane"])

        # Grab things from the "stats" block
        parse_variable(match_data, parsed_data, "Win/Loss Rate", [game_id, "participants", pid, "stats",
                                                                  "win"])
        parse_variable(match_data, parsed_data, "kills", [game_id, "participants", pid, "stats",
                                                          "kills"])
        parse_variable(match_data, parsed_data, "deaths",[game_id, "participants", pid, "stats",
                                                          "deaths"])
        parse_variable(match_data, parsed_data, "assists", [game_id, "participants", pid, "stats",
                                                            "assists"])
        parse_variable(match_data, parsed_data, "wards_placed", [game_id, "participants", pid, "stats",
                                                                 "wardsPlaced"])
        parse_variable(match_data, parsed_data, "wards_killed",[game_id, "participants", pid, "stats",
                                                                "wardsKilled"])
        parse_variable(match_data, parsed_data, "first_blood", [game_id, "participants", pid, "stats",
                                                                "firstBloodKill"])
        parse_variable(match_data, parsed_data, "first_blood_asst", [game_id, "participants", pid, "stats",
                                                                     "firstBloodAssist"])
        parse_variable(match_data, parsed_data, "gold_earned", [game_id, "participants", pid, "stats",
                                                                "goldEarned"])
        parse_variable(match_data, parsed_data, "damage_total", [game_id, "participants", pid, "stats",
                                                                 "totalDamageDealt"])
        parse_variable(match_data, parsed_data, "damage_champs", [game_id, "participants", pid, "stats",
                                                                  "totalDamageDealtToChampions"])
        parse_variable(match_data, parsed_data, "damage_taken", [game_id, "participants", pid, "stats",
                                                                 "totalDamageTaken"])
        parse_variable(match_data, parsed_data, "damage_mitigated", [game_id, "participants", pid, "stats",
                                                                     "damageSelfMitigated"])

        # Grab lane opponent stuff
        parse_variable(match_data, parsed_data, "lane_opponent_champion",
                       [game_id, "participants", oid, "championId"])
        parse_variable(match_data, parsed_data, "lane_opponent_damage_total",
                       [game_id, "participants", oid, "stats", "totalDamageDealt"])
        parse_variable(match_data, parsed_data, "lane_opponent_damage_champs",
                       [game_id, "participants", oid, "stats", "totalDamageDealtToChampions"])
        parse_variable(match_data, parsed_data, "lane_opponent_gold",
                       [game_id, "participants", oid, "stats", "goldEarned"])
        parse_variable(match_data, parsed_data, "lane_opponent_first_blood",
                       [game_id, "participants", oid, "stats", "firstBloodKill"])
        parse_variable(match_data, parsed_data, "lane_opponent_rank",
                       [game_id, "participants", oid, "highestAchievedSeasonTier"])


        # TODO add cs stuff (csd at each point in the game, etc.)
        # parse_variable(match_data, parsed_data, "cs",
        #                [game_id, "participants", pid, "timeline", "lane"])
        parsed_data["n_matches"] += 1

    parsed_data["summoner_name"] = config_info["SummonerName"]
    parsed_data["hours_played"] = 0  # the total hours played in the data set
    parsed_data["champion_name"] = []  # the pretty champion name
    parsed_data["Lane Opponent's Champion"] = []  # the pretty champion name
    parsed_data["teammates_unique"] = []  # a list of unique teammate names
    parsed_data["map_side"] = []  # red or blue side
    parsed_data["Role"] = []  # the player's role, formatted for display
    parsed_data["damage_total_frac"] = []  # player's fraction of total team damage
    parsed_data["damage_champs_frac"] = []  # player's fraction of team damage to champs
    parsed_data["damage_taken_frac"] = []  # player's fraction of team damage taken

    for ii in range(parsed_data["n_matches"]):
        parsed_data["hours_played"] += int(parsed_data["match_length"][ii]) / 3600
        parsed_data["champion_name"].append(config_info["ChampionLookup"][str(parsed_data["champion"][ii])])

        try:
            parsed_data["Lane Opponent's Champion"].append(
                config_info["ChampionLookup"][str(parsed_data["lane_opponent_champion"][ii])])
        except:
            parsed_data["Lane Opponent's Champion"].append("Unknown")

        parsed_data["teammates_unique"] += parsed_data["ally_stats"][ii]["names"]

        if parsed_data["team"][ii] == 100:
            parsed_data["map_side"].append("Blue")
        elif parsed_data["team"][ii] == 200:
            parsed_data["map_side"].append("Red")
        else:
            parsed_data["map_side"].append("Unknown")

        # Determine the role (neatly formatted)
        if parsed_data["lane"][ii].lower() == "middle" or parsed_data["lane"][ii].lower() == "mid":
            parsed_data["Role"].append("Mid")
        elif parsed_data["lane"][ii].lower() == "top":
            parsed_data["Role"].append("Top")
        elif parsed_data["lane"][ii].lower() == "jungle":
            parsed_data["Role"].append("Jungle")
        elif parsed_data["lane"][ii].lower() == "bottom" or parsed_data["lane"][ii].lower() == "bot":
            if "carry" in parsed_data["role"][ii].lower():
                parsed_data["Role"].append("Bot")
            elif "sup" in parsed_data["role"][ii].lower():
                parsed_data["Role"].append("Support")
            else:
                parsed_data["Role"].append("Bottom (Other)")
        else:
            parsed_data["Role"].append("Unknown")


        parsed_data["damage_total_frac"].append(parsed_data["damage_total"][ii] /
                                                parsed_data["ally_stats"][ii]["damage_total"])
        parsed_data["damage_champs_frac"].append(parsed_data["damage_champs"][ii] /
                                                 parsed_data["ally_stats"][ii]["damage_taken"])
        parsed_data["damage_taken_frac"].append(parsed_data["damage_taken"][ii] /
                                                parsed_data["ally_stats"][ii]["damage_taken"])

    parsed_data["hours_played"] = round(parsed_data["hours_played"], 1)
    parsed_data["teammates_unique"] = sorted(list(set(parsed_data["teammates_unique"])), key=str.lower)

    parsed_data["winrate"] = 0
    if len(parsed_data["Win/Loss Rate"]) > 0:
        parsed_data["winrate"] = sum(parsed_data["Win/Loss Rate"]) / len(parsed_data["Win/Loss Rate"])
    else:
        parsed_data["winrate"] = 0

    parsed_data["y_vars"] = sorted([
        "Win/Loss Rate", "CS Differential, <10 mins", "Gold Differential"
    ])
    parsed_data["x_vars"] = sorted([
        "Role", "Map Side", "Lane Opponent's Champion", "Champion Played"
    ])

    return parsed_data

testing=0

if testing:
    import json
    with open("ParsedData.json", "r") as file:
        parsed_data = json.load(file)
    with open("MatchData_jasparagus.json", "r") as file:
        match_data = json.load(file)

    pid = 0
    print(json.dumps(match_data["2626980870"]["participants"][pid], indent=4))



def filter_matches(config_info, parsed_data, games_to_remove, config_key, filter_keys, choices_list):
    """
    :param config_info: configuration info for the entire app, same as everywhere else
    :param parsed_data: the parsed match data
    :param games_to_remove: a list of strings whose entries are game_id values to filter out of match_data
    :param config_key: string; filter's corresponding key from the config file
    :param filter_keys: list of strings; key(s) in parsed_data that should be checked against the choices_list
    :param choices_list: list of strings; the options the user chose in the GUI
    :return:
    """

    print("Running filter_matches with ", parsed_data["n_matches"], "matches; filtering for ", config_key)
    print("    Corresponding config_info dictionary: ", config_info[config_key])
    print("    Keys to check through in parsed_data: ", filter_keys)
    print("    List of choices from the GUI", str(choices_list))

    if len(choices_list) == 0:
        print("        No active choices, skipping this filter.")
    else:
        for ii in range(parsed_data["n_matches"]):
            keep = 0  # prep a variable for whether or not to keep this match
            for choice in choices_list:  # look over each acceptable choice
                for parsed_key in filter_keys:  # check it the corresponding entry in parsed_data
                    print(
                        "        Comparing GUI choice (" + str(config_info[config_key][choice]) +
                        ") with data for this game (" + str(parsed_data[parsed_key][ii]) +
                        "), game ID = ", parsed_data["game_id"][ii]
                    )

                    # if str(config_info[config_key][choice]).lower() in str(parsed_data[parsed_key][ii]).lower():
                    keylist = config_info[config_key][choice].split("&&")
                    for config_subkey in keylist:
                        if str(config_subkey).lower() == str(parsed_data[parsed_key][ii]).lower():
                            print("        Filter applies; keeping the match")
                            keep += 1
            if keep == 0:
                games_to_remove.append(str(parsed_data["game_id"][ii]))

    # Remove duplicates and sort the games to be removed
    games_to_remove = sorted(list(set(games_to_remove)))
    print("            Will remove the following ", str(len(games_to_remove)), " games: ", games_to_remove)

    return games_to_remove


def filter_remakes(parsed_data, games_to_remove):
    """ Filter out remakes (games with length < 6 minutes) """

    for ii in range(parsed_data["n_matches"]):
        try:
            if int(parsed_data["match_length"][ii]) < 360:
                games_to_remove.append(str(parsed_data["game_id"][ii]))
        except:
            games_to_remove.append(str(parsed_data["game_id"][ii]))

    games_to_remove = sorted(list(set(games_to_remove)))

    return games_to_remove


def filter_recency(parsed_data, games_to_remove, days_to_keep):
    """ Filter for recent matches, where match_filter is a number of matches to keep """
    if int(days_to_keep) > 0:
        oldest_timestamp = int(time.time())*1000 - (int(days_to_keep) * 24 * 60 * 60 * 1000)

        nrem = 0
        for ii in range(parsed_data["n_matches"]):
            try:
                if int(parsed_data["timestamp"][ii]) < oldest_timestamp:
                    games_to_remove.append(str(parsed_data["game_id"][ii]))
                    nrem += 1
            except:
                games_to_remove.append(str(parsed_data["game_id"][ii]))
                nrem += 1

        games_to_remove = sorted(list(set(games_to_remove)))
        print("removing due to oldness:", nrem)

    return games_to_remove



















import types
import time


def get_pid(config_info, match):
    # Gets the player's ID for the match
    pid = "Unknown"
    n_players = len(match["participantIdentities"])
    for ii in range(n_players):
        if (str(match["participantIdentities"][ii]["player"]["accountId"]) == str(config_info["AccountID"])):
            pid = ii
    return pid


def get_role_pretty(config_info, match):

    pid = get_pid(config_info, match)

    try:
        role = str(match["participants"][pid]["timeline"]["role"])
        lane = str(match["participants"][pid]["timeline"]["lane"])
    except:
        role = "Unknown"
        lane = "Unknown"

    if lane.lower() == "middle" or lane.lower() == "mid":
        role_pretty = "Middle"
    elif lane.lower() == "top":
        role_pretty = "Top"
    elif lane.lower() == "jungle" or role.lower() == "jungle":
        role_pretty = "Jungle"
    elif lane.lower() == "bottom" or lane.lower() == "bot":
        if "carry" in role.lower():
            role_pretty = "Bottom/ADC"
        elif "sup" in role.lower():
            role_pretty = "Support"
        else:
            role_pretty = "Bottom (Other)"
    else:
        role_pretty = "Unknown"

    return role_pretty


def get_kda(config_info, match):
    pid = get_pid(config_info, match)

    kills = match["participants"][pid]["stats"]["kills"]
    deaths = match["participants"][pid]["stats"]["deaths"]
    assists = match["participants"][pid]["stats"]["assists"]

    try:
        kda = str(round(
            (int(kills) + int(assists))
            / int(deaths)
        , 1))
    except ZeroDivisionError:
        kda = "Perfect"
    except TypeError:
        kda = "Unknown"

    return kda


def get_oid(config_info, match):
    # Gets the player's ID for the match
    pid = get_pid(config_info, match)
    oid = "Unknown"
    n_players = len(match["participantIdentities"])

    lane = str(match["participants"][pid]["timeline"]["lane"])
    role = str(match["participants"][pid]["timeline"]["role"])

    for ii in range(n_players):
        if (str(match["participants"][ii]["timeline"]["lane"]) == str(lane) and
                    str(match["participants"][ii]["timeline"]["role"]) == str(role) and ii != pid):
            oid = ii

    return oid


def get_team(config_info, match):
    team = "Unknown"
    n_players = len(match["participantIdentities"])
    for ii in range(n_players):
        if (str(match["participantIdentities"][ii]["player"]["accountId"]) == str(config_info["AccountID"])):
            team = match["participants"][ii]["teamId"]
    return team


def get_allies_enemies(config_info, match):
    # gets allies using pid or enemies using oid
    print("parse ally/enemy function not built")
    pid = get_pid(config_info, match)
    print(pid)

    return


def get_teammate_quantity():
    return


def get_teammate_names():
    return


def clean_game_duration(config_info, game_duration):
    match_length = round(float(game_duration) / 3600, 2)
    return match_length


def clean_team(config_info, team):
    if int(team) == 100:
        map_side = "Blue"
    elif int(team) == 200:
        map_side = "Red"
    else:
        map_side = "Other"
    return map_side


def clean_win_loss(config_info, win_loss):
    if win_loss == 1 or win_loss == "True":
        win_loss_clean = 1
    elif win_loss == 0 or win_loss == "False":
        win_loss_clean = 0
    else:
        win_loss_clean = "Unknown"
    return win_loss_clean


def clean_season(config_info, season_id):
    try:
        season_clean = config_info["seasons.gameconstants"][str(season_id)]
    except:
        season_clean = "Unknown"
    return season_clean


def clean_queue(config_info, queue_id):
    queue_clean = "Unknown"
    try:
        for queues_key in list(config_info["queues.gameconstants"].keys()):
            queues_list = queues_key.split("&&")
            if str(queue_id) in queues_list:
                queue_clean = config_info["queues.gameconstants"][queues_key]
    except:
        queue_clean = "Unknown"
    return queue_clean


def clean_map(config_info, map_id):
    try:
        map_clean = config_info["maps.gameconstants"][str(map_id)]
    except:
        map_clean = "Unknown"
    return map_clean


def clean_champion(config_info, champ_id):
    try:
        champ_name = config_info["ChampionLookup"][str(champ_id)]
    except:
        champ_name = "Unknown"
    return champ_name


def clean_summoner_spell(config_info, spell_id):
    try:
        champ_name = config_info["SummonerSpellLookup"][str(spell_id)]
    except:
        champ_name = "Unknown"
    return champ_name


class Var:
    # A list of all instances of Var
    names = []
    # A list of Var instances to be plotted on the x (labels) axis in a bar chart
    x_vars = []
    # A list of Var instances to be plotted on the y (numeric) axis in a bar chart
    y_vars = []
    # A list of Var instances to be plotted in a stacked histogram of wins and losses
    h_vars = []
    # A list of Var instances (like x instances) but for which plotting requires special attention
    s_vars = []

    def __init__(self, name, types, path, cleanup=None):
        self.name = name
        self.types = types
        self.path = path
        self.cleaup = cleanup

        # Update the lists of variables and their types as applicable
        self.names.append(self.name)
        self.names = sorted(self.names)

        if "x" in str(types).lower():
            self.x_vars.append(self.name)
        if "y" in str(types).lower():
            self.y_vars.append(self.name)
        if "h" in str(types).lower():
            self.h_vars.append(self.name)
        if "s" in str(types).lower():
            self.s_vars.append(self.name)

        return

    def extract(self, config_info, match):
        # call this once or twice (e.g. for win/loss and champion) per match to get the appropriate data from the match
        self.value = match.copy()

        # Iteratively work through the list, taking the appropriate type of action as determined by the element
        for step in self.path:
            try:
                if type(step) is types.FunctionType:
                    if len(self.path) == 1:
                        # If there is only one step, it is a "get" function. Run it.
                        self.value = step(config_info, match)
                    elif step != self.path[-1]:
                        # If it is not the last step, carry it out and use result as a key
                        temp_step = step(config_info, match)
                        self.value = self.value[temp_step]
                    elif step == self.path[-1]:
                        # if it is the last step, run the parse function (cleanup)
                        self.value = step(config_info, self.value)
                else:
                    # otherwise, it is a normal key and should be used to access the next dictionary entry
                    self.value = self.value[step]
            except:
                self.value = "Unknown"
        return self.value

    @classmethod
    def create_list(cls, config_info, match_data, var_1_name, var_2_name, filters, oldest_match_days):
        # Get a list of game IDs from the match list and sort them chronologically
        game_ids = sorted(list(match_data.copy().keys()))

        # Prepare the lists, then loop over each game and extract the variable.
        var_1_list = []
        var_2_list = []

        for game_id in game_ids:
            # Grab hold of the match getting checked
            match = match_data.copy()[str(game_id)]
            remove = 0  # determines if a match will be removed (if >0)
            n_filters_skipped = 0

            for filter in filters:
                if len(filter.choices_list) != 0:
                    keys_failed = 0
                    for filter_key in filter.filter_keys:
                        # See if the match (after parsing) is missing all the choices made in the GUI
                        if (str(Vars[Var.names.index(filter_key)].extract(config_info, match)) not in
                                filter.choices_list):
                            keys_failed += 1
                    # See if the game failed every key check (if so, exclude it)
                    if keys_failed == len(filter.filter_keys):
                        remove += 1
                else:
                    n_filters_skipped += 1

            # Remove the match if it's too old or was a remake
            if int(match["gameCreation"]) < int((time.time() * 1000) - (int(oldest_match_days) * 24 * 60 * 60 * 1000)):
                if oldest_match_days != 0:
                    remove += 10000
            if int(match["gameDuration"]) < 360:
                remove += 1000

            # If the match survived the filters, add the data for the given match to the list!
            if remove == 0:
                var_1_list.append(Vars[Var.names.index(var_1_name)].extract(config_info, match))
                var_2_list.append(Vars[Var.names.index(var_2_name)].extract(config_info, match))

        return var_1_list, var_2_list


Vars = [
    Var("Game ID", "", ["gameId"]),
    Var("Timestamp", "", ["gameCreation"]),
    Var("Queue Type", "x", ["queueId", clean_queue]),
    Var("Map", "x", ["mapId", clean_map]),
    Var("Game Mode", "", ["gameMode"]),

    Var("Match Length", "y", ["gameDuration", clean_game_duration]),
    Var("Season", "x", ["seasonId", clean_season]),

    Var("Map Side", "x", ["participants", get_pid, "teamId", clean_team]),
    Var("Rank", "x", ["participants", get_pid, "highestAchievedSeasonTier"]),
    Var("Champion", "x", ["participants", get_pid, "championId", clean_champion]),
    Var("Summoner Spell 1", "x", ["participants", get_pid, "spell1Id", clean_summoner_spell]),
    Var("Summoner Spell 2", "x", ["participants", get_pid, "spell2Id", clean_summoner_spell]),

    Var("KDA", "x", [get_kda]),
    Var("Kills", "xy", ["participants", get_pid, "stats", "kills"]),
    Var("Deaths", "xy", ["participants", get_pid, "stats", "deaths"]),
    Var("Assists", "xy", ["participants", get_pid, "stats", "assists"]),
    Var("Win/Loss Rate", "y", ["participants", get_pid, "stats", "win", clean_win_loss]),
    Var("Wards Placed", "xy", ["participants", get_pid, "stats", "wardsPlaced"]),
    Var("Wards Killed", "xy", ["participants", get_pid, "stats", "wardsKilled"]),
    Var("Vision Wards Bought", "xy", ["participants", get_pid, "stats", "visionWardsBoughtInGame"]),
    Var("First Blood", "xy", ["participants", get_pid, "stats", "firstBloodKill"]),
    # TODO: figure out first blood assists (they're not working)
    Var("First Blood (Assisted)", "xy", ["participants", get_pid, "stats", "firstBloodAssist"]),
    Var("First Tower", "xy", ["participants", get_pid, "stats", "firstTowerKill"]),
    Var("First Tower (Assisted)", "xy", ["participants", get_pid, "stats", "firstTowerAssist"]),
    Var("Gold Earned", "xy", ["participants", get_pid, "stats", "goldEarned"]),
    Var("CS (Total)", "xy", ["participants", get_pid, "stats", "totalMinionsKilled"]),
    Var("Jungle CS (Your Jungle)", "yh", ["participants", get_pid, "stats", "neutralMinionsKilledTeamJungle"]),
    Var("Jungle CS (Enemy Jungle)", "yh", ["participants", get_pid, "stats", "neutralMinionsKilledEnemyJungle"]),
    Var("Damage Dealt (Total)", "yh", ["participants", get_pid, "stats", "totalDamageDealt"]),
    Var("Damage Dealt (Total, Champions)", "yh", ["participants", get_pid, "stats", "totalDamageDealtToChampions"]),
    Var("Damage Dealt (Physical)", "yh", ["participants", get_pid, "stats", "physicalDamageDealt"]),
    Var("Damage Dealt (Physical, Champs)", "yh", ["participants", get_pid, "stats", "physicalDamageDealtToChampions"]),
    Var("Damage Dealt (Magic)", "yh", ["participants", get_pid, "stats", "magicDamageDealt"]),
    Var("Damage Dealt (Magic, Champs)", "yh", ["participants", get_pid, "stats", "magicDamageDealtToChampions"]),
    Var("Damage Taken", "yh", ["participants", get_pid, "stats", "totalDamageTaken"]),
    Var("Damage Mitigated (Self)", "yh", ["participants", get_pid, "stats", "damageSelfMitigated"]),
    Var("Longest Time Alive", "yh", ["participants", get_pid, "stats", "longestTimeSpentLiving"]),

    Var("Role", "x", [get_role_pretty]),
    Var("Lane Ugly", "", ["participants", get_pid, "timeline", "lane"]),
    Var("Role Ugly", "", ["participants", get_pid, "timeline", "role"]),

    Var("CS/min (0 min -> 10 min)", "yh", ["participants", get_pid, "timeline", "creepsPerMinDeltas", "0-10"]),
    Var("CS/min (10 min -> 20 min)", "yh", ["participants", get_pid, "timeline", "creepsPerMinDeltas", "10-20"]),
    Var("CS/min (20 min -> 30 min)", "yh", ["participants", get_pid, "timeline", "creepsPerMinDeltas", "20-30"]),
    Var("CS/min (30 min -> Game End)", "yh", ["participants", get_pid, "timeline", "creepsPerMinDeltas", "30-end"]),
    Var("CS/m Diff. (0 min -> 10 min)", "yh", ["participants", get_pid, "timeline", "csDiffPerMinDeltas", "0-10"]),
    Var("CS/m Diff. (10 min -> 20 min)", "yh", ["participants", get_pid, "timeline", "csDiffPerMinDeltas", "10-20"]),
    Var("CS/m Diff. (20 min -> 30 min)", "yh", ["participants", get_pid, "timeline", "csDiffPerMinDeltas", "20-30"]),
    Var("CS/m Diff. (30 min -> Game End)", "yh", ["participants", get_pid, "timeline", "csDiffPerMinDeltas", "30-end"]),

    Var("Gold/min (0 min -> 10 min)", "yh", ["participants", get_pid, "timeline", "goldPerMinDeltas", "0-10"]),
    Var("Gold/min (10 min -> 20 min)", "yh", ["participants", get_pid, "timeline", "goldPerMinDeltas", "10-20"]),
    Var("Gold/min (20 min -> 30 min)", "yh", ["participants", get_pid, "timeline", "goldPerMinDeltas", "20-30"]),
    Var("Gold/min (30 min -> Game End)", "yh", ["participants", get_pid, "timeline", "goldPerMinDeltas", "30-end"]),

    Var("XP/min (0 min -> 10 min)", "yh", ["participants", get_pid, "timeline", "xpPerMinDeltas", "0-10"]),
    Var("XP/min (10 min -> 20 min)", "yh", ["participants", get_pid, "timeline", "xpPerMinDeltas", "10-20"]),
    Var("XP/min (20 min -> 30 min)", "yh", ["participants", get_pid, "timeline", "xpPerMinDeltas", "20-30"]),
    Var("XP/min (30 min -> Game End)", "yh", ["participants", get_pid, "timeline", "xpPerMinDeltas", "30-end"]),
    Var("XP/m Diff. (0 min -> 10 min)", "yh", ["participants", get_pid, "timeline", "xpDiffPerMinDeltas", "0-10"]),
    Var("XP/m Diff. (10 min -> 20 min)", "yh", ["participants", get_pid, "timeline", "xpDiffPerMinDeltas", "10-20"]),
    Var("XP/m Diff. (20 min -> 30 min)", "yh", ["participants", get_pid, "timeline", "xpDiffPerMinDeltas", "20-30"]),
    Var("XP/m Diff. (30 min -> Game End)", "yh", ["participants", get_pid, "timeline", "xpDiffPerMinDeltas", "30-end"]),

    Var("Lane Opponent Champion", "x", ["participants", get_oid, "championId", clean_champion]),
    Var("Lane Opponent First Blood", "y", ["participants", get_oid, "stats", "firstBloodKill"]),
    Var("Lane Opponent Rank", "x", ["participants", get_oid, "highestAchievedSeasonTier"]),

    # TODO: add these "s" type filters!
    Var("Teammates (Number of)", "s", [get_teammate_quantity]),
    Var("Teammates (By Name)", "s", [get_teammate_names]),
    Var("Items (By Name)", "s", [get_teammate_names]),
]

# This isn't actually a thing, but I need to make it one... gotta compute stuff like total time played, etc.!
Not_Made_Yet = {
    # TODO: generate all of these secondary functions
    "Total Hours Played": [sum, []],
    "Unique Champions": [],
    "Damage Fraction AND OTHERS": [],
    "Friends": [],
    "Premade Party Size": [],
    "Most Kills": "",
    "Most Deaths": "",
    "Most Assists": "",
}


testing = 0

if testing:
    import json
    with open("Configuration.json", "r") as file:
        config_info = json.load(file)
    with open("MatchData_" + config_info["SummonerName"] + ".json", "r") as file:
        match_data = json.load(file)
    match = match_data["2626980870"]
    Vars[Var.names.index("Champion")].extract(config_info, match)


# def parse_match_data(config_info, match_data, parsed_data):
#     """ Converts raw match data into a set of (mostly) lists for analysis """
#     summoner_name = config_info["SummonerName"]
#     n_matches = len(match_data)
#
#     season = []
#     timestamp = []
#     queue_type = []
#     win_lose = []
#     match_lengths = []
#     summ_num = []
#     teammates = {}
#     enemies = {}
#     champ = []
#     role = []
#     map_side = []
#     kills = []
#     deaths = []
#     assists = []
#     kda = []
#     damage_total = []
#     damage_to_champs = []
#     damage_total_frac = []
#     damage_to_champs_frac = []
#     damage_taken = []
#     damage_taken_frac = []
#     gold = []
#     gold_frac = []
#     visionscore = []
#     cs = []
#     csm_at_10 = []
#     csmd_at_10 = []
#     csm_at_20 = []
#     csmd_at_20 = []
#     csm_at_30 = []
#     csmd_at_30 = []
#     csm_aft_30 = []
#     csmd_aft_30 = []
#     wards = []
#     wards_killed = []
#
#     for match_index in range(n_matches):
#         print(match_index)
#         ii = str(match_index+1)
#         season.append(match_data[ii]["seasonId"])
#         queue_type.append(match_data[ii]["queueId"])
#         timestamp.append(match_data[ii]["gameCreation"])
#         match_lengths.append(match_data[ii]["gameDuration"]/60)
#         other_players = []
#         others_damage_total = []
#         others_damage_to_champs = []
#         others_gold = []
#         others_damage_taken = []
#         # loop over the players in the game and look for the target player
#         for pp in range(10):
#             if (str(match_data[ii]["participantIdentities"][pp]["player"]["accountId"])
#                     == config_info["AccountID"]):
#                 """ This case gathers data for the summoner using the app. """
#                 summ_num.append(pp)
#                 damage_total.append(
#                     match_data[ii]["participants"][pp]["stats"]["totalDamageDealt"])
#                 damage_to_champs.append(
#                     match_data[ii]["participants"][pp]["stats"]["totalDamageDealtToChampions"])
#                 damage_taken.append(
#                     match_data[ii]["participants"][pp]["stats"]["totalDamageTaken"])
#                 gold.append(match_data[ii]["participants"][pp]["stats"]["goldEarned"])
#                 win_lose.append(match_data[ii]["participants"][pp]["stats"]["win"])
#                 """ Some quick parsing of the lanes and roles to make it look nicer"""
#                 lane = match_data[ii]["participants"][pp]["timeline"]["lane"]
#                 if lane == "MIDDLE":
#                     lane = "MID"
#                 if lane == "BOTTOM":
#                     lane = "BOT"
#                 if lane == "JUNGLE":
#                     lane = "JUNGLE"
#                 temp_role = match_data[ii]["participants"][pp]["timeline"]["role"]
#                 if temp_role == "DUO_CARRY":
#                     temp_role = "CARRY"
#                 if temp_role == "DUO_SUPPORT":
#                     temp_role = "SUPPORT"
#                 role_string = lane + " \n" + temp_role
#                 if temp_role == "NONE":
#                     role_string = lane
#                 role.append(role_string)
#
#                 """ teamId: 100 is blue side; 200 is red side """
#                 map_side.append(match_data[ii]["participants"][pp]["teamId"])
#                 kills.append(match_data[ii]["participants"][pp]["stats"]["kills"])
#                 deaths.append(match_data[ii]["participants"][pp]["stats"]["deaths"])
#                 assists.append(match_data[ii]["participants"][pp]["stats"]["assists"])
#                 try:
#                     visionscore.append(match_data[ii]["participants"][pp]["stats"]["visionScore"])
#                 except:
#                     visionscore.append("")
#                 cs.append(match_data[ii]["participants"][pp]["stats"]["totalMinionsKilled"])
#                 try:
#                     csm_at_10.append(
#                         match_data[ii]["participants"][pp]["timeline"]["creepsPerMinDeltas"]
#                         ["zeroToTen"]
#                     )
#                 except:
#                     csm_at_10.append("None")
#                 try:
#                     csm_at_20.append(
#                         match_data[ii]["participants"][pp]["timeline"]["creepsPerMinDeltas"]
#                         ["tenToTwenty"]
#                     )
#                 except:
#                     csm_at_20.append("None")
#                 try:
#                     csm_at_30.append(
#                         match_data[ii]["participants"][pp]["timeline"]["creepsPerMinDeltas"]
#                         ["twentyToThirty"]
#                     )
#                 except:
#                     csm_aft_30.append("None")
#                 try:
#                     csm_aft_30.append(
#                         match_data[ii]["participants"][pp]["timeline"]["creepsPerMinDeltas"]
#                         ["thirtyToEnd"]
#                     )
#                 except:
#                     csm_at_10.append("None")
#
#                 # match_data[ii]["participants"][pp]["timeline"]["creepsPerMinDeltas"]["zeroToTen"]
#                 # CSDAt10(iii) = match_data(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.zeroToTen;
#                 # CSDAt20(iii) = match_data(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.tenToTwenty;
#                 # CSDAt30(iii) = match_data(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.twentyToThirty;
#                 # CSDtoEnd(iii) = match_data(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.thirtyToEnd;
#                 wards.append(match_data[ii]["participants"][pp]["stats"]["wardsPlaced"])
#                 wards_killed.append(match_data[ii]["participants"][pp]["stats"]["wardsKilled"])
#                 try:
#                     kda.append((kills[match_index]+assists[match_index])/deaths[match_index])
#                 except:
#                     kda.append("perfect")
#             else:
#                 """ This case builds temporary teammate variables that are overwritten for each new match. """
#                 other_players.append(match_data[ii]["participantIdentities"][pp]["player"]["summonerName"])
#                 others_damage_total.append(
#                     match_data[ii]["participants"][pp]["stats"]["totalDamageDealt"])
#                 others_damage_to_champs.append(
#                     match_data[ii]["participants"][pp]["stats"]["totalDamageDealtToChampions"])
#                 others_damage_taken.append(
#                     match_data[ii]["participants"][pp]["stats"]["totalDamageTaken"])
#                 others_gold.append(match_data[ii]["participants"][pp]["stats"]["goldEarned"])
#         # Team 1
#         if pp <= 4:
#             teammates[ii] = other_players[0:4]
#             enemies[ii] = other_players[4:9]
#             damage_total_frac.append(damage_total[match_index]/(damage_total[match_index]
#                                                        + 1 + sum(others_damage_total[0:4])))
#             damage_to_champs_frac.append(damage_to_champs[match_index]/(damage_to_champs[match_index]
#                                                                + 1 + sum(others_damage_to_champs[0:4])))
#             damage_taken_frac.append(damage_taken[match_index]/(damage_taken[match_index]
#                                                        + 1 + sum(others_damage_taken[0:4])))
#             gold_frac.append(gold[match_index]/(gold[match_index] + 1 + sum(others_gold[0:4])))
#         # Team 2
#         elif pp >= 5:
#             teammates[ii] = other_players[5:9]
#             enemies[ii] = other_players[0:5]
#             damage_total_frac.append(damage_total[match_index]/(damage_total[match_index]
#                                                        + 1 + sum(others_damage_total[5:9])))
#             damage_to_champs_frac.append(damage_to_champs[match_index]/(damage_to_champs[match_index]
#                                                                + 1 + sum(others_damage_to_champs[5:9])))
#             damage_taken_frac.append(damage_taken[match_index]/(damage_taken[match_index]
#                                                        + 1 + sum(others_damage_taken[5:9])))
#             gold_frac.append(gold[match_index]/(gold[match_index] + 1 + sum(others_gold[5:9])))
#         champ.append(
#             config_info["ChampionDictionary"][str(match_data[ii]["participants"][pp]["championId"])]
#         )
#     season_unique = sorted(list(set(season)))
#     queue_types = sorted(list(set(queue_type)))
#     avg_wr = sum(win_lose) / len(win_lose)
#     champs_played = sorted(list(set(champ)))
#     roles = sorted(list(set(role)))
#
#     return {
#         "summoner_name": summoner_name,
#         "season_unique": season_unique,
#         "season": season,
#         "queue_type": queue_type,
#         "queue_types": queue_types,
#         "win_lose": win_lose,
#         "avg_wr": avg_wr,
#         "timestamp": timestamp,
#         "match_lengths": match_lengths,
#         "teammates": teammates,
#         "enemies": enemies,
#         "champ": champ,
#         "champs_played": champs_played,
#         "role": role,
#         "roles": roles,
#         "map_side": map_side,
#         "kills": kills,
#         "deaths": deaths,
#         "assists": assists,
#         "kda": kda,
#         "damage_total": damage_total,
#         "damage_to_champs": damage_to_champs,
#         "damage_total_frac": damage_total_frac,
#         "damage_to_champs_frac": damage_to_champs_frac,
#         "damage_taken": damage_taken,
#         "damage_taken_frac": damage_taken_frac,
#         "gold": gold,
#         "gold_frac": gold_frac,
#         "cs": cs,
#         "csm_at_10": csm_at_10,
#         "csmd_at_10": csmd_at_10,
#         "csm_at_20": csm_at_20,
#         "csmd_at_20": csmd_at_20,
#         "csm_at_30": csm_at_30,
#         "csmd_at_30": csmd_at_30,
#         "csm_aft_30": csm_aft_30,
#         "csmd_aft_30": csmd_aft_30,
#         "wards": wards,
#         "wards_killed": wards_killed,
#     }
