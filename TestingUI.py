# PREPARE ROOT UI WINDOW (IN PROGRESS)

import tkinter.ttk # allows for making a UI box
global root
root = tkinter.Tk()
root.title("LeagueOfHistograms")
root.geometry("400x600")
# class Adder(tkinter.ttk.Frame):
#     """The adders gui and functions."""
#
#     def __init__(self, parent, *args, **kwargs):
#         tkinter.ttk.Frame.__init__(self, parent, *args, **kwargs)
#         self.root = parent
#         self.init_gui()
#
#     def init_gui(self):
#         """Builds GUI."""
#         self.root.title('Number Adder')
#
#
# if __name__ == '__main__':
#     root = tkinter.Tk()
#     Adder(root)
#     root.mainloop()