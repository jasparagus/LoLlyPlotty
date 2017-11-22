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


def get_non_player_champs(config_info, match):
    non_player_champs = []
    pid = get_pid(config_info, match)
    n_players = len(match["participantIdentities"])

    for ii in range(n_players):
        if ii != pid:
            champ_id = match["participants"][ii]["championId"]
            champ = clean_champion(config_info, champ_id)
            non_player_champs.append(champ)

    if len(non_player_champs) == 0:
        non_player_champs = ["Unknown"]

    non_player_champs = sorted(non_player_champs)

    return non_player_champs


def get_num_teammates(config_info, match_data):
    num_teammates_list = []

    return num_teammates_list

# TODO: remove testing code
testing=0











if testing:
    import json
    with open("Configuration.json", "r") as file:
        config_info = json.load(file)
    with open("MatchData_jasparagus.json", "r") as file:
        match_data = json.load(file)
    match = match_data[sorted(list(match_data.keys()))[0]]
    # print(json.dumps(match["participants"][pid], indent=4))
# testing = 1










def yvar_vs_count_in_lists(list_of_lists, y_var_list):
    # total_count = sum(sublist.count("TEAMMATENAME") for sublist in listoflists)
    return



def get_items(config_info, match):
    items = []
    pid = get_pid(config_info, match)

    for ii in range(7):
        new_item = match["participants"][pid]["stats"]["item" + str(ii)]
        if new_item != 0:
            items += [clean_item(config_info, new_item)]

    items = list(set(items))  # dump duplicate purchases

    return items


def get_gold_diffs(config_info, match):
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


def get_fractions(config_info, match):
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


def clean_timestamp(config_info, timestamp):
    try:
        age_days = (float(time.time()) - (float(timestamp) / 1000)) / 86400  # convert seconds to days
    except ValueError:
        age_days = "Unknown"
    return age_days


class Var:
    names = []  # A list of all instance names
    b_vars = []  # A list of instances for which the variable is a boolean (True/False)
    f_vars = []  # A list of instances for which the variable is best-suited to "float" type (e.g. Gold or Damage)
    s_vars = []  # A list of instances for which the variable is best stored as a string (e.g. Role))
    c_vars = []  # A list of incrementing variables (e.g. games played or time played)
    q_vars = []  # A list of quirky variables; can be any type, but getting the value requires a special function

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
        if "c" in str(types).lower():
            self.c_vars.append(self.name)
        if "q" in str(types).lower():
            self.q_vars.append(self.name)

        return

    def extract(self, config_info, match):
        # call this once or twice (e.g. for win/loss and champion) per match to get the appropriate data from the match
        self.value = match.copy()

        # Iteratively work through the list, taking the appropriate type of action as determined by the element
        for step in self.path:
            try:
                if type(step) is types.FunctionType:
                    # if you have a function, carry it out correctly...
                    if len(self.path) == 1:
                        # if there is only one step, run the appropriate function
                        self.value = step(config_info, match)
                    elif step == self.path[-1] and len(self.path) != 1:
                        # If it's the last of many steps, run it as a cleanup function
                        self.value = step(config_info, self.value)
                    elif step != self.path[-1]:
                        # if it is not the last step, run the appropriate function
                        temp_step = step(config_info, match)
                        if type(temp_step) is dict:
                            # If the output is a dictionary, it's time for the next step
                            self.value = temp_step
                        else:
                            # if the output is not a dictionary, extract the value using the appropriate key
                            self.value = self.value[temp_step]

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

        # if y var is a quirky variable, handle it now
        if vars_list[cls.names.index(y_var_name)] in cls.q_vars:
            print("It's a quirky variable")

            # somehow track these for removal as well...


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
                    print("Unexpected data type extracted from game; skipping this game's data")

                n_kept += 1

        return y_list, x_list, n_kept


