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

    plot_dict["half_max"] = float(sorted(y_list_clean)[-1] * 0.5)

    return plot_dict


def make_barchart(plot_dict, title_string="", x_label="", y_label=""):
    """
    Make a bar chart from data. Inputs: list of data to be plotted in bar form (a list of numbers
    """

    n_of_things_to_plot = len(plot_dict["var_list"])

    fig, ax = plt.subplots()
    fig.subplots_adjust(top=0.75, bottom=0.25)

    # prepare basics
    locs = range(n_of_things_to_plot)
    width = 0.75  # the width of the bars
    startx = -width - 0.25  # where the x axis starts
    endx = n_of_things_to_plot - 1 + width + 0.25  # where the x axis ends

    # create objects to plot
    bars1 = ax.bar(locs, plot_dict["avg_by_var"], width, color='r', yerr=plot_dict["error_by_var"])
    pl_avg, = plt.plot([startx, endx], [plot_dict["overall_avg"], plot_dict["overall_avg"]],
                       label="Overall Average For \"" + y_label + "\" = " + str(round(plot_dict["overall_avg"], 2)),
                       linestyle="--", color="b")

    pl_hlf, = plt.plot([startx, endx], [plot_dict["half_max"], plot_dict["half_max"]],
                       label="Half-Max = " + str(round(plot_dict["half_max"], 2)) + " " +  y_label,
                       linestyle=":", color="k")

    plt.plot([startx, endx], [0, 0], label="Zero", linestyle="-", color="k")

    # add some text for labels, title and axes ticks
    if y_label != "":
        ax.set_ylabel("Average " + y_label)
    if x_label != "":
        ax.set_xlabel(x_label)
    if title_string != "":
        ax.set_title(title_string)

    bar_labels = []
    for ii in range(len(plot_dict["var_list"])):
        bar_labels += [str(plot_dict["var_list"][ii]) + " (" + str(plot_dict["n_by_var"][ii]) + " games)"]

    ax.set_xticks(locs)
    ax.set_xticklabels(bar_labels, rotation=35, ha="right")
    plt.xlim([startx, endx])
    plt.ylim([plot_dict["min_y"]*1.15, plot_dict["max_y"]*1.15])

    leg = plt.legend(handles=(pl_avg, pl_hlf), loc=(0, 1.1), ncol=1)
    plt.gca().add_artist(leg)

    for ii in range(len(plot_dict["avg_by_var"])):
        ax.text(int(ii), plot_dict["avg_by_var"][ii] * 1.1,
                str(round(plot_dict["avg_by_var"][ii], 2)),
                ha='center', va='top')
    plt.show()


def make_scatterplot(x_list, y_list, y_name, title_string="", x_label="", y_label=""):
    """
    Make a bar chart from data. Inputs: list of data to be plotted in bar form (a list of numbers
    """

    x_list_clean = []
    y_list_clean = []

    for ii in range(len(x_list)):
        try:
            x_i = float(x_list[ii])
            y_i = float(y_list[ii])
            # If both lists have a good value here, keep the point
            x_list_clean += [x_i]
            y_list_clean += [y_i]
        except ValueError:
            pass

    fig, ax = plt.subplots()
    fig.subplots_adjust(top=0.8, bottom=0.25)

    x_min = sorted(x_list_clean)[0]
    x_max = sorted(x_list_clean)[-1]
    y_min = sorted(y_list_clean)[0]
    y_max = sorted(y_list_clean)[-1]

    y_avg = float(sum(y_list_clean) / len(y_list_clean))

    # create objects to plot

    pl_avg, = plt.plot([x_min, x_max], [y_avg, y_avg],
                       label="Overall Average For \""+ y_label + "\" is " + str(round(y_avg, 2)),
                       linestyle="--", color="b")

    pl_hlf, = plt.plot([x_min, x_max], [y_max * 0.5, y_max * 0.5],
                       label="Half-Max is " + str(round(y_max, 2)) + " " +  y_label,
                       linestyle=":", color="k")

    plt.plot(x_list_clean, y_list_clean, "r.", label=y_name)

    # add some text for labels, title and axes ticks
    if y_label != "":
        ax.set_ylabel(y_label)
    if x_label != "":
        ax.set_xlabel(x_label)
    if title_string != "":
        ax.set_title(title_string)

    leg = plt.legend(handles=(pl_avg, pl_hlf), loc=(0, 1.1), ncol=1)
    plt.gca().add_artist(leg)

    plt.show()


def make_hist(hist_list, bool_list, n_bins, title="", x_label="", y_label=""):

    green_list = []
    red_list = []

    n_bins = int(n_bins)

    for ii in range(len(bool_list)):
        try:
            h_i = float(hist_list[ii])
            if bool_list[ii] == 1 and bool_list[ii] != "Unknown":
                green_list.append(h_i)
            elif bool_list[ii] == 0 and bool_list[ii] != "Unknown":
                red_list.append(h_i)
        except ValueError:
            pass

    print(green_list," \n",red_list)

    green_mean = sum(green_list) / len(green_list)
    red_mean = sum(red_list) / len(red_list)

    fig, ax = plt.subplots()
    fig.subplots_adjust(top=0.75, bottom=0.1)
    (_, _, p1) = plt.hist(green_list, n_bins,
                          label= y_label + " True", histtype="bar", normed=0, color="green", alpha=0.5)
    (_, _, p2) = plt.hist(red_list, n_bins,
                          label= y_label + " False", histtype="bar", normed=0, color="red", alpha=0.5)
    m_g = plt.axvline(green_mean, color="green", linestyle="dashed", label="Average, " + y_label + " True")
    m_r = plt.axvline(red_mean, color="red", linestyle="dashed", label="Average, " + y_label + " False")

    if x_label != "":
        plt.xlabel(x_label)
    if y_label != "":
        plt.ylabel(y_label + " Count")
    else:
        plt.ylabel("Number of True Instances")
    if title != "":
        plt.title(title)
    ax.legend(handles=(p1[0], p2[0], m_g, m_r), loc=(0, 1.07), ncol=1)

    plt.show()


def simple_bar_plotter(x_var, y_var, threshold=1, title_string="", x_label="", y_label="Win Rate",
                       z_scores={"68%": 0.99}, conf_interval="68%"):

    plot_dict = make_plottable_dictionary(
        x_var,
        y_var,
        threshold,
        z_scores,
        conf_interval,
    )

    make_barchart(plot_dict, title_string=title_string, x_label=x_label, y_label=y_label)


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

    make_barchart(wr_partysize_dict, title_string, parsed_data["winrate"])
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