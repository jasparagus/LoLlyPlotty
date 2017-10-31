import math  # This is for various math functions (ceiling, sqrt, etc.)
import matplotlib  # This is for editing the plot renderer
matplotlib.use("TkAgg")  # This goes before pyplot import so that rendering works on MacOS
import matplotlib.pyplot as plt  # This is for making plots


def make_wr_dictionary(key_ls, win_ls, store_dict):
    """
    Find winrate, wins, losses for a given variable (key_ls) from list of total
    wins/losses (win_ls)
    stored as: {"variable": [matches, wins, winrate, 95% confidence interval]}
    NOTE: DICTIONARY MUST EXIST BEFORE YOU CALL THIS FUNCTION
    """
    ls_length = len(key_ls)
    for i in range(ls_length):
        if key_ls[i] not in store_dict:
            # Check if key already exists store_dict
            store_dict[key_ls[i]] = [0, 0, 0, 0]
        # update matches
        store_dict[key_ls[i]][0] += 1
        # update wins (note: these are bools)
        store_dict[key_ls[i]][1] += win_ls[i]
    # 1st, update win rate
    # 2nd, calculate the uncertainty (95% confidence interval) via err = 1.96 * sqrt( 1/n * mean * (1 - mean) )
    for k in store_dict:
        store_dict[k][2] = store_dict[k][1] / store_dict[k][0]
        store_dict[k][3] = 1.96 * math.sqrt(1 / store_dict[k][0] * store_dict[k][2] * (1 - store_dict[k][2]))


def make_plottable_dictionary(x_list, y_list, threshold, z_scores, conf_inverval="90%"):
    """
    Makes a dictionary that is ready to be fed to make_barchart for plotting
    :param x_list: a list of the variable to cross-reference with y_list
    :param y_list: a list of, e.g. wins and losses whose indices match those of key_ls
    :param threshold: a cutoff for number of matches to exclude (e.g. exclude data with n<3 matches)
    :param conf_interval: confidence interval (e.g. 0.9) in which conf_interval fraction of measurements will reside
    :return: plot_dict: a dictionary of:
            var_list: list of unique variable strings (e.g. champion names or roles)
            n_by_var: instances of each unique variable (e.g. number of matches played on each champion in var_list)
            y_cumul_by_var: cumulative y for each variable in var_list
            avg_by_var: mean y value for each element in var_list (e.g. winrate for each champion)
            error_by_var: uncertainty by variable (e.g. 90% confidence interval for winrates of each champ in var_list)
    """

    plot_dict = {
        "overall_avg": 0,
        "var_list": [],
        "n_by_var": [],
        "y_cumul_by_var": [],
        "y_list_by_var": {},
        "avg_by_var": [],
        "error_by_var": [],
    }

    x_list_clean = []
    y_list_clean = []

    for ii in range(len(y_list)):
        try:
            float(y_list[ii])
            if x_list[ii] != "Unknown":
                x_list_clean.append(x_list[ii])
                y_list_clean.append(float(y_list[ii]))
        except ValueError:
            pass

    # Sort by x_list using a Schwartzian transform (thanks, Ignacio Vazquez-Abrams from stackoverflow)
    x_list_clean, y_list_clean = zip(*sorted(zip(x_list_clean, y_list_clean)))

    plot_dict["overall_avg"] = sum(y_list_clean) / float(len(y_list_clean))

    ls_length = len(x_list_clean)
    for ii in range(ls_length):
        # Check to see if the given x variable has been seen yet
        if x_list_clean[ii] not in plot_dict["var_list"]:
            # If it is a new x variable: record it, its value, and one instance (for division later)
            plot_dict["var_list"].append(x_list_clean[ii])
            plot_dict["y_list_by_var"][x_list_clean[ii]] = [float(y_list_clean[ii])]
            plot_dict["n_by_var"].append(1)
            plot_dict["y_cumul_by_var"].append(float(y_list_clean[ii]))
        else:
            # If it is an existing x variable: find its index, increment the occurrences, and add to the running total
            idx = plot_dict["var_list"].index(x_list_clean[ii])
            plot_dict["y_list_by_var"][x_list_clean[ii]].append(float(y_list_clean[ii]))
            plot_dict["n_by_var"][idx] += 1
            plot_dict["y_cumul_by_var"][idx] += float(y_list_clean[ii])


    # Calculate winrate (wins/n), then the 95% confidence (err = 1.96 * sqrt[ 1/n * mean * (1 - mean)])
    var_length = len(plot_dict["var_list"])
    n_deleted = 0
    for ii in range(var_length):
        if plot_dict["n_by_var"][ii - n_deleted] >= threshold:
            curr_var = plot_dict["var_list"][ii - n_deleted]
            curr_list = plot_dict["y_list_by_var"][curr_var]
            curr_ave, curr_error = compute_error(curr_list, z_scores, conf_inverval)
            plot_dict["avg_by_var"].append(curr_ave)
            plot_dict["error_by_var"].append(curr_error)
        else:
            del plot_dict["var_list"][ii - n_deleted]
            del plot_dict["n_by_var"][ii - n_deleted]
            del plot_dict["y_cumul_by_var"][ii - n_deleted]
            n_deleted += 1

    plot_dict["min_y"] = sorted(plot_dict["avg_by_var"])[0]
    if plot_dict["min_y"] > 0:
        plot_dict["min_y"] = 0

    plot_dict["max_y"] = sorted(plot_dict["avg_by_var"])[-1]
    if plot_dict["max_y"] < 0:
        plot_dict["max_y"] = 0

    return plot_dict


