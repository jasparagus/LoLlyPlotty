def parse_variable(match_data, parsed_data, variable_name, key_list):
    """
    Creates an entry in the parsed_match_data dictionary under key "var_name" for the property at "json_path"   :param config_info:
    :param match_data: match_data dictionary
    :param variable_name: key name to use for the new
    :param key_list: list of keys, in order, where the data is located in the match_data dictionary
    :return:
    """
    variable_name = variable_name.replace(" ","_")
    value = match_data.copy()

    # Extract the nested value from the list of keys
    try:
        for key in key_list:
            value = value[key]
    except:
        value = ""

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
    n_players = len(match_data[str(game_id)]["participantIdentities"])
    ally_stats = {}
    enemy_stats = {}

    for ii in range(n_players):
        if (str(match_data[str(game_id)]["participantIdentities"][ii]["player"]["accountId"]) ==
                str(config_info["AccountID"])):
            player_id = ii
            teamId = match_data[str(game_id)]["participants"][ii]["teamId"]

    ally_stats["names"] = []
    ally_stats["gold_earned"] = 0
    ally_stats["damage_dealt"] = 0
    ally_stats["damage_champs"] = 0
    ally_stats["damage_taken"] = 0
    ally_stats["damage_mitigated"] = 0

    enemy_stats["names"] = []
    enemy_stats["gold_earned"] = 0
    enemy_stats["damage_dealt"] = 0
    enemy_stats["damage_champs"] = 0
    enemy_stats["damage_taken"] = 0
    enemy_stats["damage_mitigated"] = 0

    player_ids = list(range(n_players))
    player_ids.remove(player_id)
    for ii in range(n_players):
        # TODO: implement "highestAchievedSeasonTier" average for allies and enemies
        if teamId == match_data[str(game_id)]["participants"][ii]["teamId"] and ii != player_id:
            ally_stats["names"].append(
                match_data[str(game_id)]["participantIdentities"][ii]["player"]["summonerName"])
            ally_stats["gold_earned"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "goldEarned"]
            ally_stats["damage_dealt"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "totalDamageDealt"]
            ally_stats["damage_champs"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "totalDamageDealtToChampions"]
            ally_stats["damage_taken"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "totalDamageTaken"]
            ally_stats["damage_mitigated"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "damageSelfMitigated"]

        elif ii != player_id:
            enemy_stats["names"].append(
                match_data[str(game_id)]["participantIdentities"][ii]["player"]["summonerName"])
            enemy_stats["gold_earned"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "goldEarned"]
            enemy_stats["damage_dealt"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "totalDamageDealt"]
            enemy_stats["damage_champs"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "totalDamageDealtToChampions"]
            enemy_stats["damage_taken"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "totalDamageTaken"]
            enemy_stats["damage_mitigated"] += match_data[str(game_id)]["participants"][ii]["stats"][
                "damageSelfMitigated"]

        elif ii == player_id:
            parse_variable(match_data, parsed_data, "gold_earned",
                           [str(game_id), "participants", ii, "stats", "goldEarned"])
            parse_variable(match_data, parsed_data, "damage_dealt",
                           [str(game_id), "participants", ii, "stats", "totalDamageDealt"])
            parse_variable(match_data, parsed_data, "damage_champs",
                           [str(game_id), "participants", ii, "stats", "totalDamageDealtToChampions"])
            parse_variable(match_data, parsed_data, "damage_taken",
                           [str(game_id), "participants", ii, "stats", "totalDamageTaken"])
            parse_variable(match_data, parsed_data, "damage_mitigated",
                           [str(game_id), "participants", ii, "stats", "damageSelfMitigated"])

    return player_id, parsed_data, ally_stats, enemy_stats


