#    LICENSE INFORMATION
#    LoLlyPlotty: league of legends statistics and plots.
#    Copyright (C) 2017 Jasper Cook, league_plots@outlook.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    This program comes with ABSOLUTELY NO WARRANTY.
#    This is free software, and you are welcome to redistribute it
#    under certain conditions. See license.txt for details.

# Module-level import(s)
from webbrowser import open_new as webbrowser_open_new
from matplotlib.pyplot import show as pyplot_show

# Custom module/ imports
import api_fns
import parse
import plot_fns

# IMPORT STANDARD MODULES
import threading
import json
import time
import pathlib
import tkinter  # future: import tkinter.ttk


def refresh():
    # Updates variables from files on disk; updates GUI from variables

    try:
        reg.set(Params.config_info["Region"]) if Params.config_info["Region"] is not "" else reg.set("Choose")
    except (NameError, KeyError):
        reg.set("Choose")
    try:
        summname.set(Params.config_info["SummonerName"])
    except (NameError, KeyError):
        summname.set("")
    try:
        fp = "MatchData_" + str(Params.config_info["SummonerName"]) + "_" + str(Params.config_info["Region"]) + ".json"
        with open(fp, "r") as file:
            Params.match_data = json.loads(file.read())
        Params.match_data = api_fns.verify_matches(Params.config_info, Params.match_data)
        Params.status_string.set(value="Loaded " + str(len(Params.match_data)) + " games")
    except (FileNotFoundError, NameError, KeyError):
        Params.match_data = {}
        Params.status_string.set(value="Game data not found - check options, then try \"Get Game Data\" button")

    try:
        key, expiry = api_fns.get_api_key()
        api_key.set(key)
        if float(expiry) < float(time.time()):
            key_entry.config(fg="red")
        else:
            key_entry.config(fg="black")
    except (NameError, ValueError):
        api_key.set("Key Not Found")

    # Update region filtering options
    region_dropdown["menu"].delete(0, "end")
    try:
        region_list = list(Params.config_info["regions.gameconstants"].copy().keys())
        for region in sorted(region_list):
            region_dropdown["menu"].add_command(label=region, command=tkinter._setit(reg, region))
    except (NameError, KeyError):
        oops = "Unable to find regions.gameconstants file"
        region_dropdown["menu"].add_command(label=oops, command=tkinter._setit(reg, oops))
        pass

    # Update filter options
    for flt in Filters:
        flt.reset_box()

    return


def get_data():
    local_threads = []

    def callback():
        # Hand off the API key from the GUI
        api_fns.get_api_key(write_mode=True, key_in=api_key.get())

        Params.status_string.set("Updating settings...")
        b_get_data.config(relief="sunken", text="Please Wait...", bg=Filter.bg_HL)  # update the button's appearance

        # Update app information from the GUI, then refresh the app
        Params.config_info = api_fns.config(reg.get(), summname.get())  # update the configuration info from the GUI
        reg.set(Params.config_info["Region"])  # update the GUI
        summname.set(Params.config_info["SummonerName"])
        refresh()

        if Params.config_info["AccountID"] == "" or Params.config_info["SummonerID"] == "":
            Params.status_string.set("Check summoner name, region, and API key. New keys often don't work immediately.")
            b_get_data.config(relief="raised", text="Get Game Data", bg=Filter.bg_CT)
            return

        Params.status_string.set("Getting match list from Riot servers...")
        full_matchlist, len_full_matchlist = api_fns.get_full_matchlist(Params.config_info)
        Params.status_string.set("Found " + str(len_full_matchlist) + " matches online")

        # Check that every match in matchlist is also in the match data; retrieve missing matches
        game_ids_in_file = list(Params.match_data.copy().keys())
        mm = 0
        for game_id in full_matchlist:
            Params.status_string.set("Checking local database for GameID = " + str(game_id))
            if str(game_id) not in game_ids_in_file:
                # download missing match
                Params.status_string.set(
                    "Downloading game: ID #" + str(game_id) +
                    ". Got " + str(len(game_ids_in_file) + mm) + " of " +
                    str(len_full_matchlist) + " matches."
                )
                match = api_fns.get_match(Params.config_info, game_id, Params.status_string)

                api_fns.append_match(Params.config_info, match, game_id)
                mm += 1

        # Refresh the GUI one last time from the saved files
        refresh()
        b_get_data.config(relief="raised", text="Get Game Data")
        Params.status_string.set(
            "Downloaded " +
            str(len(Params.match_data)) +
            " of " + str(len_full_matchlist) +
            " matches. Ready to plot stuff!"
        )

        return

    local_threads.append(threading.Thread(target=callback))
    local_threads[-1].start()

    return


