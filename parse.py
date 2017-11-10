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

        parsed_data["damage_total_frac"].append(parsed_data["damage_total"][ii] /
                                                parsed_data["ally_stats"][ii]["damage_total"])
        parsed_data["damage_champs_frac"].append(parsed_data["damage_champs"][ii] /
                                                 parsed_data["ally_stats"][ii]["damage_taken"])
        parsed_data["damage_taken_frac"].append(parsed_data["damage_taken"][ii] /
                                                parsed_data["ally_stats"][ii]["damage_taken"])

    parsed_data["hours_played"] = round(parsed_data["hours_played"], 1)

    return parsed_data





















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
            role_pretty = "Bot/ADC"
        elif "sup" in role.lower():
            role_pretty = "Support"
        else:
            role_pretty = "Bot (Other)"
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


def get_count(config_info, match):
    return 1


def get_teammates(config_info, match):
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
    teammates = sorted(teammates)

    return teammates


def get_opponents(config_info, match):
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


def get_items(config_info, match):
    items = []
    pid = get_pid(config_info, match)

    for ii in range(7):
        new_item = match["participants"][pid]["stats"]["item" + str(ii)]
        if new_item != 0:
            items += [clean_item(config_info, new_item)]

    items = list(set(items))  # dump duplicate purchases

    return items


def get_cumulative_vars(config_info, match):
    cumulative_vars = {}




    return cumulative_vars


# TODO: remove testing code
testing=0

if testing:
    import json
    with open("Configuration.json", "r") as file:
        config_info = json.load(file)
    with open("MatchData_jasparagus.json", "r") as file:
        match_data = json.load(file)
    match = match_data[sorted(list(match_data.keys()))[-1]]
    # print(json.dumps(match["participants"][pid], indent=4))
testing = 1


# yvar_vs_list_of_lists(megalist, 0)


def yvar_vs_count_in_lists(list_of_lists, y_var_list):
    # total_count = sum(sublist.count("TEAMMATENAME") for sublist in listoflists)
    return



# n_players = len(match_data[str(game_id)]["participantIdentities"])
# for ii in range(n_players):
#     # Find ally players
#     if teamId == match_data[str(game_id)]["participants"][ii]["teamId"] and ii != player_id:
#         # If the participant was on your team, stick their info in ally stats
#         ally_stats["gold_earned"] += match_data[str(game_id)]["participants"][ii]["stats"][
#             "goldEarned"]
#         ally_stats["damage_total"] += match_data[str(game_id)]["participants"][ii]["stats"][
#             "totalDamageDealt"]
#         ally_stats["damage_champs"] += match_data[str(game_id)]["participants"][ii]["stats"][
#             "totalDamageDealtToChampions"]
#         ally_stats["damage_taken"] += match_data[str(game_id)]["participants"][ii]["stats"][
#             "totalDamageTaken"]
#         ally_stats["damage_mitigated"] += match_data[str(game_id)]["participants"][ii]["stats"][
#             "damageSelfMitigated"]
#
#     # Find enemy players
#     elif ii != player_id:
#         enemy_stats["gold_earned"] += match_data[str(game_id)]["participants"][ii]["stats"][
#             "goldEarned"]
#         enemy_stats["damage_total"] += match_data[str(game_id)]["participants"][ii]["stats"][
#             "totalDamageDealt"]
#         enemy_stats["damage_champs"] += match_data[str(game_id)]["participants"][ii]["stats"][
#             "totalDamageDealtToChampions"]
#         enemy_stats["damage_taken"] += match_data[str(game_id)]["participants"][ii]["stats"][
#             "totalDamageTaken"]
#         enemy_stats["damage_mitigated"] += match_data[str(game_id)]["participants"][ii]["stats"][
#             "damageSelfMitigated"]


def clean_game_duration(config_info, game_duration):
    match_length = round(float(game_duration) / 60, 2)  # match length in minutes
    return match_length


def clean_team(config_info, team):
    if int(team) == 100:
        map_side = "Blue"
    elif int(team) == 200:
        map_side = "Red"
    else:
        map_side = "Other"
    return map_side


def clean_binary(config_info, bin_var):
    if bin_var == 1 or bin_var == "True":
        clean_var = 1
    elif bin_var == 0 or bin_var == "False":
        clean_var = 0
    else:
        clean_var = "Unknown"
    return clean_var


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
        champ_name = config_info["champion"][str(champ_id)]
    except:
        champ_name = "Unknown"
    return champ_name


