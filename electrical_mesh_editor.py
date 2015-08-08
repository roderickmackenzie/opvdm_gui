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
import os
import shutil
import gobject
from inp import inp_write_lines_to_file
from inp import inp_load_file
from debug import debug_mode
from scan_item import scan_item_add

(
  COLUMN_LAYER,
  COLUMN_THICKNES
) = range(2)

(
  MESH_THICKNES,
  MESH_POINTS
) = range(2)


class electrical_mesh_editor(gtk.VBox):

	def __add_columns(self, treeview):

		model = treeview.get_model()

		# Layer tag
		render = gtk.CellRendererText()
		render.connect("edited", self.on_cell_edited, model)
		render.set_data("column", COLUMN_LAYER)
		render.set_property("editable", True)

		column = gtk.TreeViewColumn("Layer", render, text=COLUMN_LAYER,editable=True)
		treeview.append_column(column)

		# Thicknes
		render = gtk.CellRendererText()
		render.connect("edited", self.on_cell_edited, model)
		render.set_data("column", COLUMN_THICKNES)
		render.set_property("editable", True)

		column = gtk.TreeViewColumn("Thicknes", render, text=COLUMN_THICKNES,editable=True)

		treeview.append_column(column)


	def __add_columns_mesh(self, treeview):

		model = treeview.get_model()

		# Thicknes
		render = gtk.CellRendererText()
		render.connect("edited", self.on_mesh_edited, model)
		render.set_data("column", MESH_THICKNES)
		render.set_property("editable", True)

		column = gtk.TreeViewColumn("Thicknes", render, text=MESH_THICKNES, editable=True)
		if debug_mode()==False:
			column.set_visible(False)
		treeview.append_column(column)


		# Thicknes
		render = gtk.CellRendererText()
		render.connect("edited", self.on_mesh_edited, model)
		render.set_data("column", MESH_POINTS)
		render.set_property("editable", True)

		column = gtk.TreeViewColumn("Points", render, text=MESH_POINTS, editable=True)
		treeview.append_column(column)

	def on_add_item_clicked(self, button, model):
		new_item = ["#layerN","0e-9"]

		iter = model.append()
		model.set (iter,
		    COLUMN_LAYER, new_item[COLUMN_LAYER],
		    COLUMN_THICKNES, new_item[COLUMN_THICKNES]
		)

	def on_add_mesh_clicked(self, button, model):
		new_item = ["0e-9","0" ]

		iter = model.append()
		model.set (iter,
		    MESH_THICKNES, new_item[MESH_THICKNES],
		    MESH_POINTS, new_item[MESH_POINTS]
		)

	def save_model(self):
		lines=[]
		lines.append("#layers")
		lines.append(str(len(self.layer_model)))


		for item in self.layer_model:
			lines.append(item[COLUMN_LAYER])
			lines.append(item[COLUMN_THICKNES])
		lines.append("#mesh_layers")
		lines.append(str(len(self.mesh_model)))
		i=0
		for item in self.mesh_model:
			lines.append("#mesh_layer_length"+str(i))
			lines.append(item[MESH_THICKNES])
			lines.append("#mesh_layer_points"+str(i))
			lines.append(item[MESH_POINTS])
			i=i+1
		lines.append("#ver")			
		lines.append("1.1")			
		lines.append("#end")			
		inp_write_lines_to_file(os.path.join(os.getcwd(),"device_epitaxy.inp"),lines)

	def on_remove_item_clicked(self, button, treeview):

		selection = treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
			model.remove(iter)


		self.save_model()

	def on_remove_from_mesh_click(self, button, treeview):

		selection = treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
			model.remove(iter)

		self.save_model()


	def on_cell_edited(self, cell, path_string, new_text, model):

		iter = model.get_iter_from_string(path_string)
		path = model.get_path(iter)[0]
		column = cell.get_data("column")

		if column == COLUMN_LAYER:
			model.set(iter, column, new_text)

		if column == COLUMN_THICKNES:
			#old_text = model.get_value(iter, column)

			model.set(iter, column, new_text)

		self.save_model()
		self.set_data("refresh",float(new_text))
		self.emit("refresh")

	def on_mesh_edited(self, cell, path_string, new_text, model):

		iter = model.get_iter_from_string(path_string)
		path = model.get_path(iter)[0]
		column = cell.get_data("column")
		print "update=",new_text,column

		if column == MESH_THICKNES:
			self.mesh_model.set(iter, column, new_text)

		if column == MESH_POINTS:
			self.mesh_model.set(iter, column, new_text)

		self.save_model()
		#self.emit("refresh")

	def refresh(self):
		self.load()

	def load(self):
		self.layer_model.clear()
		self.mesh_model.clear()
		lines=[]
		pos=0
		if inp_load_file(lines,os.path.join(os.getcwd(),"device_epitaxy.inp"))==True:
			pos=pos+1	#first comment
			layers=int(lines[pos])

			for i in range(0, layers):
				pos=pos+1
				token=lines[pos]	#read label

				pos=pos+1
				layer_ticknes=lines[pos] 	#read thicknes

				iter = self.layer_model.append()

				self.layer_model.set (iter,
				  COLUMN_LAYER, token,
				  COLUMN_THICKNES, str(layer_ticknes)
				)

				scan_item_add("device_epitaxy.inp",token,token,1)

			pos=pos+1
			pos=pos+1
			mesh_layers=int(lines[pos])

			for i in range(0, mesh_layers):
				pos=pos+1					#token
				token=lines[pos]
				scan_item_add("device_epitaxy.inp",token,"Mesh width"+str(i),1)
				pos=pos+1
				thicknes=lines[pos]	#read value

				pos=pos+1					#token
				token=lines[pos]
				scan_item_add("device_epitaxy.inp",token,"Mesh points"+str(i),1)

				pos=pos+1
				points=lines[pos] 		#read value

				iter = self.mesh_model.append()

				self.mesh_model.set (iter,
				  MESH_THICKNES, str(thicknes),
				  MESH_POINTS, str(points)
				)


	def init(self):
		self.__gobject_init__()

		self.layer_model = gtk.ListStore(str,str)
		self.mesh_model = gtk.ListStore(str,str)

		self.load()

		frame = gtk.Frame()
		frame.set_label("Layers")
		vbox_layers = gtk.VBox(False, 2)
		treeview = gtk.TreeView(self.layer_model)
		treeview.set_size_request(200, 100)
		treeview.set_rules_hint(True)
		treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
		self.__add_columns(treeview)
		vbox_layers.pack_start(treeview, False, False, 0)

	

		if debug_mode()==True:
			add_button = gtk.Button("Add",gtk.STOCK_ADD)
			add_button.connect("clicked", self.on_add_item_clicked, self.layer_model)

			delete_button = gtk.Button("Delete",gtk.STOCK_DELETE)
			delete_button.connect("clicked", self.on_remove_item_clicked, treeview)

			hbox = gtk.HBox(False, 2)
			hbox.pack_start(add_button, False, False, 0)
			hbox.pack_start(delete_button, False, False, 0)
			vbox_layers.pack_start(hbox, False, False, 0)

		vbox_layers.show()

		frame.add(vbox_layers)
		frame.show()
		self.pack_start(frame, True, True, 0)

		#spacer
		label=gtk.Label("\n\n    ")
		label.show()
		#self.attach(label, 4, 5, 1, 2,gtk.SHRINK ,gtk.SHRINK)
		self.pack_start(label, True, True, 0)


		#mesh editor
		frame = gtk.Frame()
		frame.set_label("Mesh")
		vbox_mesh = gtk.VBox(False, 2)
		treeview = gtk.TreeView(self.mesh_model)
		treeview.set_size_request(200, 100)
		treeview.set_rules_hint(True)
		treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
		self.__add_columns_mesh(treeview)
		vbox_mesh.pack_start(treeview, False, False, 0)

		if debug_mode()==True:
			add_button = gtk.Button("Add",gtk.STOCK_ADD)
			add_button.connect("clicked", self.on_add_mesh_clicked, self.mesh_model)

			delete_button = gtk.Button("Delete",gtk.STOCK_DELETE)
			delete_button.connect("clicked", self.on_remove_from_mesh_click, treeview)

			hbox = gtk.HBox(False, 2)
			
			hbox.pack_start(add_button, False, False, 0)
			hbox.pack_start(delete_button, False, False, 0)

			vbox_mesh.pack_start(hbox, False, False, 0)

		frame.add(vbox_mesh)
		self.pack_start(frame, True, True, 0)

		self.show_all()

gobject.type_register(electrical_mesh_editor)
gobject.signal_new("refresh", electrical_mesh_editor, gobject.SIGNAL_RUN_FIRST,gobject.TYPE_NONE, ())
