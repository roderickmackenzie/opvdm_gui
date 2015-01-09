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
from search import return_file_list
from plot import plot_data
from plot_gen import plot_gen
from plot import plot_info
from util import find_data_file
from about import about_dialog_show
from used_files_menu import used_files_menu
from server import server
from scan_tab import scan_vbox
from util import dlg_get_text
import threading
import gobject
import pyinotify
import multiprocessing
import time
import glob

def get_scan_dirs(scan_dirs,sim_dir):
	ls=os.listdir(sim_dir)

	for i in range(0, len(ls)):
		dir_name=sim_dir+ls[i]
		full_name=sim_dir+ls[i]+"/opvdm_gui_config.inp"
		if os.path.isfile(full_name):
			scan_dirs.append(dir_name)

class scan_class(gtk.Window):
	param_list=[]

	icon_theme = gtk.icon_theme_get_default()

	def get_main_menu(self, window):
		accel_group = gtk.AccelGroup()


		item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)


		item_factory.create_items(self.menu_items)


		window.add_accel_group(accel_group)

		self.item_factory = item_factory

		return item_factory.get_widget("<main>")

	def callback_close(self, widget, data=None):
		self.hide()
		return True

	def callback_help(self, widget, data=None):
		cmd = 'firefox http://www.roderickmackenzie.eu/wiki/index.php?title=parameter_scan &'
		os.system(cmd)

	def callback_add_page(self, widget, data=None):
		new_sim_name=dlg_get_text( "New simulation name:", "Simulation "+str(self.number_of_tabs+1))

		if new_sim_name!=None:
			name=os.getcwd()+'/'+new_sim_name+'/'
			self.add_page(name)

	def callback_remove_page(self,widget,name):
		pageNum = self.notebook.get_current_page()
		tab = self.notebook.get_nth_page(pageNum)
		self.toggle_tab_visible(tab.tab_name)

	def callback_copy_page(self,widget,data):
		pageNum = self.notebook.get_current_page()
		tab = self.notebook.get_nth_page(pageNum)
		name=tab.tab_name
		old_dir=self.sim_dir+'/'+name
		new_sim_name=dlg_get_text( "Clone the current simulation to a new simulation called:", "New simulation")
		if new_sim_name!=None:
			new_dir=self.sim_dir+'/'+new_sim_name
			print "I will copy ",old_dir,new_dir
			shutil.copytree(old_dir, new_dir)
			self.add_page(new_sim_name)

	def callback_rename_page(self,widget,data):
		pageNum = self.notebook.get_current_page()
		tab = self.notebook.get_nth_page(pageNum)
		name=tab.tab_name
		old_dir=self.sim_dir+'/'+name
		new_sim_name=dlg_get_text( "Rename the simulation to be called:", "New simulation")

		if new_sim_name!=None:
			new_dir=self.sim_dir+'/'+new_sim_name
			shutil.move(old_dir, new_dir)
			tab.rename(new_sim_name)

	def callback_delete_page(self,widget,data):
		pageNum = self.notebook.get_current_page()
		tab = self.notebook.get_nth_page(pageNum)
		name=tab.tab_name
		dir_to_del=self.sim_dir+'/'+name

		md = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION,  gtk.BUTTONS_YES_NO, "Should I remove the simulation directory "+dir_to_del)

