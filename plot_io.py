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
from token_lib import tokens
from inp import inp_load_file
from inp import inp_search_token_value
from util import zip_get_data_file
from util import str2bool

def plot_load_token(plot_token,file_name):
	lines=[]
	if inp_load_file(lines,file_name)==True:
		plot_token.logy=str2bool(inp_search_token_value(lines, "#logy"))
		plot_token.logx=str2bool(inp_search_token_value(lines, "#logx"))
		plot_token.grid=str2bool(inp_search_token_value(lines, "#grid"))
		plot_token.invert_y=str2bool(inp_search_token_value(lines, "#invert_y"))
		plot_token.normalize=str2bool(inp_search_token_value(lines, "#normalize"))
		plot_token.norm_to_peak_of_all_data=str2bool(inp_search_token_value(lines, "#norm_to_peak_of_all_data"))
		plot_token.subtract_first_point=str2bool(inp_search_token_value(lines, "#subtract_first_point"))
		plot_token.add_min=str2bool(inp_search_token_value(lines, "#add_min"))
		plot_token.file0=inp_search_token_value(lines, "#file0")
		plot_token.file1=inp_search_token_value(lines, "#file1")
		plot_token.file2=inp_search_token_value(lines, "#file2")
		plot_token.tag0=inp_search_token_value(lines, "#tag0")
		plot_token.tag1=inp_search_token_value(lines, "#tag1")
		plot_token.tag2=inp_search_token_value(lines, "#tag2")
		plot_token.legend_pos=inp_search_token_value(lines, "#legend_pos")
		plot_token.key_units=inp_search_token_value(lines, "#key_units")
		plot_token.label_data=str2bool(inp_search_token_value(lines, "#label_data"))
		plot_token.type=inp_search_token_value(lines, "#type")
		return True
	return False


def get_plot_file_info(output,file_name):
	found,lines=zip_get_data_file(file_name)
	if found==False:
		return False

	for i in range(0, len(lines)):
		lines[i]=lines[i].rstrip()
	if len(lines)>1:
		if lines[0]=="#opvdm":
			for i in range(0, len(lines)):
				if (lines[i][0]!="#"):
					break
				else:
					command=lines[i].split(" ",1)
					if len(command)<2:
						command.append("")
					if (command[0]=="#x_mul"):
						output.x_mul=float(command[1])
					if (command[0]=="#y_mul"):
						output.y_mul=float(command[1])
					if (command[0]=="#x_label"):
						output.x_label=command[1]
					if (command[0]=="#y_label"):
						output.y_label=command[1]
					if (command[0]=="#x_units"):
						output.x_units=command[1]
					if (command[0]=="#y_units"):
						output.y_units=command[1]
					if (command[0]=="#logscale_x"):
						output.logx=bool(int(command[1]))
					if (command[0]=="#logscale_y"):
						output.logy=bool(int(command[1]))
					if (command[0]=="#type"):
						output.type=command[1]
					if (command[0]=="#title"):
						output.title=command[1]
					if (command[0]=="#section_one"):
						output.section_one=command[1]
					if (command[0]=="#section_two"):
						output.section_two=command[1]

			#print "Data read from file"
			return True

	return False
