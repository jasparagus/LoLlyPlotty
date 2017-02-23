# GET LIST OF RANKED MATCHES
MatchlistCall = BaseURL + "v2.2/matchlist/by-summoner/" + str(SID) + "?api_key=" + APIKey
print(MatchlistCall)
time.sleep(3)

TimesTried = 0
while TimesTried < 10:
    TimesTried = TimesTried+1 # increment loop variable
    print("Getting list of all ranked matches (newest first). Attempt #",TimesTried)
    try:
        time.sleep(3)
        MatchlistReply = urllib.request.urlopen(MatchlistCall)
        MatchlistData = MatchlistReply.read()
        MatchlistJSONData = json.loads(MatchlistData)
        print("Matchlist Retrieved. Found",len(MatchlistJSONData["matches"]),"matches.")
        break
    except urllib.error.URLError as MatchlistReply:
        print("Error getting matchlist. Oops.")