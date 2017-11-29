import time


def clean_binary(config_info, bin_var):
    if bin_var == 1 or bin_var == "True":
        clean_var = 1
    elif bin_var == 0 or bin_var == "False":
        clean_var = 0
    else:
        clean_var = "Unknown"
    return clean_var


def clean_champion(config_info, champ_id):
    try:
        champ_name = config_info["champion"][str(champ_id)]
    except:
        champ_name = "Unknown"
    return champ_name


def clean_game_duration(config_info, game_duration):
    match_length = round(float(game_duration) / 60, 2)  # match length in minutes
    return match_length


def clean_item(config_info, item_id):
    try:
        item_name = config_info["item"][str(item_id)]
    except KeyError:
        item_name = "Item " + str(item_id) + " (Deprecated Item ID)"
    return item_name


def clean_map(config_info, map_id):
    try:
        map_clean = config_info["maps.gameconstants"][str(map_id)]
    except:
        map_clean = "Unknown"
    return map_clean


def clean_num_teammates(config_info, num_teammates):
    num_teammates_clean = str(num_teammates)
    return num_teammates_clean


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


def clean_season(config_info, season_id):
    try:
        season_clean = config_info["seasons.gameconstants"][str(season_id)]
    except:
        season_clean = "Unknown"
    return season_clean


def clean_summoner_spell(config_info, spell_id):
    try:
        spell_name = config_info["summoner"][str(spell_id)]
    except:
        spell_name = "Unknown"
    return spell_name


def clean_team(config_info, team):
    if int(team) == 100:
        map_side = "Blue"
    elif int(team) == 200:
        map_side = "Red"
    else:
        map_side = "Other"
    return map_side


def clean_timestamp(config_info, timestamp):
    try:
        age_days = (float(time.time()) - (float(timestamp) / 1000)) / 86400  # convert seconds to days
    except ValueError:
        age_days = "Unknown"
    return age_days
