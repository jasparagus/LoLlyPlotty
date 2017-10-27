# IMPORT CUSTOM MODULES
import api_fns
import parse
import plot_fns
# IMPORT STANDARD MODULES
import threading
import json
import tkinter
# import tkinter.ttk
import matplotlib
import webbrowser
import time
matplotlib.use("TkAgg")


def refresh():
    """
    Updates variables from drive; updates GUI from variables
    """
    try:
        reg.set(PlotMaker.config_info["Region"]) if PlotMaker.config_info["Region"] is not "" else reg.set("Choose")
    except:
        reg.set("Choose")
    try:
        summname.set(PlotMaker.config_info["SummonerName"])
    except:
        summname.set("")
    try:
        with open("MatchData_" + str(PlotMaker.config_info["SummonerName"]) + ".json", "r") as file:
            PlotMaker.match_data = json.loads(file.read())
        PlotMaker.match_data = api_fns.verify_matches(PlotMaker.config_info, PlotMaker.match_data)
    except:
        PlotMaker.match_data = {}

    try:
        key, expiry = api_fns.get_api_key()
        api_key.set(key)
        if float(expiry) < float(time.time()):
            key_box.config(fg="red")
        else:
            key_box.config(fg="black")
    except:
        api_key.set("")

    # Update region filtering options
    dropdown_region["menu"].delete(0, "end")
    try:
        region_list = list(PlotMaker.config_info["regions.gameconstants"].copy().keys())
        for choice in region_list:
            dropdown_region["menu"].add_command(label=choice, command=tkinter._setit(reg, choice))
    except:
        region_list = ["Unable to find regions.gameconstants file"]
        for choice in region_list:
            dropdown_region["menu"].add_command(label=choice, command=tkinter._setit(reg, choice))
        PlotMaker.status_string.set("Unable to find regions.gameconstants file")
        root.update_idletasks()
        pass

    # Update filter options
    # TODO: move these operations into the Filters object as a function, then call that function here instead
    for filter in Filters:
        filter.reset_box()

    root.update_idletasks()

    return


def get_data():
    local_threads = []

    def callback():
        # Hand off the API key from the GUI
        api_fns.get_api_key(write_mode=True, key_in=api_key.get())

        PlotMaker.status_string.set("Downloading list of matches from Riot's servers...")
        b_get_data.config(relief="sunken", text="Updating Games")  # update the button's appearance
        root.update_idletasks()

        # Update app information from the GUI, then refresh the app
        PlotMaker.config_info = api_fns.config(reg.get(), summname.get())  # update the configuration info from the GUI
        reg.set(PlotMaker.config_info["Region"])  # update the GUI
        summname.set(PlotMaker.config_info["SummonerName"])
        refresh()

        if PlotMaker.config_info["AccountID"] == "" or PlotMaker.config_info["SummonerID"] == "":
            PlotMaker.status_string.set("Double-check summoner name, selected region, and API key")
            b_get_data.config(relief="raised", text="Get Game Data")
            root.update_idletasks()
            return

        full_matchlist, len_full_matchlist = api_fns.get_full_matchlist(PlotMaker.config_info)
        PlotMaker.status_string.set("Found " + str(len_full_matchlist) + " matches")
        root.update_idletasks()

        # Check that every match in matchlist is also in the match data; retrieve missing matches
        game_ids_in_file = list(PlotMaker.match_data.copy().keys())
        mm = 0
        for game_id in full_matchlist:
            PlotMaker.status_string.set("Checking local database for GameID = " + str(game_id))
            root.update_idletasks()
            if str(game_id) not in game_ids_in_file:
                # download missing match
                PlotMaker.status_string.set(
                    "Downloading game: ID #" + str(game_id) +
                    ". Got " + str(len(game_ids_in_file) + mm) + " of " +
                    str(len_full_matchlist) + " matches."
                )
                root.update_idletasks()
                match = api_fns.get_match(PlotMaker.config_info, game_id, PlotMaker.status_string)

                api_fns.append_match(PlotMaker.config_info, match, game_id)
                mm += 1

        # Refresh the GUI one last time from the saved files
        refresh()
        b_get_data.config(relief="raised", text="Get Game Data")
        PlotMaker.status_string.set(
            str(len(PlotMaker.match_data)) +
            "/" + str(len_full_matchlist) +
            " matches downloaded and ready to analyze"
        )

        root.update_idletasks()
        return


    local_threads.append(threading.Thread(target=callback))
    local_threads[-1].start()

    return


