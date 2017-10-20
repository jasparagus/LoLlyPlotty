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
        reg.set(Plots.config_info["Region"]) if Plots.config_info["Region"] is not "" else reg.set("Choose")
    except:
        reg.set("Choose")
    try:
        summname.set(Plots.config_info["SummonerName"])
    except:
        summname.set("")
    try:
        with open(Plots.config_info["SummonerName"] + "_MatchData.json", "r") as file:
            Plots.match_data = json.loads(file.read())
        api_fns.verify_matches(Plots.match_data)
    except:
        Plots.match_data = {}

    # Update region filtering options
    dropdown_region["menu"].delete(0, "end")
    try:
        region_list = list(Plots.config_info["GameConstants"]["regions.gameconstants"].copy().keys())
        for choice in region_list:
            dropdown_region["menu"].add_command(label=choice, command=tkinter._setit(reg, choice))
    except:
        region_list = ["Unable to find regions.gameconstants file"]
        for choice in region_list:
            dropdown_region["menu"].add_command(label=choice, command=tkinter._setit(reg, choice))
        status_string.set("Unable to find regions.gameconstants file")
        root.update_idletasks()
        pass

    # TODO: add looping over various filter elements here
    # Update champion filtering options
    try:
        ChampionFilter.filter_options.set(list(Plots.config_info["ChampionDictionary"].copy().values()))
    except:
        ChampionFilter.filter_options.set(["Error Finding Champions"])
        status_string.set("Unable to load champion list from servers or from config file")
        root.update_idletasks()
        pass

    # Update season filtering options
    try:
        SeasonFilter.filter_options.set(list(Plots.config_info["GameConstants"]["seasons.gameconstants"].copy().values()))
    except:
        SeasonFilter.filter_options.set(["Error Finding Seasons"])
        status_string.set("Unable to find seasons.gameconstants file")
        root.update_idletasks()
        pass

    # Update queue filtering options (this one is sorted for clarity)
    try:
        l = list(Plots.config_info["GameConstants"]["queues.gameconstants"].copy().values())
        l.sort()
        QueueFilter.filter_options.set(l)
    except:
        QueueFilter.filter_options.set(["Unable to find seasons.gameconstants file"])
        status_string.set("Unable to load queues.gameconstants file")
        pass

    # Update role filtering options
    try:
        RoleFilter.filter_options.set(list(Plots.config_info["GameConstants"]["roles.gameconstants"].copy().values()))
    except:
        RoleFilter.filter_options.set(["Unable to find roles.gameconstants file"])
        status_string.set("Unable to load roles.gameconstants file")
        pass

    return


