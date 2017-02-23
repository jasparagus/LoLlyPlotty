# GET SUMMONER NAME
SummonerName = "jasparagus"
BaseURL = "https://na.api.pvp.net/api/lol/na/"
SIDCall = BaseURL + "v1.4/summoner/by-name/" + SummonerName + "?api_key=" + APIKey # Put everythign together to make profile call
print(SIDCall)

TimesTried = 0
while TimesTried < 10:
    TimesTried = TimesTried+1 # increment loop variable
    print("Getting Summoner ID. Attempt #",TimesTried)
    try:
        time.sleep(3)
        ProfReply = urllib.request.urlopen(SIDCall)
        ProfReplyData = ProfReply.read()
        ProfReplyJSONData = json.loads(ProfReplyData)
        SID = ProfReplyJSONData[SummonerName]["id"]
        print("SID Retrieved:",SID)
        break
    except urllib.error.URLError as ProfReply:\
            print("Error with request: [",ProfReply,"]. Likely culprits: too many API calls; invalid API key; incorrect region.")
