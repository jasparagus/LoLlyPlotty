# import ability to make URL requests
import urllib.request
# import ability to parse JSON objects
import json
# import time to allow for use of time.sleep(secs). Prevents excessive api calls
import time


def get_sid(APIKey, Region, SummonerName):
    """ Get summoner ID from summoner name. Summoner name must be lower-case letters only """
    SID = ""
    SIDCall = (
        "https://na.api.pvp.net/api/lol/" + Region
        + "/v1.4/summoner/by-name/" + SummonerName + "?"
        + "api_key=" + APIKey
    )

    for attempt in range(10):
        try:
            # wait a sec - don't exceed API rate limit
            time.sleep(2)
            ProfReply = urllib.request.urlopen(SIDCall)
            ProfReplyData = ProfReply.read()
            ProfReplyJSONData = json.loads(ProfReplyData)
            SID = ProfReplyJSONData[SummonerName]["id"]
            SID = str(SID)
            break
        except:
            pass

    return SID


def config(enteredkey, region, summname):
    """ Take inputted info and use it to write a config file. """
    APIKey = enteredkey
    APIKey = APIKey.replace(" ", "")  # strip accidental spaces from API key
    APIKey = APIKey.replace('\n', '')  # strip accidental newline characters
    Region = region
    SummonerName = summname
    SummonerName = SummonerName.replace(" ", "").lower()  # strip spaces and caps from SummonerName (not allowed)
    SummonerName = SummonerName.replace('\n', '')  # strip accidental newline characters

    SID = get_sid(APIKey, Region, SummonerName)  # grab summoner ID using an API call

    try:
        with open("Configuration.LoHConfig", "r") as file:
            config_info = json.loads(file.read())
        RegionList = config_info["RegionList"]
    except:
        RegionList = ["br", "eune", "euw", "jp", "kr", "lan", "las", "na", "oce", "tr", "ru", "pbe", "global"]

    try:
        with open("Configuration.LoHConfig", "r") as file:
            config_info = json.loads(file.read())
        RankedQueues = config_info["RankedQueues"]
    except:
        RankedQueues = ([
            "RANKED_FLEX_SR",
            "RANKED_SOLO_5x5",
            "RANKED_TEAM_5x5",
            "TEAM_BUILDER_DRAFT_RANKED_5x5",
            "TEAM_BUILDER_RANKED_SOLO",
        ])

    config_info = {
        "Settings": {
            "APIKey": APIKey,
            "Region": Region,
            "SummonerName": SummonerName,
            "SID": SID},
        "RegionList": RegionList,
        "RankedQueues": RankedQueues
    }

    with open("Configuration.LoHConfig", 'w') as file:
        json.dump(config_info, file)

    return config_info
