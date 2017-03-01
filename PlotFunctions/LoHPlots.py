# COMPILED FUNCTIONS FOR GENERATING PLOTS

# import ability to parse JSON objects
import json
# import numpy to make working with data easier
import numpy
from APIFunctions import GetRankedMatchData

# config_file = open("Configuration.LoHConfig", "r")
# config_info = json.loads(config_file.read())
# matchlist = open(config_info["Settings"]["SummonerName"] + "_MatchList.json", "r")
# matchlist = json.loads(matchlist.read())
# match_data_all = open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "r")
# match_data_all = json.loads(match_data_all.read())


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
    print(season_unique)
    print(list(set(queue_type)))

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
                """ 100 is blue side; 200 is red side """
                map_side.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["teamId"])
                kills.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["kills"])
                deaths.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["deaths"])
                assists.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["assists"])
                cs.append(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["stats"]["minionsKilled"])
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
        champ.append(
            GetRankedMatchData.get_champ(
                config_info,
                str(matches_to_analyze[str(mm)]["participants"][summ_num[mm]]["championId"]))
        )
    champ_unique = list(set(champ))
    # match_data_parsed = {} # FIGURE OUT HOW TO COMPILE THE ABOVE VARIABLES INTO AN OBJECT/CLASS/WHATEVER.
    #
    return {
        "season_unique":season_unique,
        "season":season,
        "win_lose":win_lose,
        "match_lengths":match_lengths,
        "teammates":teammates,
        "enemies":enemies,
        "champ":champ,
        "champ_unique":champ_unique,
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
        "wards":wards,
        "wards_killed":wards_killed}

"""
%             CSAt10(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.creepsPerMinDeltas.zeroToTen;
%             CSAt20(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.creepsPerMinDeltas.tenToTwenty;
%             CSAt30(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.creepsPerMinDeltas.twentyToThirty;
%             CSDAt10(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.zeroToTen;
%             CSDAt20(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.tenToTwenty;
%             CSDAt30(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.twentyToThirty;
"""

def filter(match_data_all, parsed_match_data, filter_opts):
    filtered_parsed_match_data = {}
    if "Y" in filter_opts["BySeason"]:
        print("Filtering For Season = " + filter_opts["BySeason"]["Y"])
        filtered_parsed_match_data = parsed_match_data
        # loop over matches, checking match season against filtered season
        mm = 0
        match_data_all[str(mm)]["season"] == filter_opts["BySeason"]["Y"]
    if "Y" in filter_opts["ByChamp"]:
        print("Filtering For Champ = " + filter_opts["ByChamp"]["Y"])
    if "Y" in filter_opts["ByMatch"]:
        print("Filtering For Last " + str(filter_opts["ByMatch"]["Y"]) + " matches")

    filtered_parsed_match_data = parsed_match_data
    return(filtered_parsed_match_data)


def wr_vs_time(match_data_all):
    print("Plotting win % vs. time for selected match range.")

