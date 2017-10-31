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
import matplotlib.pyplot as plt
import webbrowser
import time
matplotlib.use("TkAgg")


def refresh():
    """
    Updates variables from drive; updates GUI from variables
    """
    try:
        reg.set(Params.config_info["Region"]) if Params.config_info["Region"] is not "" else reg.set("Choose")
    except:
        reg.set("Choose")
    try:
        summname.set(Params.config_info["SummonerName"])
    except:
        summname.set("")
    try:
        with open("MatchData_" + str(Params.config_info["SummonerName"]) + ".json", "r") as file:
            Params.match_data = json.loads(file.read())
        Params.match_data = api_fns.verify_matches(Params.config_info, Params.match_data)
    except:
        Params.match_data = {}

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
        region_list = list(Params.config_info["regions.gameconstants"].copy().keys())
        for choice in region_list:
            dropdown_region["menu"].add_command(label=choice, command=tkinter._setit(reg, choice))
    except:
        region_list = ["Unable to find regions.gameconstants file"]
        for choice in region_list:
            dropdown_region["menu"].add_command(label=choice, command=tkinter._setit(reg, choice))
        Params.status_string.set("Unable to find regions.gameconstants file")
        root.update_idletasks()
        pass

    # Update filter options
    for filter in Filters:
        filter.reset_box()

    root.update_idletasks()

    return


