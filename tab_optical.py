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
from numpy import *
from matplotlib.figure import Figure
from numpy import arange, sin, pi
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
import gobject

#   columns
(
  COLUMN_LAYER,
  COLUMN_THICKNES,
  COLUMN_MATERIAL,
  COLUMN_START,
  COLUMN_ENABLE_GEN,
  COLUMN_EDITABLE
) = range(6)

# data
articles = []

class scan_item(gtk.CheckButton):
	name=""
	token=""
	filename=""
	line=""

class tab_optical(gtk.Table):
	lines=[]
	edit_list=[]

	line_number=[]
	config_file=""

	config_file="optics_epitaxy.inp"

	enabled=os.path.exists(config_file)


	def __create_model(self):

		# create list store
		model = gtk.ListStore(
		    gobject.TYPE_STRING,
		    gobject.TYPE_STRING,
		    gobject.TYPE_STRING,
		    gobject.TYPE_STRING,
		    gobject.TYPE_STRING,
		    gobject.TYPE_BOOLEAN
		)

		# add items
		for item in articles:
			iter = model.append()

			model.set (iter,
			  COLUMN_LAYER, item[COLUMN_LAYER],
			  COLUMN_THICKNES, item[COLUMN_THICKNES],
			  COLUMN_MATERIAL, item[COLUMN_MATERIAL],
			  COLUMN_START, item[COLUMN_START],
			  COLUMN_ENABLE_GEN, item[COLUMN_ENABLE_GEN],
			  COLUMN_EDITABLE, item[COLUMN_EDITABLE]
			)
		return model


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

		# Enable generation
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", COLUMN_ENABLE_GEN)

		column = gtk.TreeViewColumn("Enable Generation", renderer, text=COLUMN_ENABLE_GEN,
				       editable=COLUMN_EDITABLE)
		treeview.append_column(column)

		# Start
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", COLUMN_START)

		column = gtk.TreeViewColumn("Start", renderer, text=COLUMN_START,
				       editable=COLUMN_EDITABLE)
		treeview.append_column(column)




	def on_add_item_clicked(self, button, model):
		new_item = [0, "Description here", "Material","Enable Gen","Start",True]
		articles.append(new_item)

		iter = model.append()
		model.set (iter,
		    COLUMN_LAYER, new_item[COLUMN_LAYER],
		    COLUMN_THICKNES, new_item[COLUMN_THICKNES],
		    COLUMN_MATERIAL, new_item[COLUMN_MATERIAL],
		    COLUMN_START, new_item[COLUMN_START],
		    COLUMN_ENABLE_GEN, new_item[COLUMN_ENABLE_GEN],
		    COLUMN_EDITABLE, new_item[COLUMN_EDITABLE]
		)

	def save_model(self, model):
		print "Saved"
		a = open("optics_epitaxy.inp", "w")
		a.write("#layers\n")
		a.write(str(len(model))+"\n")


		for item in model:
			a.write(item[COLUMN_LAYER]+"\n")
			a.write(item[COLUMN_THICKNES]+"\n")
			a.write(item[COLUMN_MATERIAL]+"\n")
			a.write(item[COLUMN_START]+"\n")
			a.write(item[COLUMN_ENABLE_GEN]+"\n")

		a.write("#ver\n")			
		a.write("1.1\n")			
		a.write("#end\n")			
		a.close()

	def on_remove_item_clicked(self, button, treeview):

		selection = treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
			model.remove(iter)

			del articles[ path ]

	def update_graph(self,model):
		cmd = './go.o --optics'
		ret= os.system(cmd)
		self.fig.clf()
		self.draw_graph(model)
		self.fig.canvas.draw()

	def on_cell_edited(self, cell, path_string, new_text, model):

		iter = model.get_iter_from_string(path_string)
		path = model.get_path(iter)[0]
		column = cell.get_data("column")

		if column == COLUMN_LAYER:
			articles[path][COLUMN_LAYER] = new_text

			model.set(iter, column, articles[path][COLUMN_LAYER])

		if column == COLUMN_THICKNES:
			#old_text = model.get_value(iter, column)
			articles[path][COLUMN_THICKNES] = new_text
			print new_text
			model.set(iter, column, articles[path][COLUMN_THICKNES])

		if column == COLUMN_MATERIAL:
			print new_text
			#old_text = model.get_value(iter, column)
			articles[path][COLUMN_MATERIAL] = new_text

			model.set(iter, column, articles[path][COLUMN_MATERIAL])

		if column == COLUMN_START:
			#old_text = model.get_value(iter, column)
			articles[path][COLUMN_START] = new_text

			model.set(iter, column, articles[path][COLUMN_START])

		if column == COLUMN_ENABLE_GEN:
			#old_text = model.get_value(iter, column)
			articles[path][COLUMN_ENABLE_GEN] = new_text

			model.set(iter, column, articles[path][COLUMN_ENABLE_GEN])

		self.save_model(model)
		self.update_graph(model)
