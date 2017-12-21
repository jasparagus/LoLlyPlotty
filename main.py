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

# Custom module/ imports
import gui

my_app = gui.App()
gui.make_resizable(my_app.root)

# Refresh everything, setting it for first-run, then start the GUI mainloop
my_app.refresh()
my_app.root.mainloop()