def parse_data(config_info, match_data):
    # Note: parse variable names must not include spaces
    parsed_data = {}
    parsed_data["ally_stats"] = []
    parsed_data["enemy_stats"] = []

    game_ids = list(match_data.copy().keys())  # list of strings of match numbers (e.g. "1") from the match data

    for game_id in game_ids:
        # Get information for allies and enemeis, as well as the player's ID for the given match
        pid, parsed_data, ally_stats, enemy_stats = find_player_id(config_info, match_data, game_id, parsed_data)

        parsed_data["ally_stats"].append(ally_stats)
        parsed_data["enemy_stats"].append(enemy_stats)

        parse_variable(match_data, parsed_data, "game_id", [game_id, "gameId"])
        parse_variable(match_data, parsed_data, "season", [game_id, "seasonId"])
        parse_variable(match_data, parsed_data, "timestamp", [game_id, "gameCreation"])
        parse_variable(match_data, parsed_data, "match_length", [game_id, "gameDuration"])
        parse_variable(match_data, parsed_data, "queue_type", [game_id, "queueId"])
        parse_variable(match_data, parsed_data, "map_id", [game_id, "mapId"])
        parse_variable(match_data, parsed_data, "game_mode", [game_id, "gameMode"])
        parse_variable(match_data, parsed_data, "team",
                       [game_id, "participants", pid, "teamId"])
        parse_variable(match_data, parsed_data, "role",
                       [game_id, "participants", pid, "timeline", "role"])
        parse_variable(match_data, parsed_data, "lane",
                       [game_id, "participants", pid, "timeline", "lane"])
        parse_variable(match_data, parsed_data, "champion",
                       [game_id, "participants", pid, "championId"])
        parse_variable(match_data, parsed_data, "win_lose",
                       [game_id, "participants", pid, "stats", "win"])
        parse_variable(match_data, parsed_data, "kills",
                       [game_id, "participants", pid, "stats", "kills"])
        parse_variable(match_data, parsed_data, "deaths",
                       [game_id, "participants", pid, "stats", "deaths"])
        parse_variable(match_data, parsed_data, "assists",
                       [game_id, "participants", pid, "stats", "assists"])
        parse_variable(match_data, parsed_data, "wards_placed",
                       [game_id, "participants", pid, "stats", "wardsPlaced"])
        parse_variable(match_data, parsed_data, "wards_killed",
                       [game_id, "participants", pid, "stats", "wardsKilled"])
        parse_variable(match_data, parsed_data, "first_blood",
                       [game_id, "participants", pid, "stats", "firstBloodKill"])
        parse_variable(match_data, parsed_data, "first_blood_asst",
                       [game_id, "participants", pid, "stats", "firstBloodAssist"])
        # TODO add cs stuff (csd at each point in the game, etc.)
        # parse_variable(match_data, parsed_data, "cs",
        #                [game_id, "participants", pid, "timeline", "lane"])
    return parsed_data


if 0:
    import json
    import api_fns
    with open("Configuration.json", "r") as file:
        config_info = json.loads(file.read())
    with open(config_info["SummonerName"] + "_MatchData.json", "r") as file:
        match_data = json.loads(file.read())


def filter_matches(config_info, parsed_data, remove_indices, config_key, filter_keys, choices_list):
    """
    :param config_info: configuration info for the entire app, same as everywhere else
    :param parsed_data: the parsed match data
    :param remove_indices: a list of integers whose entries are match indices to remove from parsed_data
    :param config_key: string; filter's corresponding key from the config file
    :param filter_keys: list of strings; key(s) in parsed_data that should be checked against the choices_list
    :param choices_list: list of strings; the options the user chose in the GUI
    :return:
    """

    n_matches = len(parsed_data["game_id"])

    print("Running filter_matches given the following:")
    print("    ", filter_keys, " is the list of keys to check through in parsed_data")
    print("    ", str(choices_list), " is the list of choices enabled in the GUI (via config_info)")
    print("     Here's the config dictionary: ", config_info[config_key])
    print("     parsed_data contained " + str(n_matches) + " matches")

    print(len(filter_keys), " is the lenght of filter_keys")
    if len(choices_list) == 0:
        print("No active choices, skipping this filter.")
    else:
        keep = 0  # prep a variable for whether or not to keep this match
        # TODO: remove hardcoding this to only 10 games lol
        n_matches = 10
        for ii in range(n_matches):
            for choice in choices_list:  # look over each acceptable choice
                for parsed_key in filter_keys:  # check it the corresponding entry in parsed_data
                    print(
                        "Comparing chosen key (" + str(config_info[config_key][choice]) +
                        ") with parsed_data value for this match (" + str(parsed_data[parsed_key][ii]) + ")"
                    )

                    if str(config_info[config_key][choice]) in str(parsed_data[parsed_key][ii]):
                        print("found what I was looking for; keeping the match")
                        keep += 1

            if keep == 0:
                remove_indices.append(ii)

            print(remove_indices)

    remove_indices = sorted(list(set(remove_indices)))

    return remove_indices


