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

import api_fns
import parse
import plot_fns

import webbrowser
import json
import time
import pathlib
import tkinter  # future: import tkinter.ttk
import threading

import matplotlib.pyplot


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


class App:
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

    pad_main = 10  # padding before frame borders
    bd_root = 1  # border width for root-level frames
    rel_root = tkinter.GROOVE

    def __init__(self):
        self.root = tkinter.Tk()  # prepare a widget to hold the UI
        self.root.configure(background=self.bg_BG)
        self.root.title("LoLlyPlotty")
        self.root.iconbitmap('icon.ico')
        # self.root.geometry("1200x680")  # TODO: set this up
        self.root.resizable(width=True, height=True)

        self.status_string = tkinter.StringVar(value="App Started")

        try:
            with open("Configuration.json", "r") as file:
                self.config_info = json.loads(file.read())
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.config_info = api_fns.config("", "")
            pass

        try:
            fp = "MatchData_" + str(self.config_info["SummonerName"]) + "_" + str(self.config_info["Region"]) + ".json"
            with open(fp, "r") as file:
                self.match_data = json.loads(file.read())
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.match_data = {}

        self.canvas = tkinter.Canvas(self.root, borderwidth=0)
        self.mainframe = tkinter.Frame(self.canvas, width=1100, height=670)
        self.mainframe_sb = tkinter.Scrollbar(self.root, command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.mainframe_sb.set)
        self.canvas.grid(row=0, column=0, sticky="NSEW")
        self.mainframe.grid(row=0, column=0, sticky="NSEW")
        self.mainframe_sb.grid(row=0, column=2, rowspan=2, sticky="NSEW")

        self.config_frame = ConfigFrame(self, self.mainframe)

        # Make the middle frame to contain the filtering options
        self.filter_frame = tkinter.Frame(self.mainframe, borderwidth=self.bd_root, relief=self.rel_root,
                                          padx=self.pad_main, pady=self.pad_main, bg=self.bg_BG)
        self.filter_frame.grid(row=0, column=1, rowspan=2, sticky="NSEW")

        self.filter_frame_label = tkinter.Label(self.filter_frame, text="Select Desired Filter(s)",
                                                bg=self.bg_BG, fg=self.fg_txt)
        self.filter_frame_label.config(font="Helvetica 12 bold")
        self.filter_frame_label.grid(sticky="NSEW")

        # Recency filter
        recency_filter_subframe = tkinter.Frame(self.filter_frame, borderwidth=self.bd_ssxn, relief=self.rel_ssxn)
        recency_filter_subframe.config(bg=self.bg_BG, padx=self.pad_main, pady=self.pad_main)
        recency_filter_subframe.grid(sticky="NSEW")

        self.recency_filter = tkinter.IntVar(value=0)
        self.recency_filter_label = tkinter.Label(recency_filter_subframe, text="Include last ", font="Helvetica 10",
                                                  anchor="e", bg=self.bg_BG, fg=self.fg_txt)
        self.recency_filter_label.grid(row=0, column=0, sticky="NSEW")

        self.recency_entry = tkinter.Entry(recency_filter_subframe, textvariable=self.recency_filter, width=4,
                                           justify="center")
        self.recency_entry.grid(row=0, column=1, sticky="NSEW")

        self.recency_entry_label = tkinter.Label(recency_filter_subframe,
                                                 text=" days worth of games (0 = include all)", font="Helvetica 10",
                                                 anchor="w", bg=self.bg_BG, fg=self.fg_txt)
        self.recency_entry_label.grid(row=0, column=2, sticky="NSEW")

        self.scrollable_filters = [
            FilterListbox(self, self.filter_frame, "Champion(s)", 0, 7, "champion",
                          ["Champion"], sort_by="values"),
            FilterListbox(self, self.filter_frame, "Season(s)", 0, 7, "seasons.gameconstants",
                          ["Season"], sort_by="keys"),
            FilterListbox(self, self.filter_frame, "Role(s)", 0, 7, "roles.gameconstants",
                          ["Role"], sort_by="keys"),
            FilterListbox(self, self.filter_frame, "Queue(s)", 0, 8, "queues.gameconstants",
                          ["Queue Type"], sort_by="values"),
            # TODO: figure out how to handle these filters
            # FilterListbox(self, self.filter_frame, "Item(s)", 0, 8, "item",
            #               ["Item"], sort_by="values"),
            # FilterListbox(self, self.filter_frame, "Summoner Spell(s)", 0, 8, "summoner",
            #               ["Summoner Spell 1", "Summoner Spell 2"], sort_by="values"),
            FilterListbox(self, self.filter_frame, "Teammate(s)", 0, 8, "Teammates",
                          ["Teammate (By Name)"], sort_by="values", display_keyval="keys"),
        ]

        self.plotter_frame = PlotterBox(self, self.mainframe)

        # Build a status label at the bottom of the UI to keep the user informed using the status string
        self.status_label = tkinter.Label(self.mainframe, textvariable=self.status_string,
                                          relief=self.rel_root, bd=self.bd_root)
        self.status_label.config(font="Helvetica 13 bold", foreground=self.bg_HL, bg=self.bg_BG,
                                 padx=self.pad_main, pady=self.pad_main)
        self.status_label.grid(columnspan=2, sticky="NSEW")

    def refresh(self):
        # Updates variables and then GUI from disk; no other changes

        try:
            if self.config_info["Region"] is not "":
                self.config_frame.reg.set(self.config_info["Region"])
            else:
                self.config_frame.reg.set("Choose")
        except (NameError, KeyError):
            self.config_frame.reg.set("Choose")
        try:
            self.config_frame.summname.set(self.config_info["SummonerName"])
        except (NameError, KeyError):
            self.config_frame.summname.set("")
        try:
            fp = ("MatchData_" + str(self.config_info["SummonerName"]) + "_" +
                  str(self.config_info["Region"]) + ".json")
            with open(fp, "r") as file:
                self.match_data = json.loads(file.read())
            self.match_data = api_fns.verify_matches(self.config_info, self.match_data)
            self.status_string.set(value="Loaded " + str(len(self.match_data)) + " games")
        except (FileNotFoundError, NameError, KeyError):
            self.match_data = {}
            self.status_string.set(value="Game data not found - check options, then try \"Get Game Data\" button")

        try:
            self.plotter_frame.threshold_var.set(int(self.config_info["Threshold"]))
        except KeyError:
            self.plotter_frame.threshold_var.set(int(5))
            self.config_info["Threshold"] = int(self.plotter_frame.threshold_var.get())

        try:
            key, expiry = api_fns.get_api_key()
            self.config_frame.api_key.set(key)
            if float(expiry) < float(time.time()):
                self.config_frame.api_key_entry.config(fg="red")
            else:
                self.config_frame.api_key_entry.config(fg="black")
        except (NameError, ValueError):
            self.config_frame.api_key.set("Key Not Found")

        # Update region filtering options
        self.config_frame.region_dropdown["menu"].delete(0, "end")
        try:
            region_list = list(self.config_info["regions.gameconstants"].copy().keys())
            for region in sorted(region_list):
                self.config_frame.region_dropdown["menu"].add_command(
                    label=region, command=tkinter._setit(self.config_frame.reg, region))
        except (NameError, KeyError):
            oops = "Unable to find regions.gameconstants file"
            self.config_frame.region_dropdown["menu"].add_command(
                label=oops, command=tkinter._setit(self.config_frame.reg, oops))
            pass

        # Update filter options
        for flt in self.scrollable_filters:
            flt.reset_box()

        self.config_info = api_fns.config_overwrite(self.config_info)

    def purge(self, purge_all=False):

        self.config_info = {}
        with open("Configuration.json", "w") as file:
            json.dump({}, file)

        if purge_all is True:
            # Clear out all match data files for every player
            match_data_files = [str(p) for p in pathlib.Path(".json").iterdir() if "MatchData_" in str(p)]
            for pp in match_data_files:
                with open(pp, "w") as file:
                    json.dump({}, file)
            self.match_data = {}


