import json
import numpy
import matplotlib.pyplot as plt


""" FOR TESTING STUFF OUT
import json
import numpy
import matplotlib.pyplot as plt
config_file = open("Configuration.LoHConfig", "r")
config_info = json.loads(config_file.read())
filtered_parsed_match_data = open(config_info["Settings"]["SummonerName"] + "_ParsedMatchData.LoHData", "r")
filtered_parsed_match_data = json.loads(filtered_parsed_match_data.read())
"""

def wr_vs_time(filtered_parsed_match_data):
    roll = 5
    n_matches = len(filtered_parsed_match_data["win_lose"])
    wr = sum(filtered_parsed_match_data["win_lose"])/n_matches
    # test = numpy.histogram([1, 2, 5], bins=10)
    if n_matches > roll:
        a, = plt.plot(running_mean(filtered_parsed_match_data["win_lose"], roll), label="Rolling Average WR")
        b, = plt.plot([0, n_matches],[wr, wr], label="Average WR", linestyle="--")
        plt.xlabel("Match Number (Chronological)")
        plt.ylabel("Win Rate")
        plt.title("Winrate Over Time")
        plt.axis([0, n_matches, 0, 1])
        l1 = plt.legend(handles=[a], loc=1)
        plt.gca().add_artist(l1)
        l2 = plt.legend(handles=[b], loc=2)
        plt.gca().add_artist(l2)
        plt.show()
    else:
        print("Too few matches")


def wr_vs_champ(filtered_parsed_match_data):
    print("wr_vs_champ DNE yet")


def wr_vs_teammate(filtered_parsed_match_data):
    print("wr_vs_teammate DNE yet")


def running_mean(l, N):
    sum = 0
    result = list( 0 for x in l)
    for i in range( 0, N ):
        sum = sum + l[i]
        result[i] = sum / (i+1)
    for i in range( N, len(l) ):
        sum = sum - l[i-N] + l[i]
        result[i] = sum / N
    return result

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
