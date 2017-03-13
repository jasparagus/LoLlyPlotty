"""
LEAGUE OF HISTOGRAMS, v0.1
--------------------------
Work in progress.
"""

# IMPORT STANDARD MODULES
import threading
import json
import tkinter
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

# IMPORT CUSTOM MODULES
from APIFunctions import ConfigureLoH
from APIFunctions import GetChamp
from APIFunctions import GetRankedMatchData
from PlotFunctions import LoHPlots
from PlotFunctions import Parse


# Declare globals
global config_info, match_list, match_data, champ_dict, parsed_match_data, filtered_parsed_match_data

# Initialize their values
config_info = {}
match_list = []
match_data = {}
parsed_match_data = {}
champ_dict = {}

def initialize():
    global config_info, match_data, champ_dict, parsed_match_data

    try:
        with open("Configuration.json", "r") as file:
            config_info = json.loads(file.read())
    except:
        config_info = {}

    try:
        with open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "r") as file:
            match_data = json.loads(file.read())
        champ_dict = GetChamp.get_champ_dict()
        parsed_match_data = Parse.parse_match_data(config_info, match_data, champ_dict)
        with open(config_info["Settings"]["SummonerName"] + "_ParsedMatchData.json", "w") as file:
            json.dump(parsed_match_data, file)
    except:
        match_data = {}

    try:
        with open(config_info["Settings"]["SummonerName"] + "_ParsedMatchData.json", "r") as file:
            parsed_match_data = json.loads(file.read())
    except:
        parsed_match_data = {}

    try:
        reg.set(config_info["Settings"]["Region"])
        apikey.set(config_info["Settings"]["APIKey"])
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

    try:
        status_label.set("Ready to analyze " + str(len(match_data)) + " matches")
    except:
        status_label.set("Initialized with no match data")


def get_matches(step=0):
    """
    Starts a new thread (different from the main thread) and runs the get match command on it.
    This prevents the main GUI thread from "freezing". Starts a new thread at each step.
    """
    if step == 0:
        thread0 = threading.Thread(target=get_matches0)
        thread0.start()
    if step == 1:
        thread1 = threading.Thread(target=get_matches1)
        thread1.start()
    elif step == 2:
        thread2 = threading.Thread(target=get_matches2)
        thread2.start()


def get_matches0():
    """
    STEP 0 - Try to get match list since it may be empty at this point
    """
    global config_info, match_list, match_data, champ_dict, parsed_match_data, status_label

    b_get_match.config(relief="sunken", text="Getting Data, Please Wait")
    config_info = ConfigureLoH.config(apikey.get(), reg.get(), summname.get())
    initialize()
    match_list = GetRankedMatchData.get_match_list(config_info)
    status_label.set("Got matchlist")
    root.update_idletasks()
    root.after(10, get_matches, 1)


def get_matches1():
    """
    STEP 1 - Using the match list, get your matches
    """
    global config_info, match_list, match_data, champ_dict, parsed_match_data, status_label

    size_match_data = len(match_data)
    size_match_list = len(match_list)

    if size_match_list > size_match_data:
        match_id = match_list[size_match_data]
        match_data = GetRankedMatchData.get_match(config_info, match_list, match_data, match_id)
        root.update_idletasks()
        root.after(10, get_matches, 1)
        status_label.set(
            "Got match " + str(match_id)
            + " (" + str(size_match_data) + " of " + str(size_match_list) + ")"
        )
    elif size_match_list == size_match_data:
        root.update_idletasks()
        root.after(10, get_matches, 2)
        status_label.set("All matches downloaded")
    else:
        root.update_idletasks()
        status_label.set("Problem getting matches - try deleting app data")


def get_matches2():
    """
    STEP 2 - With all matches downloaded, make a champion lookup dictionary and parse the data
    """
    global config_info, match_list, match_data, champ_dict, parsed_match_data, status_label

    size_match_data = len(match_data)

    if champ_dict == {}:
        champ_dict = GetChamp.get_champ_dict()

    parsed_match_data = Parse.parse_match_data(config_info, match_data, champ_dict)
    with open(config_info["Settings"]["SummonerName"] + "_ParsedMatchData.json", "w") as file:
        json.dump(parsed_match_data, file)
    initialize()  # This is necessary to update the number of matches and dropdown lists
    root.update_idletasks()
    b_get_match.config(relief="raised", text="Get Match Data")
    status_label.set("All (" + str(size_match_data) + ") matches downloaded; ready to analyze")
    root.update_idletasks()


