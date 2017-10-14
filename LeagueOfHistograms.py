"""
LEAGUE OF HISTOGRAMS, v0.1
--------------------------
Work in progress.
"""

# IMPORT STANDARD MODULES
import threading
import json
import time
import tkinter
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

# IMPORT CUSTOM MODULES
import api_fns
import parse
import plot_fns


# Load important variables from file and update menus
def refresh(firstrun=False):
    """
    :param firstrun: True (app freshly started) or False (app not started fresh)
    :return: config_info, match_data, parsed_match_data
    """
    if firstrun == True:
        try:
            with open("Configuration.json", "r") as file:
                config_info = json.loads(file.read())
                try:
                    reg.set(config_info["Region"])
                except:
                    reg.set("Choose")
                try:
                    summname.set(config_info["SummonerName"])
                except:
                    summname.set("")
        except:
            config_info = api_fns.config("", "")
            pass
    else:
        config_info = api_fns.config(reg.get(), summname.get())  # update the configuration info from the GUI
        reg.set(config_info["Region"])
        summname.set(config_info["SummonerName"])

    try:
        with open(config_info["SummonerName"] + "_MatchData.json", "r") as file:
            match_data = json.loads(file.read())
    except:
        match_data = {}

    try:
        with open(config_info["SummonerName"] + "_ParsedMatchData.json", "r") as file:
            parsed_match_data = json.loads(file.read())
    except:
        parsed_match_data = {}

    # update options in region filtering menu
    try:
        o_region["menu"].delete(0, "end")
        region_list = list(config_info["GameConstants"]["regions.gameconstants"].copy().keys())
        for choice in region_list:
            o_region["menu"].add_command(label=choice, command=tkinter._setit(reg, choice))
    except:
        status_label.set("Unable to find regions.gameconstants file")
        root.update_idletasks()
        pass

    # update options in season filtering menu
    try:
        ssn_filter.set(list(config_info["GameConstants"]["seasons.gameconstants"].copy().values()))
    except:
        ssn_filter.set(["Error Finding Seasons"])
        status_label.set("Unable to find seasons.gameconstants file")
        root.update_idletasks()
        pass

    try:
        print("setting ChampFilter's filter options")
        SeasonFilter.filter_options.set(list(config_info["GameConstants"]["seasons.gameconstants"].copy().values()))
    except:
        pass

    # update options in champ filtering menu
    try:
        champ_filter.set(list(config_info["ChampionDictionary"].copy().values()))
        ChampionFilter.filter_options.set(list(config_info["ChampionDictionary"].copy().values()))
        # o_champ["menu"].delete(0, "end")
        # champ_filter_list = sorted(list(config_info["ChampionDictionary"].copy().values()))
        # for choice in champ_filter_list:
        #     o_champ["menu"].add_command(label=choice, command=tkinter._setit(champ_filter, choice))
    except:
        status_label.set("Unable to load champion list from servers or find from config file")
        root.update_idletasks()
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

    return config_info, match_data, parsed_match_data


def update_match_data():
    """
    Starts a new thread (different from the main thread) and runs the get match command on it.
    This prevents the main GUI thread from "freezing". Starts a new thread at each step.
    """
    thread0 = threading.Thread(target=get_data)
    thread0.start()


