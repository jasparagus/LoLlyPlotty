def prep_teammates(config_info, match_data):

    match_ids = sorted(list(match_data.keys()))
    teammates = []

    for match_id in match_ids:
        match = match_data[match_id]
        n_players = len(match["participantIdentities"])
        pid = ["Unknown"]
        tid = ["Unknown"]
        for ii in range(n_players):
            if str(match["participantIdentities"][ii]["player"]["accountId"]) == str(config_info["AccountID"]):
                pid = ii
                tid = match["participants"][ii]["teamId"]
                break

        for ii in range(n_players):
            if str(match["participants"][ii]["teamId"]) == str(tid) and ii != pid:
                teammates += [match["participantIdentities"][ii]["player"]["summonerName"]]

    teammates_unique = sorted(list(set(teammates)))
    teammates_games_played = []

    for teammate in teammates_unique.copy():
        times_played_with = teammates.count(teammate)
        if int(times_played_with) < int(config_info["Threshold"]):
            teammates_unique.remove(teammate)
        else:
            teammates_games_played += [times_played_with]

    config_info["Teammates"] = teammates_unique
    config_info["TeammatesGamesPlayed"] = teammates_games_played

    return config_info
