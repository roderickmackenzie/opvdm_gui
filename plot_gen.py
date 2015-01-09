import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import shutil
from token_lib import tokens
from numpy import *
from util import pango_to_gnuplot
from plot import plot_data
from plot_window import plot_window
from matplotlib.widgets import Cursor

window=None

destroy=False

def set_plot_auto_close(value):
	global destroy
	destroy=value

def plot_gen(input_files,plot_labels,plot_token):
	if (len(input_files)==1):
		if os.path.splitext(input_files[0])[1]==".plot":
			plot_file=input_files[0]
			cmd = 'gnuplot -persist '+plot_file
			os.system(cmd)
			return
	global window
	global destroy

	if window!=None:
		if window.shown==True:
			if destroy==True:
				window.input_files=input_files
				window.plot_token=plot_token
				window.plot.load_data(input_files,plot_labels,plot_token)
				window.plot.fig.canvas.draw()
				window.window.present()
				window.window.set_keep_above(True)
				return

	window=plot_window()
	window.init(input_files,plot_labels,plot_token)