# def do_plots_parent():
#     thread99 = threading.Thread(target=do_plots)
#     thread99.start()


def do_plots_parent():
    global config_info, champ_dict, match_data, parsed_match_data
    # filter_label, ssn_filter, champ_filter, match_filter, status_label
    config_info = ConfigureLoH.config(apikey.get(), reg.get(), summname.get())
    initialize()

    # Prepare to update the label for what's been filtered
    enabled_filters_text = "Filtered By:\n"

    # prepare a variable to hold the filtered match data and quickly filter out remakes
    filtered_match_data = Parse.filter_remakes(match_data, parsed_match_data)
    filtered_parsed_match_data = Parse.parse_match_data(config_info, filtered_match_data, champ_dict)

    # apply filters if their boxes were checked
    if f_season.get() == 1:
        enabled_filters_text = enabled_filters_text + "(" + ssn_filter.get() + ") "
        filter_label.set(enabled_filters_text)
        filtered_match_data = Parse.filter_season(
            filtered_match_data, filtered_parsed_match_data, ssn_filter.get())
        filtered_parsed_match_data = Parse.parse_match_data(config_info, filtered_match_data, champ_dict)

    if f_champ.get() == 1:
        enabled_filters_text = enabled_filters_text + "(" + champ_filter.get() + ") "
        filter_label.set(enabled_filters_text)
        filtered_match_data = Parse.filter_champ(
            filtered_match_data, filtered_parsed_match_data, champ_filter.get())
        filtered_parsed_match_data = Parse.parse_match_data(config_info, filtered_match_data, champ_dict)

    if f_match.get() == 1:
        enabled_filters_text = enabled_filters_text + "(Last " + str(match_filter.get()) + " Matches) "
        filter_label.set(enabled_filters_text)
        filtered_match_data = Parse.filter_match(
            filtered_match_data, match_filter.get())
        filtered_parsed_match_data = Parse.parse_match_data(config_info, filtered_match_data, champ_dict)

    if f_QueueType.get() == 1:
        enabled_filters_text = enabled_filters_text + "(" + str(q_filter.get()) + ")"
        filter_label.set(enabled_filters_text)
        filtered_match_data = Parse.filter_qtype(
            filtered_match_data, filtered_parsed_match_data, q_filter.get())
        filtered_parsed_match_data = Parse.parse_match_data(config_info, filtered_match_data, champ_dict)

    if f_Role.get() == 1:
        enabled_filters_text = enabled_filters_text + "(" + str(role_filter.get().replace("\n", " ")) + ") "
        filter_label.set(enabled_filters_text)
        filtered_match_data = Parse.filter_role(
            filtered_match_data, filtered_parsed_match_data, role_filter.get())
        filtered_parsed_match_data = Parse.parse_match_data(config_info, filtered_match_data, champ_dict)

    # If you got here without applying any filters
    if enabled_filters_text == "Filtered By:\n":
        enabled_filters_text += "All Matches"
        filter_label.set(enabled_filters_text)


    # Close any leftover plots (otherwise they draw on top of each other or you just get too many)
    # plt.close("all")  # On second thought, it's fine to have extra plots, but keeping this for posterity.

    if len(filtered_parsed_match_data["win_lose"]) > 2:
        if cb_wr_time.get() == 1:
            LoHPlots.wr_time(filtered_parsed_match_data, ma_box_size.get(), enabled_filters_text)

        if cb_wr_champ.get() == 1:
            LoHPlots.wr_champ(filtered_parsed_match_data, n_games_champ.get(), enabled_filters_text)

        if cb_wr_teammate.get() == 1:
            LoHPlots.wr_teammate(filtered_parsed_match_data, n_games_teammate.get(), enabled_filters_text)

        if cb_wr_party.get() == 1:
            LoHPlots.wr_partysize(filtered_parsed_match_data, n_games_party.get(), enabled_filters_text)

        if cb_wr_role.get() == 1:
            LoHPlots.wr_role(filtered_parsed_match_data, n_games_role.get(), enabled_filters_text)

        if cb_wr_dmg.get() == 1:
            LoHPlots.wr_dmg(filtered_parsed_match_data, n_bins.get(), enabled_filters_text)

        if cb_wr_dmg_frac.get() == 1:
            LoHPlots.wr_dmg_frac(filtered_parsed_match_data, n_bins_frac.get(), enabled_filters_text)

        if cb_wr_mapside.get() == 1:
            LoHPlots.wr_mapside(filtered_parsed_match_data, enabled_filters_text)

        plt.show()

        status_label.set("Done Generating Plots (" + str(len(filtered_match_data)) + " Matches)")
    else:
        status_label.set("Too few matches (only found " + str(len(filtered_match_data)) + ")")