Vars = [
    Var("Game ID", "", ["gameId"]),
    Var("Matches Played", "p", []),
    Var("Total Time Played", "p", []),
    Var("Time (Days Ago)", "f", ["gameCreation", clean_timestamp]),
    Var("Queue Type", "s", ["queueId", clean_queue]),
    Var("Map", "s", ["mapId", clean_map]),
    Var("Game Mode", "", ["gameMode"]),
    Var("Number of Games", "c", [get_count]),

    Var("Game Length", "f", ["gameDuration", clean_game_duration]),
    Var("Time Played", "c", ["gameDuration", clean_game_duration]),
    Var("Season", "s", ["seasonId", clean_season]),

    Var("Map Side", "s", ["participants", get_pid, "teamId", clean_team]),
    Var("Rank", "s", ["participants", get_pid, "highestAchievedSeasonTier"]),
    Var("Champion", "s", ["participants", get_pid, "championId", clean_champion]),
    Var("Champion In Game (Played By Teammate or Enemy)", "s", [get_non_player_champs]),
    Var("Summoner Spell 1", "s", ["participants", get_pid, "spell1Id", clean_summoner_spell]),
    Var("Summoner Spell 2", "s", ["participants", get_pid, "spell2Id", clean_summoner_spell]),

    Var("KDA", "f", [get_kda]),
    Var("Kills", "f", ["participants", get_pid, "stats", "kills"]),
    Var("Kills (Double)", "c", ["participants", get_pid, "stats", "doubleKills"]),
    Var("Kills (Triple)", "c", ["participants", get_pid, "stats", "tripleKills"]),
    Var("Kills (Quadra)", "c", ["participants", get_pid, "stats", "quadraKills"]),
    Var("Kills (Penta)", "c", ["participants", get_pid, "stats", "pentaKills"]),
    Var("Deaths", "f", ["participants", get_pid, "stats", "deaths"]),
    Var("Assists", "f", ["participants", get_pid, "stats", "assists"]),
    Var("Largest Multikill", "f", ["participants", get_pid, "stats", "largestMultiKill"]),
    Var("Win/Loss", "b", ["participants", get_pid, "stats", "win", clean_binary]),

    Var("Wards Placed", "f", ["participants", get_pid, "stats", "wardsPlaced"]),
    Var("Wards Killed", "f", ["participants", get_pid, "stats", "wardsKilled"]),
    Var("Vision Wards Bought", "f", ["participants", get_pid, "stats", "visionWardsBoughtInGame"]),
    Var("First Blood", "b", ["participants", get_pid, "stats", "firstBloodKill", clean_binary]),
    # NOTE: First blood assist not implemented by Riot in API; is always false as of 20171101
    # Var("First Blood (Assisted)", "xy", ["participants", get_pid, "stats", "firstBloodAssist", clean_binary]),
    Var("First Tower", "b", ["participants", get_pid, "stats", "firstTowerKill", clean_binary]),
    Var("First Tower (Assisted)", "b", ["participants", get_pid, "stats", "firstTowerAssist", clean_binary]),
    Var("Gold Earned", "f", ["participants", get_pid, "stats", "goldEarned"]),
    Var("CS (Total)", "f", ["participants", get_pid, "stats", "totalMinionsKilled"]),
    Var("Jungle CS (Your Jungle)", "f", ["participants", get_pid, "stats", "neutralMinionsKilledTeamJungle"]),
    Var("Jungle CS (Enemy Jungle)", "f", ["participants", get_pid, "stats", "neutralMinionsKilledEnemyJungle"]),
    Var("Damage Dealt (Total)", "f", ["participants", get_pid, "stats", "totalDamageDealt"]),
    Var("Damage Dealt (To Champions)", "f", ["participants", get_pid, "stats", "totalDamageDealtToChampions"]),
    Var("Damage Dealt (To Objectives)", "f", ["participants", get_pid, "stats", "damageDealtToObjectives"]),
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
    Var("Gold/m Diff. (0 min \u2192 10 min)", "f", [get_gold_diffs, "0-10"]),
    Var("Gold/m Diff. (10 min \u2192 20 min)", "f", [get_gold_diffs, "10-20"]),
    Var("Gold/m Diff. (20 min \u2192 310 min)", "f", [get_gold_diffs, "20-30"]),
    Var("Gold/m Diff. (30 min \u2192 End)", "f", [get_gold_diffs, "30-end"]),

    Var("XP/min (0 min \u2192 10 min)", "f", ["participants", get_pid, "timeline", "xpPerMinDeltas", "0-10"]),
    Var("XP/min (10 min \u2192 20 min)", "f", ["participants", get_pid, "timeline", "xpPerMinDeltas", "10-20"]),
    Var("XP/min (20 min \u2192 30 min)", "f", ["participants", get_pid, "timeline", "xpPerMinDeltas", "20-30"]),
    Var("XP/min (30 min \u2192 End)", "f", ["participants", get_pid, "timeline", "xpPerMinDeltas", "30-end"]),
    Var("XP/m Diff. (0 min \u2192 10 min)", "f", ["participants", get_pid, "timeline", "xpDiffPerMinDeltas", "0-10"]),
    Var("XP/m Diff. (10 min \u2192 20 min)", "f", ["participants", get_pid, "timeline", "xpDiffPerMinDeltas", "10-20"]),
    Var("XP/m Diff. (20 min \u2192 30 min)", "f", ["participants", get_pid, "timeline", "xpDiffPerMinDeltas", "20-30"]),
    Var("XP/m Diff. (30 min \u2192 End)", "f", ["participants", get_pid, "timeline", "xpDiffPerMinDeltas", "30-end"]),

    Var("Fraction of Team Gold", "f", [get_fractions, "goldEarned"]),
    Var("Fraction of Team Damage (Total)", "f", [get_fractions, "totalDamageDealt"]),
    Var("Fraction of Team Damage (Total To Champs)", "f", [get_fractions, "totalDamageDealtToChampions"]),
    Var("Fraction of Team Damage (To Objectives)", "f", [get_fractions, "damageDealtToObjectives"]),
    Var("Fraction of Team Damage (Magic)", "f", [get_fractions, "magicDamageDealt"]),
    Var("Fraction of Team Damage (Magic vs. Champs)", "f", [get_fractions, "magicDamageDealtToChampions"]),
    Var("Fraction of Team Damage (Physical)", "f", [get_fractions, "physicalDamageDealt"]),
    Var("Fraction of Team Damage (Physical vs. Champs)", "f", [get_fractions, "physicalDamageDealtToChampions"]),
    Var("Fraction of Team Damage (True)", "f", [get_fractions, "trueDamageDealt"]),
    Var("Fraction of Team Damage (True vs. Champs)", "f", [get_fractions, "trueDamageDealtToChampions"]),
    Var("Fraction of Team Damage (Taken)", "f", [get_fractions, "totalDamageTaken"]),
    Var("Fraction of Team Damage (Mitigated)", "f", [get_fractions, "damageSelfMitigated"]),
    Var("Fraction of Team Damage (Taken + Mitigated)", "f", [get_fractions, "damageReceivedTotal"]),

    Var("Lane Opponent Champion", "s", ["participants", get_oid, "championId", clean_champion]),
    Var("Lane Opponent First Blood", "b", ["participants", get_oid, "stats", "firstBloodKill"]),
    Var("Lane Opponent Rank", "s", ["participants", get_oid, "highestAchievedSeasonTier"]),

    Var("Teammates (Number of)", "S", [get_num_teammates]),
    Var("Teammate (By Name)", "s", [get_teammates]),
    Var("Opponent (By Name)", "s", [get_opponents]),
    Var("Item", "s", [get_items]),
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
    "Fractions of damage-total/champs/taken, gold, xp": "",
}

# def parse_match_data(config_info, match_data, parsed_data):
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
#
#                 # match_data[ii]["participants"][pp]["timeline"]["creepsPerMinDeltas"]["zeroToTen"]
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
