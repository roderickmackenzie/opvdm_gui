import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import shutil
import copy
import pdb
import logging
from plot_command import plot_command_class
import glob
from inp import inp_search_token_value
from inp import inp_load_file

class used_files_menu:
	def __init__(self):
		self.menu=gtk.Menu()

	def refresh(self):
		try:
			for i in self.menu.get_children():
				self.menu.remove(i)
		except:
			pass

		self.list=[]
		files=[]
		for my_file in glob.glob(os.path.join(self.base_dir,"*.oplot")):
			files.append(my_file)

		sorted(files)
		for i in range(0,len(files)):
			self.append(files[i])

	def init(self,search_path,callback):

		self.base_dir=search_path
		self.callback=callback

		self.refresh()

	def append(self,file_name):
		lines=[]
		plot_token=plot_command_class()
		if plot_load_token(plot_token,file_name)==True:
			menu_item = gtk.MenuItem(os.path.basename(file_name).split(".")[0])		   
			self.menu.append(menu_item)
			self.list.append(plot_token)
			menu_item.connect("activate", self.callback,self.list[len(self.list)-1])
			menu_item.show()



