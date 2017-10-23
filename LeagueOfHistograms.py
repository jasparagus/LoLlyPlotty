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
        with open(PlotMaker.config_info["SummonerName"] + "_MatchData.json", "r") as file:
            PlotMaker.match_data = json.loads(file.read())
        PlotMaker.match_data = api_fns.verify_matches(PlotMaker.config_info, PlotMaker.match_data)
    except:
        PlotMaker.match_data = {}

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
        status_string.set("Unable to find regions.gameconstants file")
        root.update_idletasks()
        pass

    # Update filter options
    # TODO: move these operations into the Filters object as a function, then call that function here instead
    for filter in Filters:
        try:
            local_list = list(PlotMaker.config_info[str(filter.config_key)].copy().keys())

            if filter.sort_list == True:
                local_list.sort()

            filter.filter_options.set(local_list)

        except:
            filter.filter_options.set("Error Getting " + str(filter.config_key) + " Data")
            status_string.set("Unable to find " + str(filter.config_key) + " Data")
        root.update_idletasks()

    return


def get_data():
    local_threads = []

    def callback():
        status_string.set("Downloading list of matches from Riot's servers...")
        b_get_data.config(relief="sunken", text="Updating Games")  # update the button's appearance
        root.update_idletasks()

        # Update app information from the GUI, then refresh the app
        PlotMaker.config_info = api_fns.config(reg.get(), summname.get())  # update the configuration info from the GUI
        reg.set(PlotMaker.config_info["Region"])  # update the GUI
        summname.set(PlotMaker.config_info["SummonerName"])
        refresh()

        if PlotMaker.config_info["AccountID"] == "" or PlotMaker.config_info["SummonerID"] == "":
            status_string.set("Double-check summoner name, selected region, and API key")
            b_get_data.config(relief="raised", text="Get Game Data")
            root.update_idletasks()
            return

        full_matchlist, len_full_matchlist = api_fns.get_full_matchlist(PlotMaker.config_info)
        status_string.set("Found " + str(len_full_matchlist) + " matches")
        root.update_idletasks()

        # Check that every match in matchlist is also in the match data; retrieve missing matches
        game_ids_in_file = list(PlotMaker.match_data.copy().keys())
        mm = 0
        for game_id in full_matchlist:
            status_string.set("Checking local database for GameID = " + str(game_id))
            root.update_idletasks()
            if str(game_id) not in game_ids_in_file:
                # download missing match
                status_string.set(
                    "Downloading game: ID #" + str(game_id) +
                    ". Got " + str(len(game_ids_in_file) + mm) + " of " +
                    str(len_full_matchlist) + " matches."
                )
                root.update_idletasks()
                match = api_fns.get_match(PlotMaker.config_info, game_id, status_string)

                api_fns.append_match(PlotMaker.config_info, match, game_id)
                mm += 1

        # Refresh the GUI one last time from the saved files
        refresh()
        b_get_data.config(relief="raised", text="Get Game Data")
        status_string.set(
            str(len(PlotMaker.match_data)) +
            "/" + str(len_full_matchlist) +
            " matches downloaded and ready to analyze"
        )

        root.update_idletasks()
        return


    local_threads.append(threading.Thread(target=callback))
    local_threads[-1].start()

    return


def cleanup_filters(config_info, match_data):
    parsed_data = parse.parse_data(config_info, match_data)
    # use the resulting parsed data to update the filter options
    return parsed_data


def testfn(parsed_data, my_arg=0):
    # TODO: replace this with an actual function for making a plot
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


