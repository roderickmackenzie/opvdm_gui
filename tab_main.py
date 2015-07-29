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

from scan_item import scan_item_add
(
  COLUMN_LAYER,
  COLUMN_THICKNES,
  COLUMN_MATERIAL,
  COLUMN_DEVICE,
  COLUMN_EDITABLE
) = range(5)


class tab_main(gtk.VBox):

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
		self.thick=[]
		self.material=[]

		for i in range(0, items):
			pos=pos+1
			label=self.lines[pos]	#read label

			pos=pos+1
			self.thick.append(float(self.lines[pos]))

			pos=pos+1
			self.material.append(self.lines[pos])

			pos=pos+1
			device=self.lines[pos] 	#value

			self.articles.append([ label, str(self.thick[-1]),str(self.material[-1]),str(device), True ])
			scan_item_add("optics_epitaxy.inp",label,"Material for "+label,2)
			scan_item_add("optics_epitaxy.inp",label,"Layer width "+label,1)
			layer=layer+1



	def init(self):
		self.load()
		main_hbox=gtk.HBox()
		darea = gtk.DrawingArea()
		darea.connect("expose-event", self.expose)
		#darea.show()


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
		frame = gtk.Frame()
		frame.set_label("Device layers")
		frame.set_label_align(0.0, 0.0)
		frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
		frame.show()

		hbox0.show()
		frame_vbox.pack_start(treeview, False, False, 0)
		frame_vbox.pack_start(hbox, False, False, 0)


		frame.add(frame_vbox)
		frame.show_all()

		main_hbox.pack_start(frame, False, False, 0)
		main_hbox.pack_start(darea, True, True, 0)

		add_button.connect("clicked", self.on_add_item_clicked, treeview)
		delete_button.connect("clicked", self.on_remove_item_clicked, treeview)


		self.__add_columns(treeview)


		self.add(main_hbox)
		self.show_all()

	def draw_box(self,x,y,z,r,g,b,text):
		self.cr.set_source_rgb(r,g,b)

		points=[(x,y), (x+200,y), (x+200,y+z), (x,y+z)]
		print points
		self.cr.move_to(x, y)
		for px,py in points:
			self.cr.line_to(px, py)
		self.cr.fill()

		r=r*0.5
		g=g*0.5
		b=b*0.5
		self.cr.set_source_rgb(r,g,b)

		points=[(x+200,y-0),(x+200,y+z), (x+200+80,y-60+z),(x+200+80,y-60)]
		print points
		self.cr.move_to(points[0][0], points[0][1])
		for px,py in points:
			self.cr.line_to(px, py)
		self.cr.fill()

		r=r*0.5
		g=g*0.5
		b=b*0.5
		self.cr.set_source_rgb(r,g,b)

		points=[(x,y),(x+200,y), (x+200+80,y-60), (x+100,y-60)]
		self.cr.move_to(points[0][0], points[0][1])
		print points
		self.cr.move_to(x, y)
		for px,py in points:
			self.cr.line_to(px, py)
		self.cr.fill()
		self.cr.set_font_size(14)
		self.cr.move_to(x+200+80+20, y-60+z/2)
		self.cr.show_text(text)
		
	def draw(self,thick,text):
		tot=sum(thick)
		pos=0.0
		for i in range(0,len(thick)):
			thick[i]=200.0*thick[i]/tot
			pos=pos+thick[i]
			print "Draw"
			self.draw_box(-400,100.0-pos,thick[i]*0.9,random.uniform(0, 1),random.uniform(0, 1),random.uniform(0, 1),text[i])

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

		self.save_model(model)
		#self.update_graph(model)
#####################################


	def callback_edit(self, widget, data=None):
		line=self.line_number[data]
		self.lines[line]=self.edit_list[data].get_text()
		self.edit_list[data].set_text(self.lines[line])
		a = open(self.config_file, "w")
		for i in range(0,len(self.lines)):
			a.write(self.lines[i]+"\n")
		a.close()

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

	def expose(self, widget, event):

		self.cr = widget.window.cairo_create()

		self.cr.set_line_width(9)
		self.cr.set_source_rgb(0.7, 0.2, 0.0)
		        
		w = self.allocation.width
		h = self.allocation.height

		self.cr.translate(w/2, h/2)

		

		self.draw(self.thick,self.material)