class ConfigFrame:
    def __init__(self, parent_app, parent_frame):
        self.parent_app = parent_app
        self.parent_frame = parent_frame
        self.sub_frame = tkinter.Frame(self.parent_frame, borderwidth=self.parent_app.bd_root,
                                       relief=self.parent_app.rel_root, bg=self.parent_app.bg_BG,
                                       pady=self.parent_app.pad_main, padx=self.parent_app.pad_main)
        self.sub_frame.grid(row=0, column=0, sticky="NSEW")

        self.summname = tkinter.StringVar()

        summ_name_label = tkinter.Label(self.sub_frame, text="Summoner", font="Helvetica 12 bold", anchor="w",
                                        bg=self.parent_app.bg_BG, fg=self.parent_app.fg_txt)
        summ_name_label.grid(row=0, column=0, sticky="NSEW")

        summ_name_entry = tkinter.Entry(self.sub_frame, justify="center", textvariable=self.summname, width=40)
        summ_name_entry.grid(row=1, column=0, sticky="NSEW")

        self.reg = tkinter.StringVar(value="Choose")

        region_label = tkinter.Label(self.sub_frame, text="Region", font="Helvetica 12 bold", anchor="e",
                                     bg=self.parent_app.bg_BG, fg=self.parent_app.fg_txt)
        region_label.grid(row=0, column=1, sticky="NSEW")

        self.region_dropdown = tkinter.OptionMenu(self.sub_frame, self.reg, *["Choose"])
        self.region_dropdown["anchor"] = "w"
        self.region_dropdown["width"] = 4
        self.region_dropdown["relief"] = tkinter.FLAT
        self.region_dropdown["bd"] = 0
        self.region_dropdown["fg"] = self.parent_app.fg_btn
        self.region_dropdown["borderwidth"] = 0
        self.region_dropdown["padx"] = 5
        self.region_dropdown["pady"] = 2
        self.region_dropdown["highlightthickness"] = 0
        self.region_dropdown["background"] = self.parent_app.bg_CT
        self.region_dropdown["activebackground"] = self.parent_app.bg_HL
        self.region_dropdown["activeforeground"] = self.parent_app.fg_btn
        self.region_dropdown.grid(row=1, column=1, sticky="NSEW")

        self.api_key = tkinter.StringVar()
        api_key_label = tkinter.Label(self.sub_frame, text="Your API Key:", font="Helvetica 12 bold",
                                      bg=self.parent_app.bg_BG, fg=self.parent_app.fg_txt)
        api_key_label.grid(columnspan=2, sticky="NSEW")

        self.api_key_entry = tkinter.Entry(self.sub_frame, width=20, justify="center", textvariable=self.api_key)
        self.api_key_entry.config(fg="black", bg="white")
        self.api_key_entry.grid(columnspan=2, sticky="NSEW")

        riot_link = tkinter.Label(self.sub_frame, text="Get API key (free) from developer.riotgames.com",
                                  font="Helvetica 10 underline", cursor="hand2",
                                  bg=self.parent_app.bg_BG, fg=self.parent_app.fg_txt)
        riot_link.grid(columnspan=2, sticky="NSEW")
        riot_link.bind("<Button-1>", self.open_dev_site)

        self.b_get_data = tkinter.Button(self.sub_frame, text="Get Game Data", command=self.get_data)
        self.b_get_data.config(font="Helvetica 12 bold", relief=self.parent_app.rel_btn)
        self.b_get_data.config(fg=self.parent_app.fg_btn, bd=self.parent_app.bd_btn, bg=self.parent_app.bg_CT,
                               activebackground=self.parent_app.bg_HL)
        self.b_get_data.grid(columnspan=2, sticky="NSEW")

    def get_data(self):
        local_threads = []

        def callback(self):
            # Hand off the API key from the GUI
            api_fns.get_api_key(write_mode=True, key_in=self.api_key.get())

            self.parent_app.status_string.set("Updating settings...")
            self.b_get_data.config(relief="sunken", text="Please Wait...", bg=self.parent_app.bg_HL)

            # Update app information from the GUI, then refresh the app
            self.parent_app.config_info = api_fns.config(self.reg.get(),
                                                         self.summname.get())  # update configuration info from GUI
            self.reg.set(self.parent_app.config_info["Region"])  # update the GUI
            self.summname.set(self.parent_app.config_info["SummonerName"])
            self.parent_app.refresh()  # TODO: is this necessary here?

            if self.parent_app.config_info["AccountID"] == "" or self.parent_app.config_info["SummonerID"] == "":
                self.parent_app.status_string.set("Check summoner name, region, and API key." +
                                                  " New keys often don't work immediately.")
                self.b_get_data.config(relief="raised", text="Get Game Data", bg=self.parent_app.bg_CT)
                return

            self.parent_app.status_string.set("Getting match list from Riot servers...")
            full_matchlist, len_full_matchlist = api_fns.get_full_matchlist(self.parent_app.config_info)
            self.parent_app.status_string.set("Found " + str(len_full_matchlist) + " matches online")

            # Check that every match in matchlist is also in the match data; retrieve missing matches
            game_ids_in_file = list(self.parent_app.match_data.copy().keys())
            mm = 0
            for game_id in full_matchlist:
                self.parent_app.status_string.set("Checking local database for GameID = " + str(game_id))
                if str(game_id) not in game_ids_in_file:
                    # download missing match
                    self.parent_app.status_string.set(
                        "Downloading game: ID #" + str(game_id) +
                        ". Got " + str(len(game_ids_in_file) + mm) + " of " +
                        str(len_full_matchlist) + " matches."
                    )
                    match = api_fns.get_match(self.parent_app.config_info, game_id, self.parent_app.status_string)

                    api_fns.append_match(self.parent_app.config_info, match, game_id)
                    mm += 1

            # Get a list of teammates from the data (given the current "threshold")
            parse.prep_teammates(self.parent_app.config_info, self.parent_app.match_data)
            self.parent_app.status_string.set("Compiling a list of friends/teammates")
            # Refresh the GUI one last time from the saved files
            self.parent_app.refresh()
            self.b_get_data.config(relief="raised", text="Get Game Data", bg=self.parent_app.bg_CT)
            self.parent_app.status_string.set(
                "Downloaded " +
                str(len(self.parent_app.match_data)) +
                " of " + str(len_full_matchlist) +
                " matches. Ready to plot stuff!"
            )

            return

        local_threads.append(threading.Thread(target=callback, args=(self, )))
        local_threads[-1].start()

    @staticmethod
    def open_dev_site(_event):
        webbrowser.open_new(r"https://developer.riotgames.com/")


