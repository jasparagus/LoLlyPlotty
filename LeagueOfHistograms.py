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


def lc():
    global config_info
    apikey = e_apikey.get()
    region = reg.get()
    summname = e_summname.get()
    config_info = ConfigureLoH.config(apikey, region, summname)


def gm():
    global config_info, match_data_all
    match_data_all = GetRankedMatchData.update_matchdata(config_info)
    return match_data_all


def plt():
    global match_data_all

    LoHPlots.parse_match_data(match_data_all)

    if wr.get() == 1:
        print("WR trend selected.")
        LoHPlots.wr_vs_time(match_data_all)
    else:
        print("WR Trend not selected.")


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
    print("Match data loaded at startup")
except:
    match_data_all = {}
    print("Match data not found; please get match data.")

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


b_lc = tkinter.Button(root, text="Update LoH Settings", width=25, command=lc)
b_lc.grid(row=6, column=0, columnspan=2)


b_gm = tkinter.Button(root, text="Update Match Data", width=20, command=gm)
b_gm.grid(row=7, column=0, columnspan=2)

# PLOTTING OPTIONS FRAME (SHOULD MAKE THIS A FRAME... ONCE I FIGURE OUT WHAT THAT IS)
l_plots = tkinter.Label(root, text="Select Plots To Generate")
l_plots.grid(row=0, column=3)

# SELECT TIMEFRAME TO PLOT, POPULATED BASED ON KNOWN MATCH RANGE, ETC, USING RADIO BUTTON

wr = tkinter.IntVar(value=0)
c_wr = tkinter.Checkbutton(root, text="Winrate vs. Time", variable=wr)
c_wr.grid(row=1, column=3)


b_plt = tkinter.Button(root, text="Generate Selected Plots", width=20, command=plt)
b_plt.grid(row=7, column=3, columnspan=2)


# Should pack this inside a function & update it every once in a while
l_status = tkinter.Label(root, text="Status: " + status_message)
l_status.grid(row=10, column=3)


e_apikey.focus_set() # set the focus on the first entry box
root.mainloop() # start the application loop
print("Done")