#gtk.MessageDialog(self, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, 
		# gtk.BUTTONS_CLOSE, "Should I remove the simulation directory "+dir_to_del)
		response = md.run()

		if response == gtk.RESPONSE_YES:


			self.notebook.remove_page(pageNum)

			for items in self.tab_menu.get_children():
				if items.get_label()==name:
					self.tab_menu.remove(items)


			print "I am going to delete file",dir_to_del
			shutil.rmtree(dir_to_del)
			self.number_of_tabs=self.number_of_tabs-1
		elif response == gtk.RESPONSE_NO:
			print "Not deleting"


		md.destroy()

	def toggle_tab_visible(self,name):
		tabs_open=0
		print name
		for i in range(0, self.number_of_tabs):
			if self.rod[i].visible==True:
				tabs_open=tabs_open+1

		print "tabs open",tabs_open,self.number_of_tabs

		for i in range(0, self.number_of_tabs):
			print self.rod[i].tab_name, name, self.rod[i].visible
			if self.rod[i].tab_name==name:
				if self.rod[i].visible==False:
					self.rod[i].set_visible(True)
					self.rod[i].visible=True
				else:
					if tabs_open>1:
						print self.rod[i].tab_label
						self.rod[i].set_visible(False)
						self.rod[i].visible=False

	def callback_view_toggle(self, widget, data):
		#print "one",widget.get_label()
		self.toggle_tab_visible(widget.get_label())

	def callback_view_toggle_tab(self, widget, data):
		self.toggle_tab_visible(data)


	def add_page(self,name):
		hbox=gtk.HBox()

		hbox.set_size_request(-1, 25)
		label=gtk.Label("")
		sim_name=os.path.basename(os.path.normpath(name))
		print "Looking for",sim_name,name
		self.rod.append(scan_vbox())
		self.rod[len(self.rod)-1].init(self.myserver,self.tooltips,self.status_bar,self.context_id,self.param_list,self.exe_command,label,sim_name)
		label.set_justify(gtk.JUSTIFY_LEFT)
		hbox.pack_start(label, False, True, 0)

		button = gtk.Button()
		close_image = gtk.Image()
   		close_image.set_from_file(self.icon_theme.lookup_icon("window-close", 16, 0).get_filename())
		close_image.show()
		button.add(close_image)
		button.props.relief = gtk.RELIEF_NONE
		button.connect("clicked", self.callback_view_toggle_tab,self.rod[len(self.rod)-1].tab_name)
		button.set_size_request(25, 25)
		button.show()

		hbox.pack_end(button, False, False, 0)
		hbox.show_all()
		self.notebook.append_page(self.rod[len(self.rod)-1],hbox)

		menu_item = gtk.CheckMenuItem(sim_name)		   
		menu_item.set_active(True)
		self.tab_menu.append(menu_item)
		menu_item.show()
		menu_item.set_active(self.rod[len(self.rod)-1].visible)
		print "Rod",name,self.rod[len(self.rod)-1].visible
		menu_item.connect("activate", self.callback_view_toggle,menu_item)

		self.number_of_tabs=self.number_of_tabs+1

	def callback_last_menu_click(self, widget, data):
		print [data]

	def init(self,param_list,exe_name,exe_command,progress,gui_sim_start,gui_sim_stop,terminal):
		self.exe_name=exe_name
		self.param_list=param_list
		self.exe_command=exe_command
		print "constructur"

		self.rod=[]
		self.sim_dir=os.getcwd()+'/'
		self.tooltips = gtk.Tooltips()

		self.set_border_width(2)
		self.set_title("Parameter scan - opvdm")

		n=0

		self.number_of_tabs=0
		items=0

		self.status_bar = gtk.Statusbar()      

		self.status_bar.show()

		self.context_id = self.status_bar.get_context_id("Statusbar example")

		box=gtk.HBox()
		box.add(self.status_bar)
		box.set_child_packing(self.status_bar, True, True, 0, 0)
		self.progress = progress
		#self.progress.set_size_request(100, -1)
		self.gui_sim_start=gui_sim_start
		self.gui_sim_stop=gui_sim_stop

		box.show()


		self.menu_items = (
		    ( "/_File",         None,         None, 0, "<Branch>" ),
		    ( "/File/Close",     None, self.callback_close, 0, None ),
		    ( "/Simulations/_New",     None, self.callback_add_page, 0, "<StockItem>", "gtk-new" ),
		    ( "/Simulations/_Delete",     None, self.callback_delete_page, 0, "<StockItem>", "gtk-clear" ),
		    ( "/Simulations/_Rename",     None, self.callback_rename_page, 0, "<StockItem>", "gtk-edit" ),
		    ( "/Simulations/_Clone",     None, self.callback_copy_page, 0, "<StockItem>", "gtk-copy" ),

		    ( "/_Help",         None,         None, 0, "<LastBranch>" ),
		    ( "/_Help/Help",   None,         self.callback_help, 0, None ),
		    ( "/_Help/About",   None,         about_dialog_show, 0, "<StockItem>", "gtk-about" ),
		    )

		main_vbox = gtk.VBox(False, 3)

		menubar = self.get_main_menu(self)

		main_vbox.add(menubar)
		menubar.show()

		toolbar = gtk.Toolbar()
		toolbar.set_style(gtk.TOOLBAR_ICONS)
		toolbar.set_size_request(-1, 50)
		pos=0

		#image = gtk.Image()
		#image.set_from_file(find_data_file("gui/new-tab.png"))
		tb_new_scan = gtk.MenuToolButton(gtk.STOCK_NEW)
		tb_new_scan.connect("clicked", self.callback_add_page)
		self.tooltips.set_tip(tb_new_scan, "New simulation")

		self.tab_menu=gtk.Menu()
		tb_new_scan.set_menu(self.tab_menu)

		toolbar.insert(tb_new_scan, pos)
		pos=pos+1

		delete = gtk.ToolButton(gtk.STOCK_CLEAR)
		delete.connect("clicked", self.callback_delete_page,None)
		self.tooltips.set_tip(delete, "Delete simulation")
		toolbar.insert(delete, pos)
		pos=pos+1

		copy = gtk.ToolButton(gtk.STOCK_COPY)
		copy.connect("clicked", self.callback_copy_page,None)
		self.tooltips.set_tip(copy, "Clone simulation")
		toolbar.insert(copy, pos)
		pos=pos+1


		rename = gtk.ToolButton(gtk.STOCK_EDIT)
		rename.connect("clicked", self.callback_rename_page,None)
		self.tooltips.set_tip(rename, "Rename simulation")
		toolbar.insert(rename, pos)
		pos=pos+1

		sep = gtk.SeparatorToolItem()
		sep.set_draw(False)
		sep.set_expand(True)
		toolbar.insert(sep, pos)
		pos=pos+1

		tb_help = gtk.ToolButton(gtk.STOCK_HELP)
		tb_help.connect("clicked", self.callback_help)
		self.tooltips.set_tip(tb_help, "Help")
		toolbar.insert(tb_help, pos)
		pos=pos+1

		toolbar.show_all()
		main_vbox.add(toolbar)

		main_vbox.set_border_width(1)
		self.add(main_vbox)
		main_vbox.show()
		self.myserver=server()
		self.myserver.setup_gui(self.progress,self.gui_sim_start,self.gui_sim_stop)
		self.myserver.set_terminal(terminal)

		

		self.notebook = gtk.Notebook()
		self.notebook.show()
		self.notebook.set_tab_pos(gtk.POS_LEFT)

		sim_dirs=[]

		get_scan_dirs(sim_dirs,self.sim_dir)

		
		if len(sim_dirs)==0:
			sim_dirs.append("scan1")
		else:
			for i in range(0,len(sim_dirs)):
				sim_dirs[i]=sim_dirs[i]+"/"

		for i in range(0,len(sim_dirs)):
			self.add_page(sim_dirs[i])

		main_vbox.add(self.notebook)



		main_vbox.add(box)

		self.connect("delete-event", self.callback_close)

		self.set_icon_from_file(find_data_file("gui/image.jpg"))

		self.hide()

