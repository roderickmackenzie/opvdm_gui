#    Organic Photovoltaic Device Model - a drift diffusion base/Shockley-Read-Hall
#    model for organic solar cells. 
#    Copyright (C) 2012 Roderick C. I. MacKenzie
#
#	roderick.mackenzie@nottingham.ac.uk
#	www.opvdm.com
#	Room B86 Coates, University Park, Nottingham, NG7 2RD, UK
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

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