def plot_generation():
    Params.config_info["Threshold"] = int(threshold_var.get())

    # Check that valid variables have been selected
    if y_var.get() in (parse.Var.b_vars + parse.Var.f_vars + parse.Var.c_vars
                       ) and x_var.get() in (parse.Var.b_vars + parse.Var.f_vars + parse.Var.s_vars):
        Params.status_string.set(value="Parsing data...")
        y_list, x_list, n_kept = parse.Var.create_list(
            Params.config_info, Params.match_data, parse.Vars, y_var.get(), x_var.get(), Filters, recency_filter.get()
        )

        print("Lists to plot:\n", "Y: ", y_list, "\n", "X: ", x_list)

        if len(y_list) == len(x_list) and n_kept > Params.config_info["Threshold"] and len(y_list) > 2:
            Params.status_string.set(value="Preparing " + str(n_kept) + " matches for plotting")

            # If the x variable isn't countable (e.g. if it's "Champion" or "Win/Loss"), use a bar chart
            if (x_var.get() in parse.Var.s_vars + parse.Var.b_vars) and (
                        y_var.get() in parse.Var.b_vars + parse.Var.f_vars):
                plot_fns.simple_bar_plotter(x_list, y_list, threshold=Params.config_info["Threshold"],
                                            x_label=x_var.get(), y_label=y_var.get(),
                                            z_scores=plot_fns.z_scores, conf_interval=ci_var.get())
                pyplot_show()
                Params.status_string.set(value="Plotted data from " + str(n_kept) + " games")

            # If the x variable isn't countable and the y variable is cumulative, use "cumulative" bar chart
            elif x_var.get() in parse.Var.s_vars + parse.Var.b_vars and y_var.get() in parse.Var.c_vars:
                plot_fns.simple_bar_plotter(x_list, y_list, bins_var.get(),
                                            x_label=x_var.get(), y_label=y_var.get(),
                                            dict_type="Cumulative")

                Params.status_string.set(value="Plotted data from " + str(n_kept) + " games")
                pyplot_show()

            # If the x variable and y variable are numeric (e.g. "Damage" vs. "CS"), use a scatter plot
            elif x_var.get() in parse.Var.f_vars and y_var.get() in parse.Var.f_vars:
                plot_fns.make_scatterplot(x_list, y_list, y_var.get(),
                                          x_label=x_var.get(), y_label=y_var.get())

                Params.status_string.set(value="Plotted data from " + str(n_kept) + " games")
                pyplot_show()

            # If the x is a float and y is discrete, use two stacked histograms
            elif x_var.get() in parse.Var.f_vars and y_var.get() in parse.Var.b_vars:
                plot_fns.make_hist(x_list, y_list, bins_var.get(),
                                   x_label=x_var.get(), y_label=y_var.get())
                Params.status_string.set(value="Plotted data from " + str(n_kept) + " games")
                pyplot_show()

            else:
                Params.status_string.set(value="Can't make a useful plot. Try swapping the variables if possible.")

        else:
            Params.status_string.set(value="Not enough matches (" + str(len(y_list)) + " remain after filtering)")
    else:
        Params.status_string.set(value="Check that X and Y variables are valid")


root = tkinter.Tk()  # prepare a widget to hold the UI
root.configure(background="white")
root.title("LoLlyPlotty")
root.iconbitmap('icon.ico')
root.resizable(width=True, height=True)