class FilterListbox:
    pad_amt = 4
    longest_filter_item = 47
    games_to_remove = []  # an empty list to eventually hold game_ids for removal

    # Define the class FilterPane, including options for the pane (such as its name, etc.)
    def __init__(self, parent_app, parent_frame, title_string, subcolumn, box_height,
                 config_key, filter_keys, sort_by="values", display_keyval="values"):
        self.parent_app = parent_app  # the app in which you're making the set of filters
        self.parent_frame = parent_frame  # which frame to put the filter inside of
        self.title_string = title_string  # name of the filter boxes
        self.subcolumn = subcolumn
        self.box_height = box_height  # how long to make the list of filters
        self.config_key = config_key  # the filter's source from the config file
        self.filter_keys = filter_keys  # list of key names in parsed_data to check through
        self.sort_by = sort_by  # whether or not to sort the filter list alphabetically
        self.display_keyval = display_keyval  # whether to display the keys or values in the filter list
        self.choices_list = []  # a list of the stored choices for the filter, extracted from listboxes

        # Build the subframe to hold the filter panes
        self.outer_frame = tkinter.Frame(self.parent_frame, bg=self.parent_app.bg_BG)
        self.outer_frame.config(borderwidth=self.parent_app.bd_ssxn, relief=self.parent_app.rel_ssxn,
                                padx=self.pad_amt, pady=self.pad_amt)
        self.outer_frame.grid(column=self.subcolumn, sticky="NSEW")

        # Add the variables to hold the options
        self.filter_options = tkinter.StringVar(value="")  # a string of choices to populate things
        self.filter_choices = tkinter.StringVar(value="")  # a string of choices to populate the selections

        # Label left frame
        self.left_label = tkinter.Label(self.outer_frame, text="Select " + self.title_string + ":")
        self.left_label.config(font="Helvetica 10", bg=self.parent_app.bg_BG, fg=self.parent_app.fg_txt)
        self.left_label.grid(row=0, column=0)

        # Create left frame
        self.left_frame = tkinter.Frame(self.outer_frame, relief=self.parent_app.rel_SB,
                                        bg=self.parent_app.bg_BG, bd=self.parent_app.bd_SB)
        self.left_frame.grid(row=1, column=0, sticky="NSEW")

        # Add left frame contents
        self.lsb = tkinter.Scrollbar(self.left_frame)  # create a scrollbar
        self.lb = tkinter.Listbox(self.left_frame, listvariable=self.filter_options, selectmode=tkinter.EXTENDED)
        self.lb.config(bd=self.parent_app.bd_pad, height=self.box_height, relief=tkinter.FLAT, activestyle="none")
        self.lb.config(font="Helvetica 9", width=self.longest_filter_item, yscrollcommand=self.lsb.set)
        self.lb.grid(row=0, column=0, sticky="NSEW")
        self.lb.bind("<Double-Button-1>", self.update_l2r)
        self.lsb.config(command=self.lb.yview)
        self.lsb.grid(row=0, column=1, sticky="NSEW")

        # Create middle frame
        self.middle_frame = tkinter.Frame(self.outer_frame, padx=self.pad_amt, pady=self.pad_amt,
                                          relief=tkinter.FLAT, bg=self.parent_app.bg_BG)
        self.middle_frame.grid(row=1, column=1, sticky="NSEW")

        # Add arrow button to middle frame
        self.add_button = tkinter.Button(self.middle_frame, text="\u2192", command=self.update_l2r)
        self.add_button.config(font="Helvetica 16 bold", width=5, relief=self.parent_app.rel_btn)
        self.add_button.config(fg=self.parent_app.fg_btn, bd=self.parent_app.bd_btn, bg=self.parent_app.bg_CT,
                               activebackground=self.parent_app.bg_HL)
        self.add_button.grid(row=0, column=0, sticky="sew")  # this was "sew"

        # Add 2nd arrow button to middle frame for moving things in the other direction
        self.remove_button = tkinter.Button(self.middle_frame, text="\u2190", command=self.update_r2l)
        self.remove_button.config(font="Helvetica 16 bold", width=5, relief=self.parent_app.rel_btn)
        self.remove_button.config(fg=self.parent_app.fg_btn, bd=self.parent_app.bd_btn, bg=self.parent_app.bg_CT,
                                  activebackground=self.parent_app.bg_HL)
        self.remove_button.grid(row=1, column=0, sticky="new")

        # Add clear button to middle frame
        self.clear_button = tkinter.Button(self.middle_frame, text="Reset", command=self.reset_box)
        self.clear_button.config(font="Helvetica 11 bold", width=5, relief=self.parent_app.rel_btn)
        self.clear_button.config(fg=self.parent_app.fg_btn, bd=self.parent_app.bd_btn, bg=self.parent_app.bg_CT,
                                 activebackground=self.parent_app.bg_HL)
        self.clear_button.grid(row=2, column=0, sticky="ew")

        # Label the right pane
        self.right_label = tkinter.Label(self.outer_frame, text="Selected " + self.title_string + " (Blank = All):")
        self.right_label.config(font="Helvetica 10", bg=self.parent_app.bg_BG, fg=self.parent_app.fg_txt)
        self.right_label.grid(row=0, column=2)

        # Create right frame
        self.right_frame = tkinter.Frame(self.outer_frame, relief=self.parent_app.rel_SB,
                                         bg=self.parent_app.bg_BG, bd=self.parent_app.bd_SB)
        self.right_frame.grid(row=1, column=2, sticky="NSEW")

        # Add right pane contents
        self.rsb = tkinter.Scrollbar(self.right_frame)  # create a scrollbar
        self.rb = tkinter.Listbox(self.right_frame, listvariable=self.filter_choices, selectmode=tkinter.EXTENDED)
        self.rb.config(bd=self.parent_app.bd_pad, height=self.box_height, relief=tkinter.FLAT, activestyle="none")
        self.rb.config(font="Helvetica 9", width=self.longest_filter_item, yscrollcommand=self.rsb.set)
        self.rb.grid(row=0, column=0, sticky="NSEW")
        self.rb.bind("<Double-Button-1>", self.update_r2l)
        self.rsb.config(command=self.rb.yview)
        self.rsb.grid(row=0, column=1, sticky="NSEW")

    def sort_my_list(self, my_list):
        my_list_sorted = []
        if self.sort_by == "keys":
            keys = list(self.parent_app.config_info[str(self.config_key)].copy().keys())
            vals = list(self.parent_app.config_info[str(self.config_key)].copy().values())
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

    def update_l2r(self, _event=None):
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

    def update_r2l(self, _event=None):
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
            options_list = []
            if self.display_keyval == "values":
                options_list = list(self.parent_app.config_info[str(self.config_key)].copy().values())
            elif self.display_keyval == "keys":
                options_list = list(self.parent_app.config_info[str(self.config_key)].copy().keys())
            options_list = self.sort_my_list(options_list)
            # Populate the left and right panes with their initial values
            self.filter_options.set(options_list)
            self.filter_choices.set([])
            self.lb.config(state=tkinter.NORMAL)
            self.rb.config(state=tkinter.NORMAL)
        except KeyError:
            self.filter_options.set(["Couldn't Initialize " + str(self.config_key) + " Data"])
            self.parent_app.status_string.set("Unable to find " + str(self.config_key) + " Data")
            self.lb.config(state=tkinter.DISABLED)
            self.rb.config(state=tkinter.DISABLED)

        # clear out residual mouse selections on both panes and update the choices list (empty at this point)
        self.lb.selection_clear(0, tkinter.END)
        self.rb.selection_clear(0, tkinter.END)
        self.choices_list = [self.rb.get(ii) for ii in range(self.rb.size())]

        return


