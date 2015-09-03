#!/usr/bin/env python
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
import math
import gobject
from util import find_data_file
from inp import inp_update_token_value
from inp import inp_get_token_value
from inp import inp_load_file

class tb_item_sim_mode(gtk.ToolItem):

	def init(self):
		self.sim_mode = gtk.combo_box_entry_new_text()
		self.sim_mode.set_size_request(-1, 20)

		lines=[]
		inp_load_file(lines,find_data_file("sim_menu.inp"))

		for i in range(0, len(lines)):
			if lines[i]!="":
				self.sim_mode.append_text(lines[i].rstrip())

		self.sim_mode.child.connect('changed', self.call_back_sim_mode_changed)
		token=inp_get_token_value("sim.inp", "#simmode")
		liststore = self.sim_mode.get_model()
		for i in xrange(len(liststore)):
		    if liststore[i][0] == token:
		        self.sim_mode.set_active(i)

		lable=gtk.Label("Simulation mode:")
		#lable.set_width_chars(15)
		lable.show()

		hbox = gtk.HBox(False, 2)

		hbox.pack_start(lable, False, False, 0)
		hbox.pack_start(self.sim_mode, False, False, 0)

		self.add(hbox);
		self.show_all()


	def call_back_sim_mode_changed(self, widget, data=None):
		mode=self.sim_mode.get_active_text()
		inp_update_token_value("sim.inp", "#simmode", mode,1)
