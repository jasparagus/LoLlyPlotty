def get_count(config_info, match):
    # always returns 1. For incrementing games played, etc.
    return 1


def get_enemy_champs(config_info, match):
    # get a list of champions played by the enemy team
    enemy_champs = []
    pid = get_pid(config_info, match)
    n_players = len(match["participantIdentities"])

    for ii in range(n_players):
        if str(match["participants"][ii]["teamId"]) != str(match["participants"][pid]["teamId"]):
            champ_id = match["participants"][ii]["championId"]
            enemy_champs.append(champ_id)

    if len(enemy_champs) == 0:
        enemy_champs = ["Unknown"]
    return enemy_champs


def get_fractions(config_info, match):
    # get shares of damage, etc., for a variety of statistics
    fractions_dict = {
        "goldEarned": "Unknown",
        "totalDamageDealt": "Unknown",
        "totalDamageDealtToChampions": "Unknown",
        "damageDealtToObjectives": "Unknown",
        "magicDamageDealt": "Unknown",
        "magicDamageDealtToChampions": "Unknown",
        "physicalDamageDealt": "Unknown",
        "physicalDamageDealtToChampions": "Unknown",
        "trueDamageDealt": "Unknown",
        "trueDamageDealtToChampions": "Unknown",
        "totalDamageTaken": "Unknown",
        "damageSelfMitigated": "Unknown",
    }

    pid = get_pid(config_info, match)
    n_players = len(match["participantIdentities"])
    mitigated_taken_player = 0
    mitigated_taken_team = 0

    for kk in list(fractions_dict.keys()):
        try:
            player_share = 0
            teammates_share = 0
            for ii in range(n_players):
                if ii != pid and str(match["participants"][ii]["teamId"]) == str(match["participants"][pid]["teamId"]):
                    teammates_share += float(match["participants"][ii]["stats"][kk])
                elif ii == pid:
                    player_share = float(match["participants"][ii]["stats"][kk])

            fractions_dict[kk] = player_share / (player_share + teammates_share)

            if kk == "damageSelfMitigated" or kk == "totalDamageTaken":
                mitigated_taken_player += player_share
                mitigated_taken_team += (player_share + teammates_share)
        except (KeyError, ValueError, NameError, ZeroDivisionError) as e:
            pass
    try:
        fractions_dict["damageReceivedTotal"] = mitigated_taken_player / mitigated_taken_team
        if fractions_dict["damageReceivedTotal"] == fractions_dict["totalDamageTaken"]:
            raise KeyError  # Don't include games that are missing the damage mitigated stat
    except (ZeroDivisionError, KeyError):
        fractions_dict["damageReceivedTotal"] = "Unknown"

    return fractions_dict


def get_gold_diffs(config_info, match):
    # compare player gold vs. lane opponent
    gold_diffs_dict = {}
    pid = get_pid(config_info, match)
    oid = get_oid(config_info, match)

    try:
        player_gold_deltas = match["participants"][pid]["timeline"]["goldPerMinDeltas"]
        opponent_gold_deltas = match["participants"][oid]["timeline"]["goldPerMinDeltas"]
        gold_diff_keys = list(player_gold_deltas.keys())
        for kk in gold_diff_keys:
            gold_diffs_dict[kk] = float(player_gold_deltas[kk]) - float(opponent_gold_deltas[kk])

    except (KeyError, ValueError):
        pass

    return gold_diffs_dict


def get_items(config_info, match):
    # player's items
    items = []
    pid = get_pid(config_info, match)

    for ii in range(7):
        new_item = match["participants"][pid]["stats"]["item" + str(ii)]
        if new_item != 0:
            items += [new_item]

    items = list(set(items))  # dump duplicate purchases

    return items


def get_kda(config_info, match):
    # player's KDA
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


def get_non_player_champs(config_info, match):
    # list of champIDs for champs played by everyone in the game besides the selected summoner
    non_player_champs = []
    pid = get_pid(config_info, match)
    n_players = len(match["participantIdentities"])

    for ii in range(n_players):
        if ii != pid:
            champ_id = match["participants"][ii]["championId"]
            non_player_champs.append(champ_id)

    if len(non_player_champs) == 0:
        non_player_champs = ["Unknown"]

    return non_player_champs


def get_num_teammates(config_info, match):
    # figure out how many friends were in a given game
    teammates_game = get_teammates(config_info, match)
    num_teammates = 0

    for teammate in teammates_game:
        if teammate in config_info["Teammates"].keys():
            num_teammates += 1

    return num_teammates


def get_oid(config_info, match):
    # Gets the player's opponent's ID for the match
    pid = get_pid(config_info, match)
    oid = "Unknown"
    n_players = len(match["participantIdentities"])

    lane = str(match["participants"][pid]["timeline"]["lane"])
    role = str(match["participants"][pid]["timeline"]["role"])

    for ii in range(n_players):
        if (str(match["participants"][ii]["timeline"]["lane"]) == str(lane) and
                    str(match["participants"][ii]["timeline"]["role"]) == str(role) and ii != pid):
            oid = ii
            break

    return oid


def get_opponents(config_info, match):
    # Get all opponents (everyone on the enemy team)
    opponents = []
    pid = get_pid(config_info, match)

    n_players = len(match["participantIdentities"])
    for ii in range(n_players):
        if str(match["participants"][ii]["teamId"]) != str(match["participants"][pid]["teamId"]):
            opponents.append(
                match["participantIdentities"][ii]["player"]["summonerName"]
            )

    if len(opponents) == 0:
        opponents = ["Unknown"]
    opponents = sorted(opponents)

    return opponents


def get_pid(config_info, match):
    # Gets the player's ID for the match
    pid = "Unknown"
    n_players = len(match["participantIdentities"])
    for ii in range(n_players):
        if str(match["participantIdentities"][ii]["player"]["accountId"]) == str(config_info["AccountID"]):
            pid = ii
            break
    return pid


def get_role_pretty(config_info, match):
    # get the player's role in a human-readable format
    pid = get_pid(config_info, match)

    try:
        role = str(match["participants"][pid]["timeline"]["role"])
        lane = str(match["participants"][pid]["timeline"]["lane"])
    except (KeyError, NameError):
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
            role_pretty = "Bot/ADC"
        elif "sup" in role.lower():
            role_pretty = "Support"
        else:
            role_pretty = "Bot (Other)"
    else:
        role_pretty = "Unknown"

    return role_pretty


def get_teammate_champs(config_info, match):
    # Get the list of champ IDs played by teammates (not the player)
    teammate_champs = []
    pid = get_pid(config_info, match)
    n_players = len(match["participantIdentities"])

    for ii in range(n_players):
        if str(match["participants"][ii]["teamId"]) == str(match["participants"][pid]["teamId"]) and ii != pid:
            champ_id = match["participants"][ii]["championId"]
            teammate_champs.append(champ_id)

    if len(teammate_champs) == 0:
        teammate_champs = ["Unknown"]

    return teammate_champs


def get_teammates(config_info, match):
    # Get a list of teammates (people on the player's team)
    teammates = []
    pid = get_pid(config_info, match)

    n_players = len(match["participantIdentities"])
    for ii in range(n_players):
        if str(match["participants"][ii]["teamId"]) == str(match["participants"][pid]["teamId"]) and ii != pid:
            teammates.append(
                match["participantIdentities"][ii]["player"]["summonerName"]
            )

    if len(teammates) == 0:
        teammates = ["Unknown"]

    return teammates

