import numpy  # This is u
import math  # This is for various math functions (ceiling, etc.)
import matplotlib  # This is for editing the plot renderer
matplotlib.use("TkAgg")  # This goes before pyplot import so that rendering works on MacOS
import matplotlib.pyplot as plt  # This is for making plots


# TODO - Add error bars (e.g. 90% confidence interval) to all plots where that's feasible.

# FOR DEBUGGING STUFF OUT IN CONSOLE
# import json
# import numpy
# import matplotlib.pyplot as plt
# config_file = open("Configuration.json", "r")
# config_info = json.loads(config_file.read())
# filtered_parsed_match_data = open(config_info["Settings"]["SummonerName"] + "_ParsedMatchData.LoHData", "r")
# filtered_parsed_match_data = json.loads(filtered_parsed_match_data.read())


def make_wr_dictionary(key_ls, win_ls, store_dict):
    """
    Find winrate, wins, losses for a given variable (key_ls) from list of total
    wins/losses (win_ls)
    stored as: {"variable": [matches, wins, winrate]}
    NOTE: DICTIONARY MUST EXIST BEFORE YOU CALL THIS FUNCTION
    """
    ls_length = len(key_ls)
    for i in range(ls_length):
        if key_ls[i] not in store_dict:
            # Check if key already exists store_dict
            store_dict[key_ls[i]] = [0, 0, 0]
        # update matches
        store_dict[key_ls[i]][0] += 1
        # update wins (note: these are bools)
        store_dict[key_ls[i]][1] += win_ls[i]
    # Update win rate
    for k in store_dict:
        store_dict[k][2] = store_dict[k][1] / store_dict[k][0]


def make_wr_barchart(bars_data, n_per_bar, x_labels, title_string, avg_win_rate):
    """
    Make a bar chart from data. Inputs: list of data to be plotted in bar form (a list of numbers
    """
    n_of_things_to_plot = len(bars_data)

    fig, ax = plt.subplots()
    fig.subplots_adjust(top=0.8, bottom=0.2)

    # prepare basics
    locs = range(n_of_things_to_plot)
    width = 0.75  # the width of the bars
    startx = -width - 0.25  # where the x axis starts
    endx = n_of_things_to_plot - 1 + width + 0.25  # where the x axis ends

    # create objects to plot
    bars1 = ax.bar(locs, bars_data, width, color='r')
    wr_avg, = plt.plot([startx, endx], [avg_win_rate, avg_win_rate], label="Avg. WR", linestyle="--", color="b")
    wr_50, = plt.plot([startx, endx], [0.5, 0.5], label="50% WR", linestyle=":", color="k")

    # add some text for labels, title and axes ticks
    ax.set_ylabel('Winrate')
    ax.set_title(title_string)
    ax.set_xticks(locs)
    ax.set_xticklabels(x_labels, rotation=45, ha="right")
    plt.xlim([startx, endx])
    plt.ylim([0, 1.2])

    l2 = plt.legend(handles=(wr_avg, wr_50), loc=(0, 1.1), ncol=1)
    plt.gca().add_artist(l2)

    def label_bars(bars):
        """ Attach a text label above each bar displaying its height """
        rr = 0
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                    'n = %d' % n_per_bar[rr],
                    ha='center', va='top')
            rr += 1

    label_bars(bars1)


def make_hist(wins_var, losses_var, n_bins, title, xlabel, ylabel):
    fig, ax = plt.subplots()
    fig.subplots_adjust(top=0.8, bottom=0.1)
    (_, _, p1) = plt.hist(wins_var, n_bins,
                          label="Wins", histtype="bar", normed=0, color='green', alpha=0.5)
    (_, _, p2) = plt.hist(losses_var, n_bins,
                          label="Losses", histtype="bar", normed=0, color='red', alpha=0.5)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    ax.legend(handles=(p1[0], p2[0]), loc=(0, 1.1), ncol=1)
    return


