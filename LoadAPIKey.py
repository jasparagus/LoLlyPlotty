# LOAD API KEY
import tkinter.filedialog # for loading files
import time # import time to allow for use of time.sleep(secs). Prevents excessive api calls


def read_key(config):
    if config == 0:
        # If there's no config file
        try:
            api_file_path = tkinter.filedialog.askopenfilename(
                filetypes=[("API Key",".txt"), ("All Files",".*")],
                title="Select Text File With API Key",
                initialdir="C:\\Users\Jasper\OneDrive\Documents\Python"
            )
        except:
            api_file_path = tkinter.filedialog.askopenfilename(
                filetypes=[("API Key", ".txt"), ("All Files", ".*")],
                title="Select Text File With API Key"
            )

        time.sleep(2)
        api_file = open(api_file_path,"r")
        api_key = api_file.read()

    else:
        # if a config file is found
        print("Config not implemented yet")

    return api_key
