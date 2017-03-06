from APIFunctions import GetChamp


def parse_match_data(config_info, match_data, champLookup):
    """ Converts raw match data into a set of (mostly) lists for analysis """
    summoner_name = config_info["Settings"]["SummonerName"]
    n_matches = len(match_data)

    season = []
    timestamp = []
    queue_type = []
    win_lose = []
    match_lengths = []
    summ_num = []
    teammates = {}
    enemies = {}
    champ = []
    role = []
    map_side = []
    kills = []
    deaths = []
    assists = []
    kda = []
    damage_total = []
    damage_to_champs = []
    damage_total_frac = []
    damage_to_champs_frac = []
    damage_taken = []
    damage_taken_frac = []
    gold = []
    gold_frac = []
    cs = []
    csm_at_10 = []
    csmd_at_10 = []
    csm_at_20 = []
    csmd_at_20 = []
    csm_at_30 = []
    csmd_at_30 = []
    csm_aft_30 = []
    csmd_aft_30 = []
    wards = []
    wards_killed = []

    for mm in range(n_matches):
        season.append(match_data[str(mm)]["season"])
        queue_type.append(match_data[str(mm)]["queueType"])
        timestamp.append(match_data[str(mm)]["matchCreation"])
        match_lengths.append(match_data[str(mm)]["matchDuration"]/60)
        other_players = []
        others_damage_total = []
        others_damage_to_champs = []
        others_gold = []
        others_damage_taken = []
        # loop over the players in the game and look for the target player
        for pp in range(10):
            if (str(match_data[str(mm)]["participantIdentities"][pp]["player"]["summonerId"])
                    == config_info["Settings"]["SID"]):
                """ This case gathers data for the summoner using the app. """
                summ_num.append(pp)
                damage_total.append(
                    match_data[str(mm)]["participants"][summ_num[mm]]["stats"]["totalDamageDealt"])
                damage_to_champs.append(
                    match_data[str(mm)]["participants"][summ_num[mm]]["stats"]["totalDamageDealtToChampions"])
                damage_taken.append(
                    match_data[str(mm)]["participants"][summ_num[mm]]["stats"]["totalDamageTaken"])
                gold.append(match_data[str(mm)]["participants"][summ_num[mm]]["stats"]["goldEarned"])
                win_lose.append(match_data[str(mm)]["participants"][summ_num[mm]]["stats"]["winner"])
                """ Some quick parsing of the lanes and roles to make it look nicer"""
                Lane=match_data[str(mm)]["participants"][summ_num[mm]]["timeline"]["lane"]
                if (Lane == "MIDDLE"):
                    Lane = "MID"
                if (Lane == "BOTTOM"):
                    Lane = "BOT"
                if (Lane == "JUNGLE"):
                    Lane = "JUNGLE"
                TestRole=match_data[str(mm)]["participants"][summ_num[mm]]["timeline"]["role"]
                if (TestRole == "DUO_CARRY"):
                    TestRole = "CARRY"
                if (TestRole == "DUO_SUPPORT"):
                    TestRole = "SUPPORT"
                role_string = (Lane + "\n" + TestRole)
                if (TestRole == "NONE"):
                    TestRole = ""
                    role_string = (Lane)
                role.append(role_string)

                """ teamId: 100 is blue side; 200 is red side """
                map_side.append(match_data[str(mm)]["participants"][summ_num[mm]]["teamId"])
                kills.append(match_data[str(mm)]["participants"][summ_num[mm]]["stats"]["kills"])
                deaths.append(match_data[str(mm)]["participants"][summ_num[mm]]["stats"]["deaths"])
                assists.append(match_data[str(mm)]["participants"][summ_num[mm]]["stats"]["assists"])
                cs.append(match_data[str(mm)]["participants"][summ_num[mm]]["stats"]["minionsKilled"])
                # try:
                #     csm_at_10.append(
                #         match_data[str(mm)]["participants"][summ_num[mm]]["timeline"]["creepsPerMinDeltas"][
                #             "zeroToTen"])
                # except:
                #     csm_at_10.append(["NaN"])
                # match_data[str(mm)]["participants"][summ_num[mm]]["timeline"]["creepsPerMinDeltas"]["zeroToTen"]
                # CSAt10(iii) = match_data(ii).participants(MySummNum).timeline.creepsPerMinDeltas.zeroToTen;
                # CSAt20(iii) = match_data(ii).participants(MySummNum).timeline.creepsPerMinDeltas.tenToTwenty;
                # CSAt30(iii) = match_data(ii).participants(MySummNum).timeline.creepsPerMinDeltas.twentyToThirty;
                # CStoEnd(iii) = match_data(ii).participants(MySummNum).timeline.creepsPerMinDeltas.thirtyToEnd;
                # CSDAt10(iii) = match_data(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.zeroToTen;
                # CSDAt20(iii) = match_data(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.tenToTwenty;
                # CSDAt30(iii) = match_data(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.twentyToThirty;
                # CSDtoEnd(iii) = match_data(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.thirtyToEnd;
                wards.append(match_data[str(mm)]["participants"][summ_num[mm]]["stats"]["wardsPlaced"])
                wards_killed.append(match_data[str(mm)]["participants"][summ_num[mm]]["stats"]["wardsKilled"])
                try:
                    kda.append((kills[mm]+assists[mm])/deaths[mm])
                except:
                    kda.append("perfect")
            else:
                """ This case builds temporary teammate variables that are overwritten for each new match. """
                other_players.append(match_data[str(mm)]["participantIdentities"][pp]["player"]["summonerName"])
                others_damage_total.append(
                    match_data[str(mm)]["participants"][pp]["stats"]["totalDamageDealt"])
                others_damage_to_champs.append(
                    match_data[str(mm)]["participants"][pp]["stats"]["totalDamageDealtToChampions"])
                others_damage_taken.append(
                    match_data[str(mm)]["participants"][pp]["stats"]["totalDamageTaken"])
                others_gold.append(match_data[str(mm)]["participants"][pp]["stats"]["goldEarned"])
        # Team 1
        if summ_num[mm] <=4:
            teammates[str(mm)] = other_players[0:4]
            enemies[str(mm)] = other_players[4:9]
            damage_total_frac.append(damage_total[mm]/(1+sum(others_damage_total[0:4])))
            damage_to_champs_frac.append(damage_to_champs[mm]/(1+sum(others_damage_to_champs[0:4])))
            damage_taken_frac.append(damage_taken[mm]/(1+sum(others_damage_taken[0:4])))
            gold_frac.append(gold[mm]/(1+sum(others_gold[0:4])))
        # Team 2
        elif summ_num[mm] >= 5:
            teammates[str(mm)] = other_players[5:9]
            enemies[str(mm)] = other_players[0:5]
            damage_total_frac.append(damage_total[mm]/(1+sum(others_damage_total[5:9])))
            damage_to_champs_frac.append(damage_to_champs[mm]/(1+sum(others_damage_to_champs[5:9])))
            damage_taken_frac.append(damage_taken[mm]/(1+sum(others_damage_taken[5:9])))
            gold_frac.append(gold[mm]/(1+sum(others_gold[5:9])))
        champ.append(
            GetChamp.champ_name(champLookup, match_data[str(mm)]["participants"][summ_num[mm]]["championId"])
        )
    season_unique = sorted(list(set(season)))
    queue_types = sorted(list(set(queue_type)))
    champs_played = sorted(list(set(champ)))
    roles = sorted(list(set(role)))

    return {
        "summoner_name": summoner_name,
        "season_unique": season_unique,
        "season": season,
        "queue_type": queue_type,
        "queue_types": queue_types,
        "win_lose": win_lose,
        "timestamp": timestamp,
        "match_lengths": match_lengths,
        "teammates": teammates,
        "enemies": enemies,
        "champ": champ,
        "champs_played": champs_played,
        "role": role,
        "roles": roles,
        "map_side": map_side,
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "kda": kda,
        "damage_total": damage_total,
        "damage_to_champs": damage_to_champs,
        "damage_total_frac": damage_total_frac,
        "damage_to_champs_frac": damage_to_champs_frac,
        "damage_taken": damage_taken,
        "damage_taken_frac": damage_taken_frac,
        "gold": gold,
        "gold_frac": gold_frac,
        "cs": cs,
        "csm_at_10": csm_at_10,
        "csmd_at_10": csmd_at_10,
        "csm_at_20": csm_at_20,
        "csmd_at_20": csmd_at_20,
        "csm_at_30": csm_at_30,
        "csmd_at_30": csmd_at_30,
        "csm_aft_30": csm_aft_30,
        "csmd_aft_30": csmd_aft_30,
        "wards": wards,
        "wards_killed": wards_killed,
    }


