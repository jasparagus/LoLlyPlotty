"""
LEAGUE OF HISTOGRAMS, v0.1
--------------------------
Work in progress.
"""

# IMPORT STANDARD MODULES
import json
import tkinter
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")


# IMPORT CUSTOM MODULES
from APIFunctions import ConfigureLoH
from APIFunctions import GetChamp
from APIFunctions import GetRankedMatchData
from PlotFunctions import LoHPlots
from PlotFunctions import Parse


# Declare globals
global config_info, match_data, champLookup, parsed_match_data, filtered_parsed_match_data


def initialize():
    global config_info, match_data, parsed_match_data

    try:
        config_file = open("Configuration.LoHConfig", "r")
        config_info = json.loads(config_file.read())
        config_file.close()
    except:
        config_info = {}

    try:
        match_data_file = open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "r")
        match_data = json.loads(match_data_file.read())
        match_data_file.close()
    except:
        match_data = {}

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

    # update options in region filtering menu
    try:
        o_region["menu"].delete(0, "end")
        reg_list = config_info["RegionList"]
        for choice in reg_list:
            o_region["menu"].add_command(label=choice, command=tkinter._setit(reg, choice))
    except:
        pass

    # update options in season filtering menu
    try:
        o_season["menu"].delete(0, "end")
        ssn_list = parsed_match_data["season_unique"]
        for choice in ssn_list:
            o_season["menu"].add_command(label=choice, command=tkinter._setit(ssn_filter, choice))
    except:
        pass

    # update options in champ filtering menu
    try:
        o_champ["menu"].delete(0, "end")
        champ_filter_list = parsed_match_data["champs_played"]
        for choice in champ_filter_list:
            o_champ["menu"].add_command(label=choice, command=tkinter._setit(champ_filter, choice))
    except:
        pass

    try:
        o_qtype["menu"].delete(0, "end")
        q_filter_list = parsed_match_data["queue_types"]
        for choice in q_filter_list:
            o_qtype["menu"].add_command(label=choice, command=tkinter._setit(q_filter, choice))
    except:
        pass

    try:
        o_role["menu"].delete(0, "end")
        role_filter_list = parsed_match_data["roles"]
        for choice in role_filter_list:
            o_role["menu"].add_command(label=choice, command=tkinter._setit(role_filter, choice))
    except:
        pass

    status_label.set("Initialized")


def update_config():
    global config_info, status_label
    config_info = ConfigureLoH.config(apikey.get(), reg.get(), summname.get(), status_label)
    initialize()
    status_label.set("Configuration Updated")


def get_matches():
    global config_info, match_data, champLookup, parsed_match_data, status_label
    # Update the configuration in case it's new
    update_config()

    # Prepare a champion lookup dictionary
    champLookup = GetChamp.get_champ_dd()

    # First, pull down the match list and get the match data from missing matches
    matchlist, n_matches = GetRankedMatchData.get_matchlist(config_info)
    match_data = GetRankedMatchData.update_match_data(config_info, matchlist, n_matches)

    # Second, parse all of the data and return needed variables (as applicable).
    parsed_match_data = Parse.parse_match_data(config_info, match_data, champLookup)
    with open(config_info["Settings"]["SummonerName"] + "_ParsedMatchData.LoHData", "w") as file:
        json.dump(parsed_match_data, file)
    initialize()
    status_label.set("Data Downloaded, Parsed, and Saved")

    """
    New structure for this to move "getting match" info to main GUI (each step sets get_matches button true):
    1.) Try to get a champlookup from file, if fails, make it
    2.) If champlookup isn't empty, get matchlist (status update: got matchlist)
    3.) If matchlist isn't empty, check for missing matches (status update: checking for missing matches)
    4.) If there are missing matches, pull the next one and save it to file (status update: Got match ##/###)
    5.) If there are no missing matches, don't make the get_matches button true again

    Steps 3 and 4 will need to be performed by new functions made from
    pieces of GetRankedMatchData.update_match_data
    """


