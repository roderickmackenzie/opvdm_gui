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
import signal
from util import replace_file_in_zip_archive
import subprocess
from tempfile import mkstemp
import logging
import zipfile

def inp_read_next_item(lines,pos):
	token=lines[pos]
	pos=pos+1
	value=lines[pos]
	pos=pos+1
	return token,value,pos

def inp_update_token_value(file_path, token, replace,line_number):
	if token=="#Tll":
		inp_update_token_value("thermal.inp", "#Tlr", replace,1)
		inp_update_token_value("dos0.inp", "#Tstart", replace,1)
		try:
			upper_temp=str(float(replace)+5)
		except:
			upper_temp="300.0"
		inp_update_token_value("dos0.inp", "#Tstop", upper_temp,1)

	path=os.path.dirname(file_path)

	zip_file_name=os.path.join(path,"sim.opvdm")

	if os.path.isfile(file_path):
		f=open(file_path, mode='rb')
    		lines = f.read()
		f.close()
	else:
		if os.path.isfile(zip_file_name):
			zf = zipfile.ZipFile(zip_file_name, 'r')
			lines = zf.read(os.path.basename(file_path))
			zf.close()
		else:
			return "0"

	lines=lines.split("\n")

	for i in range(0, len(lines)):
		lines[i]=lines[i].rstrip()

	if lines[len(lines)-1]=='\n':
		del lines[len(lines)-1]

	for i in range(0, len(lines)):
		if lines[i]==token:
			lines[i+line_number]=replace
			break


	if os.path.isfile(file_path):
		fh, abs_path = mkstemp()
		dump=""
		for item in lines:
			dump=dump+item+"\n"

		dump=dump.rstrip("\n")
		f=open(abs_path, mode='wb')
		lines = f.write(dump)
		f.close()

		os.close(fh)
		shutil.move(abs_path, file_path)
	else:
		replace_file_in_zip_archive(zip_file_name,os.path.basename(file_path),lines)

def inp_isfile(file_path):

	path=os.path.dirname(file_path)

	zip_file_name=os.path.join(path,"sim.opvdm")

	base_name=os.path.basename(file_path)

	ret=False

	if os.path.isfile(file_path):
		ret=True
	else:
		if os.path.isfile(zip_file_name):
			zf = zipfile.ZipFile(zip_file_name, 'r')
			if base_name in zf.namelist():
				ret=True
			zf.close()
		else:
			ret=False
	
	return ret



def inp_load_file(lines,file_path):

	path=os.path.dirname(file_path)

	read_lines=[]
	zip_file_name=os.path.join(path,"sim.opvdm")

	if os.path.isfile(file_path):
		f=open(file_path, mode='rb')
    		read_lines = f.read()
		f.close()
	else:
		if os.path.isfile(zip_file_name):
			zf = zipfile.ZipFile(zip_file_name, 'r')
			if zf.namelist().count(os.path.basename(file_path))>0:
				read_lines = zf.read(os.path.basename(file_path))
				zf.close()
			else:
				zf.close()
				return False
		else:
			return False

	read_lines=read_lines.split("\n")

	del lines[:]

	for i in range(0, len(read_lines)):
		lines.append(read_lines[i].rstrip())

	return True

def inp_write_lines_to_file(file_path,lines):
	path=os.path.dirname(file_path)

	zip_file_name=os.path.join(path,"sim.opvdm")

	base_name=os.path.basename(file_path)

	if os.path.isfile(file_path)==True or os.path.isfile(zip_file_name)==False:
		inp_save_lines(file_path,lines)
	else:
		replace_file_in_zip_archive(zip_file_name,base_name,lines)

def inp_save_lines(file_path,lines):
	dump=""
	for item in lines:
		dump=dump+item+"\n"

	dump=dump.rstrip("\n")

	f=open(file_path, mode='wb')
	lines = f.write(dump)
	f.close()

def inp_search_token_value(lines, token):

	for i in range(0, len(lines)):
		if lines[i]==token:
			return lines[i+1]

	return False

def inp_get_next_token_array(lines,pos):

	ret=[]
	ret.append(lines[pos])
	pos=pos+1
	while (lines[pos][0]!="#"):
		ret.append(lines[pos])
		pos=pos+1

	return ret,pos

def inp_get_token_array(file_path, token):

	lines=[]
	ret=[]
	inp_load_file(lines,file_path)

	for i in range(0, len(lines)):
		if lines[i]==token:
			pos=i+1
			while (lines[pos][0]!="#"):
				ret.append(lines[pos])
				pos=pos+1

			return ret

	return False

def inp_get_token_value(file_path, token):

	lines=[]
	inp_load_file(lines,file_path)

	for i in range(0, len(lines)):
		if lines[i]==token:
			return lines[i+1]

	return "0"