""" ORIGINAL MATLAB CODE (REMOVING AS I GO ALONG ONCE REWRITTEN IN PYTHON)
if ChooseSeason<=length(SeasonOpts) % if you chose a season
    for ii = 1:length(MatchList.matches)
        WhatSeason(ii) = strcmp(MatchList.matches(ii).season,SeasonOpts(ChooseSeason)); % which games to keep
    end
    Keepers = logical(WhatSeason.*WhatSeason);
    MatchesToAnalyze = MatchInfo(Keepers);
elseif ChooseSeason == length(SeasonOpts)+1 % if you chose last 15
    try
        MatchesToAnalyze = MatchInfo(1:15);
    catch
        MatchesToAnalyze = MatchInfo;
        disp('Found Fewer Than 15 Games; Displaying All')
    end
elseif ChooseSeason == length(SeasonOpts)+2 % if you chose last 30
    try
        MatchesToAnalyze = MatchInfo(1:30);
    catch
        MatchesToAnalyze = MatchInfo;
        disp('Found Fewer Than 30 Games; Displaying All')
    end
elseif ChooseSeason == length(SeasonOpts)+3 % if you chose last 50
    try
        MatchesToAnalyze = MatchInfo(1:50);
    catch
        MatchesToAnalyze = MatchInfo;
        disp('Found Fewer Than 50 Games; Displaying All')
    end
elseif ChooseSeason == length(SeasonOpts)+4 % if you chose last 30
    MatchesToAnalyze = MatchInfo;
elseif ChooseSeason == length(SeasonOpts)+5 % if you chose "Other"
    try
        MatchesToAnalyze = MatchInfo(1:str2double(inputdlg('Enter # of Matches','Enter Number',1,{'10'})));
    catch
        MatchesToAnalyze = MatchInfo;
        disp('Found Fewer Than 50 Games; Displaying All')
    end
end

% Analysis of Data
[UniquePlayers,ia,ic] = unique(PlayedWith);
clear PlayedWithMat PlayedWithVec nPlayedWith WinRateWith nPlayedWithStr
clear SortInd WinRateByNTMs
for ii = 1:length(UniquePlayers)
    PlayedWithMat = strfind(PlayersByGame,UniquePlayers{ii});
    PlayedWithMat = not(cellfun('isempty',PlayedWithMat));
    PlayedWithVec(:,ii) = logical(sum(PlayedWithMat,2)');
    nPlayedWith(ii) = sum(sum(PlayedWithMat,2));
    nPlayedWithStr{ii} = num2str(nPlayedWith(ii));
    WinRateWith(ii) = mean(WinLoss(PlayedWithVec(:,ii)'));
end

[nPlayedWith,SortInd] = sort(nPlayedWith);
nPlayedWith = fliplr(nPlayedWith);
SortInd = fliplr(SortInd);
UniquePlayers = UniquePlayers(SortInd);
PlayedWithVec = PlayedWithVec(:,SortInd);
WinRateWith = WinRateWith(SortInd);

PlayedWithToKeep = [];
UniquePlayersToKeep = {};
WinRateWithToKeep = [];
nPlayedWithStr = {};
nPlayedWithToKeep = [];
for ii = 1:length(UniquePlayers)
    if nPlayedWith(ii)>2
        UniquePlayersToKeep = [UniquePlayersToKeep UniquePlayers(ii)];
        PlayedWithToKeep = [PlayedWithToKeep,PlayedWithVec(:,ii)];
        WinRateWithToKeep = [WinRateWithToKeep WinRateWith(ii)];
        nPlayedWithStr = [nPlayedWithStr {['n=' num2str(nPlayedWith(ii))]}];
        nPlayedWithToKeep = [nPlayedWithToKeep nPlayedWith(ii)];
    end
end

figure(1),clf,hold on
plot(0:length(UniquePlayersToKeep)+1,mean(WinLoss)*ones(size(0:length(UniquePlayersToKeep)+1)),'--k')
plot(0:length(UniquePlayersToKeep)+1,0.5*ones(size(0:length(UniquePlayersToKeep)+1)),':k')
bar(1:length(UniquePlayersToKeep),WinRateWithToKeep,'g')
ylim([0 1])
xlabel('Teammate')
set(gca,'xtick',1:length(UniquePlayersToKeep),'xticklabel',UniquePlayersToKeep,'XTickLabelRotation',30)
ylabel('Winrate')
for ii = 1:length(UniquePlayersToKeep)
    text(ii-.3,0.05,nPlayedWithStr{ii},'fontsize',24);
end
title(['Per-Teammate Winrates For ' MatchDate{end}(1:end-9) ' to ' MatchDate{1}(1:end-9)])
print([SummonerName ' Teammmate Stats.png'],'-dpng')

figure(2),clf % Winrate by the number of pre-grouped teammates
hold on
NumTeammates = sum(PlayedWithToKeep,2);
% [NumTeammates,TeammatesSortInd] = sort(NumTeammates);
for ii=1:5
    WinRateByNTMs(ii) = mean(WinLoss(NumTeammates==ii));
    bar(ii,WinRateByNTMs(ii),'g')
    text(ii-.3,0.05,['n=' num2str(sum(NumTeammates==ii))],'fontsize',24);
end
plot(0:6,mean(WinLoss)*ones(1,7),'--k')
plot(0:6,0.5*ones(1,7),':k')
ylim([0 1])
xlabel('Premade Queue Size')
set(gca,'xtick',1:5,'xticklabel',{1,2,3,4,5})
ylabel('Winrate')
title(['Winrates By Party Size For ' MatchDate{end}(1:end-9) ' to ' MatchDate{1}(1:end-9)])
print([SummonerName ' Per Num Teammates Chart.png'],'-dpng')

clear ChampsUnique ChampsNames ChampsDetails
[ChampsUnique,ia,ic] = unique(Champs);
for ii = 1:length(ChampsUnique)
    ChampsDetails{ii} = webread(['https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion/' num2str(ChampsUnique(ii)) '?' key]);
    ChampsNames{ii} = ChampsDetails{ii}.name;
end

for cc = 1:length(ChampsUnique)
    ChampWR{cc} = [num2str(100*mean(WinLoss(Champs==ChampsUnique(cc))),3) '%'];
end

figure(3),clf
ChampSorting = categorical(Champs,ChampsUnique,ChampsNames);
ChampHistog = histogram(ChampSorting);
for ii = 1:length(ChampsUnique)
    text(ii-0.25,max(ChampHistog.Values)*0.1,ChampWR{ii},'fontsize',24);
end
ylabel('Times Played')
hold on
title(['Champion Statistics For ' MatchDate{end}(1:end-9) ' to ' MatchDate{1}(1:end-9)])
print([SummonerName ' Champs Histogram.png'],'-dpng')

% Rolling Winrates
WinLossRolling = [];
RollSize = 2; % grab n games on either side
for ii = 1:length(WinLoss)
    if ii<=RollSize
        WinLossRolling(ii) = mean(WinLoss(1:ii+RollSize));
    elseif ii>=length(WinLoss)-RollSize
        WinLossRolling(ii) = mean(WinLoss(ii-RollSize:end));
    else
        WinLossRolling(ii) = mean(WinLoss(ii-RollSize:ii+RollSize));
    end
end
figure(4),clf,hold on
plot(fliplr(WinLossRolling),'k')
plot(0.5*ones(size(WinLossRolling)),':k')
plot(mean(WinLoss)*ones(size(WinLossRolling)),'--k')
xlabel('Game Number (Newest Last)')
ylabel('Winrate')
title(['Rolling Average Winrate (Blocks Of ' num2str(2*RollSize+1) ' Games)'])
axis([1 length(WinLoss) 0 1])
print([SummonerName ' Rolling Winrate.png'],'-dpng')

%% Feature Wishlist
% More detailed stats (CS differential, lane opponent, KDA, kill
    % participation

%% Changelog
%{

BEGIN ORIGINAL MATLAB VERSION
2016-12-06 Added "Other" option to number of games to parse so that you can
choose an arbitrary number of games to get statistics on.

2016-10-27 Added error handling for incorrect summoner names (if they have
spaces or if they have capitals). Deletes all spaces and replaces all
capital letters with lower case ones.

2016-10-25 SGS Added a feature to show winrate as a function of number of
teammates.
%}

"""
