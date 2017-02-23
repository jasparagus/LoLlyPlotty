# LOAD API KEY
APIFilePath = tkinter.filedialog.askopenfilename(filetypes=[("API Key",".txt"),("All Files",".*")],title="Choose API File")
# The above opens a file dialog - use for API key
APIFile = open(APIFilePath,"r")
APIKey = APIFile.read()