import urllib.request # import ability to make URL requests
import urllib.error # import error handler for URL requests
import json # import ability to parse JSON objects
import time # import time to allow for use of time.sleep(secs). Prevents excessive api calls


# config_file = open("Configuration.LoHConfig", "r")
# config_info = json.loads(config_file.read())
# matchlist = open(config_info["Settings"]["SummonerName"] + "_MatchList.json", "r")
# matchlist = json.loads(matchlist.read())
# from APIFunctions import GetRankedMatchData


def update_matchdata(config_info):
    """ Pulls down list of matches, checks against saved data, grabs missing data, saves everything. """
    match_data_loaded = {}
    match_data = {}
    new_matches = []
    BaseURL = "https://na.api.pvp.net/api/lol/"
    matchlist_call = (BaseURL + config_info["Settings"]["Region"]
                     + "/v2.2/matchlist/by-summoner/"
                     + config_info["Settings"]["SID"]
                     + "?api_key="
                     + config_info["Settings"]["APIKey"])
    attempt = 0
    while attempt < 10:
        print("Getting list of all ranked matches (newest first). Attempt #" + str(attempt+1) + "/10")
        time.sleep(2)  # wait a sec to avoid excessive API calls with repeated retries
        try:
            matchlist_reply = urllib.request.urlopen(matchlist_call)
            matchlist_reply = matchlist_reply.read()
            matchlist = json.loads(matchlist_reply)
            print("Matchlist retrieved. Found", len(matchlist["matches"]), "matches.")
            with open(config_info["Settings"]["SummonerName"] + "_MatchList.json", "w") as matchlist_file:
                json.dump(matchlist, matchlist_file)
            n_matches = len(matchlist["matches"])
            print("Matchlist saved.")
            print("Matchlist")
            # stop iterating if things work
            attempt = 999
        except:
            attempt += 1
            print("Error getting matchlist. No match data was saved. Exiting.")
            n_matches = 0
        if n_matches !=0:
            try:
                print("Checking saved match data against matchlist.")
                match_data_loaded = open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "r")
                match_data_loaded = json.loads(match_data_loaded.read())
                for mm in range(n_matches):
                    mid = str(matchlist["matches"][mm]["matchId"])
                    if mid in match_data_loaded:
                        print(mid, "found in file.")
                    else:
                        print(mid, "(match ",  mm, ") is new")
                        new_matches.append(mid)
                print("Found ", len(new_matches), " New Matches")
            except:
                print("Saved match data not found. Downloading all matches instead.")
                for mm in range(n_matches):
                    mid = str(matchlist["matches"][mm]["matchId"])
                    new_matches.append(mid)
            n_nm = len(new_matches)
            # prepare to compile all match data in match_data variable
            # reverse the order to grab oldest first before prepending them.
            new_matches = new_matches[::-1]
            match_data_all = match_data_loaded
            for mm in range(n_nm):
                print("preparing to pull down a new match")
                mid = str(new_matches[mm])
                BaseURL = "https://na.api.pvp.net/api/lol/"
                match_call = (BaseURL + config_info["Settings"]["Region"]
                              + "/v2.2/match/"
                              + mid
                              + "?api_key="
                              + config_info["Settings"]["APIKey"]
                              )
                attempt = 0
                for attempt in range(10):
                    try:
                        print("Trying to get match " + mid + ", Attempt #" + str(attempt + 1) + "/10")
                        time.sleep(2)  # wait a sec to avoid excessive API calls with repeated retries
                        match_data = urllib.request.urlopen(match_call)
                        match_data = match_data.read()
                        match_data = json.loads(match_data)
                        match_data_all[mid] = match_data
                        print("Succeeded - saving to file.")
                        with open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "w") as match_data_file:
                            json.dump(match_data_all, match_data_file)
                        attempt = 999
                        break
                    except:
                        attempt += 1
                        print("Failed to get match. Retrying up to 10 times.")
                        match_data = {}
                        match_data_all[mid] = match_data
        print("Done getting match data.")
    return match_data



# update_matchdata(config_info)

"""
matlab code
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
"""
