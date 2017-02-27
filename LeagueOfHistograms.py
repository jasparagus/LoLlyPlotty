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
version 0.1
2017-02-24 - Added GUI made with tkinter. To-do: stop using print and switch to info in a tkinter display
2017-02-22 - Breaking out subroutines into separate files & making UI
2017-02-18, porting code from original MATLAB(TM) version. Jasper D. Cook.

"""

# IMPORT STANDARD MODULES
import json
import tkinter

# IMPORT CUSTOM MODULES
# import ConfigureLoH
# import GetRankedMatchData
from APIFunctions import ConfigureLoH
from APIFunctions import GetRankedMatchData


def lc():
    global config_info
    apikey = e_apikey.get()
    region = reg.get()
    summname = e_summname.get()
    config_info = ConfigureLoH.config(apikey, region, summname)


def gm():
    global config_info, match_data
    match_data = GetRankedMatchData.update_matchdata(config_info)
    return match_data


def plt():
    print(wr.get())


# FIRST, TRY TO LOAD STUFF
global config_info
try:
    config_file = open("Configuration.LoHConfig", "r")
    config_info = json.loads(config_file.read())
    apikey = config_info["Settings"]["APIKey"] # check that all pieces of config_info exist - use an actual if later
    region = config_info["Settings"]["Region"]
    summname = config_info["Settings"]["SummonerName"]
    sid = config_info["Settings"]["SID"]
    print("Config File Loaded At Startup")
except:
    apikey=""
    region="na"
    summname=""
    config_info = {}

status_message = "Starting"

# PREPARE A BOX TO HOLD OPTIONS & POPULATE IT WITH DEFAULTS FROM CONFIG FILE. GRID SIZE IS 15x5
root = tkinter.Tk()  # prepare a widget to hold the UI
root.title("League of Histograms")
# root.config()
# wwid = root.winfo_screenwidth()/4
# whei = root.winfo_screenheight()/2
# w = tkinter.Canvas(root, width=wwid, height=whei)
# w.pack()
# w.create_window(0, wwid/3, 0, whei/3)

# CONFIGURATION OPTIONS FRAME (SHOULD MAKE THIS A FRAME... ONCE I FIGURE OUT WHAT THAT IS)
l_apikey = tkinter.Label(root, text="Enter API Key")
l_apikey.grid(row=0, column=0)
e_apikey = tkinter.Entry(root, width=45, justify="center")
if config_info !={}:
    e_apikey.insert(0, apikey)
e_apikey.grid(row=1, column=0)

l_region = tkinter.Label(root, text="Select Region")
l_region.grid(row=2, column=0)
if config_info !={}:
    reg = tkinter.StringVar(value=region)
else:
    reg = tkinter.StringVar(value="na")
o_region = tkinter.OptionMenu(root, reg,
                              "br", "eune", "euw", "jp", "kr", "lan", "las",
                              "na", "oce", "tr", "ru", "pbe", "global"
                              )
o_region.grid(row=3, column=0)


l_summname = tkinter.Label(root, text="Enter Summoner Name")
l_summname.grid(row=4, column=0)
e_summname = tkinter.Entry(root, width=45, justify="center")
if config_info !={}:
    e_summname.insert(0, summname)
e_summname.grid(row=5, column=0)


b_lc = tkinter.Button(root, text="Update LoH Settings", width=25, command=lc)
b_lc.grid(row=6, column=0, columnspan=2)


b_gm = tkinter.Button(root, text="Update Match Data", width=20, command=gm)
b_gm.grid(row=7, column=0, columnspan=2)

# PLOTTING OPTIONS FRAME (SHOULD MAKE THIS A FRAME... ONCE I FIGURE OUT WHAT THAT IS)
l_plots = tkinter.Label(root, text="Select Plots To Generate")
l_plots.grid(row=0, column=3)

# SELECT TIMEFRAME TO PLOT, POPULATED BASED ON KNOWN MATCH RANGE, ETC, USING RADIO BUTTON

wr = tkinter.IntVar(value=0)
c_wr = tkinter.Checkbutton(root, text="Winrate vs. Time", variable=wr)
c_wr.grid(row=1, column=3)


b_plt = tkinter.Button(root, text="Generate Selected Plots", width=20, command=plt)
b_plt.grid(row=7, column=3, columnspan=2)


# Should pack this inside a function & update it every once in a while
l_status = tkinter.Label(root, text="Status: " + status_message)
l_status.grid(row=10, column=3)


e_apikey.focus_set() # set the focus on the first entry box
root.mainloop() # start the application loop
print("Done")


""" ORIGINAL MATLAB CODE (REMOVING AS I GO ALONG ONCE REWRITTEN IN PYTHON)
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
