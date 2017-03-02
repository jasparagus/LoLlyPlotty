from APIFunctions import GetChamp


def parse_match_data(config_info, match_data_all):
    season = []
    queue_type = []

    n_matches = len(match_data_all)
    print("Parsing ", n_matches, "matches.")
    for mm in range(n_matches):
        # the below line is working
        season.append(match_data_all[str(mm)]["season"])
        queue_type.append(match_data_all[str(mm)]["queueType"])
    season_unique = list(set(season))
    # print(list(set(queue_type)))

    """ Scan through matches and only grab summoner's rift ones. """
    matches_to_analyze = {}
    mmm = 0
    for mm in range(n_matches):
        if match_data_all[str(mm)]["mapId"] == 11:
            matches_to_analyze[str(mmm)] = match_data_all[str(mm)]
            mmm += 1

    n_to_analyze = len(matches_to_analyze)

    win_lose = []
    match_lengths = []
    summ_num = []
    teammates = {}
    enemies = {}
    champ = []
    champs_played = []
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

    for mm in range(n_to_analyze):
        match_lengths.append(matches_to_analyze[str(mm)]["matchDuration"]/60)
        other_players = []
        others_damage_total = []
        others_damage_to_champs = []
        others_gold = []
        others_damage_taken = []
        for pp in range(10):
            if (str(matches_to_analyze[str(mm)]["participantIdentities"][pp]["player"]["summonerId"])
                    == config_info["Settings"]["SID"]):
                """ This case gathers data for the summoner using the app. """
                summ_num.append(pp)
                damage_total.append(
                    matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["totalDamageDealt"])
                damage_to_champs.append(
                    matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["totalDamageDealtToChampions"])
                damage_taken.append(
                    matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["totalDamageTaken"])
                gold.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["goldEarned"])
                win_lose.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["winner"])
                role.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["timeline"]["lane"])
                """ teamId: 100 is blue side; 200 is red side """
                map_side.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["teamId"])
                kills.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["kills"])
                deaths.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["deaths"])
                assists.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["assists"])
                cs.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["minionsKilled"])
                # try:
                #     csm_at_10.append(
                #         matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["timeline"]["creepsPerMinDeltas"][
                #             "zeroToTen"])
                # except:
                #     csm_at_10.append(["NaN"])
                # matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["timeline"]["creepsPerMinDeltas"]["zeroToTen"]
                # CSAt10(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.creepsPerMinDeltas.zeroToTen;
                # CSAt20(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.creepsPerMinDeltas.tenToTwenty;
                # CSAt30(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.creepsPerMinDeltas.twentyToThirty;
                # CStoEnd(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.creepsPerMinDeltas.thirtyToEnd;
                # CSDAt10(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.zeroToTen;
                # CSDAt20(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.tenToTwenty;
                # CSDAt30(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.twentyToThirty;
                # CSDtoEnd(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.thirtyToEnd;
                wards.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["wardsPlaced"])
                wards_killed.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["wardsKilled"])
                try:
                    kda.append((kills[mm]+assists[mm])/deaths[mm])
                except:
                    kda.append("perfect")
            else:
                """ This case builds temporary teammate variables that are overwritten for each new match. """
                other_players.append(matches_to_analyze[str(mm)]["participantIdentities"][pp]["player"]["summonerName"])
                others_damage_total.append(
                    matches_to_analyze[str(mm)]["participants"][pp]["stats"]["totalDamageDealt"])
                others_damage_to_champs.append(
                    matches_to_analyze[str(mm)]["participants"][pp]["stats"]["totalDamageDealtToChampions"])
                others_damage_taken.append(
                    matches_to_analyze[str(mm)]["participants"][pp]["stats"]["totalDamageTaken"])
                others_gold.append(matches_to_analyze[str(mm)]["participants"][pp]["stats"]["goldEarned"])
        if summ_num[mm] <=4:
            teammates[mm] = other_players[0:4]
            enemies[mm] = other_players[4:9]
            damage_total_frac.append(damage_total[mm]/(1+sum(others_damage_total[0:4])))
            damage_to_champs_frac.append(damage_to_champs[mm]/(1+sum(others_damage_to_champs[0:4])))
            damage_taken_frac.append(damage_taken[mm]/(1+sum(others_damage_taken[0:4])))
            gold_frac.append(gold[mm]/(1+sum(others_gold[0:4])))
        elif summ_num[mm] >= 5:
            teammates[mm] = other_players[5:9]
            enemies[mm] = other_players[0:5]
            damage_total_frac.append(damage_total[mm]/(1+sum(others_damage_total[5:9])))
            damage_to_champs_frac.append(damage_to_champs[mm]/(1+sum(others_damage_to_champs[5:9])))
            damage_taken_frac.append(damage_taken[mm]/(1+sum(others_damage_taken[5:9])))
            gold_frac.append(gold[mm]/(1+sum(others_gold[5:9])))
        # Get champ - this next part is ungodly slow because of the static API calls. Needs to be fixed.
        champ.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["championId"])
    champId_unique = list(set(champ))
    for cc in champId_unique:
        champs_played.append(GetChamp.get_champ(config_info, str(cc)))
    return {
        "season_unique":season_unique,
        "season":season,
        "win_lose":win_lose,
        "match_lengths":match_lengths,
        "teammates":teammates,
        "enemies":enemies,
        "champ":champ,
        "champs_played":champs_played,
        "role":role,
        "map_side":map_side,
        "kills":kills,
        "deaths":deaths,
        "assists":assists,
        "kda":kda,
        "damage_total":damage_total,
        "damage_to_champs":damage_to_champs,
        "damage_total_frac":damage_total_frac,
        "damage_to_champs_frac":damage_to_champs_frac,
        "damage_taken":damage_taken,
        "damage_taken_frac":damage_taken_frac,
        "gold":gold,
        "gold_frac":gold_frac,
        "cs":cs,
        "csm_at_10":csm_at_10,
        "csmd_at_10":csmd_at_10,
        "csm_at_20":csm_at_20,
        "csmd_at_20":csmd_at_20,
        "csm_at_30":csm_at_30,
        "csmd_at_30":csmd_at_30,
        "csm_aft_30":csm_aft_30,
        "csmd_aft_30":csmd_aft_30,
        "wards":wards,
        "wards_killed":wards_killed}


