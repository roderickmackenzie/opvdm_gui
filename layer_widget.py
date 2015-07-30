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

from scan_item import scan_item_add
(
  COLUMN_LAYER,
  COLUMN_THICKNES,
  COLUMN_MATERIAL,
  COLUMN_DEVICE,
  COLUMN_EDITABLE
) = range(5)

class layer_widget(gtk.Frame):

	articles = []

	def load(self):
		f = open("optics_epitaxy.inp")
		self.lines = f.readlines()
		f.close()

		for i in range(0, len(self.lines)):
			self.lines[i]=self.lines[i].rstrip()

		pos=0
		pos=pos+1
		items=int(self.lines[pos])

		self.edit_list=[]
		self.line_number=[]

		layer=0

		for i in range(0, items):
			pos=pos+1
			label=self.lines[pos]	#read label

			pos=pos+1
			thick=float(self.lines[pos])

			pos=pos+1
			material=self.lines[pos]

			pos=pos+1
			device=self.lines[pos] 	#value

			self.articles.append([ label, str(thick),str(material),str(device), True ])
			scan_item_add("optics_epitaxy.inp",label,"Material for "+label,2)
			scan_item_add("optics_epitaxy.inp",label,"Layer width "+label,1)
			layer=layer+1

	def __init__(self):
		self.__gobject_init__()

		self.load()

		add_button = gtk.Button("Add layer",gtk.STOCK_ADD)
		add_button.show()

		delete_button = gtk.Button("Delete layer",gtk.STOCK_DELETE)
		delete_button.show()

		# create tree view
		model = self.__create_model()

		treeview = gtk.TreeView(model)
		treeview.set_size_request(300, 150)
		treeview.set_rules_hint(True)
		treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)

		hbox = gtk.HBox(False, 5)

		hbox.pack_start(add_button, False, False, 0)
		hbox.pack_start(delete_button, False, False, 0)
		hbox.show()

		hbox0=gtk.HBox()
		frame_vbox=gtk.VBox()
		self.set_label("Device layers")
		self.set_label_align(0.0, 0.0)
		self.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		hbox0.show()
		frame_vbox.pack_start(treeview, False, False, 0)
		frame_vbox.pack_start(hbox, False, False, 0)
		self.add(frame_vbox)

		add_button.connect("clicked", self.on_add_item_clicked, treeview)
		delete_button.connect("clicked", self.on_remove_item_clicked, treeview)


		self.__add_columns(treeview)


		self.show_all()


        

	def __create_model(self):

		# create list store
		model = gtk.ListStore(str,str,str,str,bool)

		# add items

		for item in self.articles:
			iter = model.append()

			model.set (iter,
			  COLUMN_LAYER, item[COLUMN_LAYER],
			  COLUMN_THICKNES, item[COLUMN_THICKNES],
			  COLUMN_MATERIAL, item[COLUMN_MATERIAL],
			  COLUMN_DEVICE, item[COLUMN_DEVICE],
			  COLUMN_EDITABLE, item[COLUMN_EDITABLE]
			)
		return model

	def on_remove_item_clicked(self, button, treeview):

		selection = treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
			model.remove(iter)

			del self.articles[ path ]

			self.save_model(model)
			#self.update_graph(model)



	def __add_columns(self, treeview):

		model = treeview.get_model()

		# Layer tag
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", COLUMN_LAYER)

		column = gtk.TreeViewColumn("Layer", renderer, text=COLUMN_LAYER,
				       editable=COLUMN_EDITABLE)
		treeview.append_column(column)

		# Thicknes
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", COLUMN_THICKNES)

		column = gtk.TreeViewColumn("Thicknes", renderer, text=COLUMN_THICKNES,
				       editable=COLUMN_EDITABLE)
		treeview.append_column(column)

		# Material file
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", COLUMN_MATERIAL)

		column = gtk.TreeViewColumn("Material", renderer, text=COLUMN_MATERIAL,
				       editable=COLUMN_EDITABLE)
		treeview.append_column(column)

		# Device
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", COLUMN_DEVICE)

		column = gtk.TreeViewColumn("Active layer", renderer, text=COLUMN_DEVICE,
				       editable=COLUMN_EDITABLE)
		treeview.append_column(column)


	def on_cell_edited(self, cell, path_string, new_text, model):

		iter = model.get_iter_from_string(path_string)
		path = model.get_path(iter)[0]
		column = cell.get_data("column")

		if column == COLUMN_LAYER:
			self.articles[path][COLUMN_LAYER] = new_text

			model.set(iter, column, self.articles[path][COLUMN_LAYER])

		if column == COLUMN_THICKNES:
			#old_text = model.get_value(iter, column)
			self.articles[path][COLUMN_THICKNES] = new_text
			model.set(iter, column, self.articles[path][COLUMN_THICKNES])

		if column == COLUMN_MATERIAL:
			#old_text = model.get_value(iter, column)
			self.articles[path][COLUMN_MATERIAL] = new_text

			model.set(iter, column, self.articles[path][COLUMN_MATERIAL])

		if column == COLUMN_DEVICE:
			#old_text = model.get_value(iter, column)
			self.articles[path][COLUMN_DEVICE] = new_text

			model.set(iter, column, self.articles[path][COLUMN_DEVICE])
		self.emit("refresh")

		self.save_model(model)


	def on_add_item_clicked(self, button, treeview):
		new_item = ["#mat", "100e-9", "pcbm","0","1",True]

		selection = treeview.get_selection()
		model, iter = selection.get_selected()

		path = model.get_path(iter)[0]
		#model.remove(iter)

		#del articles[ path ]

		self.articles.insert(path, new_item) #append(new_item)

		iter = model.insert(path) #append()
		model.set (iter,
		    COLUMN_LAYER, new_item[COLUMN_LAYER],
		    COLUMN_THICKNES, new_item[COLUMN_THICKNES],
		    COLUMN_MATERIAL, new_item[COLUMN_MATERIAL],
		    COLUMN_DEVICE, new_item[COLUMN_DEVICE],
		    COLUMN_EDITABLE, new_item[COLUMN_EDITABLE]
		)
		self.save_model(model)
		#self.update_graph(model)

	def save_model(self, model):
		a = open("optics_epitaxy.inp", "w")
		a.write("#layers\n")
		a.write(str(len(model))+"\n")


		for item in model:
			a.write(item[COLUMN_LAYER]+"\n")
			a.write(item[COLUMN_THICKNES]+"\n")
			a.write(item[COLUMN_MATERIAL]+"\n")
			a.write(item[COLUMN_DEVICE]+"\n")

		a.write("#ver\n")			
		a.write("1.11\n")			
		a.write("#end\n")			
		a.close()

gobject.type_register(layer_widget)
gobject.signal_new("refresh", layer_widget, gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE, ())

