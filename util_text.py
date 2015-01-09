import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import shutil

def gkt_title_to_gnu_plot_title(in_string):
	out_string=in_string.replace("<sub>","_{")
	out_string=out_string.replace("</sub>","}")
	return out_string
