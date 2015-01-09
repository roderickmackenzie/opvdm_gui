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


(
  LUMO_FUNCTION,
  LUMO_ENABLE,
  LUMO_A,
  LUMO_B,
  LUMO_C,
  LUMO_EDITABLE
) = range(6)

(
  HOMO_FUNCTION,
  HOMO_ENABLE,
  HOMO_A,
  HOMO_B,
  HOMO_C,
  HOMO_EDITABLE
) = range(6)


articles = []
HOMO_articles = []

class tab_bands(gtk.Table):
	lines=[]
	edit_list=[]

	line_number=[]
	save_file_name=""
	enabled=os.path.exists("lumo0.inp")


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
			  LUMO_FUNCTION, item[LUMO_FUNCTION],
			  LUMO_ENABLE, item[LUMO_ENABLE],
			  LUMO_A, item[LUMO_A],
			  LUMO_B, item[LUMO_B],
			  LUMO_C, item[LUMO_C],
			  LUMO_EDITABLE, item[LUMO_EDITABLE]
			)

		return model

	def __create_model_mesh(self):

		model_mesh = gtk.ListStore(
		    gobject.TYPE_STRING,
		    gobject.TYPE_STRING,
		    gobject.TYPE_STRING,
		    gobject.TYPE_STRING,
		    gobject.TYPE_STRING,
		    gobject.TYPE_BOOLEAN
		)


		for item in HOMO_articles:
			iter = model_mesh.append()

			model_mesh.set (iter,
			  HOMO_FUNCTION, item[HOMO_FUNCTION],
			  HOMO_ENABLE, item[HOMO_ENABLE],
			  HOMO_A, item[HOMO_A],
			  HOMO_B, item[HOMO_B],
			  HOMO_C, item[HOMO_C],
			  HOMO_EDITABLE, item[HOMO_EDITABLE]
			)
		return model_mesh

	def __add_columns(self, treeview):

		model = treeview.get_model()

		# Function
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", LUMO_FUNCTION)

		column = gtk.TreeViewColumn("Function", renderer, text=LUMO_FUNCTION,
				       editable=LUMO_EDITABLE)
		treeview.append_column(column)

		# Enable
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", LUMO_ENABLE)

		column = gtk.TreeViewColumn("enabled", renderer, text=LUMO_ENABLE,
				       editable=LUMO_EDITABLE)
		treeview.append_column(column)

		# A
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", LUMO_A)

		column = gtk.TreeViewColumn("a", renderer, text=LUMO_A,
				       editable=LUMO_EDITABLE)
		treeview.append_column(column)

		# B
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", LUMO_B)

		column = gtk.TreeViewColumn("b", renderer, text=LUMO_B,
				       editable=LUMO_EDITABLE)
		treeview.append_column(column)

		# C
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", LUMO_C)

		column = gtk.TreeViewColumn("c", renderer, text=LUMO_C,
				       editable=LUMO_EDITABLE)
		treeview.append_column(column)

	def __add_columns_mesh(self, treeview):

		model = treeview.get_model()

		# Function
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_HOMO_edited, model)
		renderer.set_data("column", HOMO_FUNCTION)

		column = gtk.TreeViewColumn("Function", renderer, text=HOMO_FUNCTION,
				       editable=HOMO_EDITABLE)
		treeview.append_column(column)

		# Enable
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_HOMO_edited, model)
		renderer.set_data("column", HOMO_ENABLE)

		column = gtk.TreeViewColumn("Enable", renderer, text=HOMO_ENABLE,
				       editable=HOMO_EDITABLE)
		treeview.append_column(column)

		# A
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_HOMO_edited, model)
		renderer.set_data("column", HOMO_A)

		column = gtk.TreeViewColumn("a", renderer, text=HOMO_A,
				       editable=HOMO_EDITABLE)
		treeview.append_column(column)

		# B
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_HOMO_edited, model)
		renderer.set_data("column", HOMO_B)

		column = gtk.TreeViewColumn("b", renderer, text=HOMO_B,
				       editable=HOMO_EDITABLE)
		treeview.append_column(column)

		# C
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_HOMO_edited, model)
		renderer.set_data("column", HOMO_C)

		column = gtk.TreeViewColumn("c", renderer, text=HOMO_C,
				       editable=HOMO_EDITABLE)
		treeview.append_column(column)

	def on_add_item_clicked(self, button, model):
		new_item = ["exp","0" ,"A","B","C",True]
		articles.append(new_item)

		iter = model.append()
		model.set (iter,
		    LUMO_FUNCTION, new_item[LUMO_FUNCTION],
		    LUMO_ENABLE, new_item[LUMO_ENABLE],
		    LUMO_A, new_item[LUMO_A],
		    LUMO_B, new_item[LUMO_B],
		    LUMO_C, new_item[LUMO_C],
		    LUMO_EDITABLE, new_item[LUMO_EDITABLE]
		)

	def on_add_HOMO_clicked(self, button, model):
		new_item = ["0e-9","0" ,True]
		HOMO_articles.append(new_item)

		iter = model.append()
		model.set (iter,
		    HOMO_FUNCTION, new_item[HOMO_FUNCTION],
		    HOMO_ENABLE, new_item[HOMO_ENABLE],
		    HOMO_A, new_item[HOMO_A],
		    HOMO_B, new_item[HOMO_B],
		    HOMO_C, new_item[HOMO_C],
		    HOMO_EDITABLE, new_item[HOMO_EDITABLE]
		)
	def save_model(self, ):
		print "Saved"
		a = open("lumo0.inp", "w")
		for item in self.LUMO_model:
			a.write(item[LUMO_FUNCTION]+"\n")
			a.write(item[LUMO_ENABLE]+"\n")
			a.write(item[LUMO_A]+"\n")
			a.write(item[LUMO_B]+"\n")
			a.write(item[LUMO_C]+"\n")
		a.write("#end\n")
		a.close()

		a = open("homo0.inp", "w")
		for item in self.HOMO_model:
			a.write(item[HOMO_FUNCTION]+"\n")
			a.write(item[HOMO_ENABLE]+"\n")
			a.write(item[HOMO_A]+"\n")
			a.write(item[HOMO_B]+"\n")
			a.write(item[HOMO_C]+"\n")			
		a.write("#end\n")			
		a.close()

	def on_remove_item_clicked(self, button, treeview):

		selection = treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
			model.remove(iter)

			del articles[ path ]

		self.save_model()
		self.update_graph()

	def on_cell_edited(self, cell, path_string, new_text, model):

		iter = model.get_iter_from_string(path_string)
		path = model.get_path(iter)[0]
		column = cell.get_data("column")

		if column == LUMO_FUNCTION:
			articles[path][LUMO_FUNCTION] = new_text

			model.set(iter, column, articles[path][LUMO_FUNCTION])

		if column == LUMO_ENABLE:
			#old_text = model.get_value(iter, column)
			articles[path][LUMO_ENABLE] = new_text
			print new_text
			model.set(iter, column, articles[path][LUMO_ENABLE])

		if column == LUMO_A:
			#old_text = model.get_value(iter, column)
			articles[path][LUMO_A] = new_text
			print new_text
			model.set(iter, column, articles[path][LUMO_A])

		if column == LUMO_B:
			#old_text = model.get_value(iter, column)
			articles[path][LUMO_B] = new_text
			print new_text
			model.set(iter, column, articles[path][LUMO_B])

		if column == LUMO_C:
			#old_text = model.get_value(iter, column)
			articles[path][LUMO_C] = new_text
			print new_text
			model.set(iter, column, articles[path][LUMO_C])

		self.save_model()
		self.update_graph()

	def on_HOMO_edited(self, cell, path_string, new_text, model):

		iter = model.get_iter_from_string(path_string)
		path = model.get_path(iter)[0]
		column = cell.get_data("column")

		if column == HOMO_FUNCTION:
			articles[path][HOMO_FUNCTION] = new_text

			model.set(iter, column, articles[path][HOMO_FUNCTION])

		if column == HOMO_ENABLE:
			#old_text = model.get_value(iter, column)
			articles[path][HOMO_ENABLE] = new_text
			print new_text
			model.set(iter, column, articles[path][HOMO_ENABLE])

		if column == HOMO_A:
			#old_text = model.get_value(iter, column)
			articles[path][HOMO_A] = new_text
			print new_text
			model.set(iter, column, articles[path][HOMO_A])

		if column == HOMO_B:
			#old_text = model.get_value(iter, column)
			articles[path][HOMO_B] = new_text
			print new_text
			model.set(iter, column, articles[path][HOMO_B])

		if column == HOMO_C:
			#old_text = model.get_value(iter, column)
			articles[path][HOMO_C] = new_text
			print new_text
			model.set(iter, column, articles[path][HOMO_C])

		self.save_model()
		self.update_graph()

	def update_graph(self):
		#cmd = './go.o --onlypos'
		#ret= os.system(cmd)
		self.LUMO_fig.clf()
		self.HOMO_fig.clf()
		self.draw_graph_lumo()
		self.draw_graph_homo()
		self.LUMO_fig.canvas.draw()
		self.HOMO_fig.canvas.draw()

	def draw_graph_lumo(self):

		print "Drawing graph"

		n=0

		ax1 = self.LUMO_fig.add_subplot(111)

		ax1.set_ylabel('DoS (m^(-3) eV^(-1))')
		ax1.set_xlabel('LUMO - Energy (eV)')

		#ax2 = ax1.twinx()
		x_pos=0.0
		layer=0
		color =['r','g','b','y','o','r','g','b','y','o']
		ax1.set_yscale('log')
		ax1.set_ylim(ymin=1e12,ymax=1e28)
		pos=0
		x = linspace(0, -1, num=20)
		for item in self.LUMO_model:
			if item[LUMO_FUNCTION]=="exp":
				y = float(item[LUMO_A])*exp(x/float(item[LUMO_B]))

				line, = ax1.plot(x,y , '--', linewidth=2)
			if item[LUMO_FUNCTION]=="gaus":
	
				y = float(item[LUMO_A])*exp(-pow(((float(item[LUMO_B])+x)/(sqrt(2.0)*float(item[LUMO_C])*1.0)),2.0))

				line, = ax1.plot(x,y , color[pos], linewidth=2)
				pos=pos+1


	def draw_graph_homo(self):

		print "Drawing graph"

		n=0
		ax1 = self.HOMO_fig.add_subplot(111)
		
		ax1.set_ylabel('DoS (m^(-3) eV^(-1))')
		ax1.set_xlabel('HOMO - Energy (eV)')
		#ax2 = ax1.twinx()
		x_pos=0.0
		layer=0
		color =['r','g','b','y','o','r','g','b','y','o']
		ax1.set_yscale('log')
		ax1.set_ylim(ymin=1e12,ymax=1e28)
		ax1.set_xlim([0,-1])

		pos=0
		x = linspace(0, -1, num=10)
		for item in self.HOMO_model:
			if item[HOMO_FUNCTION]=="exp":

				y = float(item[HOMO_A])*exp(x/float(item[HOMO_B]))

				line, = ax1.plot(x,y , '--', linewidth=2)
			if item[LUMO_FUNCTION]=="gaus":
				y = float(item[HOMO_A])*exp(-pow(((float(item[HOMO_B])+x)/(sqrt(2.0)*float(item[HOMO_C])*1.0)),2.0))

				line, = ax1.plot(x,y , color[pos], linewidth=2)
				pos=pos+1


	def delete_event(self, widget, event, data=None):
		gtk.main_quit()
		return False

	def wow(self):
		self.edit_list=[]
		self.line_number=[]
		self.save_file_name="lumo0.inp"
		print "loading ",self.save_file_name
		f = open(self.save_file_name)
		self.lines = f.readlines()
		f.close()
		pos=0
		for i in range(0, len(self.lines)):
			self.lines[i]=self.lines[i].rstrip()

		n=0
		gui_pos=0
		pos=0

		while True:
			function=self.lines[pos]	#read label
			pos=pos+1
			print "My function",function
			if function=="#end":
				print "Exiting"
				break


			enabled=self.lines[pos] 	#read thicknes
			pos=pos+1
			#print "enabled=",enabled
			
			a=self.lines[pos] 	#read thicknes
			pos=pos+1
			#print "a=",a

			b=self.lines[pos] 	#read thicknes
			pos=pos+1
			#print "b=",b

			c=self.lines[pos] 	#read thicknes
			pos=pos+1
			#print "c=",c

			articles.append([ str(function), str(enabled), str(a), str(b), str(c), True ])


		self.save_file_name="homo0.inp"
		print "loading ",self.save_file_name
		f = open(self.save_file_name)
		self.lines = f.readlines()
		f.close()
		pos=0
		for i in range(0, len(self.lines)):
			self.lines[i]=self.lines[i].rstrip()

		n=0
		gui_pos=0
		pos=0

		while True:
			function=self.lines[pos]	#read label
			pos=pos+1
			print "My function",function
			if function=="#end":
				print "Exiting"
				break


			enabled=self.lines[pos] 	#read thicknes
			pos=pos+1
			#print "enabled=",enabled
			
			a=self.lines[pos] 	#read thicknes
			pos=pos+1
			#print "a=",a

			b=self.lines[pos] 	#read thicknes
			pos=pos+1
			#print "b=",b

			c=self.lines[pos] 	#read thicknes
			pos=pos+1
			#print "c=",c

			HOMO_articles.append([ str(function), str(enabled), str(a), str(b), str(c), True ])


		gui_pos=gui_pos+1
 		vbox = gtk.VBox(False, 2)
		self.LUMO_model = self.__create_model()
		self.LUMO_fig = Figure(figsize=(5,4), dpi=100)
		self.draw_graph_lumo()
		canvas = FigureCanvas(self.LUMO_fig)  # a gtk.DrawingArea
		canvas.figure.patch.set_facecolor('white')
		#canvas.set_size_request(125, -1)
		canvas.show()
		vbox.pack_start(canvas, True, True, 10)
		


		self.HOMO_model = self.__create_model_mesh()
		self.HOMO_fig = Figure(figsize=(5,4), dpi=100)
		self.draw_graph_homo()
		canvas = FigureCanvas(self.HOMO_fig)
		canvas.figure.patch.set_facecolor('white')
		#canvas.set_size_request(125, -1)
		canvas.show()
		vbox.pack_start(canvas, True, True, 10)
		self.attach(vbox, 0, 3, 0, 2)
		vbox.show()
		#Layer editor

		self.LUMO_fig.tight_layout(pad=2.5)
		self.HOMO_fig.tight_layout(pad=2.5)

	        vbox = gtk.VBox(False, 2)
		

		frame = gtk.Frame()
		frame.set_label("LUMO")
		vbox_layers = gtk.VBox(False, 2)
		treeview = gtk.TreeView(self.LUMO_model)
		treeview.set_size_request(400, 100)
		treeview.set_rules_hint(True)
		treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
		self.__add_columns(treeview)
	        vbox_layers.pack_start(treeview, False, False, 0)
		treeview.show()

		add_button = gtk.Button("Add",gtk.STOCK_ADD)
		add_button.connect("clicked", self.on_add_item_clicked, self.LUMO_model)
		add_button.show()

		delete_button = gtk.Button("Delete",gtk.STOCK_DELETE)
		delete_button.connect("clicked", self.on_remove_item_clicked, treeview)
		delete_button.show()

	        hbox = gtk.HBox(False, 2)
        
	        hbox.pack_start(add_button, False, False, 0)
	        hbox.pack_start(delete_button, False, False, 0)
		hbox.show()

		vbox_layers.pack_start(hbox, False, False, 0)
		vbox_layers.show()

		frame.add(vbox_layers)
		frame.show()
	        vbox.pack_start(frame, False, False, 0)

		#spacer
		label=gtk.Label(" \n\n    ")
		#self.attach(label, 4, 5, 1, 2,gtk.SHRINK ,gtk.SHRINK)
		vbox.pack_start(label, False, False, 0)

		label.show()



		#mesh editor
		frame = gtk.Frame()
		frame.set_label("HOMO")
		vbox_mesh = gtk.VBox(False, 2)
		treeview = gtk.TreeView(self.HOMO_model)
		treeview.set_size_request(400, 100)
		treeview.set_rules_hint(True)
		treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
		self.__add_columns_mesh(treeview)
		vbox_mesh.pack_start(treeview, False, False, 0)
		treeview.show()

		gui_pos=3
		add_button = gtk.Button("Add",gtk.STOCK_ADD)
		add_button.connect("clicked", self.on_add_HOMO_clicked, self.HOMO_model)
		add_button.show()

		delete_button = gtk.Button("Delete",gtk.STOCK_DELETE)
		delete_button.connect("clicked", self.on_remove_item_clicked, treeview)
		delete_button.show()

	        hbox = gtk.HBox(False, 2)
        
	        hbox.pack_start(add_button, False, False, 0)
	        hbox.pack_start(delete_button, False, False, 0)
		vbox_mesh.pack_start(hbox, False, False, 0)
		frame.add(vbox_mesh)
		vbox.pack_start(frame, False, False, 0)
		frame.show()
		vbox_mesh.show()
		hbox.show()
		self.attach(vbox, 3, 4, 0, 1,gtk.SHRINK ,gtk.SHRINK)
		vbox.show()