def purge(purge_all=False):
    with open("Configuration.json", "w") as file:
        json.dump({}, file)

    if purge_all == True:
        print("set this up to delete MatchData and ParsedData files, etc.")



def cleanup_filters(config_info, match_data):
    parsed_data = parse.parse_data(config_info, match_data)
    # use the resulting parsed data to update the filter options
    return parsed_data


def testfn(parsed_data, my_arg=0):
    # TODO: delete this
    # filters to run:
    # champ, season, role, queue, last n

    # potential issues:
    # no matches left after filtering
    # Too few matches remaining str(len(filtered_match_data))

    print("Plot function placeholder has run. It prints parsed_data, making no plots")

    if my_arg:
        print("    I got handed the integer : " + str(my_arg))
    else:
        print("    I got handed no integer because none was needed.")
    print("    Here's that data... ", parsed_data)

    return


root = tkinter.Tk()  # prepare a widget to hold the UI
root.configure(background="white")
root.title("League of Histograms")
root.iconbitmap('icon.ico')
root.resizable(width=True, height=True)


class Filter:
    pad_amt = 3
    longest_filter_item = 47
    games_to_remove = []  # an empty list to eventually hold game_ids for removal

    # Define the class FilterPane, including options for the pane (such as its name, etc.)
    def __init__(self, title_string, curr_frame, subcolumn, box_height,
                 config_key, filter_keys, sort_list=False):
        self.title_string = title_string  # name of the filter boxes
        self.curr_frame = curr_frame  # which frame to put the filter inside of
        self.subcolumn = subcolumn
        self.box_height = box_height  # how long to make the list of filters
        self.config_key = config_key  # the filter's source from the config file
        self.filter_keys = filter_keys  # list of key names in parsed_data to check through
        self.sort_list = sort_list  # whether or not to sort the filter list alphabetically
        self.choices_list = []  # a list of the stored choices for the filter, extracted from listboxes

        # Build the subframe to hold the filter panes
        self.sub_frame = tkinter.Frame(self.curr_frame)
        self.sub_frame.config(borderwidth=2, relief=tkinter.GROOVE, padx=self.pad_amt, pady=self.pad_amt)
        self.sub_frame.grid(column=self.subcolumn)

        # Add the variables to hold the options
        self.filter_options = tkinter.StringVar(value="")  # a string of choices to populate things
        self.filter_choices = tkinter.StringVar(value="")  # a string of choices to populate the selections

        # Label the left pane
        self.pane_label_left = tkinter.Label(self.sub_frame, text="Select " + self.title_string + ":")
        self.pane_label_left.config(font="Helvetica 10")
        self.pane_label_left.grid(row=0, column=0)

        # Add left pane contents
        self.lb = tkinter.Listbox(self.sub_frame, listvariable=self.filter_options, selectmode=tkinter.MULTIPLE)
        self.lb.config(bd=2, height=self.box_height, relief=tkinter.RIDGE, activestyle="none")
        self.lb.config(font="Helvetica 9", width=self.longest_filter_item)
        self.lb.grid(row=1, column=0, rowspan=3, sticky="nsew", padx=self.pad_amt, pady=self.pad_amt)  # rowspan was 2

        # Label the right pane
        self.pane_label_right = tkinter.Label(self.sub_frame, text="Selected " + self.title_string + ":")
        self.pane_label_right.config(font="Helvetica 10")
        self.pane_label_right.grid(row=0, column=2)

        # Add right pane contents
        self.rb = tkinter.Listbox(self.sub_frame, listvariable=self.filter_choices, selectmode=tkinter.MULTIPLE)
        self.rb.config(bd=2, height=self.box_height, relief=tkinter.RIDGE, activestyle="none")
        self.rb.config(font="Helvetica 9", width=self.longest_filter_item)
        self.rb.grid(row=1, column=2, rowspan=3, sticky="nsew", padx=self.pad_amt, pady=self.pad_amt)  # rowspan was 2

        # Add arrow button to middle pane
        self.add_button = tkinter.Button(self.sub_frame, text="\u2192", command=self.update_L2R)
        self.add_button.config(font="Helvetica 16 bold", width=5, height=1, bd=3)
        self.add_button.grid(row=1, column=1, sticky="sew")  # this was "sew"

        # Add 2nd arrow button to middle pane for moving things in the other direction
        self.remove_button = tkinter.Button(self.sub_frame, text="\u2190", command=self.update_R2L)
        self.remove_button.config(font="Helvetica 14 bold", width=5, height=1, bd=3)
        self.remove_button.grid(row=2, column=1, sticky="new")

        # Add clear button to middle pane
        self.clear_button = tkinter.Button(self.sub_frame, text="Reset", command=self.reset_box)
        self.clear_button.config(font="Helvetica 11 bold", width=5, height=1, bd=3)
        self.clear_button.grid(row=3, column=1, sticky="ew")


    def update_L2R(self):
        lb_selections = [self.lb.get(ii) for ii in self.lb.curselection()]

        lb_contents = [self.lb.get(ii) for ii in range(self.lb.size())]
        rb_contents = [self.rb.get(ii) for ii in range(self.rb.size())]

        new_lb = [selection for selection in lb_contents if selection not in lb_selections]
        new_rb = rb_contents + lb_selections

        new_lb = sorted(list(set(new_lb)))
        new_rb = sorted(list(set(new_rb)))

        self.filter_options.set(new_lb)
        self.filter_choices.set(new_rb)
        self.lb.selection_clear(0, tkinter.END)
        self.rb.selection_clear(0, tkinter.END)

        self.choices_list = [self.rb.get(ii) for ii in range(self.rb.size())]
        return

    def update_R2L(self):
        rb_selections = [self.rb.get(ii) for ii in self.rb.curselection()]

        lb_contents = [self.lb.get(ii) for ii in range(self.lb.size())]
        rb_contents = [self.rb.get(ii) for ii in range(self.rb.size())]

        new_lb = lb_contents + rb_selections
        new_rb = [selection for selection in rb_contents if selection not in rb_selections]

        new_lb = sorted(list(set(new_lb)))
        new_rb = sorted(list(set(new_rb)))

        self.filter_options.set(new_lb)
        self.filter_choices.set(new_rb)
        self.lb.selection_clear(0, tkinter.END)
        self.rb.selection_clear(0, tkinter.END)

        self.choices_list = [self.rb.get(ii) for ii in range(self.rb.size())]
        return


    def reset_box(self):
        try:
            local_list = list(PlotMaker.config_info[str(self.config_key)].copy().keys())

            if self.sort_list == True:
                local_list = sorted(local_list)

            self.filter_options.set(local_list)
            self.filter_choices.set([])

        except:
            self.filter_options.set("Error Getting " + str(self.config_key) + " Data")
            PlotMaker.status_string.set("Unable to find " + str(self.config_key) + " Data")

        # clear out selections on the left pane
        self.lb.selection_clear(0, tkinter.END)
        self.rb.selection_clear(0, tkinter.END)
        # clear the choices from the right pane

        self.choices_list = [self.rb.get(ii) for ii in range(self.rb.size())]
        return