#####################################
	def callback_edit(self, widget, data=None):
		line=self.line_number[data]
		self.lines[line]=self.edit_list[data].get_text()
		self.edit_list[data].set_text(self.lines[line])
		print "Written data to", self.config_file
		a = open(self.config_file, "w")
		for i in range(0,len(self.lines)):
			a.write(self.lines[i]+"\n")
		a.close()

	# This callback quits the program
	def delete_event(self, widget, event, data=None):
		gtk.main_quit()
		return False

	def draw_graph(self,model):

		print "Drawing graph"

		n=0

		ax1 = self.fig.add_subplot(111)
		ax2 = ax1.twinx()
		x_pos=0.0
		layer=0
		color =['r','g','b','y','o','r','g','b','y','o']

		for item in model:
			if item[COLUMN_START]=="0":
				x_pos=x_pos-float(item[COLUMN_THICKNES])

		x_pos=x_pos*1e9
		for item in model:

			label=item[COLUMN_LAYER]
			layer_ticknes=item[COLUMN_THICKNES]
			layer_material=item[COLUMN_MATERIAL]
			start=item[COLUMN_START]
			enable_gen=item[COLUMN_ENABLE_GEN]

			delta=float(layer_ticknes)*1e9

			mat_file='./phys/'+layer_material+'/mat.inp'
			print mat_file
			myfile = open(mat_file)
			self.mat_file_lines = myfile.readlines()
			myfile.close()
			
			for ii in range(0, len(self.mat_file_lines)):
				self.mat_file_lines[ii]=self.mat_file_lines[ii].rstrip()

			x = [x_pos,x_pos+delta,x_pos+delta,x_pos] #arange(0.0,3.0,0.01)
			lumo=-float(self.mat_file_lines[1])
			lumo_delta=lumo-0.1
			Eg=float(self.mat_file_lines[3])
			homo=lumo-Eg
			homo_delta=homo-0.1
			if Eg==0.0:
				lumo_delta=lumo-0.5
				homo=0.0
			lumo_shape = [lumo,lumo,lumo_delta,lumo_delta]
			x_pos=x_pos+delta
			ax2.fill(x,lumo_shape, color[layer],alpha=0.4)

			if homo!=0.0:
				homo_shape = [homo,homo,homo_delta,homo_delta]
				ax2.fill(x,homo_shape, color[layer],alpha=0.4)

			layer=layer+1

			n=n+1

		ax1.set_ylabel('Photon density')
		ax1.set_xlabel('Position (nm)')
		ax2.set_ylabel('Energy (eV)')
		try:
			t,s = loadtxt("light_1d_photons_tot.dat", unpack=True)
			t=t*1e9


			ax1.plot(t,s, 'black', linewidth=3 ,alpha=0.5)
		except:
			print "No mode file\n"

		self.fig.tight_layout()

	def wow(self):
		self.edit_list=[]
		self.line_number=[]

		print "loading ",self.config_file
		f = open(self.config_file)
		self.lines = f.readlines()
		f.close()
		pos=0
		for i in range(0, len(self.lines)):
			self.lines[i]=self.lines[i].rstrip()

		n=0
		gui_pos=0
		pos=0
		pos=pos+1	#first comment
		items=int(self.lines[pos])

		layer=0

		for i in range(0, items):
			pos=pos+1
			label=self.lines[pos]	#read label
			print label

			pos=pos+1
			layer_ticknes=self.lines[pos] 	#read thicknes

			pos=pos+1
			layer_material=self.lines[pos] 	#read thicknes

			pos=pos+1
			start=self.lines[pos] 	#read thicknes

			pos=pos+1
			enable_gen=self.lines[pos] 	#read thicknes

			articles.append([ label, str(layer_ticknes),str(layer_material),str(start),enable_gen, True ])

			layer=layer+1

			#print "out -> %s %i",out_text,len(self.edit_list)

			n=n+1

		model = self.__create_model()

		self.fig = Figure(figsize=(5,4), dpi=100)
		self.draw_graph(model)
		canvas = FigureCanvas(self.fig)  # a gtk.DrawingArea
	
		#canvas.set_background('white')
		#canvas.set_facecolor('white')
		canvas.figure.patch.set_facecolor('white')
		canvas.set_size_request(-1, 150)
		canvas.show()
		self.attach(canvas, 0, 3, gui_pos, gui_pos+1)

		# create model

		gui_pos=gui_pos+1

		add_button = gtk.Button("Add layer",gtk.STOCK_ADD)
		add_button.connect("clicked", self.on_add_item_clicked, model)
		add_button.show()

		delete_button = gtk.Button("Delete layer",gtk.STOCK_DELETE)
		delete_button.show()

	        hbox = gtk.HBox(False, 2)
        
	        hbox.pack_start(add_button, False, False, 0)
	        hbox.pack_start(delete_button, False, False, 0)
		hbox.show()
		self.attach(hbox, 2, 4, gui_pos, gui_pos+1,gtk.SHRINK ,gtk.SHRINK)
		gui_pos=gui_pos+1

		# create tree view
		treeview = gtk.TreeView(model)
		treeview.set_size_request(600, 150)
		treeview.set_rules_hint(True)
		treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)

		delete_button.connect("clicked", self.on_remove_item_clicked, treeview)

		self.__add_columns(treeview)

		#sw.add()
		
		self.attach(treeview, 0, 3, gui_pos, gui_pos+1,gtk.SHRINK ,gtk.SHRINK)
		gui_pos=gui_pos+1

		treeview.show()





