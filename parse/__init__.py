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
from parse.clean import *
from parse.get import *
from parse.prep import *

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


class Var:
    names = []  # A list of all instance names
    b_vars = []  # A list of instances for which the variable is a boolean (True/False)
    f_vars = []  # A list of instances for which the variable is best-suited to "float" type (e.g. Gold or Damage)
    s_vars = []  # A list of instances for which the variable is best stored as a string (e.g. Role))
    c_vars = []  # A list of incrementing variables (e.g. games played or time played)
    q_vars = []  # Variables that aren't plotted using a normal plot function (e.g. "Most Kills")

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
                    if step.__name__[0:6] == "clean_":
                        # clean functions take config_info and the previous step's result (the value to be cleaned)
                        if type(self.value) is list:
                            # if cleaning a list, clean each item one by one
                            vals = []
                            for vv in self.value:
                                vals += [step(config_info, vv)]
                            self.value = vals
                        else:
                            # if cleaning a single item, clean the single item...
                            self.value = step(config_info, self.value)
                    elif step.__name__[0:4] == "get_":
                        # get functions take config_info and the match, from which they get the appropriate value
                        temp_step = step(config_info, match)
                        if type(temp_step) in [dict, list]:
                            # If the output is a dictionary or list, the step is done; move on
                            self.value = temp_step
                        else:
                            # if the output is not a dictionary, extract the value using the appropriate key
                            try:
                                self.value = self.value[temp_step]
                            except KeyError as e:
                                self.value = temp_step
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

        # Handle prep steps in x and y if necessary
        for step in vars_list[cls.names.index(y_var_name)].path + vars_list[cls.names.index(x_var_name)].path:
            if type(step) is types.FunctionType:
                if step.__name__[0:5] == "prep_":
                    # prep functions go through all matches, updating config info for subsequent steps
                    config_info = step(config_info, match_data)


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
    Var("Champion (Played By Teammate or Enemy)", "s", [get_non_player_champs, clean_champion]),
    Var("Champion (Played by Teammate)", "s", [get_teammate_champs, clean_champion]),
    Var("Champion (Played by Enemy)", "s", [get_enemy_champs, clean_champion]),
    Var("Summoner Spell 1", "s", ["participants", get_pid, "spell1Id", clean_summoner_spell]),
    Var("Summoner Spell 2", "s", ["participants", get_pid, "spell2Id", clean_summoner_spell]),

    Var("Champion (Lane Opponent's)", "s", ["participants", get_oid, "championId", clean_champion]),
    Var("Lane Opponent First Blood", "b", ["participants", get_oid, "stats", "firstBloodKill"]),
    Var("Lane Opponent Rank", "s", ["participants", get_oid, "highestAchievedSeasonTier"]),

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
    Var("Gold/m Diff. (20 min \u2192 30 min)", "f", [get_gold_diffs, "20-30"]),
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
    Var("Fraction of Team Damage (Total, To Champs)", "f", [get_fractions, "totalDamageDealtToChampions"]),
    Var("Fraction of Team Damage (To Objectives)", "f", [get_fractions, "damageDealtToObjectives"]),
    Var("Fraction of Team Damage (Magic)", "f", [get_fractions, "magicDamageDealt"]),
    Var("Fraction of Team Damage (Magic, To Champs)", "f", [get_fractions, "magicDamageDealtToChampions"]),
    Var("Fraction of Team Damage (Physical)", "f", [get_fractions, "physicalDamageDealt"]),
    Var("Fraction of Team Damage (Physical, To Champs)", "f", [get_fractions, "physicalDamageDealtToChampions"]),
    Var("Fraction of Team Damage (True)", "f", [get_fractions, "trueDamageDealt"]),
    Var("Fraction of Team Damage (True, To Champs)", "f", [get_fractions, "trueDamageDealtToChampions"]),
    Var("Fraction of Team Damage (Taken)", "f", [get_fractions, "totalDamageTaken"]),
    Var("Fraction of Team Damage (Mitigated)", "f", [get_fractions, "damageSelfMitigated"]),
    Var("Fraction of Team Damage (Taken + Mitigated)", "f", [get_fractions, "damageReceivedTotal"]),

    Var("Teammates (Number of)", "s", [prep_teammates, get_num_teammates, clean_num_teammates]),
    Var("Teammate (By Name)", "s", [get_teammates]),
    Var("Opponent (By Name)", "s", [get_opponents]),
    Var("Item", "s", [get_items, clean_item]),
]

GeneralStats = {
    # TODO: generate prep functions for all of these general stats
    "Total Hours Played": [],
    "Number of Unique Champions": [],
    "Most Kills (All Time)": "",
    "Most Deaths (All Time)": "",
    "Most Assists (All Time)": "",
}
