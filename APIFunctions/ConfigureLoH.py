# IMPORT STANDARD MODULES
# for getting user input. Ideally this will be replaced.
import tkinter.simpledialog
import json

# GET SID IMPORTS
# import ability to make URL requests
import urllib.request
# import error handler for URL requests
import urllib.error
# import ability to parse JSON objects
import json
# import time to allow for use of time.sleep(secs). Prevents excessive api calls
import time

def get_sid(APIKey, Region, SummonerName):
    """Get summoner ID from summoner name. Summoner
    name must be lower-case letters only"""

    BaseURL = "https://na.api.pvp.net/api/lol/"
    SIDCall = BaseURL + Region + "/v1.4/summoner/by-name/" + SummonerName + "?api_key=" + APIKey # Put everythign together to make profile call
    TimesTried = 0
    for attempt in range(10):
        print("Getting Summoner ID. Attempt #" + str(attempt+1) + "/10")
        try:
            ProfReply = urllib.request.urlopen(SIDCall)
            ProfReplyData = ProfReply.read()
            ProfReplyJSONData = json.loads(ProfReplyData)
            SID = ProfReplyJSONData[SummonerName]["id"]
            SID = str(SID)
            print("SID Retrieved: "+SID)
            break
        except urllib.error.URLError as ProfReply:
                print("Error with request: [", ProfReply, "]. Likely culprits: invalid summoner name; invalid API key; incorrect region.")
        time.sleep(2) # wait a sec - don't exceed API rate limit
    return SID


def config(enteredkey, region, summname):
    """Try to load config file. If doesn't exist, make it from
    basic app info."""

    APIKey = enteredkey
    APIKey = APIKey.replace(" ", "")  # strip any accidental spaces

    Region = region

    SummonerName = summname
    SummonerName = SummonerName.replace(" ", "").lower()  # strip unacceptable spaces and caps from SummonerName

    SID = get_sid(APIKey, Region, SummonerName)  # grab summoner ID using an API call

    config_info = ({"Settings": {
        "APIKey": APIKey,
        "Region": Region,
        "SummonerName": SummonerName,
        "SID": SID}}
    )
    json.dump(config_info, open("Configuration.LoHConfig", 'w'))
    print("Config File Created Successfully")
    return config_info