class Filter:
    pad_amt = 4
    longest_filter_item = 47
    games_to_remove = []  # an empty list to eventually hold game_ids for removal

    # Colors: dark blue #15232b; darker blue #04090c; gold-ish #b0863e; light gold #cdbe91; near-white #f0e6d2
    bg_BG = "#15232b"  # the primary background color         "light slate gray"   "SteelBLue4"  "gray40"
    bg_CT = "#b0863e"  # the contrasting color (for buttons, dropdowns, etc.)
    bg_HL = "#cdbe91"  # the highlight color
    fg_txt = "#f0e6d2"  # the foreground (text) color - contrasts w/ BG color
    fg_btn = "#04090c"  # the foreground (text) color on buttons - contrasts with CT color
    bd_btn = 3  # Border for buttons
    bd_pad = 1  # Border for padding (e.g. inside listboxes) - ends up being internal padding
    bd_SB = 3  # Border width for frames (e.g. the seasons list with its scrollbar)
    bd_ssxn = 3  # border width for subsections (e.g. seasons filter)
    rel_ssxn = tkinter.FLAT  # relief for sub-sections (e.g. a specific filter)
    rel_btn = tkinter.RAISED  # Relief for buttons
    rel_SB = tkinter.SUNKEN  # relief for scrollboxes (e.g. season list with its scrollbar)

    # Define the class FilterPane, including options for the pane (such as its name, etc.)
    def __init__(self, title_string, curr_frame, subcolumn, box_height,
                 config_key, filter_keys, sort_by="values"):
        self.title_string = title_string  # name of the filter boxes
        self.curr_frame = curr_frame  # which frame to put the filter inside of
        self.subcolumn = subcolumn
        self.box_height = box_height  # how long to make the list of filters
        self.config_key = config_key  # the filter's source from the config file
        self.filter_keys = filter_keys  # list of key names in parsed_data to check through
        self.sort_by = sort_by  # whether or not to sort the filter list alphabetically
        self.choices_list = []  # a list of the stored choices for the filter, extracted from listboxes

        # Build the subframe to hold the filter panes
        self.outer_frame = tkinter.Frame(self.curr_frame, bg=self.bg_BG)
        self.outer_frame.config(borderwidth=self.bd_ssxn, relief=self.rel_ssxn, padx=self.pad_amt, pady=self.pad_amt)
        self.outer_frame.grid(column=self.subcolumn, sticky="NSEW")

        # Add the variables to hold the options
        self.filter_options = tkinter.StringVar(value="")  # a string of choices to populate things
        self.filter_choices = tkinter.StringVar(value="")  # a string of choices to populate the selections

        # Label left frame
        self.left_label = tkinter.Label(self.outer_frame, text="Select " + self.title_string + ":")
        self.left_label.config(font="Helvetica 10", bg=self.bg_BG, fg=self.fg_txt)
        self.left_label.grid(row=0, column=0)

        # Create left frame
        self.left_frame = tkinter.Frame(self.outer_frame, relief=self.rel_SB, bg=self.bg_BG, bd=self.bd_SB)
        self.left_frame.grid(row=1, column=0, sticky="NSEW")

        # Add left frame contents
        self.lsb = tkinter.Scrollbar(self.left_frame)  # create a scrollbar
        self.lb = tkinter.Listbox(self.left_frame, listvariable=self.filter_options, selectmode=tkinter.EXTENDED)
        self.lb.config(bd=self.bd_pad, height=self.box_height, relief=tkinter.FLAT, activestyle="none")
        self.lb.config(font="Helvetica 9", width=self.longest_filter_item, yscrollcommand=self.lsb.set)
        self.lb.grid(row=0, column=0, sticky="NSEW")
        self.lb.bind("<Double-Button-1>", self.update_l2r)
        self.lsb.config(command=self.lb.yview)
        self.lsb.grid(row=0, column=1, sticky="NSEW")

        # Create middle frame
        self.middle_frame = tkinter.Frame(self.outer_frame, padx=self.pad_amt, pady=self.pad_amt,
                                          relief=tkinter.FLAT, bg=self.bg_BG)
        self.middle_frame.grid(row=1, column=1, sticky="NSEW")

        # Add arrow button to middle frame
        self.add_button = tkinter.Button(self.middle_frame, text="\u2192", command=self.update_l2r)
        self.add_button.config(font="Helvetica 16 bold", width=5, relief=self.rel_btn)
        self.add_button.config(fg=self.fg_btn, bd=Filter.bd_btn, bg=Filter.bg_CT, activebackground=Filter.bg_HL)
        self.add_button.grid(row=0, column=0, sticky="sew")  # this was "sew"

        # Add 2nd arrow button to middle frame for moving things in the other direction
        self.remove_button = tkinter.Button(self.middle_frame, text="\u2190", command=self.update_r2l)
        self.remove_button.config(font="Helvetica 16 bold", width=5, relief=self.rel_btn)
        self.remove_button.config(fg=self.fg_btn, bd=Filter.bd_btn, bg=Filter.bg_CT, activebackground=Filter.bg_HL)
        self.remove_button.grid(row=1, column=0, sticky="new")

        # Add clear button to middle frame
        self.clear_button = tkinter.Button(self.middle_frame, text="Reset", command=self.reset_box)
        self.clear_button.config(font="Helvetica 11 bold", width=5, relief=self.rel_btn)
        self.clear_button.config(fg=self.fg_btn, bd=Filter.bd_btn, bg=Filter.bg_CT, activebackground=Filter.bg_HL)
        self.clear_button.grid(row=2, column=0, sticky="ew")

        # Label the right pane
        self.right_label = tkinter.Label(self.outer_frame, text="Selected " + self.title_string + " (Blank = All):")
        self.right_label.config(font="Helvetica 10", bg=self.bg_BG, fg=self.fg_txt)
        self.right_label.grid(row=0, column=2)

        # Create right frame
        self.right_frame = tkinter.Frame(self.outer_frame, relief=self.rel_SB, bg=self.bg_BG, bd=self.bd_SB)
        self.right_frame.grid(row=1, column=2, sticky="NSEW")

        # Add right pane contents
        self.rsb = tkinter.Scrollbar(self.right_frame)  # create a scrollbar
        self.rb = tkinter.Listbox(self.right_frame, listvariable=self.filter_choices, selectmode=tkinter.EXTENDED)
        self.rb.config(bd=self.bd_pad, height=self.box_height, relief=tkinter.FLAT, activestyle="none")
        self.rb.config(font="Helvetica 9", width=self.longest_filter_item, yscrollcommand=self.rsb.set)
        self.rb.grid(row=0, column=0, sticky="NSEW")
        self.rb.bind("<Double-Button-1>", self.update_r2l)
        self.rsb.config(command=self.rb.yview)
        self.rsb.grid(row=0, column=1, sticky="NSEW")


    def sort_my_list(self, my_list):
        my_list_sorted = []
        if self.sort_by == "keys":
            keys = list(Params.config_info[str(self.config_key)].copy().keys())
            vals = list(Params.config_info[str(self.config_key)].copy().values())
            try:
                sort_inds = [int(keys[vals.index(vv)]) for vv in my_list]  # sort by number if they're numbers
            except ValueError:
                sort_inds = [keys[vals.index(vv)] for vv in my_list]  # otherwise sort by string
            try:
                sort_inds, my_list_sorted = zip(*sorted(zip(sort_inds, my_list)))  # sort by Schwarzian if possible
            except ValueError:
                my_list_sorted = my_list  # if the list is empty or Schwarzian fails, just don't sort the list
        elif self.sort_by == "values":
            my_list_sorted = sorted(list(set(my_list)))  # sort the list alphabetically otherwise

        return my_list_sorted

    def update_l2r(self, event=None):
        lb_selections = [self.lb.get(ii) for ii in self.lb.curselection()]

        lb_contents = [self.lb.get(ii) for ii in range(self.lb.size())]
        rb_contents = [self.rb.get(ii) for ii in range(self.rb.size())]

        new_lb = [selection for selection in lb_contents if selection not in lb_selections]
        new_rb = rb_contents + lb_selections

        new_lb = self.sort_my_list(new_lb)
        new_rb = self.sort_my_list(new_rb)

        self.filter_options.set(new_lb)
        self.filter_choices.set(new_rb)
        self.lb.selection_clear(0, tkinter.END)
        self.rb.selection_clear(0, tkinter.END)

        self.choices_list = [self.rb.get(ii) for ii in range(self.rb.size())]
        return

    def update_r2l(self, event=None):
        rb_selections = [self.rb.get(ii) for ii in self.rb.curselection()]

        lb_contents = [self.lb.get(ii) for ii in range(self.lb.size())]
        rb_contents = [self.rb.get(ii) for ii in range(self.rb.size())]

        new_lb = lb_contents + rb_selections
        new_rb = [selection for selection in rb_contents if selection not in rb_selections]

        new_lb = self.sort_my_list(new_lb)
        new_rb = self.sort_my_list(new_rb)

        self.filter_options.set(new_lb)
        self.filter_choices.set(new_rb)
        self.lb.selection_clear(0, tkinter.END)
        self.rb.selection_clear(0, tkinter.END)

        self.choices_list = [self.rb.get(ii) for ii in range(self.rb.size())]
        return

    def reset_box(self):
        try:
            options_list = list(Params.config_info[str(self.config_key)].copy().values())
            options_list = self.sort_my_list(options_list)
            # Populate the left and right panes with their initial values
            self.filter_options.set(options_list)
            self.filter_choices.set([])
        except KeyError:
            self.filter_options.set("Error Getting " + str(self.config_key) + " Data")
            Params.status_string.set("Unable to find " + str(self.config_key) + " Data")

        # clear out residual mouse selections on both panes and update the choices list (empty at this point)
        self.lb.selection_clear(0, tkinter.END)
        self.rb.selection_clear(0, tkinter.END)
        self.choices_list = [self.rb.get(ii) for ii in range(self.rb.size())]

        return