def get_data():
    """
    STEP 0 - Check over the offline match list and compare it with the online match list.
    """
    status_label.set("Downloading list of matches from Riot's servers...")
    b_get_data.config(relief="sunken", text="Updating Games")  # update the button's appearance
    root.update_idletasks()

    # Refresh the app information
    config_info, match_data, parsed_match_data = refresh()

    if config_info["AccountID"] == "" or config_info["SummonerID"] == "":
        status_label.set("Double-check summoner name and selected region")
        b_get_data.config(relief="raised", text="Get Game Data")
        root.update_idletasks()
        return

    full_matchlist, len_full_matchlist = api_fns.get_full_matchlist(config_info)
    status_label.set("Found " + str(len_full_matchlist) + " matches")
    root.update_idletasks()

    # Check that every match (determined by index) in matchlist is also in match_data; retrieve missing matches
    for ii in range(len_full_matchlist):
        status_label.set("Checking local database for match #" + str(ii+1) + " of " + str(len_full_matchlist))
        root.update_idletasks()
        if str(ii + 1) not in match_data:
            # download missing match
            status_label.set(
                "Downloading new match (MatchID =" +
                full_matchlist[ii + 1] +
                ", #" + str(ii + 1) +
                " of " + str(len_full_matchlist) + ")"
            )
            root.update_idletasks()
            match = api_fns.get_match(config_info, full_matchlist[ii + 1])

            api_fns.append_match(config_info, match, ii + 1)

    # Refresh the GUI one last time from the saved files
    config_info, match_data, parsed_match_data = refresh()
    b_get_data.config(relief="raised", text="Get Game Data")
    status_label.set(
        str(len(match_data)) +
        "/" + str(len_full_matchlist) +
        " matches downloaded and ready to analyze"
    )
    root.update_idletasks()

    # Parse the data you just got (don't forget to tell the user!)
    parsed_match_data = parse.parse_match_data(config_info, match_data)
    # with open(config_info["SummonerName"] + "_ParsedMatchData.json", "w") as file:
    #     json.dump(parsed_match_data, file)


# Note: GET_FILTERS_FROM_TEXTBOXES_FROM_BUTTONS
def button_season():
    ssn_out_str = ""

    season_text.config(state=tkinter.NORMAL)
    season_text.delete(1.0, tkinter.END)
    outs = lb_season.curselection()

    for ii in outs:
        ssn_out_str += lb_season.get(ii) + "\n"

    # Empty any old entries, then insert the new ones
    season_text.insert(tkinter.END, ssn_out_str)
    season_text.config(state=tkinter.DISABLED)
    print(season_text.get(1.0, tkinter.END))

    return


def clear_season():
    season_text.config(state=tkinter.NORMAL)
    season_text.delete(1.0, tkinter.END)
    season_text.config(state=tkinter.DISABLED)
    lb_season.selection_clear(0, tkinter.END)
    return


def button_champion():
    # REFRESH

    outs = lb_season.curselection()
    champ_out_str = ""
    for ii in outs:
        champ_out_str += lb_champion.get(ii) + "\n"
    # ssn_out.set(ssn_out_str)

    # APPLY CHAMPION FILTER TO PARSED MATCHES
    parsed_data = {}
    return parsed_data