class Filter:
    pad_amt = 3
    longest_filter_item = 47
    games_to_remove = []  # an empty list to eventually hold game_ids for removal

    # Define the class FilterPane, including options for the pane (such as its name, etc.)
    def __init__(self, title_string, curr_frame, subrow, subcolumn, box_height,
                 config_key, filter_keys, sort_list=False):
        self.title_string = title_string  # name of the filter boxes
        self.curr_frame = curr_frame  # which frame to put the filter inside of
        self.subrow = subrow  # the row/column of that frame to put it inside
        self.subcolumn = subcolumn
        self.box_height = box_height  # how long to make the list of filters
        self.config_key = config_key  # the filter's source from the config file
        self.filter_keys = filter_keys  # list of key names in parsed_data to check through
        self.sort_list = sort_list  # whether or not to sort the filter list alphabetically
        self.choices_list = []  # a list of the stored choices for the filter

        # Build the subframe to hold the filter panes
        self.sub_frame = tkinter.Frame(self.curr_frame)
        self.sub_frame.config(borderwidth=2, relief=tkinter.GROOVE, padx=self.pad_amt, pady=self.pad_amt)
        self.sub_frame.grid(row=self.subrow, column=self.subcolumn)

        self.filter_options = tkinter.StringVar(value="")  # a string of choices to populate things

        # Label the left pane
        self.pane_label_left = tkinter.Label(self.sub_frame, text="Select " + self.title_string + ":")
        self.pane_label_left.config(font="Helvetica 10")
        self.pane_label_left.grid(row=0, column=0)

        # Add left pane contents
        self.lb = tkinter.Listbox(self.sub_frame, listvariable=self.filter_options, selectmode=tkinter.MULTIPLE)
        self.lb.config(bd=2, height=self.box_height, relief=tkinter.RIDGE, activestyle="none")
        self.lb.config(font="Helvetica 9", width=self.longest_filter_item)
        self.lb.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=self.pad_amt, pady=self.pad_amt)

        # Label the right pane
        self.pane_label_right = tkinter.Label(self.sub_frame, text="Selected " + self.title_string + ":")
        self.pane_label_right.config(font="Helvetica 10")
        self.pane_label_right.grid(row=0, column=2)

        # Add right pane contents
        # TODO: change this pane to a listbox (same as left pane), then pass entries between the two listboxes
        self.filter_choices = tkinter.Text(self.sub_frame)
        self.filter_choices.config(bd=2, height=self.box_height, relief=tkinter.FLAT, wrap=tkinter.NONE)
        self.filter_choices.config(font="Helvetica 9", width=self.longest_filter_item)
        self.filter_choices.config(state=tkinter.DISABLED)  # disable the box to prevent manual entry
        self.filter_choices.grid(row=1, column=2, rowspan=2, sticky="nsew", padx=self.pad_amt, pady=self.pad_amt)

        # Add arrow button to middle pane
        self.add_button = tkinter.Button(self.sub_frame, text="\u2192", command=self.update_choices)
        self.add_button.config(font="Helvetica 14 bold", width=5, height=1, bd=3)
        self.add_button.grid(row=1, column=1, sticky="sew")

        # Add clear button to middle pane
        self.clear_button = tkinter.Button(self.sub_frame, text="Clear", command=self.clear_choices)
        self.clear_button.config(font="Helvetica 12 bold", width=5, height=2, bd=3)
        self.clear_button.grid(row=2, column=1, sticky="new")

    def update_choices(self):
        self.filter_choices.config(state=tkinter.NORMAL)
        self.filter_choices.delete(1.0, tkinter.END)
        # Build the string (including newlines between entries using string.join)
        choices_string = "\n".join(self.lb.get(ii) for ii in self.lb.curselection())
        # Empty the choices box, insert choices from menu
        self.filter_choices.insert(tkinter.END, choices_string)
        self.choices_list = choices_string.split("\n")
        self.filter_choices.config(state=tkinter.DISABLED)
        return

    def clear_choices(self):
        # clear out selections on the left pane
        self.lb.selection_clear(0, tkinter.END)
        # clear the choices from the right pane
        self.filter_choices.config(state=tkinter.NORMAL)
        self.filter_choices.delete(1.0, tkinter.END)
        self.filter_choices.config(state=tkinter.DISABLED)
        self.choices_list = []
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
        with open(config_info["SummonerName"] + "_MatchData.json", "r") as file:
            match_data = json.loads(file.read())
    except:
        match_data = {}

    filtered_data = match_data.copy()

    def __init__(self, button_string, button_function, parsed_key, curr_frame, subrow, subcolumn, default_value=0):
        # I don't know if these are necessary, except perhaps to access them from outside the class
        self.button_string = button_string
        self.button_function = button_function
        self.parsed_key = parsed_key
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

        # make accompanying target for the button, including box and variable if needed
        if self.default_value:
            self.button.grid(row=0, column=0, columnspan=1, sticky="nsew")
            # make the variable and entry box
            self.variable = tkinter.IntVar(value=self.default_value)
            self.variable_box = tkinter.Entry(self.sub_frame, textvariable=self.variable)
            self.variable_box.config(font="Helvetica 10", width=5, relief=tkinter.GROOVE)
            self.variable_box.grid(row=0, column=1, sticky="nsew")
        else:
            self.button.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def button_function_callback(self):
        print("Pressed Button: " + self.button_string)

        Filter.games_to_remove = []   # clear the list of games to remove; it is remade below
        self.filtered_data = self.match_data.copy()

        # parsing should happen here
        print("Parsing Match Data...")
        parsed_data = parse.parse_data(self.config_info, self.filtered_data)
        print("Parsed data has " + str(len(parsed_data["game_id"])) + " matches. Time to loop over filters.")

        for ff in Filters:
            Filter.games_to_remove = parse.filter_matches(self.config_info, parsed_data, Filter.games_to_remove,
                                                         ff.config_key, ff.filter_keys, ff.choices_list)

        # TODO: filter out remakes (games with length < 6 mins
        Filter.games_to_remove = parse.filter_remakes(parsed_data, Filter.games_to_remove)
        Filter.games_to_remove = parse.filter_recency(parsed_data, Filter.games_to_remove, recency_filter.get())

        for game_id in Filter.games_to_remove:
            try:
                self.filtered_data.pop(str(game_id), None)
            except:
                print("A match was already gone and couldn't be removed")

        # Now that the unwanted data has been removed, parse it and make the plot!
        parsed_data = parse.parse_data(self.config_info, self.filtered_data)
        matches_left = len(parsed_data[list(parsed_data.keys())[0]])

        print("Filtering done; " + str(matches_left) + " matches remain (" +
              str(len(Filter.games_to_remove)) + " removed). Time to make the plot")

        # run the function with or without any associated argument information, as applicable
        if matches_left > 2:
            if self.default_value != 0 and matches_left > self.default_value:
                self.plot_threads.append(threading.Thread(
                    target=self.button_function(parsed_data, self.variable.get())
                ))
                self.plot_threads[-1].start()
            elif matches_left > 2:
                self.plot_threads.append(threading.Thread(
                    target=self.button_function(parsed_data)
                ))
                self.plot_threads[-1].start()
            return


