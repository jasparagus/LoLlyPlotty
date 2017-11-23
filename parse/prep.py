#TODO: make a function to "prep" teammate names - puts a list of teammate names into config_info. Inputs are config_in

def prep_teammates(config_info, match_data, int):
    teammates = []

    # TODO: implement this function
    for match in match_data:
        new_teammates = []

        teammates += match["Teammates"]

    unique_teammates = list(set(teammates))

    for teammate in unique_teammates:
        print(teammate)
        # find instances, and compare with "int" param

    return teammates
