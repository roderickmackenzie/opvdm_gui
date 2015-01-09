import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import shutil
from token_lib import tokens
from numpy import *
from util import pango_to_gnuplot
from util_text import gkt_title_to_gnu_plot_title


def plot_export(dest_dir,input_files,mygraph):
	if os.path.isdir(dest_dir)==False:
		os.makedirs(dest_dir)

	plot_file=dest_dir+'/plot.plot'

	#build plot script
	plot_string="set term postscript eps enhanced color \"Helvetica\" 28\n"
	plot_string=plot_string+"set key top left\n"
	plot_string=plot_string+"set xlabel '"+mygraph.read.x_label+"'\n"
	plot_string=plot_string+"set ylabel '"+gkt_title_to_gnu_plot_title(mygraph.read.y_label)+" ("+mygraph.read.y_units+")\n"
	plot_string=plot_string+"set format y '%.1le%T'\n"

	if (mygraph.read.logscale_y==1):
		plot_string=plot_string+"set logscale y\n"

	if (mygraph.read.logscale_x==1):
		plot_string=plot_string+"set logscale x\n"

	plot_string=plot_string+"plot \\\n"
	for i in range(0, len(input_files)):
		line_name=os.path.basename(os.path.dirname(input_files[i]))
		plot_string=plot_string+"'"+input_files[i]+"' using ($1*"+str(mygraph.read.x_mul)+"):($2*"+str(mygraph.read.y_mul)+") with lp lw 2 title '"+line_name+"',\\\n"

	plot_string=plot_string[:-3]


	text_file = open(plot_file, "w")
	text_file.write(plot_string)
	text_file.close()

	#build make file
	makefile_string="main:\n"
	makefile_string=makefile_string+"\tgnuplot plot.plot >plot.eps\n"
	makefile_string=makefile_string+"\tgs -dNOPAUSE -r600 -dEPSCrop -sDEVICE=jpeg -sOutputFile=plot.jpg plot.eps -c quit\n"
	makefile_string=makefile_string+"\tgnome-open plot.jpg\n"

	text_file = open(dest_dir+"/makefile", "w")
	text_file.write(makefile_string)
	text_file.close()