class Params:
    status_string = tkinter.StringVar(value="App Started")

    try:
        with open("Configuration.json", "r") as file:
            config_info = json.loads(file.read())
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        config_info = api_fns.config("", "")
        pass

    try:
        fp = "MatchData_" + str(config_info["SummonerName"]) + "_" + str(config_info["Region"]) + ".json"
        with open(fp, "r") as file:
            match_data = json.loads(file.read())
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        match_data = {}

    @classmethod
    def purge(cls, purge_all=False):

        cls.config_info = {}
        with open("Configuration.json", "w") as file:
            json.dump({}, file)

        if purge_all is True:
            # Clear out all match data files for every player
            match_data_files = [str(p) for p in pathlib.Path(".json").iterdir() if "MatchData_" in str(p)]
            for pp in match_data_files:
                with open(pp, "w") as file:
                    json.dump({}, file)
            cls.match_data = {}


# Make the UI
pad = 10  # padding before frame borders
bd_root = 1  # border width for root-level frames
rel_root = tkinter.GROOVE

# TODO: Put tkinter frames (the root-level frames) into ttk.Notebook pages, after switching over to ttk...

# FRAME 1 - CONFIGURATION OPTIONS
config_frame = tkinter.Frame(root, borderwidth=bd_root, relief=rel_root, padx=pad, pady=pad, bg=Filter.bg_BG)
config_frame.grid(row=0, column=0, sticky="NSEW")