def wr_time(filtered_parsed_match_data, box, enabled_filters_text):
    """
    Plots winrate trend over time using a moving average with average with width "box"
    """
    fig, ax = plt.subplots()
    fig.subplots_adjust(top=0.7, bottom=0.1)

    n_matches = len(filtered_parsed_match_data["win_lose"])
    wr = filtered_parsed_match_data["avg_wr"]
    p1, = plt.plot(
            moving_avg(filtered_parsed_match_data["win_lose"], box), label="Moving Avg.", linestyle="-", color="r")
    p2, = plt.plot([0, n_matches], [wr, wr], label="Avg. WR", linestyle="--", color="b")
    p3, = plt.plot([0, n_matches], [0.5, 0.5], label="50% WR", linestyle=":", color="k")

    ax.legend(handles=(p1, p2, p3), loc=(0, 1.1), ncol=1)

    ax.set_xlabel("Match Number (Chronological)")
    ax.set_ylabel("Win Rate")
    ax.set_title("Winrate Over Time \n" + enabled_filters_text)
    plt.xlim([0, n_matches])
    plt.ylim([0, 1])


def wr_champ(filtered_parsed_match_data, n_played, enabled_filters_text):
    """
    Winrates for each champion played more than n_games
    """
    n_champs = len(filtered_parsed_match_data["champs_played"])
    n_games = len(filtered_parsed_match_data["win_lose"])
    wr_by_champ = []
    n_by_champ = []
    champs_to_keep = []

    for cc in range(n_champs):
        wins = []
        for gg in range(n_games):
            if filtered_parsed_match_data["champs_played"][cc] == filtered_parsed_match_data["champ"][gg]:
                wins.append(filtered_parsed_match_data["win_lose"][gg])
        if len(wins) >= n_played:
            wr_by_champ.append(sum(wins)/len(wins))
            n_by_champ.append(len(wins))
            champs_to_keep.append(filtered_parsed_match_data["champs_played"][cc])

    bars_data = wr_by_champ
    n_per_bar = n_by_champ
    x_labels = champs_to_keep
    title_string = "Winrate By Champion \n" + "(Played " + str(n_played) + "+ Games)\n" + enabled_filters_text
    avg_win_rate = filtered_parsed_match_data["avg_wr"]

    make_wr_barchart(bars_data, n_per_bar, x_labels, title_string, avg_win_rate)


def wr_teammate(filtered_parsed_match_data, n_played, enabled_filters_text):
    """ Winrates on a per-teammate basis for teammates from a number of games >= n_games """
    n_games = len(filtered_parsed_match_data["win_lose"])
    all_teammates = []

    # Get a list of every teammate
    for tt in range(n_games):
        all_teammates = all_teammates + filtered_parsed_match_data["teammates"][str(tt)]

    teammates_unique = sorted(list(set(all_teammates)))
    n_teammates = len(teammates_unique)
    wr_by_teammate = []
    games_with_teammate = []
    teammates_unique_keep = []

    # For each unique teammate, look at every game and see if they were there and (if so) if it was a W/L
    for tt in range(n_teammates):
        wins = []
        for gg in range(n_games):
            if teammates_unique[tt] in filtered_parsed_match_data["teammates"][str(gg)]:
                wins.append(filtered_parsed_match_data["win_lose"][gg])
        if len(wins) >= n_played:
            wr_by_teammate.append(sum(wins)/len(wins))
            games_with_teammate.append(len(wins))
            teammates_unique_keep.append(teammates_unique[tt])

    bars_data = wr_by_teammate
    n_per_bar = games_with_teammate
    x_labels = teammates_unique_keep
    title_string = "Winrate by Teammate\n" + "(" + str(n_played) + "+ Games Together)\n" + enabled_filters_text
    avg_win_rate = filtered_parsed_match_data["avg_wr"]

    make_wr_barchart(bars_data, n_per_bar, x_labels, title_string, avg_win_rate)