root = tkinter.Tk()  # prepare a widget to hold the UI
root.configure(background="white")
root.title("League of Histograms")
root.iconbitmap('icon.ico')
root.resizable(width=False, height=False)
pad = 10  # padding before frame borders
bwid = 3  # border width for frames
wid = 20
style = tkinter.GROOVE

# TODO: Put tkinter frames (the 3 root-level ones) into ttk.Notebook pages, after switching over to ttk...

# FRAME 1 - CONFIGURATION OPTIONS
config_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
config_frame.grid(row=0, column=0)

# tkinter.Label(config_frame, text="Enter Summoner Details\n-------", font="Helvetica 14 bold").grid(
#     row=0, column=0, columnspan=2)
summname = tkinter.StringVar()
tkinter.Label(config_frame, text="Summoner Name:", font="Helvetica 12 bold").grid(
    row=1, column=0, columnspan=2)
tkinter.Entry(config_frame, width=wid, justify="center", textvariable=summname).grid(
    row=2, column=0, columnspan=2, sticky="nsew")

reg = tkinter.StringVar(value="Choose")
tkinter.Label(config_frame, text="Region:", font="Helvetica 12 bold", height=1, width=8, anchor="w").grid(
    row=3, column=0, sticky="nsew")
region_list = ["Choose"]
dropdown_region = tkinter.OptionMenu(config_frame, reg, *region_list)
dropdown_region.grid(row=3, column=1, sticky="nsew")

