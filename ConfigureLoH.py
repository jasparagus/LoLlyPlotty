# TRY TO LOAD CONFIG FILE; IF IT DOESN'T EXIST, MAKE IT FROM BASIC APP INFO


# IMPORT STANDARD MODULES
import tkinter.simpledialog # for getting user input. Ideally this will be replaced.
import json


# IMPORT CUSTOM MODULES
import GetSID


def config(enteredkey, region, summname):
    APIKey = enteredkey
    APIKey = APIKey.replace(" ", "")  # strip any accidental spaces

    RegionList = ["br", "eune", "euw", "jp", "kr", "lan", "las", "na", "oce", "tr", "ru", "pbe", "global"]
    Region = region
    # the above should eventually be changed to a dropdown list

    SummonerName = summname
    SummonerName = SummonerName.replace(" ", "").lower()  # strip unacceptable spaces and caps from SummonerName

    SID = GetSID.get_sid(APIKey, Region, SummonerName)  # grab summoner ID using an API call

    config_info = ({"Settings": {
        "APIKey": APIKey,
        "Region": Region,
        "SummonerName": SummonerName,
        "SID": SID}}
    )
    json.dump(config_info, open("Configuration.LoHConfig", 'w'))
    print("Config File Created Successfully")
    return config_info
