# COMPILED FUNCTIONS FOR GENERATING PLOTS

# import ability to parse JSON objects
import json


# config_file = open("Configuration.LoHConfig", "r")
# config_info = json.loads(config_file.read())
# matchlist = open(config_info["Settings"]["SummonerName"] + "_MatchList.json", "r")
# matchlist = json.loads(matchlist.read())
# match_data_all = open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "r")
# match_data_all = json.loads(match_data_all.read())


def parse_match_data(match_data_all):
    print(match_data_all)
    n_matches = len(match_data_all)
    print(n_matches)
    for mm in range(n_matches):
        # the below line is working
        print(match_data_all[str(mm)]["season"])



def wr_vs_time(match_data_all):
        print(match_data_all)

""" ORIGINAL MATLAB CODE (REMOVING AS I GO ALONG ONCE REWRITTEN IN PYTHON)
%% LoL Summoner Statistics
% By JDC and SGS, Initial Version 2016-Oct
% See end of file for planned features and changelog.
%% Parse Stuff
clear WhatSeason WhatRole SeasonOpts ChooseSeason WinLoss PlayedWith PlayersByGame

for ii = 1:length(MatchList.matches)
    SeasonOpts{ii} = MatchList.matches(ii).season;
end
SeasonOpts = unique(SeasonOpts); % what seasons are available?
try
    ChooseSeason = menu('What Season',[SeasonOpts 'Last 15' 'Last 30' 'Last 50' 'All Games' 'Other']); % choose one
catch
    disp('Match analysis skipped')
    return
end
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

clear Champs Roles Side WinLoss MatchData MatchLengths MatchDate PlayedWith ChampWR
iii = 0;
for ii = 1:length(MatchesToAnalyze)
    if MatchesToAnalyze(ii).mapId == 11 && ~strcmp('RANKED_TEAM_5x5',MatchesToAnalyze(ii).queueType)
        iii = iii+1;
        MatchDate{iii} = datestr(MatchesToAnalyze(ii).matchCreation/86400000+...
            datenum(1970,1,1,-6,0,0),'yyyy-mm-dd HH:MM:SS'); % get the match date
        MatchLengths(iii) = MatchesToAnalyze(ii).matchDuration/60;

        % See who played & find which one was you
        for pp = 1:10
            PlayedWith{(iii-1)*10+pp} = MatchesToAnalyze(ii).participantIdentities(pp).player.summonerName;
            PlayersByGame{iii,pp} = MatchesToAnalyze(ii).participantIdentities(pp).player.summonerName;
            if str2double(SID) == MatchesToAnalyze(ii).participantIdentities(pp).player.summonerId
                MySummNum = pp; % which summoner were you?
            end
        end

        try
            Champs(iii) = MatchesToAnalyze(ii).participants(MySummNum).championId;
            Roles{iii} = MatchesToAnalyze(ii).participants(MySummNum).timeline.lane;
            Side(iii) = MatchesToAnalyze(ii).participants(MySummNum).teamId;
            Kills(iii) = MatchesToAnalyze(ii).participants(MySummNum).stats.kills;
            Deaths(iii) = MatchesToAnalyze(ii).participants(MySummNum).stats.deaths;
            Assists(iii) = MatchesToAnalyze(ii).participants(MySummNum).stats.assists;
            Gold(iii) = MatchesToAnalyze(ii).participants(MySummNum).stats.goldEarned;
            CS(iii) = MatchesToAnalyze(ii).participants(MySummNum).stats.minionsKilled;
            Multikill(iii) = MatchesToAnalyze(ii).participants(MySummNum).stats.largestMultiKill;
            WardsPlaced(iii) = MatchesToAnalyze(ii).participants(MySummNum).stats.wardsPlaced;
            WardsKilled(iii) = MatchesToAnalyze(ii).participants(MySummNum).stats.wardsKilled;
            DamageTotal(iii) = MatchesToAnalyze(ii).participants(MySummNum).stats.totalDamageDealt;
            DamageToChamps(iii) = MatchesToAnalyze(ii).participants(MySummNum).stats.totalDamageDealtToChampions;
%             CSAt10(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.creepsPerMinDeltas.zeroToTen;
%             CSAt20(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.creepsPerMinDeltas.tenToTwenty;
%             CSAt30(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.creepsPerMinDeltas.twentyToThirty;
%             CSDAt10(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.zeroToTen;
%             CSDAt20(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.tenToTwenty;
%             CSDAt30(iii) = MatchesToAnalyze(ii).participants(MySummNum).timeline.csDiffPerMinDeltas.twentyToThirty;
        catch
            Champs(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.championId;
            Roles{iii} = MatchesToAnalyze(ii).participants{MySummNum,1}.timeline.lane;
            Side(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.teamId;
            Kills(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.stats.kills;
            Deaths(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.stats.deaths;
            Assists(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.stats.assists;
            Gold(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.stats.goldEarned;
            CS(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.stats.minionsKilled;
            Multikill(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.stats.largestMultiKill;
            WardsPlaced(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.stats.wardsPlaced;
            WardsKilled(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.stats.wardsKilled;
            DamageTotal(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.stats.totalDamageDealt;
            DamageToChamps(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.stats.totalDamageDealtToChampions;
%             CSAt10(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.timeline.creepsPerMinDeltas.zeroToTen;
%             CSAt20(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.timeline.creepsPerMinDeltas.tenToTwenty;
%             CSAt30(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.timeline.creepsPerMinDeltas.twentyToThirty;
%             CSDAt10(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.timeline.csDiffPerMinDeltas.zeroToTen;
%             CSDAt20(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.timeline.csDiffPerMinDeltas.tenToTwenty;
%             CSDAt30(iii) = MatchesToAnalyze(ii).participants{MySummNum,1}.timeline.csDiffPerMinDeltas.twentyToThirty;
        end

        % See what side I was
        if Side(iii)==100 % blue side
            WinLoss(iii) = MatchesToAnalyze(ii).teams(1).winner;
        elseif Side(iii)==200 % red side
            WinLoss(iii) = MatchesToAnalyze(ii).teams(2).winner;
        end
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