# PREPARE A BOX TO HOLD OPTIONS & POPULATE IT WITH DEFAULTS FROM CONFIG FILE.
def start_gui():
    thread999 = threading.Thread(target=draw_gui0)
    thread999.start()


def draw_gui0():
    return


root = tkinter.Tk()  # prepare a widget to hold the UI
root.title("League of Histograms")
root.iconbitmap('icon.ico')
root.resizable(width=False, height=False)
pad = 10  # padding before frame borders
bwid = 10  # border width for frames
spacing = 15  # padding between frames
style = "groove"

w = 25  # width of descriptor boxes

# Variables
apikey = tkinter.StringVar()
summname = tkinter.StringVar()
reg_list = [""]
reg = tkinter.StringVar(value="na")

f_season = tkinter.IntVar(value=0)
f_champ = tkinter.IntVar(value=0)
f_match = tkinter.IntVar(value=0)
f_QueueType = tkinter.IntVar(value=0)
f_Role = tkinter.IntVar(value=0)

filter_label = tkinter.StringVar()
ssn_filter = tkinter.StringVar(value="Select a Season")
ssn_list = [""]
champ_filter = tkinter.StringVar(value="Select a Champion")
champ_filter_list = [""]
match_filter = tkinter.IntVar(value=20)
q_filter = tkinter.StringVar(value="Select a Queue")
q_filter_list = [""]
role_filter = tkinter.StringVar(value="Select a Role")
role_filter_list = [""]
status_label = tkinter.StringVar(value="App Started")


# FRAME 1 - CONFIGURATION OPTIONS AND API CALL BUTTONS - COLUMNS c1 THROUGH c1+1
config_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
config_frame.grid(row=0, column=0)

tkinter.Label(config_frame, text="API Key:", font="Helvetica 12 bold", height=1, anchor="s").grid()
tkinter.Entry(config_frame, width=45, justify="center", textvariable=apikey).grid()

tkinter.Label(config_frame, text="Summoner Name:", font="Helvetica 12 bold", height=2, anchor="s").grid()
tkinter.Entry(config_frame, width=45, justify="center", textvariable=summname).grid()

tkinter.Label(config_frame, text="Region:", font="Helvetica 12 bold", height=2, anchor="s").grid()
o_region = tkinter.OptionMenu(config_frame, reg, *reg_list)
o_region.grid()

b_get_match = tkinter.Button(config_frame, text="Get Match Data", font="Helvetica 14 bold", width=20,
                             background="green", command=get_matches)
b_get_match.grid()


# PANEL 2 - FILTERING OPTIONS AND PLOT COMMAND
filter_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
filter_frame.grid(row=0, column=1)

tkinter.Label(filter_frame, text="Select Desired Filter(s):", font="Helvetica 12 bold",
              width=40, anchor="s").grid(columnspan=2)

tkinter.Checkbutton(filter_frame, text="By Season: ", variable=f_season).grid(row=1, column=0, sticky="w")
tkinter.Checkbutton(filter_frame, text="By Champion: ", variable=f_champ).grid(row=2, column=0, sticky="w")
tkinter.Checkbutton(filter_frame, text="By # Recent Matches: ", variable=f_match).grid(row=3, column=0, sticky="w")
tkinter.Checkbutton(filter_frame, text="By Queue Type: ", variable=f_QueueType).grid(row=4, column=0, sticky="w")
tkinter.Checkbutton(filter_frame, text="By Role: ", variable=f_Role).grid(row=5, column=0, sticky="w")

# PANEL 2 widgets for filter choices
o_season = tkinter.OptionMenu(filter_frame, ssn_filter, *ssn_list)
o_season.grid(row=1, column=1, sticky="ew")

o_champ = tkinter.OptionMenu(filter_frame, champ_filter, *champ_filter_list)
o_champ.grid(row=2, column=1, sticky="ew")

tkinter.Entry(filter_frame, width=40, justify="center", textvariable=match_filter).grid(row=3, column=1, sticky="ew")

o_qtype = tkinter.OptionMenu(filter_frame, q_filter, *q_filter_list)
o_qtype.grid(row=4, column=1, sticky="ew")

