"""
LEAGUE OF HISTOGRAMS, v0.1
--------------------------
Work in progress.
"""

# IMPORT STANDARD MODULES
import json
import tkinter

# IMPORT CUSTOM MODULES
from APIFunctions import ConfigureLoH
from APIFunctions import GetChamp
from APIFunctions import GetRankedMatchData
from PlotFunctions import LoHPlots
from PlotFunctions import Parse



# Declare globals
global config_info, match_data_all, champLookup, parsed_match_data, filtered_parsed_match_data, \
    ssn_filter, champ_filter, match_filter, filter_label


def initialize():
    global config_info, match_data_all, parsed_match_data, status_label
    try:
        config_file = open("Configuration.LoHConfig", "r")
        config_info = json.loads(config_file.read())
        config_file.close()
    except:
        config_info = {}

    try:
        match_data_all_file = open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "r")
        match_data_all = json.loads(match_data_all_file.read())
        match_data_all_file.close()
    except:
        match_data_all = {}

    try:
        parsed_match_data_file = open(config_info["Settings"]["SummonerName"] + "_ParsedMatchData.LoHData", "r")
        parsed_match_data = json.loads(parsed_match_data_file.read())
        parsed_match_data_file.close()
    except:
        parsed_match_data = {}

    try:
        reg.set(config_info["Settings"]["Region"])
    except:
        pass

    try:
        apikey.set(config_info["Settings"]["APIKey"])
    except:
        pass

    try:
        summname.set(config_info["Settings"]["SummonerName"])
    except:
        pass

    # update options in season filtering menu
    try:
        o_season["menu"].delete(0, "end")
        ssn_list = parsed_match_data["season_unique"]
        for choice in ssn_list:
            o_season["menu"].add_command(label=choice, command=tkinter._setit(ssn_filter, choice))
        ssn_filter.set(parsed_match_data["season_unique"][0])
    except:
        pass

    # update options in champ filtering menu
    try:
        o_champ["menu"].delete(0, "end")
        champ_filter_list = parsed_match_data["champs_played"]
        for choice in champ_filter_list:
            o_champ["menu"].add_command(label=choice, command=tkinter._setit(champ_filter, choice))
            # ssn_filter.set(parsed_match_data["season_unique"][0])
        champ_filter.set(parsed_match_data["champs_played"][0])
    except:
        pass


def update_config():
    global config_info, status_label
    config_info = ConfigureLoH.config(apikey.get(), reg.get(), summname.get(), status_label)
    initialize()
    status_label.set("Settings Saved")


def get_matches():
    global config_info, match_data_all, champLookup, parsed_match_data, status_label
    # Update the configuration in case it's new
    update_config()

    # Prepare a champion lookup dictionary
    champLookup = GetChamp.get_champ_dd()

    # First, update the match data
    match_data_all = GetRankedMatchData.update_matchdata(config_info)
    # Second, parse all of the data and return needed variables (as applicable).
    parsed_match_data = Parse.parse_match_data(config_info, match_data_all, champLookup)
    with open(config_info["Settings"]["SummonerName"] + "_ParsedMatchData.LoHData", "w") as file:
        json.dump(parsed_match_data, file)
    initialize()
    status_label.set("Data Pulled, Parsed, and Saved")


def do_plots():
    update_config()
    global config_info, champLookup, match_data_all, parsed_match_data, filtered_parsed_match_data, \
        filter_label, ssn_filter, champ_filter, match_filter, status_label

    enabled_filters_text = "Filtering By: "
    filter_label.set(enabled_filters_text + "All Matches")
    filter_opts = {"BySeason": {"N": ""}, "ByChamp": {"N": ""}, "ByNMatches": {"N": ""}}

    if f_season.get() == 1:
        enabled_filters_text = enabled_filters_text + "(" + ssn_filter.get() + ") "
        filter_label.set(enabled_filters_text)
        filter_opts["BySeason"] = {"Y": ssn_filter.get()}
    if f_champ.get() == 1:
        enabled_filters_text = enabled_filters_text + "(" + champ_filter.get() + ") "
        filter_label.set(enabled_filters_text)
        filter_opts["ByChamp"] = {"Y": champ_filter.get()}
    if f_match.get() == 1:
        enabled_filters_text = enabled_filters_text + "(Last " + str(match_filter.get()) + " Matches) "
        filter_label.set(enabled_filters_text)
        filter_opts["ByNMatches"] = {"Y": match_filter.get()}

    print(filter_opts)
    filtered_matches = Parse.filter(config_info, parsed_match_data, match_data_all, filter_opts)
    filtered_parsed_match_data = Parse.parse_match_data(config_info, filtered_matches, champLookup)

    print("Generating plots. [NOT IMPLEMENTED]")
    if cb_w_v_time.get() == 1:
        print("Winrate vs. time checked.")
        LoHPlots.wr_vs_time(filtered_parsed_match_data)
    else:
        print("Winrate vs. time not checked.")

    if False:
        print("test")

    status_label.set("Done Generating Plots")


