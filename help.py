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
import commands
import subprocess
from win_lin import running_on_linux
from cal_path import get_exe_command
import socket 
import time
import urlparse
import re
import os
from ver import ver_core
from ver import ver_mat
from ver import ver_gui
import gobject
from util import find_data_file
from global_objects import global_object_register

class help_class(gtk.Window):
	def init(self):

		s=gtk.gdk.screen_get_default()
		w,h=self.get_size()

		x=s.get_width()-w
		y=0#s.get_height()-h

		self.move(x,y)
		global_object_register("help_set_text",self.help_set_text)
		global_object_register("help_set_icon",self.help_set_icon)

		self.box=gtk.HBox()
		self.add(self.box)
		self.image = gtk.Image()
		self.image.set_from_file(find_data_file("gui/play.png"))
		self.image.show()




		self.label = gtk.Label()
		self.text="<big>Hi!</big>\n I'm the on-line help system :) .\n Click on the play icon to start a simulation."

		self.label.set_markup(self.text)
		self.label.show()

		self.box.pack_start(self.image, True, True, 0)
		self.box.pack_start(self.label, True, True, 0)

		self.box.show()
		self.set_border_width(10)
		self.set_title("Help")
		self.resize(300,100)
		self.show()

	def help_set_icon(self,file_name):
		self.image.set_from_file(find_data_file(file_name))

	def help_set_text(self,input_text):
		self.label.set_markup(input_text)