summname = tkinter.StringVar()

summ_name_label = tkinter.Label(config_frame, text="Summoner", font="Helvetica 12 bold", anchor="w",
                                bg=Filter.bg_BG, fg=Filter.fg_txt)
summ_name_label.grid(row=0, column=0, sticky="NSEW")

summ_name_entry = tkinter.Entry(config_frame, justify="center", textvariable=summname, width=40)
summ_name_entry.grid(row=1, column=0, sticky="NSEW")

reg = tkinter.StringVar(value="Choose")

region_label = tkinter.Label(config_frame, text="Region", font="Helvetica 12 bold", anchor="e",
                             bg=Filter.bg_BG, fg=Filter.fg_txt)
region_label.grid(row=0, column=1, sticky="NSEW")

region_dropdown = tkinter.OptionMenu(config_frame, reg, *["Choose"])
region_dropdown["anchor"] = "w"
region_dropdown["width"] = 4
region_dropdown["relief"] = tkinter.FLAT
region_dropdown["bd"] = 0
region_dropdown["fg"] = Filter.fg_btn
region_dropdown["borderwidth"] = 0
region_dropdown["padx"] = 5
region_dropdown["pady"] = 2
region_dropdown["highlightthickness"] = 0
region_dropdown["background"] = Filter.bg_CT
region_dropdown["activebackground"] = Filter.bg_HL
region_dropdown["activeforeground"] = Filter.fg_btn
region_dropdown.grid(row=1, column=1, sticky="NSEW")


