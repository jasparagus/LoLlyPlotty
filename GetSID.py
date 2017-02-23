# GET SUMMONER ID FROM SUMMONER NAME


import tkinter.simpledialog # for getting user input
import urllib.request # import ability to make URL requests
import urllib.error # import error handler for URL requests
import json # import ability to parse JSON objects
import time # import time to allow for use of time.sleep(secs). Prevents excessive api calls


def get_sid(config,APIKey):
    SummonerName = tkinter.simpledialog.askstring("Enter Summoner Name", "Summoner Name", initialvalue="SUMMONERNAME")
    SummonerName = SummonerName.replace(" ", "").lower() # strip unacceptable spaces and caps from SummonerName
    BaseURL = "https://na.api.pvp.net/api/lol/na/"
    SIDCall = BaseURL + "v1.4/summoner/by-name/" + SummonerName + "?api_key=" + APIKey # Put everythign together to make profile call
    TimesTried = 0
    while TimesTried < 10:
        TimesTried = TimesTried+1
        print("Getting Summoner ID. Attempt #",TimesTried)
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
                print("Error with request: [", ProfReply, "]. Likely culprits: too many API calls; invalid API key; incorrect region.")
    return SID