def make_barchart(bars_data, n_per_bar, error_bars, x_labels, avg_y, min_y, max_y, title_string="", y_label="",
                     x_label=""):
    """
    Make a bar chart from data. Inputs: list of data to be plotted in bar form (a list of numbers
    """
    n_of_things_to_plot = len(bars_data)

    fig, ax = plt.subplots()
    fig.subplots_adjust(top=0.8, bottom=0.25)

    # prepare basics
    locs = range(n_of_things_to_plot)
    width = 0.75  # the width of the bars
    startx = -width - 0.25  # where the x axis starts
    endx = n_of_things_to_plot - 1 + width + 0.25  # where the x axis ends

    # create objects to plot
    if error_bars == 0:
        bars1 = ax.bar(locs, bars_data, width, color='r')
    else:
        bars1 = ax.bar(locs, bars_data, width, color='r', yerr=error_bars)
    pl_avg, = plt.plot([startx, endx], [avg_y, avg_y], label="Average for "+y_label, linestyle="--", color="b")
    pl_half, = plt.plot([startx, endx], [max_y*0.5, max_y*0.5], label="Half-Maximum", linestyle=":", color="k")
    pl_zero, = plt.plot([startx, endx], [0, 0], label="Zero", linestyle="-", color="k")

    # add some text for labels, title and axes ticks
    if y_label != "":
        ax.set_ylabel(y_label)
    if x_label != "":
        ax.set_xlabel(x_label)
    if title_string != "":
        ax.set_title(title_string)

    ax.set_xticks(locs)
    ax.set_xticklabels(x_labels, rotation=35, ha="right")
    plt.xlim([startx, endx])
    plt.ylim([min_y*1.1, max_y*1.15])

    leg = plt.legend(handles=(pl_avg, pl_half), loc=(0, 1.1), ncol=1)
    plt.gca().add_artist(leg)

    def label_bars(bars):
        """ Attach a text label above each bar displaying its height """
        rr = 0
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height*1.1,
                    'n=%d' % n_per_bar[rr],
                    ha='center', va='top')
            rr += 1

    label_bars(bars1)


