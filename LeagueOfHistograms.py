"""
LEAGUE OF HISTOGRAMS, v0.1
--------------------
Obtains ranked summoner information and visualizes it.
Features (planned or completed):
Per-champion winrates
Per-teammate winrates
Per-number-teammate winrates (for most-played-with teammates)
Rolling average winrate
Per-role winrates

Changelog:
version 0.1, 2017-02-18, porting code from original MATLAB(TM) version. Jasper D. Cook.
2017-02-22 - Breaking out subroutines into separate files & making UI
"""

# IMPORT STANDARD MODULES
import numpy # import numpy to data manipulation and plotting
import matplotlib.pyplot # no idea if this is useful yet
import tkinter.simpledialog # for getting user input
import json


# IMPORT CUSTOM MODULES
import GetSID


# PREPARE A BOX TO HOLD OPTIONS
root = tkinter.Toplevel()  # prepare a toplevel widget to hold the UI
root.title("League of Histograms")
root.config(width=400, height=800)


# the above is necessary or tkinter doesn't seem to know where to put things... turns out I have no idea what I'm doing.
test = tkinter.simpledialog.askstring(title="test title", prompt="testprompt")

# TRY TO LOAD CONFIG FILE; IF IT DOESN'T EXIST, MAKE IT FROM BASIC APP INFO
try:
    config_file = open("Configuration.LoHConfig", "r")
    import json
    config_loaded = json.loads(config_file.read())
    APIKey = config_loaded["settings"]["APIKey"]
    SummonerName = config_loaded["settings"]["SummonerName"]
    SID = config_loaded["settings"]["SID"]
    print("Config File Loaded Successfully")
except:
    # GRAB API KEY AND SUMMONER ID IF NEEDED
    config_info = {} # try to create a JSON object for config info
    APIKey = tkinter.simpledialog.askstring(title="Enter API Key", prompt="API Key")
    APIKey = APIKey.replace(" ", "")  # strip any accidental spaces
    RegionList = ["br", "eune", "euw", "jp", "kr", "lan", "las", "na", "oce", "tr", "ru", "pbe", "global"]

    Region = tkinter.simpledialog.askstring("Select Region", "Region", initialvalue="na")
    # the above should eventually be changed to a dropdown list

    SummonerName = tkinter.simpledialog.askstring(title="Enter Summoner Name", prompt="Summoner Name", initialvalue="SUMMONERNAME")
    SummonerName = SummonerName.replace(" ", "").lower()  # strip unacceptable spaces and caps from SummonerName

    SID = GetSID.get_sid(APIKey, Region, SummonerName)

    config_info = ({"settings":{
        "APIKey": APIKey,
        "region":Region,
        "SummonerName":SummonerName,
        "SID":SID}}
    )
    json.dump(config_info, open("Configuration.LoHConfig", 'w'))
    print("Config File Created Successfully")


# GET LIST OF RANKED MATCHES
# exec(open("GetRankedMatches.py").read(), globals())

print("Done")

# Matlab code for this part follows
# %% Get Match Info
# clear MatchInfo MatchesToAdd
# try % try to load existing match info file, if it exists.
#     load(['MatchInfo_' SummonerName '.mat']);
#     LastMatchSaved = num2str(MatchInfo(1).matchId); % get the most recent match
#         % that's in the match info file
#     for ii = 1:length(matchIDs)
#         MatchesSaved(ii) = strcmp(LastMatchSaved,matchIDs{ii}); % make a logical
#             % array of the retrieved matches with a 1 where the most recent
#             % match in the match info file is located
#     end
#     if sum(MatchesSaved)==1 % there should only be one one in the above array
#         [~,FirstMatchFound] = max(MatchesSaved); % find the index in the above
#             % array where the 1 is. That's where you'll start
#     else
#         disp('Something Wrong With Loaded Matches, Reloading')
#         FirstMatchFound = length(matchIDs);
#         MatchInfo = {};
#     end
# catch
#     disp('Unable to Load Existing Matches From File; Starting Fresh')
#     FirstMatchFound = length(matchIDs)+1; % this +1 is necessary to load the
#         % very first match.
#     MatchInfo = {};
# end
#
# MatchesToAdd = fliplr(matchIDs(1:FirstMatchFound-1)); % I think this may be
#     % the problem line
# ii=1;
# while ii<=length(MatchesToAdd)
#     disp(['Getting Info For Match ' num2str(ii) '/' num2str(length(MatchesToAdd))])
#     retried = 0;
#     while retried < MaxRetries
#         try
#             MatchInfo = [webread([base 'v2.2/match/' MatchesToAdd{ii} '?' key]) MatchInfo];
#             GotMatch(ii) = 1;
#             break
#         catch
#             GotMatch(ii) = 0; % haven't gotten it yet
#             retried = retried+1;
#             disp(['Retried ' num2str(retried) ' Times. Pausing Before Retrying Again.'])
#             pause(3)
#         end
#     end
#     pause(1.3)
#     ii=ii+1;
# end
#
# for ii = 1:length(MatchInfo)
#     Gotmatches(ii) = MatchInfo(ii).matchId == str2double(matchIDs{ii});
# end
# disp(['Are All Matches Loaded? (1/0): ' num2str(sum(Gotmatches)==length(matchIDs))])
# save(['MatchInfo_' SummonerName '.mat'],'MatchInfo')