class PlotMaker:
    # shared class variables
    pad_amt = 5
    plot_threads = []

    # load in configuration and match data as shared class variables
    try:
        with open("Configuration.json", "r") as file:
            config_info = json.loads(file.read())
    except:
        config_info = api_fns.config("", "")
        pass

    try:
        with open("MatchData_" + str(config_info["SummonerName"]) + ".json", "r") as file:
            match_data = json.loads(file.read())
    except:
        match_data = {}

    filtered_data = match_data.copy()
    parsed_data = {}

    status_string = tkinter.StringVar(value="App Started")

    def __init__(self, button_string, button_function, curr_frame, subcolumn, include_box=False, func_args=[]):
        # I don't know if these are necessary, except perhaps to access them from outside the class
        self.button_string = button_string
        self.button_function = button_function
        self.curr_frame = curr_frame
        self.subcolumn = subcolumn
        self.include_box = include_box
        self.func_args = func_args

        # prepare a sub-frame to hold the button and (if applicable) option box
        self.sub_frame = tkinter.Frame(self.curr_frame)
        self.sub_frame.config(borderwidth=2, relief=tkinter.FLAT, padx=self.pad_amt, pady=self.pad_amt)
        self.sub_frame.grid(column=self.subcolumn, sticky="nsew")

        # make a variable & entry box for handing to the target function, if needed
        self.int_idx = 0
        for ii in range(len(self.func_args)):
            if type(self.func_args[ii]) == int:
                self.int_idx = ii

        if self.include_box:  # checks if there was an integer argument passed and makes an entry box for it
            # make the variable and entry box
            self.variable = tkinter.IntVar(value=self.func_args[self.int_idx])
            self.variable_box = tkinter.Entry(self.sub_frame, textvariable=self.variable)
            self.variable_box.config(font="Helvetica 10", width=5, relief=tkinter.GROOVE)
            self.variable_box.grid(row=0, column=1, sticky="nsew")

        # make the button
        self.button = tkinter.Button(self.sub_frame, text=self.button_string, font="Helvetica 10")
        self.button.config(command=self.button_function_callback, bd=3, width=40)
        self.button.grid(row=0, column=0, sticky="nsew")

    def button_function_callback(self):
        Filter.games_to_remove = []   # clear the list of games to remove; it is remade below
        self.filtered_data = self.match_data.copy()

        self.status_string.set(value="Parsing downloaded data...")
        status_label.after(100)
        PlotMaker.parsed_data = parse.parse_data(self.config_info, self.filtered_data)
        print("Parsed " + str(PlotMaker.parsed_data["n_matches"]) + " matches. Filtering now.")
        self.status_string.set(value="Parsed " + str(PlotMaker.parsed_data["n_matches"]) + " matches. Filtering now.")
        status_label.after(100)

        for ff in Filters:
            Filter.games_to_remove = parse.filter_matches(self.config_info, PlotMaker.parsed_data,
                                                          Filter.games_to_remove, ff.config_key,
                                                          ff.filter_keys, ff.choices_list)

        Filter.games_to_remove = parse.filter_remakes(PlotMaker.parsed_data, Filter.games_to_remove)
        Filter.games_to_remove = parse.filter_recency(PlotMaker.parsed_data, Filter.games_to_remove,
                                                      recency_filter.get())

        for game_id in Filter.games_to_remove:
            try:
                self.status_string.set(value="Removing Game (ID = " + str(game_id) + ")")
                self.filtered_data.pop(str(game_id), None)
            except:
                self.status_string.set(value="Game (ID = " + str(game_id) + ") was already removed")
                print("Match ", game_id, "was already gone and couldn't be removed")

        # Now that the unwanted data has been removed, parse it and make the plot!
        self.status_string.set(value="Preparing data for plotting")
        PlotMaker.parsed_data = parse.parse_data(self.config_info, self.filtered_data)

        # Check to see that there are enough games remaining (store result as a boolean)
        if self.include_box:
            enough_remaining = PlotMaker.parsed_data["n_matches"] > self.variable.get()
            self.func_args[self.int_idx] = self.variable.get()  # if there are integer args
        else:
            enough_remaining = PlotMaker.parsed_data["n_matches"] > 2  # this is a bare minimum...

        # TODO remove saving parsed_data once debugging is done
        with open("ParsedData.json", "w") as file:
            json.dump(PlotMaker.parsed_data, file)

        self.status_string.set(value="Matches after filtering: " + str(PlotMaker.parsed_data["n_matches"]))

        # run the plot function with correct # of arguments (depends on button) only if you have enough matches
        if enough_remaining:

            self.status_string.set(value="Generating plot for " + str(PlotMaker.parsed_data["n_matches"]) + " matches (" +
                                         str(PlotMaker.parsed_data["hours_played"]) + " hours of gameplay). " +
                                         str(len(Filter.games_to_remove)) +
                                         " games were excluded by filters (or as remakes)")

            self.plot_threads.append(threading.Thread(
                target=self.button_function(PlotMaker.parsed_data, *self.func_args)
            ))
            self.plot_threads[-1].start()

        else:
            self.status_string.set(value="Not enough matches to make the plot (" + str(PlotMaker.parsed_data["n_matches"]) +
                                         " of " + str(len(self.match_data)) + " games remain after filtering)")

        return