def make_hist(win_loss_list, hist_list, n_bins, title="", x_label="", y_label=""):

    green_list = []
    red_list = []

    n_bins = int(n_bins)

    for ii in range(len(win_loss_list)):
        try:
            float(hist_list[ii])
            if win_loss_list[ii] == 1 and win_loss_list[ii] != "Unknown":
                green_list.append(hist_list[ii])
            elif win_loss_list[ii] == 0 and win_loss_list[ii] != "Unknown":
                red_list.append(hist_list[ii])
        except:
            pass

    fig, ax = plt.subplots()
    fig.subplots_adjust(top=0.8, bottom=0.1)
    (_, _, p1) = plt.hist(green_list, n_bins,
                          label="Wins", histtype="bar", normed=0, color='green', alpha=0.5)
    (_, _, p2) = plt.hist(red_list, n_bins,
                          label="Losses", histtype="bar", normed=0, color='red', alpha=0.5)
    if x_label != "":
        plt.xlabel(x_label)
    if y_label != "":
        plt.ylabel(y_label)
    else:
        plt.ylabel("Frequency")
    if title != "":
        plt.title(title)
    ax.legend(handles=(p1[0], p2[0]), loc=(0, 1.1), ncol=1)

    plt.show()


def simple_bar_plotter(y_var, x_var, threshold=1, title_string="", x_label="", y_label="Win Rate",
                       z_scores={"68%": 0.99}, conf_interval="68%"):

    plot_dict = make_plottable_dictionary(
        x_var,
        y_var,
        threshold,
        z_scores,
        conf_interval,
    )

    make_barchart(
        plot_dict["avg_by_var"], plot_dict["n_by_var"], plot_dict["error_by_var"], plot_dict["var_list"],
        plot_dict["overall_avg"], plot_dict["min_y"], plot_dict["max_y"],
        title_string=title_string, x_label=x_label, y_label=y_label
    )
    plt.show()


def wr_time(parsed_data, box=0, addtl_text=""):
    """
    Plots winrate trend over time using a moving average with average with width "box"
    """

    fig, ax = plt.subplots()
    fig.subplots_adjust(top=0.7, bottom=0.1)

    win_lose_chrono = [x for y, x in sorted(zip(parsed_data["timestamp"], parsed_data["Win/Loss Rate"]))]

    p1, = plt.plot(
            moving_avg(win_lose_chrono, box), label="Moving Avg.", linestyle="-", color="r")
    p2, = plt.plot([0, parsed_data["n_matches"]], [parsed_data["winrate"], parsed_data["winrate"]], label="Avg. WR", linestyle="--", color="b")
    p3, = plt.plot([0, parsed_data["n_matches"]], [0.5, 0.5], label="50% WR", linestyle=":", color="k")

    ax.legend(handles=(p1, p2, p3), loc=(0, 1.1), ncol=1)

    ax.set_xlabel("Match Number (Chronological)")
    ax.set_ylabel("Win Rate")
    ax.set_title("Winrate Over Time \n" + addtl_text)
    plt.xlim([0, parsed_data["n_matches"]])
    plt.ylim([0, 1])

    plt.show()


def wr_teammate(parsed_data, n_played, z_scores={"68%": 0.99}, conf_interval="68%", addtl_text=""):
    """ Winrates on a per-teammate basis for teammates from a number of games >= n_games """
    all_teammates = []

    # Get a list of every teammate
    # for ii in range(parsed_data["n_matches"]):
    #     all_teammates = all_teammates + parsed_data["ally_stats"][ii]["names"]
    #
    # teammates_unique = sorted(list(set(all_teammates)), key=str.lower)
    n_teammates = len(parsed_data["teammates_unique"])
    wr_by_teammate = []
    games_with_teammate = []
    teammates_unique_keep = []
    error = []

    # For each unique teammate, look at every game and see if they were there and (if so) if it was a W/L
    n_deleted = 0
    for tt in range(n_teammates):
        wins = []
        for ii in range(parsed_data["n_matches"]):
            if parsed_data["teammates_unique"][tt] in parsed_data["ally_stats"][ii]["names"]:
                wins.append(parsed_data["Win/Loss Rate"][ii])
        if len(wins) >= n_played:
            wr_by_teammate.append(sum(wins)/len(wins))
            games_with_teammate.append(len(wins))
            teammates_unique_keep.append(parsed_data["teammates_unique"][tt])
            error.append(
                1.96*math.sqrt(
                    1/(games_with_teammate[tt-n_deleted])
                    * wr_by_teammate[tt-n_deleted] * (1-wr_by_teammate[tt-n_deleted]))
            )
        else:
            n_deleted += 1

    bars_data = wr_by_teammate
    n_per_bar = games_with_teammate
    x_labels = teammates_unique_keep
    title_string = "Winrate by Teammate\n" + "(" + str(n_played) + "+ Games Together)\n" + addtl_text

    make_barchart(bars_data, n_per_bar, error, x_labels, 0, 1, title_string, parsed_data["winrate"])
    plt.show()