def wr_partysize(filtered_parsed_match_data, n_played_with,enabled_filters_text):
    """
    Winrates by number of recurring teammates (with an N game cutoff for "teammates")
    n_played_with is threshold # of games with teammate to be considered part of a a "premade"
    """
    n_games = len(filtered_parsed_match_data["win_lose"])
    all_teammates = []

    # Get a list of every teammate
    for game in range(n_games):
        all_teammates += filtered_parsed_match_data["teammates"][str(game)]
    # Get rid of duplicates
    teammates_unique = sorted(list(set(all_teammates)))

    # Filter out the teammates with whom you played too few games
    teammates = []
    for teammate in teammates_unique:
        if all_teammates.count(teammate) >= n_played_with:
            teammates.append(teammate)

    # Go through each game and count number of teammates, storing the result in a dictionary
    party_size = []
    for game in range(n_games):
        party_size.append(
            len(set(teammates) & set(filtered_parsed_match_data["teammates"][str(game)]))
        )

    wr_partysize_dict = {}
    make_wr_dictionary(party_size, filtered_parsed_match_data["win_lose"], wr_partysize_dict)

    bars_data = []
    n_per_bar = []
    x_labels = []
    for p_size in sorted(list(wr_partysize_dict.keys())):
        bars_data.append(wr_partysize_dict[p_size][1] / wr_partysize_dict[p_size][0])
        n_per_bar.append(wr_partysize_dict[p_size][0])
        x_labels.append(str(p_size) + " Friend(s)")

    title_string = "Winrate by Number of Friends\n(" + str(n_played_with) + "+ Games Together)\n" + enabled_filters_text
    avg_win_rate = filtered_parsed_match_data["avg_wr"]

    make_wr_barchart(bars_data, n_per_bar, x_labels, title_string, avg_win_rate)


def wr_role(filtered_parsed_match_data, n_games_role, enabled_filters_text):
    """ Winrate as a function of role """
    # list of roles
    role_ls = filtered_parsed_match_data["role"]

    # list of wins/losses
    # TODO - win_ls SHOULD BE DEFINED ELSEWHERE. ALL winrate functions use this...
    win_ls = filtered_parsed_match_data["win_lose"]

    # dictionary {"role" [matches, wins, winrate]}
    wr_role_dict = {}
    # Fill in the dictionary
    make_wr_dictionary(role_ls, win_ls, wr_role_dict)
    bars_data = []
    n_per_bar = []
    x_labels = []
    title_string = "Winrate By Role\n" + enabled_filters_text
    avg_win_rate = filtered_parsed_match_data["avg_wr"]

    for role in wr_role_dict.keys():
        # winrate for each role to bars_data
        bars_data.append(wr_role_dict[role][1]/wr_role_dict[role][0])
        # total matches for each role to n_per_bar
        n_per_bar.append(wr_role_dict[role][0])
        x_labels.append(role)

    make_wr_barchart(bars_data, n_per_bar, x_labels, title_string, avg_win_rate)


def wr_dmg(filtered_parsed_match_data, n_bins, enabled_filters_text):
    # Histograms of damage in won and lost games
    n_matches = len(filtered_parsed_match_data["win_lose"])

    damage_total_win = []
    damage_total_lose = []

    damage_to_champs_win = []
    damage_to_champs_lose = []

    damage_taken_win = []
    damage_taken_lose = []

    for mm in range(n_matches):
        if filtered_parsed_match_data["win_lose"][mm] == 1:
            damage_total_win.append(filtered_parsed_match_data["damage_total"][mm])
            damage_to_champs_win.append(filtered_parsed_match_data["damage_to_champs"][mm])
            damage_taken_win.append(filtered_parsed_match_data["damage_taken"][mm])
        else:
            damage_total_lose.append(filtered_parsed_match_data["damage_total"][mm])
            damage_to_champs_lose.append(filtered_parsed_match_data["damage_to_champs"][mm])
            damage_taken_lose.append(filtered_parsed_match_data["damage_taken"][mm])

    title = "Damage Dealt by\n" + filtered_parsed_match_data["summoner_name"] + "\n" + enabled_filters_text
    make_hist(damage_total_win, damage_total_lose, n_bins, title, "Damage Dealt", "Number of Games")

    title = "Damage To Champs by\n" + filtered_parsed_match_data["summoner_name"] + "\n" + enabled_filters_text
    make_hist(damage_to_champs_win, damage_to_champs_lose, n_bins, title, "Damage To Champs", "Number of Games")

    title = "Damage Taken by\n" + filtered_parsed_match_data["summoner_name"] + "\n" + enabled_filters_text
    make_hist(damage_taken_win, damage_taken_lose, n_bins, title, "Damage Taken", "Number of Games")