def do_plots_parent():
    # this could stand to be built on a new thread.... make this a container function to create a plot on a new thread

    # filter_label, ssn_filter, champ_filter, match_filter, status_label
    refresh()

    GET_FILTERS_FROM_TEXTBOXES_FROM_BUTTONS

    # Prepare to update the label for what's been filtered
    enabled_filters_text = "Filtered By:\n"

    # prepare a variable to hold the filtered match data and quickly filter out remakes
    filtered_match_data = parse.filter_remakes(match_data, parsed_match_data)
    filtered_parsed_match_data = parse.parse_match_data(config_info, filtered_match_data)

    # apply filters if their boxes were checked
    if f_season.get() == 1:
        enabled_filters_text = enabled_filters_text + "(" + ssn_filter.get() + ") "
        filter_label.set(enabled_filters_text)
        filtered_match_data = parse.filter_season(
            filtered_match_data, filtered_parsed_match_data, ssn_filter.get())
        filtered_parsed_match_data = parse.parse_match_data(config_info, filtered_match_data)

    if f_champ.get() == 1:
        enabled_filters_text = enabled_filters_text + "(" + champ_filter.get() + ") "
        filter_label.set(enabled_filters_text)
        filtered_match_data = parse.filter_champ(
            filtered_match_data, filtered_parsed_match_data, champ_filter.get())
        filtered_parsed_match_data = parse.parse_match_data(config_info, filtered_match_data)

    if f_match.get() == 1:
        enabled_filters_text = enabled_filters_text + "(Last " + str(match_filter.get()) + " Matches) "
        filter_label.set(enabled_filters_text)
        filtered_match_data = parse.filter_match(
            filtered_match_data, match_filter.get())
        filtered_parsed_match_data = parse.parse_match_data(config_info, filtered_match_data)

    if f_QueueType.get() == 1:
        enabled_filters_text = enabled_filters_text + "(" + str(q_filter.get()) + ")"
        filter_label.set(enabled_filters_text)
        filtered_match_data = parse.filter_qtype(
            filtered_match_data, filtered_parsed_match_data, q_filter.get())
        filtered_parsed_match_data = parse.parse_match_data(config_info, filtered_match_data)

    if f_Role.get() == 1:
        enabled_filters_text = enabled_filters_text + "(" + str(role_filter.get().replace("\n", " ")) + ") "
        filter_label.set(enabled_filters_text)
        filtered_match_data = parse.filter_role(
            filtered_match_data, filtered_parsed_match_data, role_filter.get())
        filtered_parsed_match_data = parse.parse_match_data(config_info, filtered_match_data)

    # If you got here without applying any filters
    if enabled_filters_text == "Filtered By:\n":
        enabled_filters_text += "All Matches"
        filter_label.set(enabled_filters_text)

    # Close any leftover plots (otherwise they draw on top of each other or you just get too many)
    # plt.close("all")  # On second thought, it's fine to have extra plots, but keeping this for posterity.

    if len(filtered_parsed_match_data["win_lose"]) > 2:
        if cb_wr_time.get() == 1:
            plot_fns.wr_time(filtered_parsed_match_data, ma_box_size.get(), enabled_filters_text)

        if cb_wr_champ.get() == 1:
            plot_fns.wr_champ(filtered_parsed_match_data, n_games_champ.get(), enabled_filters_text)

        if cb_wr_teammate.get() == 1:
            plot_fns.wr_teammate(filtered_parsed_match_data, n_games_teammate.get(), enabled_filters_text)

        if cb_wr_party.get() == 1:
            plot_fns.wr_partysize(filtered_parsed_match_data, n_games_party.get(), enabled_filters_text)

        if cb_wr_role.get() == 1:
            plot_fns.wr_role(filtered_parsed_match_data, n_games_role.get(), enabled_filters_text)

        if cb_wr_dmg.get() == 1:
            plot_fns.wr_dmg(filtered_parsed_match_data, n_bins.get(), enabled_filters_text)

        if cb_wr_dmg_frac.get() == 1:
            plot_fns.wr_dmg_frac(filtered_parsed_match_data, n_bins_frac.get(), enabled_filters_text)

        if cb_wr_mapside.get() == 1:
            plot_fns.wr_mapside(filtered_parsed_match_data, enabled_filters_text)

        plt.show()

        status_label.set("Done Generating Plots (" + str(len(filtered_match_data)) + " Matches)")
    else:
        status_label.set("Too few matches (only found " + str(len(filtered_match_data)) + ")")


# PREPARE A BOX TO HOLD OPTIONS & POPULATE IT WITH DEFAULTS FROM CONFIG FILE.
# def start_gui():
#     thread999 = threading.Thread(target=draw_gui0)
#     thread999.start()
#
#
# def draw_gui0():
#     return


root = tkinter.Tk()  # prepare a widget to hold the UI
root.configure(background="white")
root.title("League of Histograms")
root.iconbitmap('icon.ico')
root.resizable(width=False, height=False)
pad = 10  # padding before frame borders
bwid = 10  # border width for frames
spacing = 15  # padding between frames
style = "groove"

w = 25  # width of descriptor boxes

# Variables
summname = tkinter.StringVar()
region_list = [""]
reg = tkinter.StringVar(value="Choose")

filter_label = tkinter.StringVar()
champ_filter = tkinter.StringVar(value="")
match_filter = tkinter.IntVar(value=20)
q_filter = tkinter.StringVar(value="Select a Queue")
q_filter_list = [""]
role_filter = tkinter.StringVar(value="Select a Role")
role_filter_list = [""]
status_label = tkinter.StringVar(value="App Started")