"""
random_state = numpy.random.RandomState(19680801)
X = random_state.randn(10000)

fig, ax = plt.subplots()
ax.hist(X, bins=25, normed=True)
x = numpy.linspace(-5, 5, 1000)
ax.plot(x, 1 / numpy.sqrt(2*np.pi) * numpy.exp(-(x**2)/2), linewidth=4)
ax.set_xticks(numpy.linspace(-5,5,5))
ax.set_yticks(numpy.linspace(0,1,5))
fig.savefig("histogram.png", dpi=150)  # results in 160x120 px image
"""


""" ORIGINAL MATLAB CODE (REMOVE AS ADAPTED FOR PYTHON
%% LoL Summoner Statistics
% By JDC and SGS, Initial Version 2016-Oct
% See end of file for planned features and changelog.
clear all
SummonerName = inputdlg('Enter Summoner Name (No Caps/Spaces)','Summoner Name',1,{'jasparagus'});
SummonerName = SummonerName{1};
SummonerName = lower(SummonerName); % Convert it to lower case
SummonerName(SummonerName==' ')='';
key = 'api_key=RGAPI-d89bba97-f44c-433f-baf0-75e5fbe4db9c'; % Jasper's key
base = 'https://na.api.pvp.net/api/lol/na/'; % Base URL for all API calls
MaxRetries = 75; % Upper limit of API calls before ending the program

%% GET SUMMONER ID - PORTED/WORKING

%% GET LIST OF MATCHES - PORTED/WORKING
for ii = 1:length(MatchList.matches)
    matchIDs{ii} = num2str(MatchList.matches(ii).matchId);
end

%% Get Match Info
clear MatchInfo MatchesToAdd
try % try to load existing match info file, if it exists.
    load(['MatchInfo_' SummonerName '.mat']);
    LastMatchSaved = num2str(MatchInfo(1).matchId); % get the most recent match
        % that's in the match info file
    for ii = 1:length(matchIDs)
        MatchesSaved(ii) = strcmp(LastMatchSaved,matchIDs{ii}); % make a logical
            % array of the retrieved matches with a 1 where the most recent
            % match in the match info file is located
    end
    if sum(MatchesSaved)==1 % there should only be one one in the above array
        [~,FirstMatchFound] = max(MatchesSaved); % find the index in the above
            % array where the 1 is. That's where you'll start
    else
        disp('Something Wrong With Loaded Matches, Reloading')
        FirstMatchFound = length(matchIDs);
        MatchInfo = {};
    end
catch
    disp('Unable to Load Existing Matches From File; Starting Fresh')
    FirstMatchFound = length(matchIDs)+1; % this +1 is necessary to load the
        % very first match.
    MatchInfo = {};
end

MatchesToAdd = fliplr(matchIDs(1:FirstMatchFound-1)); % I think this may be
    % the problem line
ii=1;
while ii<=length(MatchesToAdd)
    disp(['Getting Info For Match ' num2str(ii) '/' num2str(length(MatchesToAdd))])
    retried = 0;
    while retried < MaxRetries
        try
            MatchInfo = [webread([base 'v2.2/match/' MatchesToAdd{ii} '?' key]) MatchInfo];
            GotMatch(ii) = 1;
            break
        catch
            GotMatch(ii) = 0; % haven't gotten it yet
            retried = retried+1;
            disp(['Retried ' num2str(retried) ' Times. Pausing Before Retrying Again.'])
            pause(3)
        end
    end
    pause(1.3)
    ii=ii+1;
end

for ii = 1:length(MatchInfo)
    Gotmatches(ii) = MatchInfo(ii).matchId == str2double(matchIDs{ii});
end
disp(['Are All Matches Loaded? (1/0): ' num2str(sum(Gotmatches)==length(matchIDs))])
save(['MatchInfo_' SummonerName '.mat'],'MatchInfo')

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