def open_dev_site(event):
    webbrowser_open_new(r"https://developer.riotgames.com/")


api_key = tkinter.StringVar()
api_key_label = tkinter.Label(config_frame, text="Your API Key:", font="Helvetica 12 bold",
                              bg=Filter.bg_BG, fg=Filter.fg_txt)
api_key_label.grid(columnspan=2, sticky="NSEW")

key_entry = tkinter.Entry(config_frame, width=20, justify="center", textvariable=api_key)
key_entry.config(fg="black", bg="white")
key_entry.grid(columnspan=2, sticky="NSEW")

riot_link = tkinter.Label(config_frame, text="Get API key (free) from developer.riotgames.com",
                          font="Helvetica 10 underline", cursor="hand2", bg=Filter.bg_BG, fg=Filter.fg_txt)
riot_link.grid(columnspan=2, sticky="NSEW")
riot_link.bind("<Button-1>", open_dev_site)

b_get_data = tkinter.Button(config_frame, text="Get Game Data", command=get_data)
b_get_data.config(font="Helvetica 12 bold", width=5, relief=Filter.rel_btn)
b_get_data.config(fg=Filter.fg_btn, bd=Filter.bd_btn, bg=Filter.bg_CT, activebackground=Filter.bg_HL)
b_get_data.grid(columnspan=2, sticky="NSEW")

# Make the middle frame to contain the filtering options
filter_frame = tkinter.Frame(root, borderwidth=bd_root, relief=rel_root, padx=pad, pady=pad, bg=Filter.bg_BG)
filter_frame.grid(row=0, column=1, rowspan=2, sticky="NSEW")

filter_frame_label = tkinter.Label(filter_frame, text="Select Desired Filter(s)", bg=Filter.bg_BG, fg=Filter.fg_txt)
filter_frame_label.config(font="Helvetica 12 bold")
filter_frame_label.grid(sticky="NSEW")

# Add the filters to the middle of the filter frame
Filters = [
    Filter("Champion(s)", filter_frame, 0, 5, "champion", ["Champion"], sort_by="values"),
    Filter("Season(s)", filter_frame, 0, 5, "seasons.gameconstants", ["Season"], sort_by="keys"),
    Filter("Role(s)", filter_frame, 0, 7, "roles.gameconstants", ["Role"], sort_by="keys"),
    Filter("Queue(s)", filter_frame, 0, 8, "queues.gameconstants", ["Queue Type"], sort_by="values")
    ]

# Number of matches filter
recency_filter_subframe = tkinter.Frame(filter_frame, borderwidth=Filter.bd_ssxn, relief=Filter.rel_ssxn)
recency_filter_subframe.config(bg=Filter.bg_BG, padx=pad, pady=pad)
recency_filter_subframe.grid(sticky="NSEW")

recency_filter = tkinter.IntVar(value=0)
recency_filter_label = tkinter.Label(recency_filter_subframe, text="Include last ", font="Helvetica 10", anchor="e",
                                     bg=Filter.bg_BG, fg=Filter.fg_txt)
recency_filter_label.grid(row=0, column=0, sticky="NSEW")

recency_entry = tkinter.Entry(recency_filter_subframe, width=4, justify="center", textvariable=recency_filter)
recency_entry.grid(row=0, column=1, sticky="NSEW")

recency_entry_label = tkinter.Label(recency_filter_subframe,
                                    text=" days worth of games (0 = include all)", font="Helvetica 10", anchor="w",
                                    bg=Filter.bg_BG, fg=Filter.fg_txt)