def do_plots():
    global config_info, champLookup, match_data, parsed_match_data
    # filter_label, ssn_filter, champ_filter, match_filter, status_label
    update_config()

    champLookup = GetChamp.get_champ_dd()

    # Prepare to update the label for what's been filtered
    enabled_filters_text = "Filtered By: "
    filter_label.set(enabled_filters_text + "All Matches")

    # prepare a variable to hold the filtered match data and quickly filter out remakes
    filtered_match_data = Parse.filter_remakes(match_data, parsed_match_data)
    filtered_parsed_match_data = Parse.parse_match_data(config_info, filtered_match_data, champLookup)

    # apply filters if their boxes were checked
    if f_season.get() == 1:
        enabled_filters_text = enabled_filters_text + "(" + ssn_filter.get() + ") "
        filter_label.set(enabled_filters_text)
        filtered_match_data = Parse.filter_season(
            filtered_match_data, filtered_parsed_match_data, ssn_filter.get())
        filtered_parsed_match_data = Parse.parse_match_data(config_info, filtered_match_data, champLookup)

    if f_champ.get() == 1:
        enabled_filters_text = enabled_filters_text + "(" + champ_filter.get() + ") "
        filter_label.set(enabled_filters_text)
        filtered_match_data = Parse.filter_champ(
            filtered_match_data, filtered_parsed_match_data, champ_filter.get())
        filtered_parsed_match_data = Parse.parse_match_data(config_info, filtered_match_data, champLookup)

    if f_match.get() == 1:
        enabled_filters_text = enabled_filters_text + "(Last " + str(match_filter.get()) + " Matches) "
        filter_label.set(enabled_filters_text)
        filtered_match_data = Parse.filter_match(
            filtered_match_data, match_filter.get())
        filtered_parsed_match_data = Parse.parse_match_data(config_info, filtered_match_data, champLookup)

    if f_QueueType.get() == 1:
        enabled_filters_text = enabled_filters_text + "(" + str(q_filter.get()) + ")"
        filter_label.set(enabled_filters_text)
        filtered_match_data = Parse.filter_qtype(
            filtered_match_data, filtered_parsed_match_data, q_filter.get())
        filtered_parsed_match_data = Parse.parse_match_data(config_info, filtered_match_data, champLookup)

    if f_Role.get() == 1:
        enabled_filters_text = enabled_filters_text + "(" + str(role_filter.get()) + ") "
        filter_label.set(enabled_filters_text)
        filtered_match_data = Parse.filter_role(
            filtered_match_data, filtered_parsed_match_data, role_filter.get())
        filtered_parsed_match_data = Parse.parse_match_data(config_info, filtered_match_data, champLookup)

    # Close any leftover plots (otherwise they draw on top of each other or you just get too many)
    # plt.close("all")

    if cb_wr_time.get() == 1:
        LoHPlots.wr_time(filtered_parsed_match_data, 7)

    if cb_wr_champ.get() == 1:
        LoHPlots.wr_champ(filtered_parsed_match_data, 2)

    if cb_wr_teammate.get() == 1:
        LoHPlots.wr_teammate(filtered_parsed_match_data, 3)

    if cb_wr_partysize.get() == 1:
        LoHPlots.wr_partysize(filtered_parsed_match_data, 3)

    if cb_wr_role.get() == 1:
        LoHPlots.wr_role(filtered_parsed_match_data)

    if cb_wr_dmg.get() == 1:
        LoHPlots.wr_dmg(filtered_parsed_match_data)

    if cb_wr_mapside.get() == 1:
        LoHPlots.wr_mapside(filtered_parsed_match_data)

    plt.show()

    status_label.set("Done Generating Plots (" + str(len(filtered_match_data)) + " Matches)")


# PREPARE A BOX TO HOLD OPTIONS & POPULATE IT WITH DEFAULTS FROM CONFIG FILE.
root = tkinter.Tk()  # prepare a widget to hold the UI
root.title("League of Histograms")
c1 = 1  # column 1 startpoint
c2 = 4  # column 2 startpoint
spw = 4  # spacer width
w = 25  # width of descriptor boxes

# PANEL 1 - CONFIGURATION OPTIONS AND API CALL BUTTONS - COLUMNS c1 THROUGH c1+1
# PANEL 1 variables
apikey = tkinter.StringVar()
summname = tkinter.StringVar()
reg_list = [""]
reg = tkinter.StringVar(value="na")

# PANEL 1 labels and other widgets
tkinter.Label(root, width=spw).grid(row=0, column=0)
tkinter.Label(root, text="Enter API Key:", height=2, anchor="s").grid(row=0, column=c1, columnspan=2)
tkinter.Entry(root, width=45, justify="center", textvariable=apikey).grid(row=1, column=c1, columnspan=2)
tkinter.Label(root, text="Enter Summoner Name:", height=2, anchor="s").grid(row=2, column=c1, columnspan=2)
tkinter.Entry(root, width=45, justify="center", textvariable=summname).grid(row=3, column=c1, columnspan=2)
tkinter.Label(root, text="Select Region:", anchor="e").grid(row=4, column=c1, sticky="e", rowspan=2)
o_region = tkinter.OptionMenu(root, reg, *reg_list)
o_region.grid(row=4, column=c1+1, sticky="w", rowspan=2)
tkinter.Button(root, text="Get Match Data", width=20, command=get_matches).grid(row=6, column=c1, columnspan=2)


# SPACER BETWEEN PANEL 1 AND 2 -
tkinter.Label(root, width=spw).grid(row=0, column=c2-(c1+1)+1)


# PANEL 2 - FILTERING OPTIONS AND PLOT COMMAND - COLUMNS c2 THROUGH c2+1
tkinter.Label(root, text="Select Desired Filter(s):", width=60).grid(row=0, column=c2, columnspan=2, sticky="ew")