def clean_summoner_spell(config_info, spell_id):
    try:
        spell_name = config_info["summoner"][str(spell_id)]
    except:
        spell_name = "Unknown"
    return spell_name


def clean_item(config_info, item_id):
    try:
        item_name = config_info["item"][str(item_id)]
    except KeyError:
        item_name = "Item " + str(item_id) + " (Deprecated Item ID)"
    return item_name


class Var:
    names = []  # A list of all instance names
    b_vars = []  # A list of instances for which the variable is a boolean (True/False)
    f_vars = []  # A list of instances for which the variable is best-suited to "float" type (e.g. Gold or Damage)
    s_vars = []  # A list of instances for which the variable is best stored as a string (e.g. Role))
    p_vars = []  # A list of instances (like x instances) but for which plotting requires special attention
    c_vars = []  # A list of incrementing variables (e.g. games played or time played)  # TODO: is this doable?

    def __init__(self, name, types, path, cleanup=None):
        self.name = name
        self.types = types
        self.path = path
        self.cleaup = cleanup

        # Update the lists of variables and their types as applicable
        self.names.append(self.name)
        self.names = sorted(self.names)

        if "b" in str(types).lower():
            self.b_vars.append(self.name)
        if "f" in str(types).lower():
            self.f_vars.append(self.name)
        if "s" in str(types).lower():
            self.s_vars.append(self.name)
        if "p" in str(types).lower():
            self.p_vars.append(self.name)
        if "c" in str(types).lower():
            self.c_vars.append(self.name)

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
    def check_removal(cls, config_info, match, vars_list, filters, oldest_match_days):
        # Prepare a variable to track removal of the match (if the variable becomes > 0)
        remove = 0
        n_filters_skipped = 0

        for flt in filters:
            if len(flt.choices_list) != 0:
                keys_failed = 0
                for filter_key in flt.filter_keys:
                    # See if the match (after parsing) is missing all the choices made in the GUI
                    if (str(vars_list[cls.names.index(filter_key)].extract(config_info, match)) not in
                            flt.choices_list):
                        keys_failed += 1
                # See if the game failed every key check (if so, exclude it)
                if keys_failed == len(flt.filter_keys):
                    remove += 1
            else:
                n_filters_skipped += 1

        # Remove the match if it's too old or was a remake
        if int(match["gameCreation"]) < int((time.time() * 1000) - (int(oldest_match_days) * 24 * 60 * 60 * 1000)):
            if oldest_match_days != 0:
                remove += 10000
        if int(match["gameDuration"]) < 360:
            remove += 1000

        return remove


    @classmethod
    def create_list(cls, config_info, match_data, vars_list, y_var_name, x_var_name, filters, oldest_match_days):
        # Get a list of game IDs from the match list and sort them chronologically
        game_ids = sorted(list(match_data.copy().keys()))

        # Prepare the lists, then loop over each game and extract the variable.
        y_list = []
        x_list = []
        n_kept = 0

        for game_id in game_ids:
            # Grab hold of the match getting checked
            match = match_data.copy()[str(game_id)]
            remove = cls.check_removal(config_info, match, vars_list, filters, oldest_match_days)

            # If the match survived the filters, add the data for the given match to the list!
            if remove == 0:
                y_element = vars_list[cls.names.index(y_var_name)].extract(config_info, match)
                x_element = vars_list[cls.names.index(x_var_name)].extract(config_info, match)

                if type(x_element) is not list and type(y_element) is not list:
                    y_list += [y_element]
                    x_list += [x_element]
                elif type(y_element) is list and type(x_element) is not list:
                    y_list += y_element
                    x_list += [x_element] * len(y_element)
                elif type(x_element) is list and type(y_element) is not list:
                    y_list += [y_element] * len(x_element)
                    x_list += x_element
                elif type(x_element) is list and type(y_element) is list:
                    y_list += [y_element] * len(x_element)
                    x_list += [x_element] * len(y_element)
                else:
                    print("Unexpected data type extracted from game; not appending it to list")

                n_kept += 1

        return y_list, x_list, n_kept

    @classmethod
    def special_list(cls, config_info, match_data, var_1_name, var_2_name, filters, oldest_match_days):
        # Prepare the lists to hold the variables
        var_1_list = []
        var_2_list = []

        return var_1_list, var_2_list


