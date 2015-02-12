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
import pdb
import pygtk
pygtk.require('2.0')
import gtk

import os

undo=[]
undo_enabled=True

class undo_list_class():
	def init(self):
		global undo_enabled
		undo_enabled=True

	def add(self,items):
		global undo
		if undo_enabled==True:
			undo.append(items)

	def enable(self):
		global undo_enabled
		undo_enabled=True

	def disable(self):
		global undo_enabled
		undo_enabled=False

	def get_list(self):
		global undo
		return undo

