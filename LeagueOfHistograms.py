"""
LEAGUE OF HISTOGRAMS, v0.1
--------------------
Obtains ranked summoner information and visualizes it.
Features (planned or completed):
Per-champion winrates
Per-teammate winrates
Per-number-teammate winrates (for most-played-with teammates)
Rolling average winrate
Per-role winrates

Changelog:
version 0.1
2017-02-24 - Added GUI made with tkinter. To-do: stop using print and switch to info in a tkinter display
2017-02-22 - Breaking out subroutines into separate files & making UI
2017-02-18, porting code from original MATLAB(TM) version. Jasper D. Cook.

"""

# IMPORT STANDARD MODULES
import json
import tkinter

# IMPORT CUSTOM MODULES
from APIFunctions import ConfigureLoH
from APIFunctions import GetRankedMatchData
from PlotFunctions import LoHPlots


def update_config():
    global config_info
    apikey = e_apikey.get()
    region = reg.get()
    summname = e_summname.get()
    config_info = ConfigureLoH.config(apikey, region, summname)


def get_matches():
    global config_info, match_data_all, parsed_data
    # First, update the match data.
    match_data_all = GetRankedMatchData.update_matchdata(config_info)

    # Second, parse all of the data and return needed variables (as applicable).
    parsed_data = LoHPlots.parse_match_data(config_info, match_data_all)
    with open(config_info["Settings"]["SummonerName"] + "_ParsedMatchData.LoHData", "w") as parsed_data_file:
        json.dump(parsed_data, parsed_data_file)
    global ssn
    ssn = tkinter.StringVar(value=parsed_data["season_unique"][0])
    print("Data pulled from web, parsed, and saved.")
    return match_data_all


def do_plots():
    """ Apply filters. """
    print("Applying filters. [NOT IMPLEMENTED]")
    """ Run the selected analyses. This is probably better suited to a module with external functions. """
    print("Generating plots. [NOT IMPLEMENTED]")
    if wr.get() == 1:
        print("Winrate vs. time checked.")
        LoHPlots.wr_vs_time(match_data_all)
    else:
        print("Winrate vs. time not checked.")
    print("Done generating selected plots. Just kidding, this isn't implemented yet.")


# TRY TO LOAD PREEXISTING CONFIGRAUTION FILE AND MATCH DATA
global config_info
try:
    config_file = open("Configuration.LoHConfig", "r")
    config_info = json.loads(config_file.read())
    apikey = config_info["Settings"]["APIKey"] # check that all pieces of config_info exist - use an actual if later
    region = config_info["Settings"]["Region"]
    summname = config_info["Settings"]["SummonerName"]
    sid = config_info["Settings"]["SID"]
    print("Configuration options found and loaded at startup")
except:
    apikey=""
    region="na"
    summname=""
    config_info = {}
    print("Configuration options not found. Please configure.")

global match_data
try:
    match_data_all = open(config_info["Settings"]["SummonerName"] + "_MatchData.json", "r")
    match_data_all = json.loads(match_data_all.read())
    print("Match data loaded at startup (may be outdated).")
except:
    match_data_all = {}
    print("Match data not found; please get match data.")

global parsed_data
try:
    parsed_data = open(config_info["Settings"]["SummonerName"] + "_ParsedMatchData.LoHData", "r")
    parsed_data = json.loads(parsed_data.read())
    print("Parsed data found at startup (may be outdated).")
except:
    parsed_data = {}
    print("Parsed data not found at startup; please load and parse data.")

status_message = "Starting"

# PREPARE A BOX TO HOLD OPTIONS & POPULATE IT WITH DEFAULTS FROM CONFIG FILE. GRID SIZE IS 15x5
root = tkinter.Tk()  # prepare a widget to hold the UI
root.title("League of Histograms")
# root.config()
# wwid = root.winfo_screenwidth()/4
# whei = root.winfo_screenheight()/2
# w = tkinter.Canvas(root, width=wwid, height=whei)
# w.pack()
# w.create_window(0, wwid/3, 0, whei/3)

