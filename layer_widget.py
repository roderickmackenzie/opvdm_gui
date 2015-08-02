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
import random
import gobject
import os
from optics import find_materials
from inp import inp_write_lines_to_file
from inp import inp_load_file
from util import str2bool
from inp import inp_search_token_value
from inp import inp_update_token_value

from scan_item import scan_item_add
(
  COLUMN_THICKNES,
  COLUMN_MATERIAL,
  COLUMN_DEVICE
) = range(3)

class layer_widget(gtk.VBox):

	material_files=gtk.ListStore(str)
	active_layer=gtk.ListStore(str)
	def combo_changed(self, widget, path, text, model):
		#print model[path][1] 
		self.model[path][COLUMN_MATERIAL] = text
		self.save_model()
		self.emit("refresh")

	def sync_to_electrical_mesh(self):
		count=0
		found_layer=0
		for i in range(0,len(self.model)):
			if str2bool(self.model[i][COLUMN_DEVICE])==True:
				count=count+1
				found_layer=i

		if count==1:
			lines=[]
			if inp_load_file(lines,os.path.join(os.getcwd(),"device_epitaxy.inp"))==True:
				layers=int(inp_search_token_value(lines, "#layers"))
				mesh_layers=int(inp_search_token_value(lines, "#mesh_layers"))
				if layers==1 and mesh_layers==1:
					thickness=self.model[found_layer][COLUMN_THICKNES]
					inp_update_token_value(os.path.join(os.getcwd(),"device_epitaxy.inp"), "#layer0", thickness,1)
					inp_update_token_value(os.path.join(os.getcwd(),"device_epitaxy.inp"), "#mesh_layer_length0", thickness,1)


	def active_layer_edit(self, widget, path, text, model):
		#print model[path][1]
		#count=0
		#for i in range(0,len(self.model)):
		#	if str2bool(self.model[i][COLUMN_DEVICE])==True:
		#		count=count+1

		#If we only have one true in the list and the user wants to set it to false don't let them
		#if count==1 and str2bool(self.model[path][COLUMN_DEVICE])==True and str2bool(text)==False:
		#	md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, 
		#			gtk.BUTTONS_CLOSE, "You must assign at least one layer to be the active layer")
		#	md.run()
		#	md.destroy()
		#	return

		#print len(self.model[path])

		for i in range(0,len(self.model)):
			self.model[i][COLUMN_DEVICE]="False"

		self.model[path][COLUMN_DEVICE] = "True"
		self.save_model()
		self.emit("refresh")



	def rebuild_mat_list(self):
		self.material_files.clear()
		self.active_layer.clear()
		mat=find_materials()
		print mat
		for i in range(0,len(mat)):
			self.material_files.append([mat[i]])

		self.active_layer.append(["True"])
		#self.active_layer.append(["False"])
		#for i in range(0,len(self.liststore_combobox)):
		#	if self.liststore_combobox[i][0]!="Select parameter":
		#		self.material_files.append([self.liststore_combobox[i][0]])

	def callback_move_down(self, widget, data=None):

		selection = self.treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
 			model.move_after( iter,model.iter_next(iter))
			self.save_model()
			self.emit("refresh")

	def __init__(self,tooltips):
		self.frame=gtk.Frame()

		self.__gobject_init__()

		add_button = gtk.Button("Add layer",gtk.STOCK_ADD)
		add_button.show()

		delete_button = gtk.Button("Delete layer",gtk.STOCK_DELETE)
		delete_button.show()

		# create tree view
		self.model = self.__create_model()

		self.treeview = gtk.TreeView(self.model)
		self.treeview.set_size_request(300, 150)
		self.treeview.set_rules_hint(True)
		self.treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)

		toolbar = gtk.Toolbar()
		toolbar.set_style(gtk.TOOLBAR_ICONS)
		toolbar.set_size_request(-1, 50)
		pos=0

		add = gtk.ToolButton(gtk.STOCK_ADD)
		add.connect("clicked", self.on_add_item_clicked)
		tooltips.set_tip(add, "Add device layer")
		toolbar.insert(add, pos)
		pos=pos+1


		remove = gtk.ToolButton(gtk.STOCK_CLEAR)
		remove.connect("clicked", self.on_remove_item_clicked)
		tooltips.set_tip(remove, "Delete device layer")
		toolbar.insert(remove, pos)
		pos=pos+1

		move = gtk.ToolButton(gtk.STOCK_GO_DOWN)
		move.connect("clicked", self.callback_move_down)
		tooltips.set_tip(move, "Move device layer")
		toolbar.insert(move, pos)
		pos=pos+1


		hbox0=gtk.HBox()

		self.frame.set_label("Device layers")
		self.frame.set_label_align(0.0, 0.0)
		self.frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		hbox0.show()

		self.pack_start(toolbar, False, False, 0)
		self.frame.add(self.treeview)
		self.pack_start(self.frame, True, True, 0)

		self.__add_columns(self.treeview)


		self.show_all()


        

	def __create_model(self):

		# create list store
		model = gtk.ListStore(str,str,str,bool)

		# add items

		self.rebuild_mat_list()
		lines=[]
		inp_load_file(lines,os.path.join(os.getcwd(),"optics_epitaxy.inp"))

		pos=0
		pos=pos+1
		items=int(lines[pos])

		self.edit_list=[]
		self.line_number=[]

		layer=0

		for i in range(0, items):
			pos=pos+1
			#label=lines[pos]	#read label

			pos=pos+1
			thick=float(lines[pos])

			pos=pos+1
			material=lines[pos]

			pos=pos+1
			device=lines[pos] 	#value

			scan_item_add("optics_epitaxy.inp","#layer"+str(layer),"Material for "+str(material),2)
			scan_item_add("optics_epitaxy.inp","#layer"+str(layer),"Layer width "+str(material),1)
			layer=layer+1

			iter = model.append()

			model.set (iter,
			  COLUMN_THICKNES, str(thick),
			  COLUMN_MATERIAL, str(material),
			  COLUMN_DEVICE, str(bool(int(device)))
			)
		return model

	def on_remove_item_clicked(self, button):

		selection = self.treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
			model.remove(iter)

			self.save_model()
			self.emit("refresh")



	def __add_columns(self, treeview):

		model = treeview.get_model()


		# Thicknes
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", COLUMN_THICKNES)
		renderer.set_property("editable", True)
		column = gtk.TreeViewColumn("Thicknes", renderer, text=COLUMN_THICKNES,editable=True)
		treeview.append_column(column)

		# Material file
		column = gtk.TreeViewColumn("Material")
		cellrenderer_combo = gtk.CellRendererCombo()
		cellrenderer_combo.set_property("editable", True)
		cellrenderer_combo.set_property("model", self.material_files)
		cellrenderer_combo.set_property("text-column", 0)
		cellrenderer_combo.connect("edited", self.combo_changed, self.material_files)
		column.pack_start(cellrenderer_combo, False)
		column.add_attribute(cellrenderer_combo, "text", COLUMN_MATERIAL)
		treeview.append_column(column)

		# Device
		#renderer = gtk.CellRendererText()
		#renderer.connect("edited", self.on_cell_edited, model)
		#renderer.set_data("column", COLUMN_DEVICE)
		#renderer.set_property("editable", True)
		#column = gtk.TreeViewColumn("Active layer", renderer, text=COLUMN_DEVICE,editable=True)

		column = gtk.TreeViewColumn("Active layer")
		render = gtk.CellRendererCombo()
		render.set_property("editable", True)
		render.set_property("model", self.active_layer)
		render.set_property("text-column", 0)
		render.connect("edited", self.active_layer_edit, self.active_layer)
		column.pack_start(render, False)
		column.add_attribute(render, "text", COLUMN_DEVICE)
		treeview.append_column(column)


	def on_cell_edited(self, cell, path_string, new_text, model):

		iter = model.get_iter_from_string(path_string)
		path = model.get_path(iter)[0]
		column = cell.get_data("column")

		model.set(iter, column, new_text)

		self.save_model()
		self.emit("refresh")


	def on_add_item_clicked(self, button):
		new_item = ["100e-9", "pcbm","0","1",False]

		selection = self.treeview.get_selection()
		model, iter = selection.get_selected()

		path = model.get_path(iter)[0]

		iter = model.insert(path)
		model.set (iter,
		    COLUMN_THICKNES, new_item[COLUMN_THICKNES],
		    COLUMN_MATERIAL, new_item[COLUMN_MATERIAL],
		    COLUMN_DEVICE, new_item[COLUMN_DEVICE]
		)
		self.save_model()
		self.emit("refresh")

	def save_model(self):
		lines=[]
		lines.append("#layers")
		lines.append(str(len(self.model)))

		layer=0
		for item in self.model:
			lines.append("#layer"+str(layer))
			lines.append(item[COLUMN_THICKNES])
			lines.append(item[COLUMN_MATERIAL])
			out=int(str2bool(item[COLUMN_DEVICE]))
			lines.append(str(out))
			layer=layer+1
		lines.append("#ver")			
		lines.append("1.11")			
		lines.append("#end")
		
		inp_write_lines_to_file(os.path.join(os.getcwd(),"optics_epitaxy.inp"),lines)
		self.sync_to_electrical_mesh()

gobject.type_register(layer_widget)
gobject.signal_new("refresh", layer_widget, gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE, ())