# FRAME 1 - CONFIGURATION OPTIONS - COLUMNS c1 THROUGH c1+1
config_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
config_frame.grid(row=0, column=0)

tkinter.Label(config_frame, text="Summoner Name:", font="Helvetica 12 bold", height=2, anchor="s").grid()
tkinter.Entry(config_frame, width=45, justify="center", textvariable=summname).grid()

tkinter.Label(config_frame, text="Region:", font="Helvetica 12 bold", height=2, anchor="s").grid()
o_region = tkinter.OptionMenu(config_frame, reg, *region_list)
o_region.grid()

b_get_data = tkinter.Button(config_frame, text="Get Game Data", font="Helvetica 14 bold")
b_get_data.config(width=20, command=update_match_data, bd=5)
b_get_data.grid()


# FRAME 2 - FILTERING OPTIONS
filter_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
filter_frame.grid(row=0, column=1)
tkinter.Label(filter_frame, text="Select Desired Filter(s)", font="Helvetica 12 bold", width=30, anchor="s").grid(columnspan=2)


class MakeFilter:
    # Shared class variables go here
    but_why = "to make a filter that can be used"
    and_how = "using classes, obviously"

    # Define the class FilterPane, including options for the pane (such as its name, etc.)
    def __init__(self, title_string, curr_frame, subrow, subcolumn):
        # I don't know if these are necessary, except perhaps to access them from outside the class
        self.title_string = title_string
        self.curr_frame = curr_frame
        self.subrow = subrow
        self.subcolumn = subcolumn

        # Build the subframe to hold the filter panes
        self.sub_frame = tkinter.Frame(self.curr_frame)
        self.sub_frame.config(borderwidth=2, relief=tkinter.GROOVE, padx=10, pady=10)
        self.sub_frame.grid(row=self.subrow, column=self.subcolumn)

        self.filter_options = tkinter.StringVar(value="") # a string of choices to populate things

        # Label the left pane
        self.pane_label_left = tkinter.Label(self.sub_frame, text="Select " + self.title_string + ":")
        self.pane_label_left.config(font="Helvetica 10", width=20, anchor="s")
        self.pane_label_left.grid(row=0, column=0)

        # Add left pane contents
        self.lb = tkinter.Listbox(self.sub_frame, listvariable=self.filter_options, selectmode=tkinter.MULTIPLE)
        self.lb.config(bd=2, width=20, height=10, relief=tkinter.RIDGE, activestyle="none")
        self.lb.grid(row=1, column=0, rowspan=2, sticky="nsew")

        # Label the right pane
        self.pane_label_right = tkinter.Label(self.sub_frame, text="Selected " + self.title_string + ":")
        self.pane_label_right.config(font="Helvetica 10", width=20, anchor="s")
        self.pane_label_right.grid(row=0, column=2)

        # Add right pane contents
        self.filter_choices = tkinter.Text(self.sub_frame)
        self.filter_choices.config(font="Helvetica 10", bd=2, width=20, height=10, relief=tkinter.FLAT)
        self.filter_choices.config(state=tkinter.DISABLED)  # disable the box to prevent manual entry
        self.filter_choices.grid(row=1, column=2, rowspan=2, sticky="nsew")

        # Add arrow button to middle pane
        self.add_button = tkinter.Button(self.sub_frame, text="\u2192", command=self.update_choices)
        self.add_button.config(font="Helvetica 14 bold", width=6, height=1, bd=3)
        self.add_button.grid(row=1, column=1, sticky="sew")

        # Add clear button to middle pane
        self.clear_button = tkinter.Button(self.sub_frame, text="Clear", command=self.clear_choices)
        self.clear_button.config(font="Helvetica 12 bold", width=6, height=2, bd=3)
        self.clear_button.grid(row=2, column=1, sticky="new")

    def update_choices(self):
        self.filter_choices.config(state=tkinter.NORMAL)
        self.filter_choices.delete(1.0, tkinter.END)

        # Build the string (including newlines between entries using string.join)
        output_string = "\n".join(self.lb.get(ii) for ii in self.lb.curselection())

        # Empty the choices box, insert choices from menu
        self.filter_choices.insert(tkinter.END, output_string)
        self.filter_choices.config(state=tkinter.DISABLED)
        print(self.filter_choices.get(1.0, tkinter.END))

        return

    def clear_choices(self):
        self.lb.selection_clear(0, tkinter.END)

        self.filter_choices.config(state=tkinter.NORMAL)
        self.filter_choices.delete(1.0, tkinter.END)
        self.filter_choices.config(state=tkinter.DISABLED)

        return


