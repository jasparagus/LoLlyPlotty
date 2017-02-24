import urllib.request  # import ability to make URL requests
import urllib.error  # import error handler for URL requests
import json  # import ability to parse JSON objects
import time  # gonna do a lot of API calls here...


config_info = open("Configuration.LoHConfig", "r")
config_info = json.loads(config_info.read())

matchlist = open(config_info["Settings"]["SummonerName"] + "_MatchList.json", "r")  # load saved data
matchlist = json.loads(matchlist.read())

match_data_all = {}
for mm in range(len(matchlist["matches"])):
    time.sleep(2)  # wait a sec to avoid excessive API calls with repeated retries
    mid = str(matchlist["matches"][mm]["matchId"])
    print("Trying to get match" + mid)
    BaseURL = "https://na.api.pvp.net/api/lol/"
    match_call = (BaseURL + config_info["Settings"]["Region"]
                  + "/v2.2/match/"
                  + mid
                  + "?api_key="
                  + config_info["Settings"]["APIKey"])
    match_data = urllib.request.urlopen(match_call)
    match_data = match_data.read()
    match_data = json.loads(match_data)

    match_data_all[mm] = match_data

with open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "w") as match_data_file:
    json.dump(match_data_all, match_data_file)

print(match_data_all[0]["matchId"])