def get_data():
    local_threads = []

    def callback():
        # Hand off the API key from the GUI
        api_fns.get_api_key(write_mode=True, key_in=api_key.get())

        Params.status_string.set("Downloading list of matches from Riot's servers...")
        b_get_data.config(relief="sunken", text="Updating Games")  # update the button's appearance
        root.update_idletasks()

        # Update app information from the GUI, then refresh the app
        Params.config_info = api_fns.config(reg.get(), summname.get())  # update the configuration info from the GUI
        reg.set(Params.config_info["Region"])  # update the GUI
        summname.set(Params.config_info["SummonerName"])
        refresh()

        if Params.config_info["AccountID"] == "" or Params.config_info["SummonerID"] == "":
            Params.status_string.set("Double-check summoner name, selected region, and API key")
            b_get_data.config(relief="raised", text="Get Game Data")
            root.update_idletasks()
            return

        full_matchlist, len_full_matchlist = api_fns.get_full_matchlist(Params.config_info)
        Params.status_string.set("Found " + str(len_full_matchlist) + " matches")
        root.update_idletasks()

        # Check that every match in matchlist is also in the match data; retrieve missing matches
        game_ids_in_file = list(Params.match_data.copy().keys())
        mm = 0
        for game_id in full_matchlist:
            Params.status_string.set("Checking local database for GameID = " + str(game_id))
            root.update_idletasks()
            if str(game_id) not in game_ids_in_file:
                # download missing match
                Params.status_string.set(
                    "Downloading game: ID #" + str(game_id) +
                    ". Got " + str(len(game_ids_in_file) + mm) + " of " +
                    str(len_full_matchlist) + " matches."
                )
                root.update_idletasks()
                match = api_fns.get_match(Params.config_info, game_id, Params.status_string)

                api_fns.append_match(Params.config_info, match, game_id)
                mm += 1

        # Refresh the GUI one last time from the saved files
        refresh()
        b_get_data.config(relief="raised", text="Get Game Data")
        Params.status_string.set(
            str(len(Params.match_data)) +
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


def bar_plotter():
    # Check that valid variables have been selected
    print("making barplot")
    if y_var.get() in parse.Var.y_vars and x_var.get() in parse.Var.x_vars:
        Params.status_string.set(value="Analyzing data...")
        y_list, x_list = parse.Var.create_list(
            Params.config_info, Params.match_data, y_var.get(), x_var.get(), Filters, recency_filter.get()
        )

        if len(y_list) == len(x_list) and len(y_list) > int(threshold_var.get()) and len(y_list) > 2:
            Params.status_string.set(value="Preparing " + str(len(y_list)) + " matches for plotting")

            plot_fns.simple_bar_plotter(y_list, x_list, threshold=int(threshold_var.get()),
                                        x_label=x_var.get(), y_label=y_var.get(),
                                        z_scores=plot_fns.z_scores, conf_interval=ci_var.get())

            Params.status_string.set(value="Plot made using " + str(len(y_list)) + " games")
        else:
            Params.status_string.set(value="Not enough matches (only " + str(len(y_list)) + " remain)")
    else:
        Params.status_string.set(value="Check that X and Y variables are valid")


def histogram_plotter():
    if h_var.get() in h_var.get() in parse.Var.h_vars:

        Params.status_string.set(value="Analyzing data...")

        h_list, win_loss_list = parse.Var.create_list(
            Params.config_info, Params.match_data, h_var.get(), "Win/Loss Rate", Filters, recency_filter.get()
        )

        Params.status_string.set(value="Preparing " + str(len(h_list)) + " matches for plotting")

        plot_fns.make_hist(win_loss_list, h_list, h_bins.get(), x_label=h_var.get())

        Params.status_string.set(value="Plot made using " + str(len(h_list)) + " games")
    else:
        Params.status_string.set(value="Check that histogram variable is valid")
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
        self.add_button = tkinter.Button(self.sub_frame, text="\u2192", command=self.update_l2r)
        self.add_button.config(font="Helvetica 16 bold", width=5, height=1, bd=3)
        self.add_button.grid(row=1, column=1, sticky="sew")  # this was "sew"

        # Add 2nd arrow button to middle pane for moving things in the other direction
        self.remove_button = tkinter.Button(self.sub_frame, text="\u2190", command=self.update_r2l)
        self.remove_button.config(font="Helvetica 14 bold", width=5, height=1, bd=3)
        self.remove_button.grid(row=2, column=1, sticky="new")

        # Add clear button to middle pane
        self.clear_button = tkinter.Button(self.sub_frame, text="Reset", command=self.reset_box)
        self.clear_button.config(font="Helvetica 11 bold", width=5, height=1, bd=3)
        self.clear_button.grid(row=3, column=1, sticky="ew")

    def update_l2r(self):
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

    def update_r2l(self):
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
            local_list = list(Params.config_info[str(self.config_key)].copy().values())

            if self.sort_list == True:
                local_list = sorted(local_list)

            self.filter_options.set(local_list)
            self.filter_choices.set([])

        except:
            self.filter_options.set("Error Getting " + str(self.config_key) + " Data")
            Params.status_string.set("Unable to find " + str(self.config_key) + " Data")

        # clear out selections on the left pane
        self.lb.selection_clear(0, tkinter.END)
        self.rb.selection_clear(0, tkinter.END)
        # clear the choices from the right pane

        self.choices_list = [self.rb.get(ii) for ii in range(self.rb.size())]
        return


class Params:
    status_string = tkinter.StringVar(value="App Started")

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


# Finalize the UI
pad = 10  # padding before frame borders
bwid = 3  # border width for frames
wid = 20
style = tkinter.GROOVE

# TODO: Put tkinter frames (the root-level frames) into ttk.Notebook pages, after switching over to ttk...

# FRAME 1 - CONFIGURATION OPTIONS
config_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
config_frame.grid(row=0, column=0)

# Build a status label at the bottom of the UI to keep the user informed using the status string
status_label = tkinter.Label(root, textvariable=Params.status_string)
status_label.config(height=2, font="Helvetica 14 bold", foreground="blue", bg="white")
status_label.grid(row=99, column=0, columnspan=3, sticky="s")


summname = tkinter.StringVar()
tkinter.Label(config_frame, text="Summoner Name:", font="Helvetica 12 bold").grid()
tkinter.Entry(config_frame, width=wid, justify="center", textvariable=summname).grid(sticky="nsew")

reg = tkinter.StringVar(value="Choose")
tkinter.Label(config_frame, text="\nRegion:", font="Helvetica 12 bold", width=8, anchor="s").grid()
region_list = ["Choose"]
dropdown_region = tkinter.OptionMenu(config_frame, reg, *region_list)
dropdown_region.grid()


def open_dev_site(event):
    webbrowser.open_new(r"https://developer.riotgames.com/")
    print(event)


api_key = tkinter.StringVar()
tkinter.Label(config_frame, text="\nYour API Key:", font="Helvetica 12 bold", width=28).grid()
riot_link = tkinter.Label(config_frame, text="Get free key at developer.riotgames.com",
                          font="Helvetica 10 underline", fg="blue", cursor="hand2")
riot_link.grid()
key_box = tkinter.Entry(config_frame, width=wid, justify="center", textvariable=api_key)
key_box.config(fg="black")
key_box.grid(sticky="nsew")
riot_link.bind("<Button-1>", open_dev_site)

tkinter.Label(config_frame, text="", font="Helvetica 12 bold").grid(columnspan=2)

b_get_data = tkinter.Button(config_frame, text="Get Game Data")
b_get_data.config(font="Helvetica 12 bold", width=wid, command=get_data, bd=5)
b_get_data.grid(sticky="nsew")

# Make the middle frame to contain the filtering options
filter_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
filter_frame.grid(row=0, column=1, rowspan=2)
filter_frame_label = tkinter.Label(filter_frame, text="Select Desired Filter(s)")
filter_frame_label.config(font="Helvetica 14 bold", width=30, anchor="s")
filter_frame_label.grid(columnspan=1)

# Add the filters to the middle frame
Filters = [
    Filter("Champion(s)", filter_frame, 0, 8, "ChampionLookup", ["Champion"], sort_list=True),
    Filter("Season(s)", filter_frame, 0, 6, "seasons.gameconstants", ["Season"], sort_list=True),
    Filter("Role(s)", filter_frame, 0, 7, "roles.gameconstants", ["Role"], sort_list=True),
    Filter("Queue(s)", filter_frame, 0, 12, "queues.gameconstants", ["Queue Type"], sort_list=True)
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

plotter_frame = tkinter.Frame(root, borderwidth=bwid, relief=style, padx=pad, pady=pad)
plotter_frame.grid(row=1, column=0)

bar_frame = tkinter.Frame(plotter_frame, borderwidth=bwid, relief=style, padx=pad, pady=pad)
bar_frame.grid(row=0, column=0)

tkinter.Label(bar_frame, text="Bar Plots", font="Helvetica 14 bold", fg="Green").grid()

tkinter.Label(bar_frame, text="Choose Variables:", font="Helvetica 12 bold").grid()

y_var = tkinter.StringVar(value="Y Variable")
tkinter.OptionMenu(bar_frame, y_var, *sorted(parse.Var.y_vars)).grid()

tkinter.Label(bar_frame, text="vs.", font="Helvetica 12 bold").grid()

x_var = tkinter.StringVar(value="X Variable")
tkinter.OptionMenu(bar_frame, x_var, *sorted(parse.Var.x_vars)).grid()

tkinter.Label(bar_frame, text="Specify minimum instances", font="Helvetica 10").grid()
threshold_var = tkinter.StringVar(value=5)
tkinter.Entry(bar_frame, textvariable=threshold_var, width=5).grid()

tkinter.Label(bar_frame, text="Choose Confidence Interval\n(For Error Bars)").grid()
ci_var = tkinter.StringVar(value="68%")
tkinter.OptionMenu(bar_frame, ci_var, *sorted(list(plot_fns.z_scores.keys()))).grid()

custom_plot_button = tkinter.Button(bar_frame, text="Make Your Plot")
custom_plot_button.config(font="Helvetica 12 bold", command=bar_plotter, bd=5, state="active")
custom_plot_button.grid()

hist_frame = tkinter.Frame(plotter_frame, borderwidth=bwid, relief=style, padx=pad, pady=pad)
hist_frame.grid(row=0, column=1)

tkinter.Label(hist_frame, text="Histograms", font="Helvetica 14 bold", fg="Green").grid()
tkinter.Label(hist_frame, text="Choose Variable", font="Helvetica 12 bold").grid()

h_var = tkinter.StringVar(value="Histogram Variable")
tkinter.OptionMenu(hist_frame, h_var, *sorted(parse.Var.h_vars)).grid()

tkinter.Label(hist_frame, text="Number of Bins", font="Helvetica 10").grid()
h_bins = tkinter.StringVar(value=7)
tkinter.Entry(hist_frame, textvariable=h_bins, width=5).grid()

histogram_button = tkinter.Button(hist_frame, text="Make Histogram")
histogram_button.config(font="Helvetica 12 bold", command=histogram_plotter, bd=5, state="active")
histogram_button.grid()


# TODO: wr/time
# TODO: game frequency played vs. time


# Refresh everything, setting it for first-run
refresh()
Params.status_string.set(value="App started; loaded " + str(len(Params.match_data)) + " matches")
root.update_idletasks()

# TODO: Move config stuff out of PlotMaker and into the Params class?
# print(Params.config_info)

# Start the mainloop of the GUI
root.mainloop()