# PANEL 2 filter checkbox variables (enabled/disabled)
f_season = tkinter.IntVar(value=0)
f_champ = tkinter.IntVar(value=0)
f_match = tkinter.IntVar(value=0)
f_QueueType = tkinter.IntVar(value=0)
f_Role = tkinter.IntVar(value=0)

# PANEL 2 filter variables
# global filter_label
filter_label = tkinter.StringVar(root)
# global ssn_filter
ssn_filter = tkinter.StringVar(root, value="Select a Season")
ssn_list = [""]
# global champ_filter
champ_filter = tkinter.StringVar(root, value="Select a Champion")
champ_filter_list = [""]
# global match_filter
match_filter = tkinter.IntVar(root)
q_filter = tkinter.StringVar(root, value="Select a Queue")
q_filter_list = [""]
role_filter = tkinter.StringVar(root, value="Select a Role")
role_filter_list = [""]
status_label = tkinter.StringVar(root)

# PANEL 2 checkboxes for filter enabling
tkinter.Checkbutton(root, text="By Season: ", variable=f_season).grid(row=1, column=c2, sticky="w")
tkinter.Checkbutton(root, text="By Champion: ", variable=f_champ).grid(row=2, column=c2, sticky="w")
tkinter.Checkbutton(root, text="By # Recent Matches: ", variable=f_match).grid(row=3, column=c2, sticky="w")
tkinter.Checkbutton(root, text="By Queue Type: ", variable=f_QueueType).grid(row=4, column=c2, sticky="w")
tkinter.Checkbutton(root, text="By Role: ", variable=f_Role).grid(row=5, column=c2, sticky="w")

# PANEL 2 widgets for filter choices
o_season = tkinter.OptionMenu(root, ssn_filter, *ssn_list)
o_season.grid(row=1, column=c2+1, sticky="w")

o_champ = tkinter.OptionMenu(root, champ_filter, *champ_filter_list)
o_champ.grid(row=2, column=c2+1, sticky="w")

match_filter.set(20)
tkinter.Entry(root, width=10, justify="center", textvariable=match_filter).grid(row=3, column=c2+1, sticky="w")

o_qtype = tkinter.OptionMenu(root, q_filter, *q_filter_list)
o_qtype.grid(row=4, column=c2+1, sticky="w")

o_role = tkinter.OptionMenu(root, role_filter, *role_filter_list)
o_role.grid(row=5, column=c2+1, sticky="w")

filter_label.set("Filtered By: All Matches")
tkinter.Label(root, textvariable=filter_label).grid(row=6, column=c2, columnspan=2)
tkinter.Label(root, text="     ").grid(row=7, column=c2, columnspan=2, sticky="ew")

# PLOTTING OPTIONS SUB-PANEL
tkinter.Label(root, text="Select Plots To Generate From Filtered Data:").grid(row=8, column=c2, columnspan=2)

# checkbox variables and their checkboxes
cb_wr_time = tkinter.IntVar(value=0)
cb_wr_champ = tkinter.IntVar(value=0)
cb_wr_teammate = tkinter.IntVar(value=0)
cb_wr_partysize = tkinter.IntVar(value=0)
cb_wr_role = tkinter.IntVar(value=0)
cb_wr_dmg = tkinter.IntVar(value=0)
cb_wr_mapside = tkinter.IntVar(value=0)

tkinter.Checkbutton(root, text="Winrate Over Time (Moving Average)",
                    variable=cb_wr_time).grid(row=9, column=c2, sticky="w")
tkinter.Checkbutton(root, text="Winrate by Champion", variable=cb_wr_champ).grid(row=10, column=c2, sticky="w")
tkinter.Checkbutton(root, text="Winrate by Teammate", variable=cb_wr_teammate).grid(row=11, column=c2, sticky="w")
tkinter.Checkbutton(root, text="Winrate by Party Size", variable=cb_wr_partysize).grid(row=12, column=c2, sticky="w")
tkinter.Checkbutton(root, text="Winrate by Role", variable=cb_wr_role).grid(row=13, column=c2, sticky="w")
tkinter.Checkbutton(root, text="Winrate by Damage", variable=cb_wr_dmg).grid(row=14, column=c2, sticky="w")
tkinter.Checkbutton(root, text="Winrate by Map Side", variable=cb_wr_mapside).grid(row=15, column=c2, sticky="w")

tkinter.Button(root, text="Generate Selected Plots", width=30, command=do_plots).grid(row=997, column=c2, columnspan=2)

status_label.set("App Started")
tkinter.Label(root, textvariable=status_label).grid(row=998, column=c1, columnspan=2, sticky="ew")

tkinter.Label(root, width=spw).grid(row=999, column=c2+2)

initialize()
root.mainloop() # start the application loop
print("Exiting program gracefully")