# TODO: separate discrete and continuous variables rather than "x" and "y" variables so plotting can be smarter
# Result: a discrete x gets a bar chart, while a continuous x gets a scatter plot. Continuous x cannot have a discrete y
Vars = [
    Var("Game ID", "", ["gameId"]),
    Var("Matches Played", "p", []),
    Var("Total Time Played", "p", []),
    Var("Timestamp", "f", ["gameCreation"]),
    Var("Queue Type", "s", ["queueId", clean_queue]),
    Var("Map", "s", ["mapId", clean_map]),
    Var("Game Mode", "", ["gameMode"]),
    Var("Games Played", "c", [get_count]),  # TODO make this work

    Var("Game Length", "f", ["gameDuration", clean_game_duration]),
    Var("Time Played", "c", ["gameDuration", clean_game_duration]),
    Var("Season", "s", ["seasonId", clean_season]),

    Var("Map Side", "s", ["participants", get_pid, "teamId", clean_team]),
    Var("Rank", "s", ["participants", get_pid, "highestAchievedSeasonTier"]),
    Var("Champion", "s", ["participants", get_pid, "championId", clean_champion]),
    Var("Summoner Spell 1", "s", ["participants", get_pid, "spell1Id", clean_summoner_spell]),
    Var("Summoner Spell 2", "s", ["participants", get_pid, "spell2Id", clean_summoner_spell]),

    Var("KDA", "f", [get_kda]),
    Var("Kills", "f", ["participants", get_pid, "stats", "kills"]),
    Var("Deaths", "f", ["participants", get_pid, "stats", "deaths"]),
    Var("Assists", "f", ["participants", get_pid, "stats", "assists"]),
    Var("Win/Loss", "b", ["participants", get_pid, "stats", "win", clean_binary]),

    Var("Wards Placed", "f", ["participants", get_pid, "stats", "wardsPlaced"]),
    Var("Wards Killed", "f", ["participants", get_pid, "stats", "wardsKilled"]),
    Var("Vision Wards Bought", "f", ["participants", get_pid, "stats", "visionWardsBoughtInGame"]),
    Var("First Blood", "b", ["participants", get_pid, "stats", "firstBloodKill", clean_binary]),
    # NOTE: First blood assist not implemented by Riot in API; always returns false as of 20171101
    # Var("First Blood (Assisted)", "xy", ["participants", get_pid, "stats", "firstBloodAssist", clean_binary]),
    Var("First Tower", "b", ["participants", get_pid, "stats", "firstTowerKill", clean_binary]),
    Var("First Tower (Assisted)", "b", ["participants", get_pid, "stats", "firstTowerAssist", clean_binary]),
    Var("Gold Earned", "f", ["participants", get_pid, "stats", "goldEarned"]),
    Var("CS (Total)", "f", ["participants", get_pid, "stats", "totalMinionsKilled"]),
    Var("Jungle CS (Your Jungle)", "f", ["participants", get_pid, "stats", "neutralMinionsKilledTeamJungle"]),
    Var("Jungle CS (Enemy Jungle)", "f", ["participants", get_pid, "stats", "neutralMinionsKilledEnemyJungle"]),
    Var("Damage Dealt (Total)", "f", ["participants", get_pid, "stats", "totalDamageDealt"]),
    Var("Damage Dealt (Total, Champions)", "f", ["participants", get_pid, "stats", "totalDamageDealtToChampions"]),
    Var("Damage Dealt (Physical)", "f", ["participants", get_pid, "stats", "physicalDamageDealt"]),
    Var("Damage Dealt (Physical, Champs)", "f", ["participants", get_pid, "stats", "physicalDamageDealtToChampions"]),
    Var("Damage Dealt (Magic)", "f", ["participants", get_pid, "stats", "magicDamageDealt"]),
    Var("Damage Dealt (Magic, Champs)", "f", ["participants", get_pid, "stats", "magicDamageDealtToChampions"]),
    Var("Damage Taken", "f", ["participants", get_pid, "stats", "totalDamageTaken"]),
    Var("Damage Mitigated (Self)", "f", ["participants", get_pid, "stats", "damageSelfMitigated"]),
    Var("Longest Time Alive", "f", ["participants", get_pid, "stats", "longestTimeSpentLiving"]),
    Var("Vision Score", "f", ["participants", get_pid, "stats", "visionScore"]),
    Var("Healing Done", "f", ["participants", get_pid, "stats", "totalHeal"]),
    Var("Healing (Units Healed)", "f", ["participants", get_pid, "stats", "totalUnitsHealed"]),

    Var("Role", "s", [get_role_pretty]),
    Var("Lane Ugly", "", ["participants", get_pid, "timeline", "lane"]),
    Var("Role Ugly", "", ["participants", get_pid, "timeline", "role"]),

    Var("CS/min (0 min \u2192 10 min)", "f", ["participants", get_pid, "timeline", "creepsPerMinDeltas", "0-10"]),
    Var("CS/min (10 min \u2192 20 min)", "f", ["participants", get_pid, "timeline", "creepsPerMinDeltas", "10-20"]),
    Var("CS/min (20 min \u2192 30 min)", "f", ["participants", get_pid, "timeline", "creepsPerMinDeltas", "20-30"]),
    Var("CS/min (30 min \u2192 End)", "f", ["participants", get_pid, "timeline", "creepsPerMinDeltas", "30-end"]),
    Var("CS/m Diff. (0 min \u2192 10 min)", "f", ["participants", get_pid, "timeline", "csDiffPerMinDeltas", "0-10"]),
    Var("CS/m Diff. (10 min \u2192 20 min)", "f", ["participants", get_pid, "timeline", "csDiffPerMinDeltas", "10-20"]),
    Var("CS/m Diff. (20 min \u2192 30 min)", "f", ["participants", get_pid, "timeline", "csDiffPerMinDeltas", "20-30"]),
    Var("CS/m Diff. (30 min \u2192 End)", "f", ["participants", get_pid, "timeline", "csDiffPerMinDeltas", "30-end"]),

    Var("Gold/min (0 min \u2192 10 min)", "f", ["participants", get_pid, "timeline", "goldPerMinDeltas", "0-10"]),
    Var("Gold/min (10 min \u2192 20 min)", "f", ["participants", get_pid, "timeline", "goldPerMinDeltas", "10-20"]),
    Var("Gold/min (20 min \u2192 30 min)", "f", ["participants", get_pid, "timeline", "goldPerMinDeltas", "20-30"]),
    Var("Gold/min (30 min \u2192 End)", "f", ["participants", get_pid, "timeline", "goldPerMinDeltas", "30-end"]),
    # TODO: add gold differential

    Var("XP/min (0 min \u2192 10 min)", "f", ["participants", get_pid, "timeline", "xpPerMinDeltas", "0-10"]),
    Var("XP/min (10 min \u2192 20 min)", "f", ["participants", get_pid, "timeline", "xpPerMinDeltas", "10-20"]),
    Var("XP/min (20 min \u2192 30 min)", "f", ["participants", get_pid, "timeline", "xpPerMinDeltas", "20-30"]),
    Var("XP/min (30 min \u2192 End)", "f", ["participants", get_pid, "timeline", "xpPerMinDeltas", "30-end"]),
    Var("XP/m Diff. (0 min \u2192 10 min)", "f", ["participants", get_pid, "timeline", "xpDiffPerMinDeltas", "0-10"]),
    Var("XP/m Diff. (10 min \u2192 20 min)", "f", ["participants", get_pid, "timeline", "xpDiffPerMinDeltas", "10-20"]),
    Var("XP/m Diff. (20 min \u2192 30 min)", "f", ["participants", get_pid, "timeline", "xpDiffPerMinDeltas", "20-30"]),
    Var("XP/m Diff. (30 min \u2192 End)", "f", ["participants", get_pid, "timeline", "xpDiffPerMinDeltas", "30-end"]),

    Var("Lane Opponent Champion", "s", ["participants", get_oid, "championId", clean_champion]),
    Var("Lane Opponent First Blood", "b", ["participants", get_oid, "stats", "firstBloodKill"]),
    Var("Lane Opponent Rank", "s", ["participants", get_oid, "highestAchievedSeasonTier"]),

    Var("Teammates (Number of) - WILL BE A STRING (BAR CHART) VARIABLE", "", []),
    Var("Teammate (By Name)", "s", [get_teammates]),
    Var("Opponent (By Name)", "s", [get_opponents]),
    Var("Item", "s", [get_items]),
]

# TODO: make s type filters (see Vars list)

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
    "Fractions of damage-total/champs/taken, gold, xp": "",
}

# def parse_match_data(config_info, match_data, parsed_data):
#     visionscore = []
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