# Finalize the UI
pad = 10  # padding before frame borders
bwid = 3  # border width for frames
wid = 20
style = tkinter.GROOVE

# TODO: Put tkinter frames (the 3 root-level ones) into ttk.Notebook pages, after switching over to ttk...

# FRAME 1 - CONFIGURATION OPTIONS
config_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
config_frame.grid(row=0, column=0)

# Build a status label at the bottom of the UI to keep the user informed using the status string
status_label = tkinter.Label(root, textvariable=PlotMaker.status_string)
status_label.config(height=2, font="Helvetica 14 bold", foreground="blue", bg="white")
status_label.grid(row=99, column=0, columnspan=3, sticky="s")


summname = tkinter.StringVar()
tkinter.Label(config_frame, text="Summoner Name:", font="Helvetica 12 bold").grid(row=0, columnspan=2)
tkinter.Entry(config_frame, width=wid, justify="center", textvariable=summname).grid(row=1, columnspan=2, sticky="nsew")

reg = tkinter.StringVar(value="Choose")
tkinter.Label(config_frame, text="Region:", font="Helvetica 12 bold", height=1, width=8, anchor="w").grid(
    row=2, column=0, sticky="nsew")
region_list = ["Choose"]
dropdown_region = tkinter.OptionMenu(config_frame, reg, *region_list)
dropdown_region.grid(row=2, column=1, sticky="nsew")


