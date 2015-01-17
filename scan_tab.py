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
import gc
import gtk
import sys
import os
import shutil
from inp import inp_update_token_value
from inp import inp_get_token_value
from search import return_file_list
from plot import plot_data
from plot import plot_info
from plot import check_info_file
from util import find_data_file
from about import about_dialog_show
from used_files_menu import used_files_menu
from server import server
from plot_dlg import plot_dlg_class
from plot_gen import plot_gen
from plot_state import plot_state
import threading
import gobject
#import pyinotify
import multiprocessing
import time
from util import get_cache_path
from cmp_class import cmp_class
from scan_select import select_param
from config import config
import hashlib
from os.path import expanduser
from token_lib import tokens
from util import delete_link_tree
from scan_item import scan_items_get_list
from win_lin import running_on_linux
from scan_tree import tree_gen
from scan_tree import tree_load_program
from scan_item import scan_item_save
from scan_plot import scan_gen_plot_data
class scan_vbox(gtk.VBox):

	icon_theme = gtk.icon_theme_get_default()

	def rename(self,new_name):
		self.sim_name=os.path.basename(new_name)
		self.sim_dir=new_name
		self.status_bar.push(self.context_id, self.sim_dir)
		self.set_tab_caption(self.sim_name)
		#self.tab_label.set_text(os.path.basename(new_name))
		self.reload_liststore()
		self.plotted_graphs.init(self.sim_dir,self.callback_last_menu_click)
		

	def callback_move_down(self, widget, data=None):

		selection = self.treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
 			self.liststore_combobox.move_after( iter,self.liststore_combobox.iter_next(iter))
			#self.liststore_combobox.swap(path+1,path)
	def add_line(self,data):
		selection = self.treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
			self.liststore_combobox.insert(path+1,data)
		else:
			self.liststore_combobox.append(data)
		self.save_combo()
		self.rebuild_liststore_op_type()

	def callback_add_item(self, widget, data=None):
		self.add_line(["Select parameter", "0.0 0.0", "scan"])
		

	def callback_copy_item(self, widget, data=None):
		selection = self.treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			build=model[0][0]+"\n"+model[0][1]+"\n"+model[0][2]
			self.clipboard.set_text(build, -1)

	def callback_paste_item(self, widget, data=None):
		selection = self.treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			text = self.clipboard.wait_for_text()
			if text != None:
				array=text.rstrip().split('\n')
				self.add_line(array)
				#build=model[0][0]+"\n"+model[0][1]+"\n"+model[0][2]
				#self.clipboard.set_text(build, -1)
	def callback_show_list(self, widget, data=None):
		self.select_param_window.select_window.show()

	def callback_delete_item(self, widget, data=None):
		#self.liststore_combobox.append(["Television", "Samsung"])

		selection = self.treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
			model.remove(iter)
			self.save_combo()

		self.rebuild_liststore_op_type()

	def plot_results(self,plot_tokens):
		plot_files, plot_labels, save_file = scan_gen_plot_data(plot_tokens,self.sim_dir)
		units=self.get_units()
		plot_gen(plot_files,plot_labels,plot_tokens,save_file,units)
		self.plot_open.set_sensitive(True)

		self.last_plot_data=plot_tokens

		return 

	def get_units(self):
		token=""
		for i in range(0,len(self.liststore_combobox)):
			if self.liststore_combobox[i][2]=="scan":
				for ii in range(0,len(self.param_list)):
					if self.liststore_combobox[i][0]==self.param_list[ii].name:
						token=self.param_list[ii].token
				break
		if token!="":
			found_token=self.tokens.find(token)
			if type(found_token)!=bool:
				return found_token.units

		return ""



	def make_sim_dir(self):
		if os.path.isdir(self.sim_dir)==False:
			os.makedirs(self.sim_dir)


	def stop_simulation(self):
		self.myserver.killall()



	def delete_simulations(self,dirs_to_del):
		for i in range(0, len(dirs_to_del)):
			delete_link_tree(dirs_to_del[i])

	def list_simulations(self,dirs_to_del):
		ls=os.listdir(self.sim_dir)
		print ls
		for i in range(0, len(ls)):
			full_name=os.path.join(self.sim_dir,ls[i])
			if os.path.isdir(full_name):
				if os.path.isfile(os.path.join(full_name,'scan.inp')):
					dirs_to_del.append(full_name)

	def simulate(self):

		base_dir=os.getcwd()
		run=True

		if len(self.liststore_combobox) == 0:
			message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
			message.set_markup("You have not selected any parameters to scan through.  Use the add button.")
			message.run()
			message.destroy()
			return


		if self.sim_name=="":
			message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
			message.set_markup("No sim dir name")
			message.run()
			message.destroy()
			return

		self.make_sim_dir()
		dirs_to_del=[]
		self.list_simulations(dirs_to_del)

		if (len(dirs_to_del)!=0):

			settings = gtk.settings_get_default()
			settings.set_property('gtk-alternative-button-order', True)

			dialog = gtk.Dialog()
			cancel_button = dialog.add_button(gtk.STOCK_YES, gtk.RESPONSE_YES)

			ok_button = dialog.add_button(gtk.STOCK_NO, gtk.RESPONSE_NO)
			ok_button.grab_default()

			help_button = dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)

			label = gtk.Label("Should I delete the old simualtions first?:\n"+"\n".join(dirs_to_del))
			dialog.vbox.pack_start(label, True, True, 0)
			label.show()

			dialog.set_alternative_button_order([gtk.RESPONSE_YES, gtk.RESPONSE_NO,
						       gtk.RESPONSE_CANCEL])

			#dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION,  gtk.BUTTONS_YES_NO, str("Should I delete the old simualtions first?:\n"+"\n".join(dirs_to_del)))
			response = dialog.run()
			
			if response == gtk.RESPONSE_YES:
					self.delete_simulations(dirs_to_del)
			elif response == gtk.RESPONSE_NO:
				print "Not deleting"
			elif response == gtk.RESPONSE_CANCEL:
				run=False
				print "Cancel"

			dialog.destroy()


		for i in range(0,len(self.liststore_combobox)):
			found=False
			for ii in range(0,len(self.liststore_op_type)):
				if self.liststore_combobox[i][2]==self.liststore_op_type[ii][0]:
					found=True
			if found==False:
				run=False

				md = gtk.MessageDialog(None, 
				0, gtk.MESSAGE_ERROR, 
				gtk.BUTTONS_CLOSE, self.liststore_combobox[i][2]+"Not valid")
				md.run()
				md.destroy()
				break



		if run==True:
			program_list=[]
			for i in range(0,len(self.liststore_combobox)):
				program_list.append([self.liststore_combobox[i][0],self.liststore_combobox[i][1],self.liststore_combobox[i][2]])
			print "Feeding,",base_dir,self.sim_dir
			commands=tree_gen(program_list,base_dir,self.sim_dir)

			self.myserver.init(self.sim_dir)

			if self.myserver.start_threads()==0:
				self.myserver.clear_cache()
				for i in range(0, len(commands)):
					self.myserver.add_job(commands[i])
					print "Adding job"+commands[i]

				self.myserver.start(self.exe_command)


			else:
				message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
				message.set_markup("I can't connect to the server")
				message.run()
				message.destroy()

		self.save_combo()
		os.chdir(base_dir)
		gc.collect()

	def callback_plot_results(self, widget, data=None):
		self.plot_results(self.last_plot_data)

	def callback_last_menu_click(self, widget, data):
		self.plot_results(data)

	def callback_reopen_xy_window(self, widget, data=None):

		if len(self.plotted_graphs)>0:
			pos=len(self.plotted_graphs)-1
			plot_data=plot_state()
			plot_data.file0=self.plotted_graphs[pos].file0
			plot_xy_window=plot_dlg_class(gtk.WINDOW_TOPLEVEL)
			plot_xy_window.my_init(plot_data)
			plot_now=plot_xy_window.my_run(plot_data)

			if plot_now==True:
				self.plot_results(plot_data)
				self.plotted_graphs.refresh()

	def callback_gen_plot_command(self, widget, data=None):
		dialog = gtk.FileChooserDialog("File to plot",
               None,
               gtk.FILE_CHOOSER_ACTION_OPEN,
               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		dialog.set_current_folder(self.sim_dir)
		filter = gtk.FileFilter()
		filter.set_name("Data files")
		filter.add_pattern("*.dat")
		dialog.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name("Input files")
		filter.add_pattern("*.inp")
		dialog.add_filter(filter)

		dialog.set_action(gtk.FILE_CHOOSER_ACTION_OPEN)


		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			full_file_name=dialog.get_filename()
			dialog.destroy()
			#print cur_dir=os.getcwd()
			#print full_file_name
			file_name=os.path.basename(full_file_name)

			plot_data=plot_state()
			plot_data.path=self.sim_dir
			plot_data.example_file0=full_file_name
			plot_data.example_file1=full_file_name

			plot_now=False
			if check_info_file(file_name)==True:
				plot_data.file0=file_name
				plot_xy_window=plot_dlg_class(gtk.WINDOW_TOPLEVEL)
				plot_xy_window.my_init(plot_data)
				plot_now=plot_xy_window.my_run(plot_data)
			else:
				plot_data.file0=file_name
				plot_data.tag0=""
				plot_data.file1=""
				plot_data.tag1=""
				plot_now=True

			if plot_now==True:
				self.plot_results(plot_data)

				self.plotted_graphs.refresh()

		else:
			print 'Closed, no files selected'
			dialog.destroy()

	def save_combo(self):
		self.make_sim_dir()
		a = open(os.path.join(self.sim_dir,"opvdm_gui_config.inp"), "w")
		a.write(str(len(self.liststore_combobox))+"\n")


		for item in self.liststore_combobox:
			a.write(item[0]+"\n")
			a.write(item[1]+"\n")
			a.write(item[2]+"\n")	
		
		a.close()

		scan_item_save(os.path.join(self.sim_dir,"scan_items.inp"))

	def combo_changed(self, widget, path, text, model):
		model[path][0] = text
		self.rebuild_liststore_op_type()
		self.save_combo()

	def combo_mirror_changed(self, widget, path, text, model):
		model[path][2] = text
		if model[path][2]!="constant":
			if model[path][2]!="scan":
				model[path][1] = "mirror"
		self.save_combo()


	def text_changed(self, widget, path, text, model):
		model[path][1] = text
		self.save_combo()


	def reload_liststore(self):
		self.liststore_combobox.clear()
		tree_load_program(self.liststore_combobox,self.sim_dir)



	def on_treeview_button_press_event(self, treeview, event):
		if event.type == gtk.gdk.BUTTON_PRESS and event.button == 3:
			self.popup_menu.popup(None, None, None, event.button, event.time)
			pass

	def callback_close(self,widget):
		self.hide()

	def rebuild_liststore_op_type(self):
		self.liststore_op_type.clear()
		self.liststore_op_type.append(["scan"])
		self.liststore_op_type.append(["constant"])

		for i in range(0,len(self.liststore_combobox)):
			if self.liststore_combobox[i][0]!="Select parameter":
				self.liststore_op_type.append([self.liststore_combobox[i][0]])
	def set_tab_caption(self,name):
		mytext=name
		if len(mytext)<10:
			for i in range(len(mytext),10):
				mytext=mytext+" "
		self.tab_label.set_text(mytext)

	def set_visible(self,value):
		if value==True:
			self.visible=True
			self.config.set_value("#visible",True)
			self.show()
		else:
			self.visible=False
			self.config.set_value("#visible",False)
			self.hide()

	def callback_run_simulation(self,widget):
		self.simulate()

	def callback_stop_simulation(self,widget):
		self.stop_simulation()

	def callback_examine(self, widget, data=None):
		mycmp=cmp_class()
		ret=mycmp.init(self.sim_dir,self.exe_command)
		if ret==False:
			md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,  gtk.BUTTONS_CLOSE, "Re-run the simulation with 'dump all slices' set to one to use this tool.")
        		md.run()
        		md.destroy()
			return

	def init(self,myserver,tooltips,status_bar,context_id,exe_command,tab_label,scan_root_dir,sim_name):

		self.tokens=tokens()
		self.config=config()
		self.sim_name=sim_name
		self.clipboard = gtk.clipboard_get(gtk.gdk.SELECTION_CLIPBOARD)
		self.popup_menu = gtk.Menu()
		menu_item = gtk.MenuItem("Copy")
		menu_item.connect("activate", self.callback_copy_item)
		self.popup_menu.append(menu_item)

		menu_item = gtk.MenuItem("Paste")
		menu_item.connect("activate", self.callback_paste_item)
		self.popup_menu.append(menu_item)

		menu_item = gtk.MenuItem("Delete")
		menu_item.connect("activate", self.callback_delete_item)
		self.popup_menu.append(menu_item)
		self.popup_menu.show_all()

		self.myserver=myserver
		self.tooltips=tooltips
		self.status_bar=status_bar
		self.context_id=context_id
		self.param_list=scan_items_get_list()
		self.exe_command=exe_command
		self.tab_label=tab_label
		self.liststore_op_type = gtk.ListStore(str)


		self.sim_dir=os.path.join(scan_root_dir,sim_name)
		self.tab_name=os.path.basename(os.path.normpath(self.sim_dir))

		self.status_bar.push(self.context_id, self.sim_dir)
		self.set_tab_caption(self.tab_name)

		toolbar = gtk.Toolbar()
		toolbar.set_style(gtk.TOOLBAR_ICONS)
		toolbar.set_size_request(-1, 50)
		pos=0

		image = gtk.Image()
		image.set_from_file(find_data_file("gui/forward.png"))
		tb_simulate = gtk.ToolButton(image)
		tb_simulate.connect("clicked", self.callback_run_simulation)
		self.tooltips.set_tip(tb_simulate, "Run simulation")
		toolbar.insert(tb_simulate, pos)
		pos=pos+1

	        image = gtk.Image()
   		image.set_from_file(find_data_file("gui/pause.png"))
		self.stop = gtk.ToolButton(image)
		self.tooltips.set_tip(self.stop, "Stop the simulation")
		self.stop.connect("clicked", self.callback_stop_simulation)
		toolbar.insert(self.stop, pos)
		pos=pos+1

		sep = gtk.SeparatorToolItem()
		sep.set_draw(True)
		sep.set_expand(False)
		toolbar.insert(sep, pos)
		pos=pos+1

		image = gtk.Image()
		image.set_from_file(find_data_file("gui/plot.png"))
		plot_select = gtk.MenuToolButton(image,"hello")
		plot_select.connect("clicked", self.callback_gen_plot_command)
		self.tooltips.set_tip(plot_select, "Find a file to plot")

		self.plotted_graphs = used_files_menu()
		self.plotted_graphs.init(self.sim_dir,self.callback_last_menu_click)
		plot_select.set_menu(self.plotted_graphs.menu)
		toolbar.insert(plot_select, pos)

		pos=pos+1

	        image = gtk.Image()
   		image.set_from_file(self.icon_theme.lookup_icon("view-refresh", 32, 0).get_filename())
		self.plot_open = gtk.ToolButton(image)
		self.plot_open.connect("clicked", self.callback_plot_results)
		self.plot_open.set_sensitive(False)
		self.tooltips.set_tip(self.plot_open, "Replot the graph")
		toolbar.insert(self.plot_open, pos)
		pos=pos+1

	        image = gtk.Image()
   		image.set_from_file(find_data_file("gui/plot_time.png"))
		self.examine = gtk.ToolButton(image)
		self.tooltips.set_tip(self.examine, "Examine results in time domain")
		self.examine.connect("clicked", self.callback_examine)
		toolbar.insert(self.examine, pos)
		pos=pos+1

		sep = gtk.SeparatorToolItem()
		sep.set_draw(True)
		sep.set_expand(False)
		toolbar.insert(sep, pos)
		pos=pos+1

		add = gtk.ToolButton(gtk.STOCK_ADD)
		add.connect("clicked", self.callback_add_item)
		self.tooltips.set_tip(add, "Add parameter to scan")
		toolbar.insert(add, pos)
		pos=pos+1


		remove = gtk.ToolButton(gtk.STOCK_CLEAR)
		remove.connect("clicked", self.callback_delete_item)
		self.tooltips.set_tip(remove, "Delete item")
		toolbar.insert(remove, pos)
		pos=pos+1

		move = gtk.ToolButton(gtk.STOCK_GO_DOWN)
		move.connect("clicked", self.callback_move_down)
		self.tooltips.set_tip(move, "Move down")
		toolbar.insert(move, pos)
		pos=pos+1

		sep = gtk.SeparatorToolItem()
		sep.set_draw(True)
		sep.set_expand(False)
		toolbar.insert(sep, pos)
		pos=pos+1

		quick = gtk.ToolButton(gtk.STOCK_INDEX)
		quick.connect("clicked", self.callback_show_list)
		self.tooltips.set_tip(quick, "Show quick selector")
		toolbar.insert(quick, pos)
		pos=pos+1

		#reopen_xy = gtk.ToolButton(gtk.STOCK_SELECT_COLOR)
		#reopen_xy.connect("clicked", self.callback_reopen_xy_window)
		#self.tooltips.set_tip(reopen_xy, "Reopen xy window selector")
		#toolbar.insert(reopen_xy, pos)
		#pos=pos+1

		toolbar.show_all()
		self.pack_start(toolbar, False, False, 0)#.add()

		liststore_manufacturers = gtk.ListStore(str)
		for i in range(0,len(self.param_list)):
		    liststore_manufacturers.append([self.param_list[i].name])

		self.liststore_combobox = gtk.ListStore(str, str, str)

		self.config.load(self.sim_dir)
		self.visible=self.config.get_value("#visible",True)
		self.reload_liststore()


		self.treeview = gtk.TreeView(self.liststore_combobox)
		self.treeview.connect("button-press-event", self.on_treeview_button_press_event)


		self.select_param_window=select_param()
		self.select_param_window.init(self.liststore_combobox,self.treeview)

		column_text = gtk.TreeViewColumn("Values")
		column_combo = gtk.TreeViewColumn("Parameter to change")
		column_mirror = gtk.TreeViewColumn("Opperation")
		self.treeview.append_column(column_combo)
		self.treeview.append_column(column_text)
		self.treeview.append_column(column_mirror)

		cellrenderer_combo = gtk.CellRendererCombo()
		cellrenderer_combo.set_property("editable", True)
		cellrenderer_combo.set_property("model", liststore_manufacturers)
		cellrenderer_combo.set_property("text-column", 0)
		cellrenderer_combo.connect("edited", self.combo_changed, self.liststore_combobox)

		column_combo.pack_start(cellrenderer_combo, False)
		column_combo.set_min_width(240)
		column_combo.add_attribute(cellrenderer_combo, "text", 0)

		cellrenderer_mirror = gtk.CellRendererCombo()
		cellrenderer_mirror.set_property("editable", True)
		self.rebuild_liststore_op_type()
		cellrenderer_mirror.set_property("model", self.liststore_op_type)
		cellrenderer_mirror.set_property("text-column", 0)
		cellrenderer_mirror.connect("edited", self.combo_mirror_changed, self.liststore_combobox)

		column_mirror.pack_start(cellrenderer_mirror, False)
		column_mirror.set_min_width(240)
		column_mirror.add_attribute(cellrenderer_mirror, "text", 2)

		cellrenderer_text = gtk.CellRendererText()
		cellrenderer_text.set_property("editable", True)
		cellrenderer_text.connect("edited", self.text_changed, self.liststore_combobox)
		cellrenderer_text.props.wrap_width = 400
		cellrenderer_text.props.wrap_mode = gtk.WRAP_WORD
		column_text.pack_start(cellrenderer_text, False)
		column_text.set_min_width(240)
		column_text.add_attribute(cellrenderer_text, "text", 1)



		#window.connect("destroy", lambda w: gtk.main_quit())
		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
		scrolled_window.add(self.treeview)
		scrolled_window.set_size_request(1000, 500)
		#scrolled_window.set_min_content_height(200)

		self.pack_start(scrolled_window, True, True, 0)
		self.treeview.show()
		self.show_all()

		if self.visible==False:
			self.hide()

