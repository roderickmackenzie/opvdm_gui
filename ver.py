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
from cal_path import find_data_file
from inp import inp_load_file

def ver_core():
	lines=[]
	inp_load_file(lines,find_data_file("ver.inp"))
	return lines[1]

def ver_gui():
	lines=[]
	inp_load_file(lines,find_data_file("ver.inp"))
	return lines[3]

def ver_mat():
	lines=[]
	inp_load_file(lines,find_data_file("ver.inp"))
	return lines[5]

def ver():
	lines=[]
	inp_load_file(lines,find_data_file("ver.inp"))
	ver_string="core: Version "+lines[1]+", gui: Version "+lines[3]+", materials: Version "+lines[5]

	string=ver_string
	return string
