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

# IMPORT CUSTOM MODULES
import api_fns
import parse
import plot_fns


# Load important variables from file and update menus
def refresh(firstrun=False):
    """
    :param firstrun: True (app freshly started) or False (app not started fresh)
    :return: config_info, match_data, parsed_data
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
        api_fns.verify_matches(match_data)
    except:
        match_data = {}

    # Try to parse the match data, if it was loaded up
    try:
        parsed_data = parse.parse_data(config_info, match_data)
    except:
        parsed_data = {}

    # Update region filtering options
    try:
        dropdown_region["menu"].delete(0, "end")
        region_list = list(config_info["GameConstants"]["regions.gameconstants"].copy().keys())
        for choice in region_list:
            dropdown_region["menu"].add_command(label=choice, command=tkinter._setit(reg, choice))
    except:
        status_string.set("Unable to find regions.gameconstants file")
        root.update_idletasks()
        pass

    # Update champion filtering options
    try:
        ChampionFilter.filter_options.set(list(config_info["ChampionDictionary"].copy().values()))
    except:
        ChampionFilter.filter_options.set(["Error Finding Champions"])
        status_string.set("Unable to load champion list from servers or from config file")
        root.update_idletasks()
        pass

    # Update season filtering options
    try:
        SeasonFilter.filter_options.set(list(config_info["GameConstants"]["seasons.gameconstants"].copy().values()))
    except:
        SeasonFilter.filter_options.set(["Error Finding Seasons"])
        status_string.set("Unable to find seasons.gameconstants file")
        root.update_idletasks()
        pass

    # Update queue filtering options
    try:
        l = list(config_info["GameConstants"]["queues.gameconstants"].copy().values())
        l.sort()
        QueueFilter.filter_options.set(l)
    except:
        QueueFilter.filter_options.set(["Unable to find seasons.gameconstants file"])
        status_string.set("Unable to load queues.gameconstants file")
        pass

    # Update role filtering options
    try:
        RoleFilter.filter_options.set(list(config_info["GameConstants"]["roles.gameconstants"].copy().values()))
    except:
        RoleFilter.filter_options.set(["Unable to find roles.gameconstants file"])
        status_string.set("Unable to load roles.gameconstants file")
        pass

    return config_info, match_data, parsed_data


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
    status_string.set("Downloading list of matches from Riot's servers...")
    b_get_data.config(relief="sunken", text="Updating Games")  # update the button's appearance
    root.update_idletasks()

    # Refresh the app information
    config_info, match_data, _ = refresh()

    if config_info["AccountID"] == "" or config_info["SummonerID"] == "":
        status_string.set("Double-check summoner name, selected region, and API key")
        b_get_data.config(relief="raised", text="Get Game Data")
        root.update_idletasks()
        return

    full_matchlist, len_full_matchlist = api_fns.get_full_matchlist(config_info)
    status_string.set("Found " + str(len_full_matchlist) + " matches")
    root.update_idletasks()

    # Check that every match (determined by index) in matchlist is also in match_data; retrieve missing matches
    for ii in range(len_full_matchlist):
        status_string.set("Checking local database for match #" + str(ii+1) + " of " + str(len_full_matchlist))
        root.update_idletasks()
        if str(ii + 1) not in match_data:
            # download missing match
            status_string.set(
                "Downloading new match (MatchID =" +
                full_matchlist[ii + 1] +
                ", #" + str(ii + 1) +
                " of " + str(len_full_matchlist) + ")"
            )
            root.update_idletasks()
            match = api_fns.get_match(config_info, full_matchlist[ii + 1])

            api_fns.append_match(config_info, match, ii + 1)

    # Refresh the GUI one last time from the saved files
    config_info, match_data, parsed_data = refresh()
    b_get_data.config(relief="raised", text="Get Game Data")
    status_string.set(
        str(len(match_data)) +
        "/" + str(len_full_matchlist) +
        " matches downloaded and ready to analyze"
    )
    root.update_idletasks()


def do_plots_parent():
    # this could stand to be built on a new thread.... make this a container function to create a plot on a new thread

    # ssn_filter, champ_filter, match_filter, status_string
    refresh()

    GET_FILTERS_FROM_TEXTBOXES_FROM_BUTTONS

    # Prepare to update the label for what's been filtered

    # prepare a variable to hold the filtered match data and quickly filter out remakes
    filtered_match_data = parse.filter_remakes(match_data, parsed_match_data)
    filtered_parsed_match_data = parse.parse_match_data(config_info, filtered_match_data)

    # apply filters if their boxes were checked
    if f_season.get() == 1:
        filtered_match_data = parse.filter_season(
            filtered_match_data, filtered_parsed_match_data, ssn_filter.get())
        filtered_parsed_match_data = parse.parse_match_data(config_info, filtered_match_data)

    if f_champ.get() == 1:
        filtered_match_data = parse.filter_champ(
            filtered_match_data, filtered_parsed_match_data, champ_filter.get())
        filtered_parsed_match_data = parse.parse_match_data(config_info, filtered_match_data)

    if f_match.get() == 1:
        filtered_match_data = parse.filter_match(
            filtered_match_data, match_filter.get())
        filtered_parsed_match_data = parse.parse_match_data(config_info, filtered_match_data)

    if f_QueueType.get() == 1:
        filtered_match_data = parse.filter_qtype(
            filtered_match_data, filtered_parsed_match_data, q_filter.get())
        filtered_parsed_match_data = parse.parse_match_data(config_info, filtered_match_data)

    if f_Role.get() == 1:
        filtered_match_data = parse.filter_role(
            filtered_match_data, filtered_parsed_match_data, role_filter.get())
        filtered_parsed_match_data = parse.parse_match_data(config_info, filtered_match_data)

    # Close any leftover plots (otherwise they draw on top of each other or you just get too many)
    # plt.close("all")  # On second thought, it's fine to have extra plots, but keeping this for posterity.

        status_string.set("Done Generating Plots (" + str(len(filtered_match_data)) + " Matches)")
    else:
        status_string.set("Too few matches (only found " + str(len(filtered_match_data)) + ")")


def testfn(my_arg=0):
    if my_arg:
        print(str(my_arg))
    else:
        print("no_arg")
    print("test fn ran OK")
    return


class MakeFilter:
    # Shared class variables
    pad_amt = 5

    # Define the class FilterPane, including options for the pane (such as its name, etc.)
    def __init__(self, title_string, curr_frame, subrow, subcolumn, box_height):
        # I don't know if these are necessary, except perhaps to access them from outside the class
        self.title_string = title_string
        self.curr_frame = curr_frame
        self.subrow = subrow
        self.subcolumn = subcolumn
        self.box_height = box_height

        # Build the subframe to hold the filter panes
        self.sub_frame = tkinter.Frame(self.curr_frame)
        self.sub_frame.config(borderwidth=2, relief=tkinter.GROOVE, padx=self.pad_amt, pady=self.pad_amt)
        self.sub_frame.grid(row=self.subrow, column=self.subcolumn)

        self.filter_options = tkinter.StringVar(value="")  # a string of choices to populate things

        # Label the left pane
        self.pane_label_left = tkinter.Label(self.sub_frame, text="Select " + self.title_string + ":")
        self.pane_label_left.config(font="Helvetica 10", width=20, anchor="s")
        self.pane_label_left.grid(row=0, column=0)

        # Add left pane contents
        self.lb = tkinter.Listbox(self.sub_frame, listvariable=self.filter_options, selectmode=tkinter.MULTIPLE)
        self.lb.config(bd=2, width=20, height=self.box_height, relief=tkinter.RIDGE, activestyle="none")
        self.lb.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=self.pad_amt, pady=self.pad_amt)

        # Label the right pane
        self.pane_label_right = tkinter.Label(self.sub_frame, text="Selected " + self.title_string + ":")
        self.pane_label_right.config(font="Helvetica 10", width=20, anchor="s")
        self.pane_label_right.grid(row=0, column=2)

        # Add right pane contents
        self.filter_choices = tkinter.Text(self.sub_frame)
        self.filter_choices.config(font="Helvetica 10", bd=2, width=20, height=self.box_height, relief=tkinter.FLAT)
        self.filter_choices.config(state=tkinter.DISABLED)  # disable the box to prevent manual entry
        self.filter_choices.grid(row=1, column=2, rowspan=2, sticky="nsew", padx=self.pad_amt, pady=self.pad_amt)

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
        # print(self.filter_choices.get(1.0, tkinter.END))

        return


    def clear_choices(self):
        # clear out selections on the left pane
        self.lb.selection_clear(0, tkinter.END)

        # clear the choices from the right pane
        self.filter_choices.config(state=tkinter.NORMAL)
        self.filter_choices.delete(1.0, tkinter.END)
        self.filter_choices.config(state=tkinter.DISABLED)

        return


class PlotGen:
    # shared class variables
    pad_amt = 5

    def __init__(self, button_string, button_function, curr_frame, subrow, subcolumn, default_value=0):
        # I don't know if these are necessary, except perhaps to access them from outside the class
        self.button_string = button_string
        self.button_function = button_function
        self.curr_frame = curr_frame
        self.subrow = subrow
        self.subcolumn = subcolumn
        self.default_value = default_value

        # prepare a sub-frame to hold the button and (if applicable) option box
        self.sub_frame = tkinter.Frame(self.curr_frame)
        self.sub_frame.config(borderwidth=2, relief=tkinter.FLAT, padx=self.pad_amt, pady=self.pad_amt)
        self.sub_frame.grid(row=self.subrow, column=self.subcolumn, sticky="nsew")

        # make the button
        self.button = tkinter.Button(self.sub_frame, text=self.button_string, font="Helvetica 10")
        self.button.config(command=self.button_function_callback, bd=3, width=40)

        if self.default_value:
            self.button.grid(row=0, column=0, columnspan=1, sticky="nsew")
        else:
            self.button.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # Prepare necessary integer variable and box if necessary
        if self.default_value:
            self.variable = tkinter.IntVar(value=self.default_value)
            self.variable_box = tkinter.Entry(self.sub_frame, textvariable=self.variable)
            self.variable_box.config(font="Helvetica 10", width=5, relief=tkinter.GROOVE)
            self.variable_box.grid(row=0, column=1, sticky="nsew")


    def button_function_callback(self):
        print("This is a wrapper function for the accompanying plot function " + self.button_string)
        # run the function with or without any associated argument information, as applicable
        if self.default_value:
            self.thread = threading.Thread(target=self.button_function(self.variable.get()))
            self.thread.start()
        else:
            self.thread = threading.Thread(target=self.button_function())
            self.thread.start()
        return

root = tkinter.Tk()  # prepare a widget to hold the UI
root.configure(background="white")
root.title("League of Histograms")
root.iconbitmap('icon.ico')
root.resizable(width=False, height=False)
pad = 10  # padding before frame borders
bwid = 3  # border width for frames
style = tkinter.GROOVE

# FRAME 1 - CONFIGURATION OPTIONS
config_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
config_frame.grid(row=0, column=0)

summname = tkinter.StringVar()
tkinter.Label(config_frame, text="Summoner Name:", font="Helvetica 12 bold", height=2, anchor="s").grid()
tkinter.Entry(config_frame, width=45, justify="center", textvariable=summname).grid()

reg = tkinter.StringVar(value="Choose")
tkinter.Label(config_frame, text="Region:", font="Helvetica 12 bold", height=2, anchor="s").grid()
region_list = [""]
dropdown_region = tkinter.OptionMenu(config_frame, reg, *region_list)
dropdown_region.grid()

b_get_data = tkinter.Button(config_frame, text="Get Game Data")
b_get_data.config(font="Helvetica 14 bold", width=20, command=update_match_data, bd=5)
b_get_data.grid()

# Make the middle frame to contain the filtering options
filter_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
filter_frame.grid(row=0, column=1)
filter_frame_label = tkinter.Label(filter_frame, text="Select Desired Filter(s)")
filter_frame_label.config(font="Helvetica 12 bold", width=30, anchor="s")
filter_frame_label.grid(columnspan=1)

# Add the filters to the middle frame
ChampionFilter = MakeFilter("Champion(s)", filter_frame, 1, 0, 8)
RoleFilter = MakeFilter("Role(s)", filter_frame, 3, 0, 6)
SeasonFilter = MakeFilter("Season(s)", filter_frame, 2, 0, 6)
QueueFilter = MakeFilter("Queue(s)", filter_frame, 4, 0, 10)

# Number of matches filter
match_filter_subframe = tkinter.Frame(filter_frame, borderwidth=2, relief=tkinter.GROOVE, padx=10, pady=10)
match_filter_subframe.grid(row=5, column=0, sticky="ew")
number_of_matches = tkinter.IntVar(value=20)
tkinter.Label(match_filter_subframe, text="Include last ").grid(row=0, column=0)
number_of_matches_entry = tkinter.Entry(match_filter_subframe, width=8, justify="center",
                                        textvariable=number_of_matches)
number_of_matches_entry.grid(row=0, column=1, sticky="ew")
tkinter.Label(match_filter_subframe, text=" matches that meet criteria (0 = include all)").grid(row=0, column=2)

# Create the rightmost frame to contain the plot buttons
plot_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
plot_frame.grid(row=0, column=2)
plot_frame_label = tkinter.Label(filter_frame, text="Generate Plots")
plot_frame_label.config(font="Helvetica 12 bold", width=30, anchor="s")
plot_frame_label.grid(columnspan=1)

WinrateTime = PlotGen("Winrate Over Time\n(Moving Average; Specify Average Width)",
                      testfn, plot_frame, 1, 0, default_value=10)
WinrateChamp = PlotGen("Winrate by Champion\n(Specify Minimum Games Played)",
                       testfn, plot_frame, 2, 0, default_value=5)
WinrateTeammate = PlotGen("Winrate by Teammate\n(Specify Minimum Games Played Together)",
                          testfn, plot_frame, 3, 0, default_value=10)
WinratePartySize = PlotGen("Winrate by Party Size\n(Enter # Games Together to be Considered \"Teammates\")",
                           testfn, plot_frame, 4, 0, default_value=5)
WinrateRole = PlotGen("Winrate by Role\n(Specify Minimum Games Played)",
                      testfn, plot_frame, 5, 0, default_value=5)
WinrateDamage = PlotGen("Winrate by Damage\n(Specify Number of Bins)",
                        testfn, plot_frame, 6, 0, default_value=5)
WinrateDamageFrac = PlotGen("Winrate by Damage Fraction\n(Specify Number of Bins)",
                            testfn, plot_frame, 7, 0, default_value=5)
WinrateMapside = PlotGen("Winrate by Map Side",
                         testfn, plot_frame, 8, 0, default_value=0)

# if len(filtered_parsed_match_data["win_lose"]) > 2:
#     if cb_wr_time.get() == 1:
#         plot_fns.wr_time(filtered_parsed_match_data, ma_box_size.get())
#     if cb_wr_champ.get() == 1:
#         plot_fns.wr_champ(filtered_parsed_match_data, n_games_champ.get())
#     if cb_wr_teammate.get() == 1:
#         plot_fns.wr_teammate(filtered_parsed_match_data, n_games_teammate.get())
#     if cb_wr_party.get() == 1:
#         plot_fns.wr_partysize(filtered_parsed_match_data, n_games_party.get())
#     if cb_wr_role.get() == 1:
#         plot_fns.wr_role(filtered_parsed_match_data, n_games_role.get())
#     if cb_wr_dmg.get() == 1:
#         plot_fns.wr_dmg(filtered_parsed_match_data, n_bins.get())
#     if cb_wr_dmg_frac.get() == 1:
#         plot_fns.wr_dmg_frac(filtered_parsed_match_data, n_bins_frac.get())
#     if cb_wr_mapside.get() == 1:
#         plot_fns.wr_mapside(filtered_parsed_match_data)
#     plt.show()

# Build a status label at the bottom of the UI to keep the user informed
status_string = tkinter.StringVar(value="App Started")
status_label = tkinter.Label(root, textvariable=status_string)
status_label.config(height=2, font="Helvetica 14 bold", foreground="blue", bg="white")
status_label.grid(row=99, column=0, columnspan=9, sticky="s")

# Refresh everything, setting it for first-run
refresh(firstrun=True)

# Start the mainloop of the GUI
root.mainloop()