def get_data():
    local_threads = []

    def callback():
        status_string.set("Downloading list of matches from Riot's servers...")
        b_get_data.config(relief="sunken", text="Updating Games")  # update the button's appearance
        root.update_idletasks()

        # Update app information from the GUI, then refresh the app
        Plots.config_info = api_fns.config(reg.get(), summname.get())  # update the configuration info from the GUI
        reg.set(Plots.config_info["Region"])  # update the GUI
        summname.set(Plots.config_info["SummonerName"])
        refresh()

        if Plots.config_info["AccountID"] == "" or Plots.config_info["SummonerID"] == "":
            status_string.set("Double-check summoner name, selected region, and API key")
            b_get_data.config(relief="raised", text="Get Game Data")
            root.update_idletasks()
            return

        full_matchlist, len_full_matchlist = api_fns.get_full_matchlist(Plots.config_info)
        status_string.set("Found " + str(len_full_matchlist) + " matches")
        root.update_idletasks()

        # Check that every match in matchlist is also in the match data; retrieve missing matches
        for ii in range(len_full_matchlist):
            status_string.set("Checking local database for match #" + str(ii+1) + " of " + str(len_full_matchlist))
            root.update_idletasks()
            if str(ii + 1) not in Plots.match_data:
                # download missing match
                status_string.set(
                    "Downloading new match (MatchID =" +
                    full_matchlist[ii + 1] +
                    ", #" + str(ii + 1) +
                    " of " + str(len_full_matchlist) + ")"
                )
                root.update_idletasks()
                match = api_fns.get_match(Plots.config_info, full_matchlist[ii + 1])
                api_fns.append_match(Plots.config_info, match, ii + 1)

        # Refresh the GUI one last time from the saved files
        refresh()
        b_get_data.config(relief="raised", text="Get Game Data")
        status_string.set(
            str(len(Plots.match_data)) +
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


def testfn(my_arg=0):
    # TODO: replace this with an actual function for making a plot
    # filters to run:
    # champ, season, role, queue, last n

    # potential issues:
    # no matches left after filtering
    # Too few matches remaining str(len(filtered_match_data))

    print("I'm the plot function. I somehow need to get fed filtered match data.")

    if my_arg:
        print("I got handed the integer : " + str(my_arg))
    else:
        print("I got handed no integer because none was needed.")
    print("Test function finished. Plot would be made now.")
    return


class Filter:
    pad_amt = 3
    longest_filter_item = 47
    filters_dictionary = {}

    # Define the class FilterPane, including options for the pane (such as its name, etc.)
    def __init__(self, title_string, curr_frame, subrow, subcolumn, box_height, filter_key, config_key):
        # I don't know if these are necessary, except perhaps to access them from outside the class
        self.title_string = title_string
        self.curr_frame = curr_frame
        self.subrow = subrow
        self.subcolumn = subcolumn
        self.box_height = box_height
        self.filter_key = filter_key

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
        output_string = "\n".join(self.lb.get(ii) for ii in self.lb.curselection())
        # Empty the choices box, insert choices from menu
        self.filter_choices.insert(tkinter.END, output_string)
        self.filter_choices.config(state=tkinter.DISABLED)
        # Store the selections as a string inside of a shared class dictionary
        self.filters_dictionary[self.filter_key] = output_string
        return

    def clear_choices(self):
        # clear out selections on the left pane
        self.lb.selection_clear(0, tkinter.END)
        # clear the choices from the right pane
        self.filter_choices.config(state=tkinter.NORMAL)
        self.filter_choices.delete(1.0, tkinter.END)
        self.filter_choices.config(state=tkinter.DISABLED)
        # Store the selections as a string inside of a shared class dictionary
        self.filters_dictionary[self.filter_key] = ""
        return


class Plots:
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
        print("I'm trying to call a plot for: " + self.button_string)

        # parsing should happen here
        print("First, parse the match data and print it. Here is the result:")
        parsed_data = parse.parse_data(self.config_info, self.match_data)

        print("Parsed " + str(len(parsed_data["win_lose"])) + " matches. Applying each filter")

        ii = 0
        for key in Filter.filters_dictionary:
            print("Filter #" + str(ii+1) + " is " + str(key) + ". Here is a list of the chosen options:")
            # filter the parsed data using the appropriate filters
            filter_list = Filter.filters_dictionary[key].split("\n")
            parsed_data = parse.filter_matches(self.config_info, parsed_data, 0, key, filter_list)
            ii += 1

        print("Filters listed out. Now the plot function is called.")
        # run filter on the data here (loop over them somehow?)

        # run the function with or without any associated argument information, as applicable
        if self.default_value:
            self.plot_threads.append(threading.Thread(target=self.button_function(self.variable.get())))
            self.plot_threads[-1].start()
        else:
            self.plot_threads.append(threading.Thread(target=self.button_function()))
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

# TODO: Put tkinter frames (the 3 root-level ones) into ttk.Notebook pages

# FRAME 1 - CONFIGURATION OPTIONS
config_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
config_frame.grid(row=0, column=0)

summname = tkinter.StringVar()
tkinter.Label(config_frame, text="Summoner Name:", font="Helvetica 12 bold").grid(
    row=0, column=0, columnspan=2)
tkinter.Entry(config_frame, width=wid, justify="center", textvariable=summname).grid(
    row=1, column=0, columnspan=2, sticky="nsew")

reg = tkinter.StringVar(value="Choose")
tkinter.Label(config_frame, text="Region:", font="Helvetica 12 bold", height=1, width=8, anchor="w").grid(
    row=2, column=0, sticky="nsew")
region_list = ["Choose"]
dropdown_region = tkinter.OptionMenu(config_frame, reg, *region_list)
dropdown_region.grid(row=2, column=1, sticky="nsew")

b_get_data = tkinter.Button(config_frame, text="Get Game Data")
b_get_data.config(font="Helvetica 12 bold", width=wid, command=get_data, bd=5)
b_get_data.grid(row=3,column=0, columnspan=2, sticky="nsew")

# Make the middle frame to contain the filtering options
filter_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
filter_frame.grid(row=0, column=1)
filter_frame_label = tkinter.Label(filter_frame, text="Select Desired Filter(s)")
filter_frame_label.config(font="Helvetica 12 bold", width=30, anchor="s")
filter_frame_label.grid(columnspan=1)

# Add the filters to the middle frame
# TODO: put this in list instead of calling them by name, then loop over that list within the refresh() function
ChampionFilter = Filter("Champion(s)", filter_frame, 1, 0, 8, "champion", "ChampionDictionary")
RoleFilter = Filter("Role(s)", filter_frame, 3, 0, 6, ["role", "lane"], "roles.gameconstants")
SeasonFilter = Filter("Season(s)", filter_frame, 2, 0, 6, "season", "seasons.gameconstants")
QueueFilter = Filter("Queue(s)", filter_frame, 4, 0, 10, ["map_id", "queue_type"], "queues.gameconstants")

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

# Make the plot buttons
# TODO: add various plotting functions to the plot buttons
WinrateTime = Plots("Winrate Over Time\n(Moving Average; Specify Width in Games)", testfn, "timestamp",
                    plot_frame, 1, 0, default_value=10)
WinrateChamp = Plots("Winrate by Champion\n(Specify Minimum Games Played)", testfn, "champion",
                     plot_frame, 2, 0, default_value=5)
WinrateTeammate = Plots("Winrate by Teammate\n(Specify Minimum Games Played Together)", testfn, "key",
                        plot_frame, 3, 0, default_value=3)
WinratePartySize = Plots("Winrate by Party Size\n(Specify Minimum Games Played Together)", testfn, "key",
                         plot_frame, 4, 0, default_value=3)
WinrateRole = Plots("Winrate by Role\n(Specify Minimum Games Played)", testfn, "key",
                    plot_frame, 5, 0, default_value=5)
WinrateDamage = Plots("Winrate by Damage\n(Specify Number of Bins)", testfn, "key",
                      plot_frame, 6, 0, default_value=5)
WinrateDamageFrac = Plots("Winrate by Damage Fraction\n(Specify Number of Bins)", testfn, "key",
                          plot_frame, 7, 0, default_value=5)
WinrateMapside = Plots("Winrate by Map Side", testfn, "key",
                       plot_frame, 8, 0, default_value=0)

# Build a status label at the bottom of the UI to keep the user informed
status_string = tkinter.StringVar(value="App Started")
status_label = tkinter.Label(root, textvariable=status_string)
status_label.config(height=2, font="Helvetica 14 bold", foreground="blue", bg="white")
status_label.grid(row=99, column=0, columnspan=9, sticky="s")

# Refresh everything, setting it for first-run
refresh()

# Start the mainloop of the GUI
root.mainloop()
