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
from APIFunctions import GetRankedMatchData
from PlotFunctions import LoHPlots

# Declare globals
global status_label, config_info, match_data_all, parsed_match_data, filtered_parsed_match_data

def update_config():
    global config_info, status_label
    status_label.set("Updating App Settings")
    config_info = ConfigureLoH.config(e_apikey.get(), reg.get(), e_summname.get(), status_label)


def get_matches():
    global config_info, match_data_all, parsed_match_data
    # First, update the match data.
    match_data_all = GetRankedMatchData.update_matchdata(config_info)
    # Second, parse all of the data and return needed variables (as applicable).
    parsed_match_data = LoHPlots.parse_match_data(config_info, match_data_all)
    with open(config_info["Settings"]["SummonerName"] + "_ParsedMatchData.LoHData", "w") as parsed_match_data_file:
        json.dump(parsed_match_data, parsed_match_data_file)
    status_label.set("Data pulled from web, parsed, and saved.")
    print("Updating filter options [NOT IMPLEMENTED]")


# TRY TO LOAD PREEXISTING CONFIGRAUTION FILE AND MATCH DATA
def initialize():
    global config_info, match_data_all, parsed_match_data, status_label
    try:
        config_file = open("Configuration.LoHConfig", "r")
        config_info = json.loads(config_file.read())
        # status_label.set("Configuration options found and loaded at startup")
    except:
        config_info = {}
        # status_label.set("Configuration options not found. Please run configuration.")

    try:
        match_data_all = open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "r")
        match_data_all = json.loads(match_data_all.read())
        print("Match data loaded at startup (may be outdated).")
    except:
        match_data_all = {}
        print("Match data not found; please get match data.")

    try:
        parsed_match_data = open(config_info["Settings"]["SummonerName"] + "_ParsedMatchData.LoHData", "r")
        parsed_match_data = json.loads(parsed_match_data.read())
        print("Parsed match data found at startup (may be outdated).")
    except:
        parsed_match_data = {}
        print("Parsed match data not found at startup; please update match data.")
initialize()

# PREPARE A BOX TO HOLD OPTIONS & POPULATE IT WITH DEFAULTS FROM CONFIG FILE. GRID SIZE IS 15x5
root = tkinter.Tk()  # prepare a widget to hold the UI
root.title("League of Histograms")
# root.config()
# wwid = root.winfo_screenwidth()/4
# whei = root.winfo_screenheight()/2
# w = tkinter.Canvas(root, width=wwid, height=whei)
# w.pack()
# w.create_window(0, wwid/3, 0, whei/3)


def do_plots():
    global config_info, match_data_all, parsed_match_data, filtered_parsed_match_data, \
        filter_label, ssn_filter, champ_filter, match_filter

    enabled_filters_text = "Filtering By: "
    filter_label.set(enabled_filters_text + "All Matches")
    filter_opts = {"BySeason": {"N": ""}, "ByChamp": {"N": ""}, "ByMatch": {"N": ""}}

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
        filter_opts["ByMatch"] = {"Y": match_filter.get()}

    print(filter_opts)
    LoHPlots.filter(match_data_all, parsed_match_data, filter_opts)

    print("Generating plots. [NOT IMPLEMENTED]")
    if cb_w_v_time.get() == 1:
        print("Winrate vs. time checked.")
        LoHPlots.wr_vs_time(match_data_all)
    else:
        print("Winrate vs. time not checked.")
    print("Done generating selected plots. [NOT IMPLEMENTED]")
    filtered_parsed_match_data = parsed_match_data
    return filtered_parsed_match_data


# CONFIGURATION OPTIONS FRAME (SHOULD MAKE THIS A FRAME... ONCE I FIGURE OUT WHAT THAT IS)
l_apikey = tkinter.Label(root, text="Enter API Key:").grid(row=0, column=0)
e_apikey = tkinter.Entry(root, width=45, justify="center")
e_apikey.grid(row=1, column=0)
try:
    e_apikey.insert(0, config_info["Settings"]["APIKey"])
except:
    pass