# TODO: FIX INDEXING IN FILTERS
def filter_remakes(match_data, parsed_match_data):
    """ Filter out remakes (games with length < 6 minutes) """
    n_mat = len(match_data)
    filtered_match_data = {}
    nn = 0
    for match_index in range(n_mat):
        if parsed_match_data["match_length"][match_index] > 6:
            filtered_match_data[str(nn)] = match_data[str(match_index)]
            nn += 1
    return filtered_match_data


def filter_season(match_data, parsed_match_data, ssn_filter):
    """ Filter by desired season """
    n_mat = len(match_data)
    filtered_match_data = {}
    nn = 0
    for match_index in range(n_mat):
        if parsed_match_data["season"][match_index] == ssn_filter:
            filtered_match_data[str(nn)] = match_data[str(match_index)]
            nn += 1
    return filtered_match_data


def filter_champ(match_data, parsed_match_data, champ_filter):
    """ Filter by desired champ """
    n_mat = len(match_data)
    filtered_match_data = {}
    nn = 0
    for match_index in range(n_mat):
        if parsed_match_data["champ"][match_index] == champ_filter:
            filtered_match_data[str(nn)] = match_data[str(match_index)]
            nn += 1
    return filtered_match_data


def filter_match(match_data, match_filter):
    """ Filter for recent matches, where match_filter is a number of matches to keep """
    n_mat = len(match_data)
    filtered_match_data = {}
    if match_filter < n_mat:
        nn = 0
        for match_index in range(n_mat-match_filter, n_mat):
            filtered_match_data[str(nn)] = match_data[str(match_index)]
            nn += 1
    else:
        filtered_match_data = match_data
    return filtered_match_data


def filter_qtype(match_data, parsed_match_data, q_filter):
    """ Filter for recent matches """
    n_mat = len(match_data)
    filtered_match_data = {}
    nn = 0
    for match_index in range(n_mat):
        if parsed_match_data["queue_type"][match_index] == q_filter:
            filtered_match_data[str(nn)] = match_data[str(match_index)]
            nn += 1
    return filtered_match_data


def filter_role(match_data, parsed_match_data, role_filter):
    """ Filter for recent matches """
    n_mat = len(match_data)
    filtered_match_data = {}
    nn = 0
    for match_index in range(n_mat):
        if parsed_match_data["role"][match_index] == role_filter:
            filtered_match_data[str(nn)] = match_data[str(match_index)]
            nn += 1
    return filtered_match_data


def filter_map(match_data, map_id):
    """ filter out matches by map (e.g. summoner's rift) """
    # New summoner's rift is mapId = 11
    n_mat = len(match_data)
    filtered_match_data = {}
    nn = 0
    for match_index in range(n_mat):
        if match_data[str(match_index)]["mapId"] == map_id:
            filtered_match_data[str(nn)] = match_data[ii]
            nn += 1
    return filtered_match_data



# for debugging
if 0:
    import json
    with open("Configuration.json", "r") as file:
        config_info = json.loads(file.read())
    with open(config_info["SummonerName"] + "_MatchData.json", "r") as file:
        match_data = json.loads(file.read())

    try:
        with open(config_info["SummonerName"] + "_ParsedData.LoHData", "r") as file:
            parsed_data = json.loads(file.read())
    except:
        parsed_data = {}
        pass

    parsed_data = parse_data(config_info, match_data)







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