def wr_partysize(parsed_data, n_played_with, z_scores={"68%": 0.99}, conf_interval="68%", addtl_text=""):
    """
    Winrates by number of recurring teammates (with an N game cutoff for "teammates")
    n_played_with is threshold # of games with teammate to be considered part of a a "premade"
    """
    all_teammates = []

    # Get a list of every teammate
    for ii in range(parsed_data["n_matches"]):
        all_teammates += parsed_data["ally_stats"][ii]["names"]
    # Get rid of duplicates

    # Filter out the teammates with whom you played too few games
    teammates = []
    for teammate in parsed_data["teammates_unique"]:
        if all_teammates.count(teammate) >= n_played_with:
            teammates.append(teammate)

    # Go through each game and count number of teammates, storing the result in a dictionary
    party_size = []
    for ii in range(parsed_data["n_matches"]):
        party_size.append(
            len(set(teammates) & set(parsed_data["ally_stats"][ii]["names"]))
        )

    wr_partysize_dict = make_plottable_dictionary(
        party_size,
        parsed_data["Win/Loss Rate"],
        1,
        z_scores,
        conf_interval,
    )

    title_string = "Winrate by Number of Friends\n(" + str(n_played_with) + "+ Games Together)\n" + addtl_text

    make_barchart(
        wr_partysize_dict["avg_by_var"], wr_partysize_dict["n_by_var"], wr_partysize_dict["error_by_var"],
        wr_partysize_dict["var_list"], 0, 1, title_string, parsed_data["winrate"]
    )
    plt.show()


def games_vs_time(parsed_data, addtl_text=""):
    """ frequency  of games played over time NOT WRITTEN YET"""
    print("I Don't exist yet...")
    # TODO: make this function
    # plt.show()


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

    b_fwd = int(math.ceil((box - 1) / 2))  # points to grab after -3 in test
    b_rev = int(math.floor((box - 1) / 2))  # points to grab before -2 in test

    # prepare a list to hold the moving average
    mov_avg = [0 for ii in ls]
    # populate the points before the box size (not enough points to left of box)
    for ii in range(0, b_rev):
        mov_avg[ii] = sum(ls[0:ii + b_fwd + 1]) / len(ls[0:ii + b_fwd + 1])
    # populate the points in the region where the box fits around the current point
    for ii in range(b_rev, length - b_fwd):
        mov_avg[ii] = sum(ls[ii - b_rev:ii + b_fwd + 1]) / box
    # populate the points in the region approaching the end (not enough points to right of box)
    for ii in range(length - b_fwd, length):
        mov_avg[ii] = sum(ls[(ii - b_rev):]) / len(ls[(ii - b_rev):])

    return mov_avg


def compute_error(data_list, z_scores, conf_interval="90%"):

    if conf_interval in list(z_scores.keys()):
        z_score = float(z_scores[conf_interval])
    else:
        z_score = 0.99
        print("Couldn't figure out desired confidence interval; showing one standard deviation (68%)")

    continuous = 0
    for ii in data_list:
        if ii != 0 and ii != 1:
            continuous += 1

    if continuous:
        n = float(len(data_list) + 1)  # can never be 0
        u = sum(data_list) / n
        s = math.sqrt(sum((x - u) ** 2 for x in data_list) / len(data_list))
        ci = z_score * s / math.sqrt(len(data_list))

    else:
        n = float(len(data_list) + 1)  # can never be zero
        u = sum(data_list) / n
        ci = z_score * math.sqrt(u * (1 - u) / n)

    return u, ci


z_scores = {
        "68%": 0.99,
        "80%": 1.28,
        "85%": 1.44,
        "90%": 1.64,
        "95%": 1.96,
        "98%": 2.33,
        "99%": 2.58,
}