# PREPARE A BOX TO HOLD OPTIONS & POPULATE IT WITH DEFAULTS FROM CONFIG FILE.
root = tkinter.Tk()  # prepare a widget to hold the UI
root.title("League of Histograms")
c1 = 1 # column 1 startpoint
c2 = 4 # column 2 startpoint

# PANEL 1 - CONFIGURATION OPTIONS AND API CALL BUTTONS
tkinter.Label(root, text="   ").grid(row=0, column=0)

tkinter.Label(root, text="Enter API Key:").grid(row=0, column=c1, columnspan=2)
apikey = tkinter.StringVar()
tkinter.Entry(root, width=45, justify="center", textvariable=apikey).grid(row=1, column=c1, columnspan=2)

tkinter.Label(root, text="Enter Summoner Name:").grid(row=2, column=c1, columnspan=2)
summname = tkinter.StringVar()
tkinter.Entry(root, width=45, justify="center", textvariable=summname).grid(row=3, column=c1, columnspan=2)

tkinter.Label(root, text="     ").grid(row=4, column=c1+1, columnspan=2)

tkinter.Label(root, text="Select Region:").grid(row=5, column=c1, sticky="w")
reg_list = ["br", "eune", "euw", "jp", "kr", "lan", "las", "na", "oce", "tr", "ru", "pbe", "global"]
try:
    reg = tkinter.StringVar(value=config_info["Settings"]["Region"])
except:
    reg = tkinter.StringVar(value="na")
o_region = tkinter.OptionMenu(root, reg, *reg_list)
o_region.grid(row=5, column=c1+1, sticky="w")

tkinter.Button(root, text="Load Data", width=20, command=get_matches).grid(row=8, column=c1, columnspan=2)

# SPACER BETWEEN PANEL 1 AND 2
tkinter.Label(root, text="   ").grid(row=0, column=c2-c1)

# PANEL 2 - FILTERING OPTIONS AND PLOT COMMAND
tkinter.Label(root, text="Select Desired Filter(s):").grid(row=0, column=c2, columnspan=2, sticky="ew")

# make variables for filter checkboxes (true/false variables for enabled check buttons)
f_season = tkinter.IntVar(value=0)
f_champ = tkinter.IntVar(value=0)
f_match = tkinter.IntVar(value=0)

# make filter checkboxes with (if needed) additional entry options
tkinter.Checkbutton(root, text="By Season: ", variable=f_season).grid(row=1, column=c2, sticky="w")
tkinter.Checkbutton(root, text="By Champion: ", variable=f_champ).grid(row=2, column=c2, sticky="w")
tkinter.Checkbutton(root, text="By # Recent Matches: ", variable=f_match).grid(row=3, column=c2, sticky="w")

# add options menus/entry boxes for filters and create their corresponding variables
ssn_filter = tkinter.StringVar(root, value="Please select a season")
ssn_list = [""]
champ_filter = tkinter.StringVar(root, value="Please select a champion")
champ_filter_list = [""]
match_filter = tkinter.IntVar(root)
filter_label = tkinter.StringVar(root)
status_label = tkinter.StringVar(root)

# take a stab at setting up buttons for season and champ filtering - need to work out a way to repopulate the dropdowns.
o_season = tkinter.OptionMenu(root, ssn_filter, *ssn_list)
o_season.grid(row=1, column=c2+1, sticky="ew")

o_champ = tkinter.OptionMenu(root, champ_filter, *champ_filter_list)
o_champ.grid(row=2, column=c2+1, sticky="ew")

match_filter.set(20)
tkinter.Entry(root, width=10, justify="center", textvariable=match_filter).grid(row=3, column=c2+1, sticky="w")

filter_label.set("Filtering By: All Matches")
tkinter.Label(root, textvariable=filter_label).grid(row=5, column=c2, columnspan=2)
tkinter.Label(root, text="     ").grid(row=6, column=c2, columnspan=2, sticky="ew")

# PLOTTING OPTIONS SUB-PANEL
tkinter.Label(root, text="Select Plots To Generate:").grid(row=7, column=c2, columnspan=2)

cb_w_v_time = tkinter.IntVar(value=1)
tkinter.Checkbutton(root, text="Winrate vs. Time", variable=cb_w_v_time).grid(row=8, column=c2, sticky="w")

tkinter.Button(root, text="Generate Selected Plots", width=30, command=do_plots).grid(row=10, column=c2, columnspan=2)

status_label.set("App Started...")
tkinter.Label(root, textvariable=status_label).grid(row=998, column=c1, columnspan=2, sticky="ew")

tkinter.Label(root, text="   ").grid(row=999, column=c2+2)

initialize()
root.mainloop() # start the application loop
print("Done")
