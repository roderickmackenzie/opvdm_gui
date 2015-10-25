#    Organic Photovoltaic Device Model - a drift diffusion base/Shockley-Read-Hall
#    model for organic solar cells. 
#    Copyright (C) 2012 Roderick C. I. MacKenzie
#
#	roderick.mackenzie@nottingham.ac.uk
#	www.opvdm.com
#	Room B86 Coates, University Park, Nottingham, NG7 2RD, UK
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License v2.0, as published by
#    the Free Software Foundation.
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
from inp import inp_update_token_value
from inp import inp_write_lines_to_file
from inp import inp_load_file
from inp import inp_search_token_value
from scan_item import scan_item
from scan_item import scan_item_add
from util import find_data_file
import glob
from util import time_with_units
from plot_widget import plot_widget
from util_zip import zip_get_data_file
from window_list import windows
from plot_state import plot_state
from plot_io import plot_load_info
from cal_path import get_exe_command


layers=0
electrical_layers=0
width=[]
mat_file=[]
dos_file=[]
electrical_layer=[]

def epitaxy_load():
	lines=[]
	global layers
	global electrical_layers
	global width
	global mat_file
	global dos_file
	global electrical_layer

	layers=0
	electrical_layers=0
	width=[]
	mat_file=[]
	dos_file=[]
	electrical_layer=[]

	if inp_load_file(lines,"epitaxy.inp")==True:
		pos=0
		pos=pos+1

		for i in range(0, int(lines[pos])):
			pos=pos+1
			#label=lines[pos]				#read label

			pos=pos+1
			width.append(float(lines[pos]))

			pos=pos+1
			mat_file.append(lines[pos])

			pos=pos+1
			temp_dos_file=lines[pos]		#value

			if temp_dos_file=="none":
				electrical_layer.append(-1)
			else:
				electrical_layer.append(electrical_layers)
				dos_file.append(temp_dos_file)
				electrical_layers=electrical_layers+1

			layers=layers+1


def epitaxy_get_dos_files():
	global dos_file
	return dos_file

def epitaxy_get_layers():
	global layers
	return layers

def epitaxy_get_electrical_layer(i):
	global electrical_layer
	print electrical_layer,i
	return electrical_layer[i]

def epitaxy_get_mat_file(i):
	global mat_file
	return mat_file[i]
