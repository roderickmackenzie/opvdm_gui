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
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from plot_export import plot_export 
from numpy import arange, sin, pi, zeros
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
#from matplotlib.backends.backend_gtk import FigureCanvasGTK as FigureCanvas
from matplotlib.figure import Figure
from plot_info import plot_info
from plot_widget import plot_widget

class plot_window():
	def __init__(self):
		self.shown=False

	def destroy(self):
		self.shown=False
		self.window.destroy()

	def callback_destroy(self,widget):
		self.destroy()

	def init(self,input_files,plot_labels,plot_token,config_file,units):
		self.shown=True
		self.window = gtk.Window()
		self.window.set_border_width(10)
		self.plot=plot_widget()
		self.plot.init(self.window)

		print "here1"
		print plot_labels
		if len(plot_labels)==0:
			for i in range(0,len(input_files)):
				plot_labels.append(os.path.basename(input_files[i]))

		#print plot_labels
		for i in range(0,len(plot_labels)):
			if len(plot_labels[i])>0:
				if plot_labels[i][0]=="\\":
					plot_labels[i]=plot_labels[i][1:]
			plot_labels[i].replace("\\","/")

		ids=[]
		for i in range(0,len(input_files)):
			ids.append(0)
		self.plot.load_data(input_files,ids,plot_labels,plot_token,config_file,units)

		self.plot.do_plot()
		self.plot.show()
		self.window.add(self.plot)

		self.window.show_all()
		self.window.connect("destroy", self.callback_destroy)