SeasonFilter = MakeFilter("Season", filter_frame, 1, 0)
ChampionFilter = MakeFilter("Champion", filter_frame, 2, 0)

# FRAME 2A - SEASON FILTERING ALL OF THIS IS EXTRANEOUS NOW
season_frame = tkinter.Frame(filter_frame, borderwidth=bwid, relief=style, padx=pad, pady=pad)
season_frame.grid(row=1, column=0)

ssn_filter = tkinter.StringVar(value="")
tkinter.Label(season_frame, text="Select Season(s) Below:", font="Helvetica 10",
              width=20, anchor="s").grid(row=0, column=0)
lb_season = tkinter.Listbox(season_frame, listvariable=ssn_filter, selectmode=tkinter.MULTIPLE)
lb_season.config(bd=2, height=10, width=20, relief=tkinter.RIDGE, activestyle="none")
lb_season.grid(row=1, column=0, rowspan=2, sticky="nsew")

b_season = tkinter.Button(season_frame, text="\u2192", font="Helvetica 14 bold")
b_season.config(width=6, height=1, command=button_season, bd=3)
b_season.grid(row=1, column=1, sticky="sew")

tkinter.Label(season_frame, text="Selected Season(s):", font="Helvetica 10",
              width=20, anchor="s").grid(row=0, column=2)
season_text = tkinter.Text(season_frame, font="Helvetica 10")
season_text.configure(state=tkinter.DISABLED, width=20, height=9, bd=2, relief=tkinter.FLAT)
season_text.grid(row=1, column=2, rowspan=2, sticky="nsew")

b_clear_season = tkinter.Button(season_frame, text="Clear", command=clear_season)
b_clear_season.config(font="Helvetica 10 bold", width=6, height=2)
b_clear_season.grid(row=2, column=1, sticky="new")



# Role filtering and other stuff yet to be rebuilt
tkinter.Entry(filter_frame, width=40, justify="center", textvariable=match_filter).grid(row=4, column=1, sticky="ew")

o_qtype = tkinter.OptionMenu(filter_frame, q_filter, *q_filter_list)
o_qtype.grid(row=5, column=1, sticky="ew")

o_role = tkinter.OptionMenu(filter_frame, role_filter, *role_filter_list)
o_role.grid(row=6, column=1, sticky="ew")

filter_label.set("Filtered By:\nAll Matches")
tkinter.Label(filter_frame, textvariable=filter_label, font="Helvetica 10", foreground="blue",
              height=3, anchor="s").grid(columnspan=2)

# PLOTTING OPTIONS SUB-PANEL
plot_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
plot_frame.grid(row=0, column=2)

tkinter.Label(plot_frame, text="Plots", font="Helvetica 12 bold").grid(columnspan=2)

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

b_plot = tkinter.Button(plot_frame, text="Generate Selected Plots", font="Helvetica 14 bold")
b_plot.config(width=25, command=do_plots_parent, bd=5)
b_plot.grid(column=0, columnspan=2)

tkinter.Label(root, textvariable=status_label, height=2, font="Helvetica 14 bold", foreground="blue"
              ).grid(row=1, column=0, columnspan=3, sticky="s")

refresh(firstrun=True)  # run "refresh" with firstrun=True
root.mainloop()

# Now that everything is ready, initialize the program and enter the main loop of tkinter.
# draw_gui()
