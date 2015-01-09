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