def open_dev_site(event):
    webbrowser.open_new(r"https://developer.riotgames.com/")
    print(event)

api_key = tkinter.StringVar()
tkinter.Label(config_frame, text="\nYour API Key:", font="Helvetica 12 bold", width=28).grid(columnspan=2)
riot_link = tkinter.Label(config_frame, text="Get free key at developer.riotgames.com",
                          font="Helvetica 10 underline", fg="blue", cursor="hand2")
riot_link.grid(columnspan=2)
key_box = tkinter.Entry(config_frame, width=wid, justify="center", textvariable=api_key)
key_box.config(fg="black")
key_box.grid(columnspan=2, sticky="nsew")
riot_link.bind("<Button-1>", open_dev_site)


tkinter.Label(config_frame, text="", font="Helvetica 12 bold").grid(columnspan=2)

b_get_data = tkinter.Button(config_frame, text="Get Game Data")
b_get_data.config(font="Helvetica 12 bold", width=wid, command=get_data, bd=5)
b_get_data.grid(row=10, column=0, columnspan=2, sticky="nsew")

# Make the middle frame to contain the filtering options
filter_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
filter_frame.grid(row=0, column=1)
filter_frame_label = tkinter.Label(filter_frame, text="Select Desired Filter(s)")
filter_frame_label.config(font="Helvetica 14 bold", width=30, anchor="s")
filter_frame_label.grid(columnspan=1)