def filter(config_info, parsed_match_data, match_data_all, filter_opts):
    # Filters raw match data according to filter_opts; return surviving raw match data
    filtered_match_data = {}

    # Filter out remakes (games with length < 6 mins)
    n_mat = len(match_data_all)
    nn = 0
    for mm in range(n_mat):
        if parsed_match_data["match_lengths"][mm] > 6:
            filtered_match_data[str(nn)] = match_data_all[str(mm)]
            nn += 1
    # print(len(filtered_match_data))

    # Filter by desired season
    if "Y" in filter_opts["BySeason"]:
        # Overwrite "all" with previously filtered data
        match_data_all = filtered_match_data
        parsed_match_data = parse_match_data(config_info, match_data_all)
        n_mat = len(match_data_all)
        # Clear "filtered" data to begin rebuilding according to new filter
        filtered_match_data = {}
        nn=0
        for mm in range(n_mat):
            if parsed_match_data["season"][mm] == filter_opts["BySeason"]["Y"]:
                filtered_match_data[str(nn)] = match_data_all[str(mm)]
                print(filtered_match_data[str(nn)]["season"])
                nn += 1

    # Filter by desired champ
    # if "Y" in filter_opts["ByChamp"]:
    #     # Overwrite "all" with previously filtered data
    #     match_data_all = filtered_match_data
    #     parsed_match_data = parse_match_data(config_info, match_data_all)
    #     n_mat = len(match_data_all)
    #     # Clear "filtered" data to begin rebuilding according to new filter
    #     filtered_match_data = {}
    #     nn=0
    #     for mm in range(n_mat):
    #         champ = GetChamp.get_champ(config_info, parsed_match_data["champ"][mm])
    #         if champ == filter_opts["ByChamp"]["Y"]:
    #             print(champ)
    #             filtered_match_data[str(nn)] = match_data_all[str(mm)]
    #             print(filtered_match_data[str(nn)]["season"])
    #             nn += 1

    # Filter for only recent matches
    if "Y" in filter_opts["ByNMatches"]:
    # Overwrite "all" with previously filtered data
        match_data_all = filtered_match_data
        parsed_match_data = parse_match_data(config_info, match_data_all)
        n_mat = len(match_data_all)
        n_new_mat = filter_opts["ByNMatches"]["Y"]
        # Clear "filtered" data to begin rebuilding according to new filter
        filtered_match_data = {}
        for mm in range(n_mat-n_new_mat, n_mat):
            filtered_match_data[str(nn)] = match_data_all[str(mm)]
            print(mm)
            nn += 1

    return filtered_match_data
