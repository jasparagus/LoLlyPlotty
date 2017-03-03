import json
import numpy
import matplotlib
matplotlib.use("TkAgg")
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


def wr_time(filtered_parsed_match_data):
    roll = 6
    n_matches = len(filtered_parsed_match_data["win_lose"])
    wr = sum(filtered_parsed_match_data["win_lose"])/n_matches
    # test = numpy.histogram([1, 2, 5], bins=10)
    if n_matches > roll:
        a, = plt.plot(
            running_mean(filtered_parsed_match_data["win_lose"], roll), label="Rolling WR", linestyle="-", color="r")
        b, = plt.plot([0, n_matches],[wr, wr], label="Avg. WR", linestyle="--", color="b")
        c, = plt.plot([0, n_matches],[0.5, 0.5], label="50% WR", linestyle=":", color="k")
        plt.xlabel("Match Number (Chronological)")
        plt.ylabel("Win Rate")
        plt.title("Winrate Over Time")
        plt.axis([0, n_matches, 0, 1])
        l1 = plt.legend(handles=[a], loc=1)
        plt.gca().add_artist(l1)
        l2 = plt.legend(handles=[b], loc=2)
        plt.gca().add_artist(l2)
        l3 = plt.legend(handles=[c], loc=3)
        plt.gca().add_artist(l3)
    else:
        print("Too few matches")


def wr_champ(filtered_parsed_match_data):
    """ Winrates for each champion played more than 3 games. """
    print("In progress")

    n_champs = len(filtered_parsed_match_data["champs_played"])
    n_games = len(filtered_parsed_match_data["win_lose"])
    wr = sum(filtered_parsed_match_data["win_lose"])/len(filtered_parsed_match_data["win_lose"])
    wins_by_champ = []
    n_by_champ = []

    for cc in range(n_champs):
        wins = []
        for gg in range(n_games):
            if filtered_parsed_match_data["champs_played"][cc] == filtered_parsed_match_data["champ"][gg]:
                wins.append(filtered_parsed_match_data["win_lose"][gg])
        wins_by_champ.append(sum(wins)/len(wins))
        n_by_champ.append(len(wins))

    # Make a figure to hold the plot and move it up relative to the baseline to leave room for labels
    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.2)

    locs = numpy.arange(n_champs)  # the x locations for the groups
    width = 0.5  # the width of the bars

    rects1 = ax.bar(locs, wins_by_champ, width, color='r')
    wrA, = plt.plot([0-width, n_champs+width], [wr, wr], label="Avg. WR", linestyle="--", color="b")
    wr50, = plt.plot([0-width, n_champs+width], [0.5, 0.5], label="50% WR", linestyle=":", color="k")

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Winrate')
    ax.set_title('Winrate by Champion')
    ax.set_xticks(locs)
    ax.set_xticklabels(filtered_parsed_match_data["champs_played"], rotation=45, ha="right")
    plt.xlim([0-width, n_champs+width])
    plt.ylim([0, 1.2])

    l2 = plt.legend(handles=[wrA], loc=2)
    plt.gca().add_artist(l2)
    l3 = plt.legend(handles=[wr50], loc=1)
    plt.gca().add_artist(l3)

    def autolabel(rects):
        """
        Attach a text label above each bar displaying its height
        """
        rr = 0
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2., height + 0.05,
                    'n = %d' % n_by_champ[rr],
                    ha='center', va='top')
            rr += 1

    autolabel(rects1)


def wr_teammate(filtered_parsed_match_data, n_played):
    """ Winrates on a per-teammate basis (with an N game cutoff for "teammates") """
    print("wr_teammate in progress")
    n_games = len(filtered_parsed_match_data["win_lose"])
    all_teammates = []

    # Get a list of every teammate
    for tt in range(n_games):
        all_teammates = all_teammates + filtered_parsed_match_data["teammates"][str(tt)]

    teammates_unique = sorted(list(set(all_teammates)))
    n_teammates = len(teammates_unique)
    wr = sum(filtered_parsed_match_data["win_lose"])/len(filtered_parsed_match_data["win_lose"])
    wins_by_teammate = []
    games_with_teammate = []
    teammates_unique_keep = []

    # For each unique teammate, look at every game and see if they were there and (if so) if it was a W/L
    for tt in range(n_teammates):
        wins = []
        for gg in range(n_games):
            if teammates_unique[tt] in filtered_parsed_match_data["teammates"][str(gg)]:
                wins.append(filtered_parsed_match_data["win_lose"][gg])
        if len(wins) >= n_played:
            wins_by_teammate.append(sum(wins)/len(wins))
            games_with_teammate.append(len(wins))
            teammates_unique_keep.append(teammates_unique[tt])

    n_teammates_kept = len(teammates_unique_keep)

    # Make plot
    fig, ax = plt.subplots()
    fig.subplots_adjust(bottom=0.3)

    locs = numpy.arange(n_teammates_kept)  # the x locations for the groups
    width = 0.5  # the width of the bars

    rects1 = ax.bar(locs, wins_by_teammate, width, color='r')
    wrA, = plt.plot([0-width, n_teammates_kept+width], [wr, wr], label="Avg. WR", linestyle="--", color="b")
    wr50, = plt.plot([0-width, n_teammates_kept+width], [0.5, 0.5], label="50% WR", linestyle=":", color="k")

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Winrate')
    ax.set_title('Winrate by Teammate')
    ax.set_xticks(locs)
    ax.set_xticklabels(teammates_unique_keep, rotation=45, ha="right")
    plt.xlim([0-width, n_teammates_kept+width])
    plt.ylim([0, 1.2])

    l2 = plt.legend(handles=[wrA], loc=2)
    plt.gca().add_artist(l2)
    l3 = plt.legend(handles=[wr50], loc=1)
    plt.gca().add_artist(l3)

    def autolabel(rects):
        """
        Attach a text label above each bar displaying its height
        """
        rr = 0
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2., height + 0.05,
                    'n = %d' % games_with_teammate[rr],
                    ha='center', va='top')
            rr += 1

    autolabel(rects1)


def wr_partysize(filtered_parsed_match_data, N):
    """ Winrates by number of recurring teammates (with an N game cutoff for "teammates") """
    plt.figure()
    x = 10 + 1 * numpy.random.randn(10000)
    n, bins, patches = plt.hist(x, 50, normed=0, facecolor='green', alpha=0.75)

    plt.xlabel('Meh')
    plt.ylabel('Probability')
    plt.title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
    # plt.axis([40, 160, 0, 0.03])
    plt.grid(True)


    print("wr_by_partysize in progress")


def wr_role(filtered_parsed_match_data):
    """ Winrate as a function of map side """
    plt.figure()
    print("wr_by_role DNE")

def wr_dmg(filtered_parsed_match_data):
    """ Winrate as a function of damage share (to champs / total / taken) """
    plt.figure()
    print("wr_vs_dmg DNE")


def wr_mapside(filtered_parsed_match_data):
    """ Winrate as a function of map side """
    plt.figure()
    print("wr_vs_mapside DNE")


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