"""
# For debugging
import json
import urllib.request
config_info = json.loads(open("Configuration.LoHConfig", "r").read())
match_data = json.loads(open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "r").read())
parsed_match_data = json.loads(open(config_info["Settings"]["SummonerName"] + "_ParsedMatchData.LoHData", "r").read())
champLookup = get_champ_dd()
"""

"""
LIST OF CURRENT FILTERS
- remakes (removes remakes, determined by match length)
- season (desired season only, such as PRESEASON 2016)
- champ (desired champion only)
- match (number of most recent matches)
- qtype (chooses specific queue type only, such as Ranked Flex or Ranked Solo/Duo)
- role (desired role only, such as JUNGLE)
- map (desired map ID)

ADDITIONAL POSSIBLE FILTERS
- inverses of some of the other filters (e.g. role, as in "exclude support" instead of support only))

"""


def filter_remakes(match_data, parsed_match_data):
    """ Filter out remakes (games with length < 6 minutes) """
    n_mat = len(match_data)
    filtered_match_data = {}
    nn = 0
    for mm in range(n_mat):
        if parsed_match_data["match_lengths"][mm] > 6:
            filtered_match_data[str(nn)] = match_data[str(mm)]
            nn += 1
    return filtered_match_data


def filter_season(match_data, parsed_match_data, ssn_filter):
    """ Filter by desired season """
    n_mat = len(match_data)
    filtered_match_data = {}
    nn = 0
    for mm in range(n_mat):
        if parsed_match_data["season"][mm] == ssn_filter:
            filtered_match_data[str(nn)] = match_data[str(mm)]
            nn += 1
    return filtered_match_data