recency_entry_label.grid(row=0, column=2, sticky="NSEW")

# Plots
plotter_frame = tkinter.Frame(root, borderwidth=bd_root, relief=rel_root, padx=pad, pady=pad, bg=Filter.bg_BG)
plotter_frame.grid(row=1, column=0, sticky="NSEW")

plotter_frame_label = tkinter.Label(plotter_frame, text="Plots", font="Helvetica 12 bold",
                                    bg=Filter.bg_BG, fg=Filter.fg_txt)
plotter_frame_label.grid()


def assign(event, string_var=None):
    curr_box = event.widget

    for selection in curr_box.curselection():
        # Only use the last selection; handles
        value = curr_box.get(int(selection))
        curr_box.selection_set(int(selection))
        if string_var is not None:
            string_var.set(value)

    plot_button.config(text="Make Plot:\n" + y_var.get() + "\nvs.\n" + x_var.get())


# Identify the longest variable to set the width of the x and y variable boxes
long_var = sorted([len(var) for var in parse.Var.b_vars + parse.Var.f_vars + parse.Var.c_vars + parse.Var.s_vars])[-1]

y_var = tkinter.StringVar(value="Choose Y Variable")
y_vars = tkinter.StringVar(value=sorted(parse.Var.b_vars + parse.Var.f_vars + parse.Var.c_vars))

y_var_label = tkinter.Label(plotter_frame, text="Select Y Variable:")
y_var_label.config(font="Helvetica 10", bg=Filter.bg_BG, fg=Filter.fg_txt)
y_var_label.grid()

y_frame = tkinter.Frame(plotter_frame, relief=Filter.rel_SB, bg=Filter.bg_BG, bd=Filter.bd_SB)
y_frame.grid(sticky="NSEW")

y_sb = tkinter.Scrollbar(y_frame)
y_box = tkinter.Listbox(y_frame, listvariable=y_vars, selectmode=tkinter.SINGLE)
y_box.config(activestyle="none", exportselection=False, yscrollcommand=y_sb.set, width=long_var, height=7)
y_box.config(font="Helvetica 9", relief=tkinter.FLAT, bd=Filter.bd_pad)
y_box.grid(row=0, column=0, sticky="NSEW")
y_box.bind("<<ListboxSelect>>", lambda event: assign(event, string_var=y_var))
y_sb.config(command=y_box.yview, relief=tkinter.GROOVE)
y_sb.grid(row=0, column=1, sticky="NSEW")

x_var_label = tkinter.Label(plotter_frame, text="Select X Variable:")
x_var_label.config(font="Helvetica 10", bg=Filter.bg_BG, fg=Filter.fg_txt)
x_var_label.grid()

x_var = tkinter.StringVar(value="Choose X Variable")
x_vars = tkinter.StringVar(value=sorted(parse.Var.b_vars + parse.Var.f_vars + parse.Var.s_vars))

x_frame = tkinter.Frame(plotter_frame, relief=Filter.rel_SB, bg=Filter.bg_BG, bd=Filter.bd_SB)
x_frame.grid(sticky="NSEW")

x_sb = tkinter.Scrollbar(x_frame)
x_box = tkinter.Listbox(x_frame, listvariable=x_vars, selectmode=tkinter.SINGLE)
x_box.config(activestyle="none", exportselection=False, yscrollcommand=x_sb.set, width=long_var, height=7)
x_box.config(font="Helvetica 9", relief=tkinter.FLAT, bd=Filter.bd_pad)
x_box.grid(row=0, column=0, sticky="NSEW")
x_box.bind("<<ListboxSelect>>", lambda event: assign(event, string_var=x_var))
x_sb.config(command=x_box.yview)
x_sb.grid(row=0, column=1, sticky="NSEW")

plotter_opts_frame = tkinter.Frame(plotter_frame, borderwidth=0, relief=tkinter.FLAT, padx=0, pady=5, bg=Filter.bg_BG)
plotter_opts_frame.grid(sticky="NSEW")