# CONFIGURATION OPTIONS FRAME (SHOULD MAKE THIS A FRAME... ONCE I FIGURE OUT WHAT THAT IS)
l_apikey = tkinter.Label(root, text="Enter API Key")
l_apikey.grid(row=0, column=0)
e_apikey = tkinter.Entry(root, width=45, justify="center")
if config_info !={}:
    e_apikey.insert(0, apikey)
e_apikey.grid(row=1, column=0)

l_region = tkinter.Label(root, text="Select Region")
l_region.grid(row=2, column=0)
if config_info !={}:
    reg = tkinter.StringVar(value=region)
else:
    reg = tkinter.StringVar(value="na")
o_region = tkinter.OptionMenu(root, reg,
                              "br", "eune", "euw", "jp", "kr", "lan", "las",
                              "na", "oce", "tr", "ru", "pbe", "global"
                              )
o_region.grid(row=3, column=0)


l_summname = tkinter.Label(root, text="Enter Summoner Name")
l_summname.grid(row=4, column=0)
e_summname = tkinter.Entry(root, width=45, justify="center")
if config_info !={}:
    e_summname.insert(0, summname)
e_summname.grid(row=5, column=0)

l_region = tkinter.Label(root, text="")
l_region.grid(row=6, column=0)

b_lc = tkinter.Button(root, text="Update LoH Settings", width=25, command=update_config)
b_lc.grid(row=7, column=0)

b_gm = tkinter.Button(root, text="Update Match Data", width=20, command=get_matches)
b_gm.grid(row=8, column=0)

# FILTER OPTIONS FRAME
l_analysis_range = tkinter.Label(root, text="Select Filter For Matches [NOT IMPLEMENTED]")
l_analysis_range.grid(row=0, column=3, columnspan=2)

def callback():
    print("Radio-d")

r_filter = tkinter.IntVar(value=1)
rb1 = tkinter.Radiobutton(root, text="Analyze All Matches [Apply No Filters]", variable=r_filter, value=1, anchor="w"
                          ).grid(row=1, column=3, sticky="w")

rb2 = tkinter.Radiobutton(root, text="Filter By Season:", variable=r_filter, value=2).grid(row=2, column=3, sticky="w")
global ssn
if parsed_data !={}:
    ssn = tkinter.StringVar(value=parsed_data["season_unique"][0])
    o_ssn = tkinter.OptionMenu(root, ssn, *parsed_data["season_unique"]).grid(row=2, column=4, sticky="w")
else:
    ssn = tkinter.StringVar(value="Unknown")

rb3 = tkinter.Radiobutton(root, text="Filter By Most Recent [Enter Number of Matches]:", variable=r_filter, value=3
                          ).grid(row=3, column=3, sticky="w")
n_mat = tkinter.IntVar(value=20)
e_rb3 = tkinter.Entry(root, width=8, justify="center").grid(row=3, column=4, sticky="w")

l_filter = tkinter.Label(root, text="Selected: All Matches [not implemented]").grid(row=4, column=3, columnspan=2)


# PLOTTING OPTIONS FRAME (SHOULD MAKE THIS A FRAME... ONCE I FIGURE OUT WHAT THAT IS)
l_plots = tkinter.Label(root, text="Select Plots To Generate")
l_plots.grid(row=8, column=3)

wr = tkinter.IntVar(value=0)
c_wr = tkinter.Checkbutton(root, text="Winrate vs. Time", variable=wr)
c_wr.grid(row=9, column=3, sticky="w")

b_plt = tkinter.Button(root, text="Generate Selected Plots", width=30, command=do_plots)
b_plt.grid(row=10, column=3, columnspan=2)


# Should pack this inside a function & update it every once in a while
l_status = tkinter.Label(root, text="Status: " + status_message)
l_status.grid(row=999, column=0)

l_spacer = tkinter.Label(root, text="     ").grid(row=999, column=1)


e_apikey.focus_set() # set the focus on the first entry box
root.mainloop() # start the application loop
print("Done")