reg_list = ["br", "eune", "euw", "jp", "kr", "lan", "las", "na", "oce", "tr", "ru", "pbe", "global"]
l_region = tkinter.Label(root, text="Select Region:").grid(row=2, column=0)
try:
    reg = tkinter.StringVar(value=config_info["Settings"]["Region"])
except:
    reg = tkinter.StringVar(value="na")
o_region = tkinter.OptionMenu(root, reg, *reg_list)
o_region.grid(row=3, column=0)


l_summname = tkinter.Label(root, text="Enter Summoner Name:").grid(row=4, column=0)
e_summname = tkinter.Entry(root, width=45, justify="center")
if config_info !={}:
    e_summname.insert(0, config_info["Settings"]["SummonerName"])
e_summname.grid(row=5, column=0)

b_lc = tkinter.Button(root, text="Update LoH Settings", width=25, command=update_config)
b_lc.grid(row=7, column=0)

b_gm = tkinter.Button(root, text="Update Match Data", width=20, command=get_matches)
b_gm.grid(row=8, column=0)

# FILTER OPTIONS FRAME
l_analysis_range = tkinter.Label(root, text="Select Filter(s) For Analysis (None: All Matches):                   ")
l_analysis_range.grid(row=0, column=3, columnspan=2, sticky="w")

# make variables for filter checkboxes (true/false variables for enabled check buttons)
f_season = tkinter.IntVar(value=0)
f_champ = tkinter.IntVar(value=0)
f_match = tkinter.IntVar(value=0)

# make filter checkboxes with (if needed) additional entry options
c_season = tkinter.Checkbutton(root, text="By Season: ", variable=f_season).grid(row=1, column=3, sticky="w")
c_champ = tkinter.Checkbutton(root, text="By Champion: ", variable=f_champ).grid(row=2, column=3, sticky="w")
c_match = tkinter.Checkbutton(root, text="By # Recent Matches: ", variable=f_match).grid(row=3, column=3, sticky="w")

# add options menus/entry boxes for filters and create their corresponding variables
global ssn_filter, champ_filter, match_filter, filter_label, status_label
ssn_filter = tkinter.StringVar(value="Please select a season")
champ_filter = tkinter.StringVar(value="Unknown")
match_filter = tkinter.IntVar()
filter_label = tkinter.StringVar()
status_label = tkinter.StringVar()

ssn_list = [""]
try:
    ssn_list = parsed_match_data["season_unique"]
    ssn_filter = tkinter.StringVar(value=parsed_match_data["season_unique"][0])
except:
    pass
o_season = tkinter.OptionMenu(root, ssn_filter, *ssn_list)
o_season.grid(row=1, column=4, sticky="ew")


try:
    champ_filter = tkinter.StringVar(value=parsed_match_data["champ_unique"][0])
    o_champ = tkinter.OptionMenu(root, champ_filter, *parsed_match_data["champ_unique"])
    o_champ.grid(row=2, column=4, sticky="ew")
except:
    pass


match_filter.set(20)
e_match = tkinter.Entry(root, width=10, justify="center", textvariable=match_filter)
e_match.grid(row=3, column=4, sticky="w")

filter_label.set("Filtering By: All Matches")
l_filter = tkinter.Label(root, textvariable=filter_label).grid(row=5, column=3, columnspan=2)
tkinter.Label(root, text="     ").grid(row=6, column=1)

# PLOTTING OPTIONS FRAME (SHOULD MAKE THIS A FRAME... ONCE I FIGURE OUT WHAT THAT IS)
l_plots = tkinter.Label(root, text="Select Plots To Generate").grid(row=7, column=3, sticky="w")

cb_w_v_time = tkinter.IntVar(value=0)
c_w_v_time = tkinter.Checkbutton(root, text="Winrate vs. Time", variable=cb_w_v_time)
c_w_v_time.grid(row=8, column=3, sticky="w")

b_plt = tkinter.Button(root, text="Generate Selected Plots", width=30, command=do_plots)
b_plt.grid(row=10, column=3, columnspan=2)

status_label.set("Starting app")
l_status = tkinter.Label(root, textvariable=status_label).grid(row=998, column=0)

tkinter.Label(root, text="     ").grid(row=999, column=1)

e_apikey.focus_set() # set the focus on the first entry box
root.mainloop() # start the application loop
print("Done")
