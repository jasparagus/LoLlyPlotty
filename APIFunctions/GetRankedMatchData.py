# GET DATA FOR RANKED MATCHES
# 1) Gets matchlist & check against any stored matches, save
# 2) Pull down match info for all matches


import urllib.request # import ability to make URL requests
import urllib.error # import error handler for URL requests
import json # import ability to parse JSON objects
import time # import time to allow for use of time.sleep(secs). Prevents excessive api calls


def update_matchdata(config_info):
    match_data = {}
    BaseURL = "https://na.api.pvp.net/api/lol/"
    matchlist_call = (BaseURL + config_info["Settings"]["Region"]
                     + "/v2.2/matchlist/by-summoner/"
                     + config_info["Settings"]["SID"]
                     + "?api_key="
                     + config_info["Settings"]["APIKey"])

    for attempt in range(10):
        print("Getting list of all ranked matches (newest first). Attempt #" + str(attempt+1) + "/10")
        time.sleep(2)  # wait a sec to avoid excessive API calls with repeated retries
        try:
            matchlist_reply = urllib.request.urlopen(matchlist_call)
            matchlist_reply = matchlist_reply.read()
            matchlist = json.loads(matchlist_reply)
            print("Matchlist Retrieved. Found", len(matchlist["matches"]), "matches.")
            with open(config_info["Settings"]["SummonerName"] + "_MatchList.json", "w") as matchlist_file:
                json.dump(matchlist, matchlist_file)

            print("Loading Match Data For XX New Matches")
            # Check for saved matches and make a list of new matches. For now it's just doing all of them.
            # try:
            #     MatchDataLoaded = open(config_info["settings"]["SummonerName"] + "_MatchData.json", "r")  # load saved data
            #     MatchDataLoaded = json.loads(MatchDataLoaded.read())
            #     for mm in range(len(MatchDataLoadedJSON["matches"])):
            #         if matchlist["matches"][mm]["matchId"] == MatchDataLoadedJSON["matches"][0]["matchId"]:
            #             print("Found", mm, "new matches")
            #             print("First match: " + matchlist[1])
            # except:
            # print("Saved match data not found. Downloading all matches instead.")
            # matchlist = {}
            new_matches = matchlist

            # prepare the match_data variable
            match_data_all = {}
            for mm in range(len(new_matches["matches"])):
                mid = str(new_matches["matches"][mm]["matchId"])
                BaseURL = "https://na.api.pvp.net/api/lol/"
                match_call = (BaseURL + config_info["Settings"]["Region"]
                              + "/v2.2/match/"
                              + mid
                              + "?api_key="
                              + config_info["Settings"]["APIKey"]
                              )
                for attempt in range(10):
                    try:
                        print("Trying to get match " + mid + ", Attempt #" + str(attempt + 1) + "/10")
                        match_data = urllib.request.urlopen(match_call)
                        match_data = match_data.read()
                        match_data = json.loads(match_data)
                        match_data_all[mid] = match_data
                        print("Succeeded - saving to file.")
                        with open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "w") as match_data_file:
                            json.dump(match_data_all, match_data_file)
                        break
                    except:
                        print("Failed to get match. Retrying up to 10 times.")
                        match_data = {}
                        match_data_all[mid] = match_data
                    time.sleep(2)  # wait a sec to avoid excessive API calls with repeated retries
            break
        except:
            print("Error getting matchlist. This shouldn't happen ever, and no match data was saved. Oops. Exiting.")
            matchlist = {}
        print("Done")
    return match_data

# LOAD EXISTING MATCH DATA, GET NEW MATCH DATA, APPEND DATA, SAVE EVERYTHING -------- IN PROGRESS 2017-02-21
# for mm in range(len(MatchlistJSONData["matches"])): # for each match found
#     print("Grabbing info from match", mm+1,"/",len(MatchlistJSONData["matches"]))
    # MatchlistJSONData["matches"][mm]["matchId"]
    # MatchlistJSONData["matches"][mm]["champion"]
    # MatchlistJSONData["matches"][mm]["lane"]

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
