# import ability to make URL requests
import urllib.request
# import ability to parse JSON objects
import json
# import time to allow for use of time.sleep(secs). Prevents excessive api calls
import time


def get_sid(APIKey, Region, SummonerName, status_label):
    """ Get summoner ID from summoner name. Summoner name must be lower-case letters only """
    SID = ""
    BaseURL = "https://na.api.pvp.net/api/lol/"
    SIDCall = BaseURL + Region + "/v1.4/summoner/by-name/" + SummonerName + "?api_key=" + APIKey
    TimesTried = 0
    for attempt in range(10):
        status_label.set("Getting Summoner ID. Attempt #" + str(attempt+1) + "/10")
        try:
            # wait a sec - don't exceed API rate limit
            time.sleep(2)
            ProfReply = urllib.request.urlopen(SIDCall)
            ProfReplyData = ProfReply.read()
            ProfReplyJSONData = json.loads(ProfReplyData)
            SID = ProfReplyJSONData[SummonerName]["id"]
            SID = str(SID)
            status_label.set("SID Retrieved (" + SID + ")")
            break
        except:
            status_label.set("Error with request. Likely culprits: invalid summoner name, API key, or region.")
    return SID


def config(enteredkey, region, summname, status_label):
    """ Take inputted info and use it to write a config file. """
    APIKey = enteredkey
    APIKey = APIKey.replace(" ", "")  # strip any accidental spaces
    APIKey = APIKey.replace('\n', '')
    Region = region
    SummonerName = summname
    SummonerName = SummonerName.replace(" ", "").lower()  # strip unacceptable spaces and caps from SummonerName
    SummonerName = SummonerName.replace('\n', '')

    SID = get_sid(APIKey, Region, SummonerName, status_label)  # grab summoner ID using an API call

    config_info = ({"Settings": {
        "APIKey": APIKey,
        "Region": Region,
        "SummonerName": SummonerName,
        "SID": SID}}
    )
    json.dump(config_info, open("Configuration.LoHConfig", 'w'))
    return config_info