# Add the filters to the middle frame
Filters = [
    Filter("Champion(s)", filter_frame, 0, 8, "ChampionDictionary", ["champion"], sort_list=True),
    Filter("Season(s)", filter_frame, 0, 6, "seasons.gameconstants", ["season"], sort_list=True),
    Filter("Role(s)", filter_frame, 0, 6, "roles.gameconstants", ["role", "lane"], sort_list=True),
    Filter("Queue(s)", filter_frame, 0, 12, "queues.gameconstants", ["queue_type"], sort_list=True)
    ]

# Number of matches filter
recency_filter_subframe = tkinter.Frame(filter_frame, borderwidth=2, relief=tkinter.GROOVE, padx=10, pady=10)
recency_filter_subframe.grid(row=5, column=0, sticky="ew")
recency_filter = tkinter.IntVar(value=0)
tkinter.Label(recency_filter_subframe, text="Include last ").grid(row=0, column=0)
recency_entry = tkinter.Entry(recency_filter_subframe, width=8, justify="center",
                              textvariable=recency_filter)
recency_entry.grid(row=0, column=1, sticky="ew")
tkinter.Label(recency_filter_subframe, text=" days worth of games (0 = include all games)").grid(row=0, column=2)

# Create the rightmost frame to contain the plot buttons
plot_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
plot_frame.grid(row=0, column=2)
plot_frame_label = tkinter.Label(plot_frame, text="Make Plots")
plot_frame_label.config(font="Helvetica 14 bold", width=30, anchor="s")
plot_frame_label.grid(columnspan=2)

# Make the plot buttons
Plots = [
    PlotMaker("Winrate Over Time\n(Moving Average; Specify Width in Games)", plot_fns.wr_time,
              plot_frame, 0,
              func_args=[10]),
    PlotMaker("Games Played vs. Time", testfn,
              plot_frame, 0,
              func_args=[]),
    PlotMaker("Winrate by Teammate\n(Specify Minimum Games Played Together)", plot_fns.wr_teammate,
              plot_frame, 0, include_box=True,
              func_args=[5]),
    PlotMaker("Winrate by Party Size\n(Specify Minimum Games Played Together)", plot_fns.wr_partysize,
              plot_frame, 0, include_box=True,
              func_args=[5]),
    PlotMaker("Winrate by Role\n(Specify Minimum Games Played)", plot_fns.simple_wr_var,
              plot_frame, 0, include_box=True,
              func_args=[["role_pretty"], ["win_lose"], 5, "Winrate By Role"]),
    PlotMaker("Winrate by Map Side", plot_fns.simple_wr_var,
              plot_frame, 0,
              func_args=[["map_side"], ["win_lose"], 1, "Winrate By Map Side"]),
    PlotMaker("Winrate by Lane Opponent's Champion\n(Specify Minimum Games Against)", plot_fns.simple_wr_var,
              plot_frame, 0, include_box=True,
              func_args=[["lane_opponent_champion_name"], ["win_lose"], 10, "Winrate By Lane Opponent"]),
    PlotMaker("Winrate by Champion\n(Specify Minimum Games Played)", plot_fns.simple_wr_var,
              plot_frame, 0, include_box=True,
              func_args=[["champion_name"], ["win_lose"], 5, "Winrate By Champion"]),
    PlotMaker("Winrate by Damage\n(Specify Number of Bins)", plot_fns.wr_dmg,
              plot_frame, 0, include_box=True,
              func_args=[5]),
    PlotMaker("Winrate by Damage Fraction\n(Specify Number of Bins)", plot_fns.wr_dmg_frac,
              plot_frame, 0, include_box=True,
              func_args=[5]),
]

# Refresh everything, setting it for first-run
refresh()
PlotMaker.status_string.set(value="App started; loaded " + str(len(PlotMaker.match_data)) + " matches")
root.update_idletasks()

# Start the mainloop of the GUI
root.mainloop()
