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

class used_files_menu:
	def __init__(self):
		self.menu=gtk.Menu()

	def init(self,config_file,callback):
		logging.info("used_file_menu init")
		try:
			for i in self.menu.get_children():
				self.menu.remove(i)
		except:
			pass

		self.last_items=[]
		self.config_file=config_file
		self.callback=callback
		self.base_dir=os.path.dirname(config_file)+'/'
	
	def plot_token_id_gen(self,plot_token):
		return plot_token.file0+plot_token.tag0+plot_token.file1+plot_token.tag1

	def plot_token_check_list(self,items,plot_token_id):
		for i in range(0,len(items)):
			check=self.plot_token_id_gen(items[i])
			if check==plot_token_id:
				return True
		return False

	def append(self,plot_token,save):
		logging.info("used_file_menu append")
		file_name=self.plot_token_id_gen(plot_token)
		
		if self.plot_token_check_list(self.last_items,file_name)==False:
			menu_item = gtk.MenuItem(file_name)		   
			self.menu.append(menu_item)
			self.last_items.append(plot_token)
			ref=self.last_items[len(self.last_items)-1]
			menu_item.connect("activate", self.callback,ref)
			if save==True:
				self.save_list()
			menu_item.show()

	def save_list(self):
		a = open(self.config_file, "w")
		a.write(str(len(self.last_items))+"\n")
		for i in range(0,len(self.last_items)):
			a.write(self.last_items[i].path+"\n")
			a.write(self.last_items[i].file0+"\n")
			a.write(self.last_items[i].tag0+"\n")
			a.write(self.last_items[i].file1+"\n")
			a.write(self.last_items[i].tag1+"\n")
		
		a.close()

	def reload_list(self):
		logging.info("used_file_menu reload_list")
		print "Loading menu",self.config_file

		for i in self.menu.get_children():
			self.menu.remove(i)
		try:
			f=open(self.config_file)
			config = f.readlines()
			f.close()

			for ii in range(0, len(config)):
				config[ii]=config[ii].rstrip()

			number=int(config[0])
			for ii in range(0, number):
				pos=1+ii*5

				readitem=plot_command_class()
				readitem.path=config[pos+0]
				readitem.file0=config[pos+1]
				readitem.tag0=config[pos+2]
				readitem.file1=config[pos+3]
				readitem.tag1=config[pos+4]

				if readitem.path.startswith(self.base_dir)==True:
					self.append(readitem,False)

		except IOError:
			print "No file found"



