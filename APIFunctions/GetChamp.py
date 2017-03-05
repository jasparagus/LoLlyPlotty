import urllib.request # import ability to make URL requests
import json # import ability to parse JSON objects
import time # for sleeping in case of too many API calls


def get_champ(config_info, champ_id):
    """ Method deprecated. Use get_champ_dd() followed by champ_name() instead. """
    champ_name = "MissingNo."
    champ_call = ("https://global.api.pvp.net/api/lol/static-data/"
                  + config_info["Settings"]["Region"]
                  + "/v1.2/champion/"
                  + str(champ_id)
                  + "?api_key="
                  + config_info["Settings"]["APIKey"])

    attempt = 0
    while attempt < 5:
        try:
            champ_name = urllib.request.urlopen(champ_call).read()
            champ_name = json.loads(champ_name)
            champ_name = champ_name["name"]
            # stop iterating if things work
            attempt = 999
        except:
            attempt += 1
            time.sleep(1.4)
    return champ_name


def get_champ_dict():
    """ Creates a champion lookup table using Riot's Data Dragon. """
    dd_version = json.loads(urllib.request.urlopen("http://ddragon.leagueoflegends.com/realms/na.json").read())
    champ_version = dd_version["n"]["champion"]
    champ_call = "http://ddragon.leagueoflegends.com/cdn/" + champ_version + "/data/en_US/champion.json"
    champ_data = json.loads(urllib.request.urlopen(champ_call).read())
    time.sleep(1.4)
    with open("Champion.json", "w") as file:
        json.dump(champ_data, file)

    champ_data = champ_data["data"]
    champ_IDs = champ_data.keys()
    champ_dict = {}

    # For every champ ID (unformatted champion name) get the pretty name and ID (with spaces, etc.)
    for name in champ_IDs:
        champ_dict[champ_data[name]["key"]] = champ_data[name]["name"]

    return champ_dict


def champ_name(champ_dict, cId):
    """ Returns a champion name from its champion ID. """
    try:
        cName = champ_dict[str(cId)]
    except:
        cName = "MissingNo"
    return cName