def filter_champ(match_data, parsed_match_data, champ_filter):
    """ Filter by desired champ """
    n_mat = len(match_data)
    filtered_match_data = {}
    nn = 0
    for mm in range(n_mat):
        if parsed_match_data["champ"][mm] == champ_filter:
            filtered_match_data[str(nn)] = match_data[str(mm)]
            nn += 1
    return filtered_match_data


def filter_match(match_data, match_filter):
    """ Filter for recent matches, where match_filter is a number of matches to keep """
    n_mat = len(match_data)
    filtered_match_data = {}
    if match_filter < n_mat:
        nn = 0
        for mm in range(n_mat-match_filter, n_mat):
            filtered_match_data[str(nn)] = match_data[str(mm)]
            nn += 1
    else:
        filtered_match_data = match_data
    return filtered_match_data


def filter_qtype(match_data, parsed_match_data, q_filter):
    """ Filter for recent matches """
    n_mat = len(match_data)
    filtered_match_data = {}
    nn = 0
    for mm in range(n_mat):
        if parsed_match_data["queue_type"][mm] == q_filter:
            filtered_match_data[str(nn)] = match_data[str(mm)]
            nn += 1
    return filtered_match_data


def filter_role(match_data, parsed_match_data, role_filter):
    """ Filter for recent matches """
    n_mat = len(match_data)
    filtered_match_data = {}
    nn = 0
    for mm in range(n_mat):
        if parsed_match_data["role"][mm] == role_filter:
            filtered_match_data[str(nn)] = match_data[str(mm)]
            nn += 1
    return filtered_match_data


def filter_map(match_data, map_id):
    """ filter out matches by map (e.g. summoner's rift) """
    # New summoner's rift is mapId = 11
    n_mat = len(match_data)
    filtered_match_data = {}
    nn = 0
    for mm in range(n_mat):
        if match_data[str(mm)]["mapId"] == map_id:
            filtered_match_data[str(nn)] = match_data[str(mm)]
            nn += 1
    return filtered_match_data