class PlotterBox:
    def __init__(self, parent_app, parent_frame):
        self.parent_app = parent_app
        self.parent_frame = parent_frame

        self.sub_frame = tkinter.Frame(parent_frame, borderwidth=self.parent_app.bd_root,
                                       relief=self.parent_app.rel_root, bg=self.parent_app.bg_BG,
                                       padx=self.parent_app.pad_main, pady=self.parent_app.pad_main)
        self.sub_frame.grid(row=1, column=0, sticky="NSEW")

        self.sub_frame_label = tkinter.Label(self.sub_frame, text="Plots", font="Helvetica 12 bold",
                                             bg=self.parent_app.bg_BG, fg=self.parent_app.fg_txt)
        self.sub_frame_label.grid()

        # Identify the longest variable to set the width of the x and y variable boxes
        self.long_var = sorted([len(var) for var in parse.Var.b_vars + parse.Var.f_vars + parse.Var.c_vars +
                                parse.Var.s_vars])[-1]

        self.y_var = tkinter.StringVar(value="Choose Y Variable")
        self.y_vars = tkinter.StringVar(value=sorted(parse.Var.b_vars + parse.Var.f_vars + parse.Var.c_vars))

        self.y_var_label = tkinter.Label(self.sub_frame, text="Select Y Variable:")
        self.y_var_label.config(font="Helvetica 10", bg=self.parent_app.bg_BG, fg=self.parent_app.fg_txt)
        self.y_var_label.grid()

        self.y_frame = tkinter.Frame(self.sub_frame, relief=self.parent_app.rel_SB,
                                     bg=self.parent_app.bg_BG, bd=self.parent_app.bd_SB)
        self.y_frame.grid(sticky="NSEW")

        self.y_sb = tkinter.Scrollbar(self.y_frame)
        self.y_box = tkinter.Listbox(self.y_frame, listvariable=self.y_vars, selectmode=tkinter.SINGLE)
        self.y_box.config(activestyle="none", exportselection=False, width=self.long_var, height=7,
                          yscrollcommand=self.y_sb.set)
        self.y_box.config(font="Helvetica 9", relief=tkinter.FLAT, bd=self.parent_app.bd_pad)
        self.y_box.grid(row=0, column=0, sticky="NSEW")
        self.y_box.bind("<<ListboxSelect>>", lambda event: self.assign(event, string_var=self.y_var))
        self.y_sb.config(command=self.y_box.yview, relief=tkinter.GROOVE)
        self.y_sb.grid(row=0, column=1, sticky="NSEW")

        self.x_var_label = tkinter.Label(self.sub_frame, text="Select X Variable:")
        self.x_var_label.config(font="Helvetica 10", bg=self.parent_app.bg_BG, fg=self.parent_app.fg_txt)
        self.x_var_label.grid()

        self.x_var = tkinter.StringVar(value="Choose X Variable")
        self.x_vars = tkinter.StringVar(value=sorted(parse.Var.b_vars + parse.Var.f_vars + parse.Var.s_vars))

        self.x_frame = tkinter.Frame(self.sub_frame, relief=self.parent_app.rel_SB,
                                     bg=self.parent_app.bg_BG, bd=self.parent_app.bd_SB)
        self.x_frame.grid(sticky="NSEW")

        self.x_sb = tkinter.Scrollbar(self.x_frame)
        self.x_box = tkinter.Listbox(self.x_frame, listvariable=self.x_vars, selectmode=tkinter.SINGLE)
        self.x_box.config(activestyle="none", exportselection=False, width=self.long_var, height=7,
                          yscrollcommand=self.x_sb.set)
        self.x_box.config(font="Helvetica 9", relief=tkinter.FLAT, bd=self.parent_app.bd_pad)
        self.x_box.grid(row=0, column=0, sticky="NSEW")
        self.x_box.bind("<<ListboxSelect>>", lambda event: self.assign(event, string_var=self.x_var))
        self.x_sb.config(command=self.x_box.yview)
        self.x_sb.grid(row=0, column=1, sticky="NSEW")

        self.plotter_opts_frame = tkinter.Frame(self.sub_frame, borderwidth=0, relief=tkinter.FLAT, padx=0, pady=5,
                                                bg=self.parent_app.bg_BG)
        self.plotter_opts_frame.grid(sticky="NSEW")

        self.threshold_label = tkinter.Label(self.plotter_opts_frame, text="Specify minimum instances:", anchor="w")
        self.threshold_label.config(font="Helvetica 10", bg=self.parent_app.bg_BG, fg=self.parent_app.fg_txt)
        self.threshold_label.grid(row=0, column=0, sticky="NSEW")
        self.threshold_var = tkinter.StringVar(value=5)
        self.threshold_entry = tkinter.Entry(self.plotter_opts_frame, textvariable=self.threshold_var, width=3)
        self.threshold_entry.grid(row=0, column=1, sticky="NSEW")

        self.ci_label = tkinter.Label(self.plotter_opts_frame, text="Confidence Interval (Error Bars):", anchor="w")
        self.ci_label.config(font="Helvetica 10", bg=self.parent_app.bg_BG, fg=self.parent_app.fg_txt)
        self.ci_label.grid(row=1, column=0, sticky="NSEW")
        self.ci_var = tkinter.StringVar(value="68%")
        self.ci_menu = tkinter.OptionMenu(self.plotter_opts_frame, self.ci_var, *sorted(list(plot_fns.z_scores.keys())))
        self.ci_menu["anchor"] = "w"
        self.ci_menu["width"] = 4
        self.ci_menu["relief"] = tkinter.FLAT
        self.ci_menu["bd"] = 0
        self.ci_menu["fg"] = self.parent_app.fg_btn
        self.ci_menu["borderwidth"] = 0
        self.ci_menu["padx"] = 3
        self.ci_menu["pady"] = 2
        self.ci_menu["highlightthickness"] = 0
        self.ci_menu["background"] = self.parent_app.bg_CT
        self.ci_menu["activebackground"] = self.parent_app.bg_HL
        self.ci_menu["activeforeground"] = self.parent_app.fg_btn

        self.ci_menu.grid(row=1, column=1, sticky="NSEW")

        self.bins_label = tkinter.Label(self.plotter_opts_frame, text="Number of Bins (For Histograms):", anchor="w")
        self.bins_label.config(font="Helvetica 10", bg=self.parent_app.bg_BG, fg=self.parent_app.fg_txt)
        self.bins_label.grid(row=2, column=0, sticky="NSEW")
        self.bins_var = tkinter.StringVar(value=10)
        self.bins_entry = tkinter.Entry(self.plotter_opts_frame, textvariable=self.bins_var, width=3)
        self.bins_entry.grid(row=2, column=1, sticky="NSEW")

        self.plot_button = tkinter.Button(self.sub_frame,
                                          text="Please See Above To Select\nY Variable\nand\nX Variable",
                                          command=self.plot_generation)
        self.plot_button.config(font="Helvetica 9 bold", width=5, relief=self.parent_app.rel_btn)
        self.plot_button.config(fg=self.parent_app.fg_btn, bd=self.parent_app.bd_btn, bg=self.parent_app.bg_CT,
                                activebackground=self.parent_app.bg_HL)
        self.plot_button.grid(sticky="NSEW")

    def plot_generation(self):
        self.parent_app.config_info["Threshold"] = int(self.threshold_var.get())
        self.parent_app.config_info = api_fns.config_overwrite(self.parent_app.config_info)

        # Check that valid variables have been selected
        if self.y_var.get() in (parse.Var.b_vars + parse.Var.f_vars + parse.Var.c_vars
                                ) and self.x_var.get() in (parse.Var.b_vars + parse.Var.f_vars + parse.Var.s_vars):
            self.parent_app.status_string.set(value="Parsing data...")
            y_list, x_list, n_kept = parse.Var.create_list(
                self.parent_app.config_info, self.parent_app.match_data,
                parse.Vars, self.y_var.get(), self.x_var.get(), self.parent_app.scrollable_filters,
                self.parent_app.recency_filter.get()
            )

            print("Lists to plot:\n", "Y: ", y_list, "\n", "X: ", x_list)

            if len(y_list) == len(x_list) and n_kept > self.parent_app.config_info["Threshold"] and len(y_list) > 2:
                self.parent_app.status_string.set(value="Preparing " + str(n_kept) + " matches for plotting")

                # If the x variable isn't countable (e.g. if it's "Champion" or "Win/Loss"), use a bar chart
                if (self.x_var.get() in parse.Var.s_vars + parse.Var.b_vars) and (
                            self.y_var.get() in parse.Var.b_vars + parse.Var.f_vars):
                    plot_fns.simple_bar_plotter(x_list, y_list, threshold=self.parent_app.config_info["Threshold"],
                                                x_label=self.x_var.get(), y_label=self.y_var.get(),
                                                z_scores=plot_fns.z_scores, conf_interval=self.ci_var.get())
                    matplotlib.pyplot.show()
                    self.parent_app.status_string.set(value="Plotted data from " + str(n_kept) + " games")

                # If the x variable isn't countable and the y variable is cumulative, use "cumulative" bar chart
                elif self.x_var.get() in parse.Var.s_vars + parse.Var.b_vars and self.y_var.get() in parse.Var.c_vars:
                    plot_fns.simple_bar_plotter(x_list, y_list, self.bins_var.get(),
                                                x_label=self.x_var.get(), y_label=self.y_var.get(),
                                                dict_type="Cumulative")

                    self.parent_app.status_string.set(value="Plotted data from " + str(n_kept) + " games")
                    matplotlib.pyplot.show()

                # If the x variable and y variable are numeric (e.g. "Damage" vs. "CS"), use a scatter plot
                elif self.x_var.get() in parse.Var.f_vars and self.y_var.get() in parse.Var.f_vars:
                    plot_fns.make_scatterplot(x_list, y_list, self.y_var.get(),
                                              x_label=self.x_var.get(), y_label=self.y_var.get())

                    self.parent_app.status_string.set(value="Plotted data from " + str(n_kept) + " games")
                    matplotlib.pyplot.show()

                # If the x is a float and y is discrete, use two stacked histograms
                elif self.x_var.get() in parse.Var.f_vars and self.y_var.get() in parse.Var.b_vars:
                    plot_fns.make_hist(x_list, y_list, self.bins_var.get(),
                                       x_label=self.x_var.get(), y_label=self.y_var.get())
                    self.parent_app.status_string.set(value="Plotted data from " + str(n_kept) + " games")
                    matplotlib.pyplot.show()

                else:
                    self.parent_app.status_string.set(
                        value="Can't make a useful plot. Try swapping the variables if possible.")

            else:
                self.parent_app.status_string.set(
                    value="Not enough matches (" + str(len(y_list)) + " remain after filtering)")
        else:
            self.parent_app.status_string.set(value="Check that X and Y variables are valid")

    def assign(self, event, string_var=None):
        curr_box = event.widget

        for selection in curr_box.curselection():
            # Only use the last selection; handles
            value = curr_box.get(int(selection))
            curr_box.selection_set(int(selection))
            if string_var is not None:
                string_var.set(value)

        self.plot_button.config(text="Make Plot:\n" + self.y_var.get() + "\nvs.\n" + self.x_var.get())
