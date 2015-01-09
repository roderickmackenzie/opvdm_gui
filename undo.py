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