def wr_dmg_frac(filtered_parsed_match_data, n_bins, enabled_filters_text):
    # Histograms of damage fractions in won and lost games
    n_matches = len(filtered_parsed_match_data["win_lose"])

    damage_total_frac_win = []
    damage_total_frac_lose = []

    damage_to_champs_frac_win = []
    damage_to_champs_frac_lose = []

    damage_taken_frac_win = []
    damage_taken_frac_lose = []

    for mm in range(n_matches):
        if filtered_parsed_match_data["win_lose"][mm] == 1:
            damage_total_frac_win.append(filtered_parsed_match_data["damage_total_frac"][mm])
            damage_to_champs_frac_win.append(filtered_parsed_match_data["damage_to_champs_frac"][mm])
            damage_taken_frac_win.append(filtered_parsed_match_data["damage_taken_frac"][mm])
        else:
            damage_total_frac_lose.append(filtered_parsed_match_data["damage_total_frac"][mm])
            damage_to_champs_frac_lose.append(filtered_parsed_match_data["damage_to_champs_frac"][mm])
            damage_taken_frac_lose.append(filtered_parsed_match_data["damage_taken_frac"][mm])

    title = "% of Team Damage Dealt by\n" + filtered_parsed_match_data["summoner_name"] \
            + "\n" + enabled_filters_text
    make_hist(damage_total_frac_win, damage_total_frac_lose, n_bins,
              title, "Damage Share", "Number of Games")

    title = "% of Team Damage To Champs by\n" + filtered_parsed_match_data["summoner_name"] \
            + "\n" + enabled_filters_text
    make_hist(damage_to_champs_frac_win, damage_to_champs_frac_lose, n_bins,
              title, "Damage To Champs", "Number of Games")

    title = "% of Team Damage Taken by\n" + filtered_parsed_match_data["summoner_name"] \
            + "\n" + enabled_filters_text
    make_hist(damage_taken_frac_win, damage_taken_frac_lose, n_bins,
              title, "Damage Taken", "Number of Games")


def wr_mapside(filtered_parsed_match_data, enabled_filters_text):
    """ Winrate as a function of map side """
    # list of map sides
    side_ls = filtered_parsed_match_data["map_side"]

    # list of wins/losses
    win_ls = filtered_parsed_match_data["win_lose"]

    # dictionary {"role" [matches, wins, winrate]}
    wr_side_dict = {}
    # Fill in the dictionary
    make_wr_dictionary(side_ls, win_ls, wr_side_dict)
    bars_data = []
    n_per_bar = []
    x_labels = []
    title_string = "Winrate By Map Side\n" + enabled_filters_text
    avg_win_rate = filtered_parsed_match_data["avg_wr"]

    for side in wr_side_dict.keys():
        # winrate for each side to bars_data
        bars_data.append(wr_side_dict[side][1]/wr_side_dict[side][0])
        # total matches for each side to n_per_bar
        n_per_bar.append(wr_side_dict[side][0])
        if side == 100:
            x_labels.append("Blue")
        elif side == 200:
            x_labels.append("Red")
        else:
            x_labels.append("Unknown")

    make_wr_barchart(bars_data, n_per_bar, x_labels, title_string, avg_win_rate)


def moving_avg(ls, box):
    """
    Creates a list with the same shape as ls composed of moving average of ls at each point.
    If box is odd, the moving average is centered at the data point in question
    If box is even, the moving average is centered after the data point in question
    :param ls: list for which to compute moving average
    :param box: box size for box average. Coerced to be at most the length of ls.
    :return:
    """

    if box > len(ls):
        box = len(ls)

    length = len(ls)

    b_fwd = math.ceil((box-1)/2)  # points to grab after -3 in test
    b_rev = math.floor((box-1)/2)  # points to grab before -2 in test

    # prepare a list to hold the moving average
    mov_avg = [0 for ii in ls]
    # populate the points before the box size (not enough points to left of box)
    for ii in range(0, b_rev):
        mov_avg[ii] = sum(ls[0:ii+b_fwd+1]) / len(ls[0:ii+b_fwd+1])
    # populate the points in the region where the box fits around the current point
    for ii in range(b_rev, length-b_fwd):
        mov_avg[ii] = sum(ls[ii-b_rev:ii+b_fwd+1]) / box
    # populate the points in the region approaching the end (not enough points to right of box)
    for ii in range(length-b_fwd, length):
        mov_avg[ii] = sum(ls[(ii-b_rev):]) / len(ls[(ii-b_rev):])

    return mov_avg