o_role = tkinter.OptionMenu(filter_frame, role_filter, *role_filter_list)
o_role.grid(row=5, column=1, sticky="ew")

filter_label.set("Filtered By:\nAll Matches")
tkinter.Label(filter_frame, textvariable=filter_label, font="Helvetica 10", foreground="blue",
              height=3, anchor="s").grid(columnspan=2)


# PLOTTING OPTIONS SUB-PANEL
plot_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
plot_frame.grid(row=0, column=2)

tkinter.Label(plot_frame, text="Select Plots To Make\nFrom Filtered Data:", font="Helvetica 12 bold"
              ).grid(columnspan=2)

# checkbox variables and their checkboxes
cb_wr_time = tkinter.IntVar(value=0)
ma_box_size = tkinter.IntVar(value=10)
cb_wr_champ = tkinter.IntVar(value=0)
n_games_champ = tkinter.IntVar(value=5)
cb_wr_teammate = tkinter.IntVar(value=0)
n_games_teammate = tkinter.IntVar(value=5)
cb_wr_party = tkinter.IntVar(value=0)
n_games_party = tkinter.IntVar(value=5)
cb_wr_role = tkinter.IntVar(value=0)
n_games_role = tkinter.IntVar(value=5)
cb_wr_dmg = tkinter.IntVar(value=0)
n_bins = tkinter.IntVar(value=30)
cb_wr_dmg_frac = tkinter.IntVar(value=0)
n_bins_frac = tkinter.IntVar(value=30)
cb_wr_mapside = tkinter.IntVar(value=0)

tkinter.Checkbutton(plot_frame, text="Winrate Over Time (Moving Average, Specify Average Width)",
                    variable=cb_wr_time).grid(row=9, column=0, sticky="w")
tkinter.Entry(plot_frame, width=6, justify="center", textvariable=ma_box_size).grid(row=9, column=1, sticky="w")

tkinter.Checkbutton(plot_frame, text="Winrate by Champion (Specify Minimum Games Played)",
                    variable=cb_wr_champ).grid(row=10, column=0, sticky="w")
tkinter.Entry(plot_frame, width=6, justify="center", textvariable=n_games_champ).grid(row=10, column=1, sticky="w")

tkinter.Checkbutton(plot_frame, text="Winrate by Teammate (Specify Minimum Games Played)",
                    variable=cb_wr_teammate).grid(row=11, column=0, sticky="w")
tkinter.Entry(plot_frame, width=6, justify="center", textvariable=n_games_teammate).grid(row=11, column=1, sticky="w")

tkinter.Checkbutton(plot_frame,
                    text="Winrate by Party Size (Enter Minimum Games \nPlayed to be Considered a \"Teammate\")",
                    variable=cb_wr_party).grid(row=12, column=0, sticky="w")
tkinter.Entry(plot_frame, width=6, justify="center", textvariable=n_games_party).grid(row=12, column=1, sticky="w")

tkinter.Checkbutton(plot_frame, text="Winrate by Role (Specify Minimum Games Played)",
                    variable=cb_wr_role).grid(row=13, column=0, sticky="w")
tkinter.Entry(plot_frame, width=6, justify="center", textvariable=n_games_role).grid(row=13, column=1, sticky="w")

tkinter.Checkbutton(plot_frame, text="Wins by Damage (Enter Number of Bins)",
                    variable=cb_wr_dmg).grid(row=14, column=0, sticky="w")
tkinter.Entry(plot_frame, width=6, justify="center", textvariable=n_bins).grid(row=14, column=1, sticky="w")

tkinter.Checkbutton(plot_frame, text="Wins by Damage Fraction (Enter Number of Bins)",
                    variable=cb_wr_dmg_frac).grid(row=15, column=0, sticky="w")
tkinter.Entry(plot_frame, width=6, justify="center", textvariable=n_bins_frac).grid(row=15, column=1, sticky="w")

tkinter.Checkbutton(plot_frame, text="Winrate by Map Side", variable=cb_wr_mapside).grid(row=16, column=0, sticky="w")

tkinter.Button(plot_frame, text="Generate Selected Plots", font="Helvetica 14 bold", background="red",
               width=25, command=do_plots_parent).grid(column=0, columnspan=2)

tkinter.Label(root, textvariable=status_label, height=2, font="Helvetica 10 bold", foreground="blue"
              ).grid(row=1, column=0, columnspan=3, sticky="s")

initialize()
root.mainloop()

# Now that everything is ready, initialize the program and enter the main loop of tkinter.
# draw_gui()