b_get_data = tkinter.Button(config_frame, text="Get Game Data")
b_get_data.config(font="Helvetica 12 bold", width=wid, command=get_data, bd=5)
b_get_data.grid(row=4,column=0, columnspan=2, sticky="nsew")

# Make the middle frame to contain the filtering options
filter_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
filter_frame.grid(row=0, column=1)
filter_frame_label = tkinter.Label(filter_frame, text="Select Desired Filter(s)")
filter_frame_label.config(font="Helvetica 14 bold", width=30, anchor="s")
filter_frame_label.grid(columnspan=1)

# Add the filters to the middle frame
Filters = [
    Filter("Champion(s)", filter_frame, 1, 0, 8, "ChampionDictionary", ["champion"]),
    Filter("Season(s)", filter_frame, 2, 0, 6, "seasons.gameconstants", ["season"]),
    Filter("Role(s)", filter_frame, 3, 0, 6, "roles.gameconstants", ["role", "lane"]),
    Filter("Queue(s)", filter_frame, 4, 0, 12, "queues.gameconstants", ["queue_type"], sort_list=True)
    ]

# Number of matches filter
recency_filter_subframe = tkinter.Frame(filter_frame, borderwidth=2, relief=tkinter.GROOVE, padx=10, pady=10)
recency_filter_subframe.grid(row=5, column=0, sticky="ew")
recency_filter = tkinter.IntVar(value=0)
tkinter.Label(recency_filter_subframe, text="Include last ").grid(row=0, column=0)
recency_entry = tkinter.Entry(recency_filter_subframe, width=8, justify="center",
                                        textvariable=recency_filter)
recency_entry.grid(row=0, column=1, sticky="ew")
tkinter.Label(recency_filter_subframe, text=" days worth of matches (0 = include all)").grid(row=0, column=2)

# Create the rightmost frame to contain the plot buttons
plot_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
plot_frame.grid(row=0, column=2)
plot_frame_label = tkinter.Label(plot_frame, text="Make Plots")
plot_frame_label.config(font="Helvetica 14 bold", width=30, anchor="s")
plot_frame_label.grid(columnspan=2)

# Make the plot buttons
Plots = [
    PlotMaker("Winrate Over Time\n(Moving Average; Specify Width in Games)", plot_fns.wr_time, "timestamp",
                    plot_frame, 1, 0, default_value=10),
    PlotMaker("Winrate by Champion\n(Specify Minimum Games Played)", testfn, "champion",
                     plot_frame, 2, 0, default_value=5),
    PlotMaker("Winrate by Teammate\n(Specify Minimum Games Played Together)", testfn, "key",
                        plot_frame, 3, 0, default_value=3),
    PlotMaker("Winrate by Party Size\n(Specify Minimum Games Played Together)", testfn, "key",
                         plot_frame, 4, 0, default_value=3),
    PlotMaker("Winrate by Role\n(Specify Minimum Games Played)", testfn, "key",
                    plot_frame, 5, 0, default_value=5),
    PlotMaker("Winrate by Damage\n(Specify Number of Bins)", testfn, "key",
                      plot_frame, 6, 0, default_value=5),
    PlotMaker("Winrate by Damage Fraction\n(Specify Number of Bins)", testfn, "key",
                          plot_frame, 7, 0, default_value=5),
    PlotMaker("Winrate by Map Side", testfn, "key",
              plot_frame, 8, 0),
    PlotMaker("Games Played vs. Time", testfn, "timestamp",
              plot_frame, 9, 0)
]

# Build a status label at the bottom of the UI to keep the user informed
status_string = tkinter.StringVar(value="App Started")
status_label = tkinter.Label(root, textvariable=status_string)
status_label.config(height=2, font="Helvetica 14 bold", foreground="blue", bg="white")
status_label.grid(row=99, column=0, columnspan=9, sticky="s")

# Refresh everything, setting it for first-run
refresh()
status_string.set(value="App started; loaded " + str(len(PlotMaker.match_data)) + " matches")
root.update_idletasks()

# Start the mainloop of the GUI
root.mainloop()
