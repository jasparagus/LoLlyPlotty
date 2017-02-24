# GET SUMMONER ID FROM SUMMONER NAME
# Summoner name must be lower-case letters only (no exceptions)


import urllib.request # import ability to make URL requests
import urllib.error # import error handler for URL requests
import json # import ability to parse JSON objects
import time # import time to allow for use of time.sleep(secs). Prevents excessive api calls


def get_sid(APIKey, Region, SummonerName):
    BaseURL = "https://na.api.pvp.net/api/lol/"
    SIDCall = BaseURL + Region + "/v1.4/summoner/by-name/" + SummonerName + "?api_key=" + APIKey # Put everythign together to make profile call
    TimesTried = 0
    for attempt in range(10):
        print("Getting Summoner ID. Attempt #" + str(attempt+1) + "/10")
        try:
            time.sleep(2) # wait a sec - don't exceed API rate limit
            ProfReply = urllib.request.urlopen(SIDCall)
            ProfReplyData = ProfReply.read()
            ProfReplyJSONData = json.loads(ProfReplyData)
            SID = ProfReplyJSONData[SummonerName]["id"]
            SID = str(SID)
            print("SID Retrieved: "+SID)
            break
        except urllib.error.URLError as ProfReply:
                print("Error with request: [", ProfReply, "]. Likely culprits: invalid summoner name; invalid API key; incorrect region.")
    return SID
