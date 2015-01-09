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
import signal
import subprocess
from tempfile import mkstemp

def replace(file_path, token, replace):
	if os.access(file_path, os.W_OK)==False:
		print "I don't have access to "+file_path
		return

	token=token+"\n"
	replace=replace+"\n"
	fh, abs_path = mkstemp()
	new_file = open(abs_path,'w')
	old_file = open(file_path)
	skip=False

	for line in old_file:

		if skip == False:
			if line != token:
				new_file.write(line)
			else:
				new_file.write(line)
				new_file.write(replace)
				skip=True
		else:
			skip=False

	new_file.close()
	os.close(fh)
	old_file.close()
	os.remove(file_path)
	shutil.move(abs_path, file_path)

def get_token_value(file_path, token):
	old_file = open(file_path)
		
	output=False

	
	for line in old_file:
		line=line.rstrip()
		if output==True:
			old_file.close()
			return line

		if line==token:
			output=True

	old_file.close()
	return "0"


