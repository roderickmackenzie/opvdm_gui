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
from scan_item import scan_item
import vte

class tab_terminal(gtk.VBox):

	lines=[]
	edit_list=[]
	file_name=""
	line_number=[]
	name="Terminal"
	visible=1
	


	def wow(self,sim_dir):
		self.main_box=gtk.VBox()
		self.sim_dir=sim_dir
		self.edit_list=[]
		self.line_number=[]


		self.terminal     = vte.Terminal()
		self.terminal.fork_command("/bin/sh")
		self.terminal.feed_child('opvdm --version\n')
		self.terminal.set_scrollback_lines(10000)
		self.terminal.show()
		self.main_box.add(self.terminal)

		self.add(self.main_box)
		self.main_box.show()

