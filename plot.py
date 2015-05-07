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

import sys
import os
import shutil
from token_lib import tokens
from util import pango_to_gnuplot
from plot_info import plot_info
from util import zip_get_data_file

def load_graph(path):
	cmd = '/usr/bin/gnuplot -persist '+path
	print cmd
	os.system(cmd)

def check_info_file(search_string):
	files=["dos0.inp","dos1.inp","photokit_ri.dat","photokit_real.dat","photokit_imag.dat","jv_psun_voc.dat","jv_voc_nt.dat","jv_voc_pt.dat","jv_psun_nf_nt.dat","jv_psun_pf_pt.dat","jv_psun_np_tot.dat","sim_info.dat","light.inp","points.dat","stark.inp"]
	if files.count(search_string)> 0:
		return True
	else:
		return False

def file_name_to_latex(in_string):
	out_string=in_string.replace("_","\\_")
	return out_string

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

def plot_populate_plot_token(plot_token,file_name):
	if file_name!=None:
		ret=get_plot_file_info(plot_token,file_name)
		print "ret====",ret
		if ret==True:
			return True

	#check to see if I have been provided with a token

	if plot_token!=None:
		my_token_lib=tokens()
		result0=my_token_lib.find(plot_token.tag0)
		result1=my_token_lib.find(plot_token.tag1)
		print "one=",plot_token.tag0,result0
		print "two=",plot_token.tag1,result1
		if result0!=False:
			plot_token.x_label=result0.info
			plot_token.x_units=result0.units
			plot_token.y_label=result1.info
			plot_token.y_units=result1.units
			plot_token.title=result0.info+" "+result1.info

			print "Found tokens",plot_token.tag0,plot_token.tag1
			return True
		else:
			print "Tokens not found",plot_token.tag0,plot_token.tag1

	return False