threshold_label = tkinter.Label(plotter_opts_frame, text="Specify minimum instances:", anchor="w")
threshold_label.config(font="Helvetica 10", bg = Filter.bg_BG, fg = Filter.fg_txt)
threshold_label.grid(row=0, column=0, sticky="NSEW")
threshold_var = tkinter.StringVar(value=5)
threshold_entry = tkinter.Entry(plotter_opts_frame, textvariable=threshold_var, width=3)
threshold_entry.grid(row=0, column=1, sticky="NSEW")

ci_label = tkinter.Label(plotter_opts_frame, text="Confidence Interval (Error Bars):", anchor="w")
ci_label.config(font="Helvetica 10", bg = Filter.bg_BG, fg = Filter.fg_txt)
ci_label.grid(row=1, column=0, sticky="NSEW")
ci_var = tkinter.StringVar(value="68%")
ci_menu = tkinter.OptionMenu(plotter_opts_frame, ci_var, *sorted(list(plot_fns.z_scores.keys())))
ci_menu["anchor"] = "w"
ci_menu["width"] = 4
ci_menu["relief"] = tkinter.FLAT
ci_menu["bd"] = 0
ci_menu["fg"] = Filter.fg_btn
ci_menu["borderwidth"] = 0
ci_menu["padx"] = 3
ci_menu["pady"] = 2
ci_menu["highlightthickness"] = 0
ci_menu["background"] = Filter.bg_CT
ci_menu["activebackground"] = Filter.bg_HL
ci_menu["activeforeground"] = Filter.fg_btn

ci_menu.grid(row=1, column=1, sticky="NSEW")

bins_label = tkinter.Label(plotter_opts_frame, text="Number of Bins (For Histograms):", anchor="w")
bins_label.config(font="Helvetica 10", bg=Filter.bg_BG, fg=Filter.fg_txt)
bins_label.grid(row=2, column=0, sticky="NSEW")
bins_var = tkinter.StringVar(value=10)
bins_entry = tkinter.Entry(plotter_opts_frame, textvariable=bins_var, width=3)
bins_entry.grid(row=2, column=1, sticky="NSEW")

plot_button = tkinter.Button(plotter_frame, text="Please See Above To Select\nY Variable\nand\nX Variable",
                             command=plot_generation)
plot_button.config(font="Helvetica 9 bold", width=5, relief=Filter.rel_btn)
plot_button.config(fg=Filter.fg_btn, bd=Filter.bd_btn, bg=Filter.bg_CT, activebackground=Filter.bg_HL)
plot_button.grid(sticky="NSEW")

# Build a status label at the bottom of the UI to keep the user informed using the status string
status_label = tkinter.Label(root, textvariable=Params.status_string, relief=rel_root, bd=bd_root)
status_label.config(font="Helvetica 13 bold", foreground=Filter.bg_HL, bg=Filter.bg_BG, padx=pad, pady=pad)
status_label.grid(columnspan=2, sticky="NSEW")


def make_resizable(frame):
    non_resizing_column = ["Menubutton", "Scrollbar"]
    non_resizing_row = ["Label", "Button"]
    # non_resizing_column = []
    # non_resizing_row = []

    # print("Frame is", frame.winfo_class())
    for ii in [0] + list(range(frame.grid_size()[0])):
        if frame.winfo_class() not in non_resizing_column:
            frame.grid_columnconfigure(ii, weight=10)
            # print("  didit")
        else:
            frame.grid_columnconfigure(ii, weight=0)
            # print("  didn't didit")
    for ii in [0] + list(range(frame.grid_size()[1])):
        if frame.winfo_class() not in non_resizing_row:
            frame.grid_rowconfigure(ii, weight=10)
            # print("  didit")
        else:
            frame.grid_rowconfigure(ii, weight=0)
            # print("  didn't didit")

    slaves = frame.grid_slaves()
    if len(slaves) == 0:
        return
    else:
        for slave in slaves:
            make_resizable(slave)
        return

make_resizable(root)

# for widget in []:
#     widget.rowconfigure(0, weight=1)
# for widget in []:
#     widget.columnconfigure(0, weight=1)

# Refresh everything, setting it for first-run, then start the GUI mainloop
refresh()
root.mainloop()
