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
from util import set_exe_command
from numpy import *
from matplotlib.figure import Figure
from numpy import arange, sin, pi
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
import gobject
from util import find_data_file
from scan_item import scan_item_add

(
  COLUMN_LAYER,
  COLUMN_THICKNES,
  COLUMN_EDITABLE
) = range(3)

(
  MESH_THICKNES,
  MESH_POINTS,
  MESH_EDITABLE
) = range(3)


class tab_electrical_mesh(gtk.Window):
	lines=[]
	edit_list=[]

	line_number=[]
	save_file_name=""

	file_name=""
	name=""
	visible=1

	def __create_model(self):

		# create list store
		model = gtk.ListStore(
		    gobject.TYPE_STRING,
		    gobject.TYPE_STRING,
		    gobject.TYPE_BOOLEAN
		)

		# add items
		for item in self.articles:
			iter = model.append()

			model.set (iter,
			  COLUMN_LAYER, item[COLUMN_LAYER],
			  COLUMN_THICKNES, item[COLUMN_THICKNES],
			  COLUMN_EDITABLE, item[COLUMN_EDITABLE]
			)

		return model

	def __create_model_mesh(self):

		model_mesh = gtk.ListStore(
		    gobject.TYPE_STRING,
		    gobject.TYPE_STRING,
		    gobject.TYPE_BOOLEAN
		)


		for item in self.mesh_articles:
			iter = model_mesh.append()

			model_mesh.set (iter,
			  MESH_THICKNES, item[MESH_THICKNES],
			  MESH_POINTS, item[MESH_POINTS],
			  MESH_EDITABLE, item[MESH_EDITABLE]
			)
		return model_mesh

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


	def __add_columns_mesh(self, treeview):

		model = treeview.get_model()

		# Thicknes
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_mesh_edited, model)
		renderer.set_data("column", MESH_THICKNES)

		column = gtk.TreeViewColumn("Thicknes", renderer, text=MESH_THICKNES,
				       editable=MESH_EDITABLE)
		treeview.append_column(column)

		# Thicknes
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_mesh_edited, model)
		renderer.set_data("column", MESH_POINTS)

		column = gtk.TreeViewColumn("Points", renderer, text=MESH_POINTS,
				       editable=MESH_EDITABLE)
		treeview.append_column(column)



	def on_add_item_clicked(self, button, model):
		new_item = ["#layerN","0e-9" ,True]
		self.articles.append(new_item)

		iter = model.append()
		model.set (iter,
		    COLUMN_LAYER, new_item[COLUMN_LAYER],
		    COLUMN_THICKNES, new_item[COLUMN_THICKNES],
		    COLUMN_EDITABLE, new_item[COLUMN_EDITABLE]
		)

	def on_add_mesh_clicked(self, button, model):
		new_item = ["0e-9","0" ,True]
		self.mesh_articles.append(new_item)

		iter = model.append()
		model.set (iter,
		    MESH_THICKNES, new_item[MESH_THICKNES],
		    MESH_POINTS, new_item[MESH_POINTS],
		    MESH_EDITABLE, new_item[MESH_EDITABLE]
		)

	def save_model(self, ):
		a = open("device_epitaxy.inp", "w")
		a.write("#layers\n")
		a.write(str(len(self.layer_model))+"\n")


		for item in self.layer_model:
			a.write(item[COLUMN_LAYER]+"\n")
			a.write(item[COLUMN_THICKNES]+"\n")
		a.write("#mesh_layers\n")
		a.write(str(len(self.mesh_model))+"\n")
		i=0
		for item in self.mesh_model:
			a.write("#mesh_layer_length"+str(i)+"\n")
			a.write(item[MESH_THICKNES]+"\n")
			a.write("#mesh_layer_points"+str(i)+"\n")
			a.write(item[MESH_POINTS]+"\n")
			i=i+1
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

			del self.articles[ path ]

		self.save_model()

	def on_remove_from_mesh_click(self, button, treeview):

		selection = treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
			model.remove(iter)

			del self.mesh_articles[ path ]

		self.save_model()

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

		self.save_model()

	def on_mesh_edited(self, cell, path_string, new_text, model):

		iter = model.get_iter_from_string(path_string)
		path = model.get_path(iter)[0]
		column = cell.get_data("column")


		if column == MESH_THICKNES:
			self.mesh_articles[path][MESH_THICKNES] = new_text

			model.set(iter, column, self.mesh_articles[path][MESH_THICKNES])

		if column == MESH_POINTS:
			#old_text = model.get_value(iter, column)
			self.mesh_articles[path][MESH_POINTS] = new_text
			model.set(iter, column, self.mesh_articles[path][MESH_POINTS])

		self.save_model()
		self.update_graph()

	def update_graph(self):
		cmd = self.exe_command+' --onlypos'
		ret= os.system(cmd)
		self.fig.clf()
		self.draw_graph()
		self.fig.canvas.draw()

	def draw_graph(self):

		n=0
		
		self.fig.clf()
		self.fig.subplots_adjust(bottom=0.2)
		self.fig.subplots_adjust(left=0.1)
		self.ax1 = self.fig.add_subplot(111)

		#ax2 = ax1.twinx()
		x_pos=0.0
		layer=0
		color =['r','g','b','y','o','r','g','b','y','o']

		self.ax1.set_ylabel('Energy (eV)')
		#ax2.set_ylabel('Energy (eV)')
		self.ax1.set_xlabel('Position (nm)')
		try:
			t,s = loadtxt("Ec.dat", unpack=True)
			t=t*1e9
			Ec, = self.ax1.plot(t,s, 'ro-', linewidth=3 ,alpha=0.5)

			t,s = loadtxt("Ev.dat", unpack=True)
			t=t*1e9
			Ev,=self.ax1.plot(t,s, 'go-', linewidth=3 ,alpha=0.5)

			t,s = loadtxt("Fi.dat", unpack=True)
			t=t*1e9
			Fi,=self.ax1.plot(t,s, 'bo-', linewidth=3 ,alpha=0.5)
			
			if self.show_key==True:
				self.fig.legend((Ec, Ev, Fi), ('LUMO', 'HOMO', 'Fi'), 'upper right')
			else:
				self.ax1.legend_ = None
			self.fig.canvas.draw()
			
		except:
			print "No mode file\n"

		
	def save_image(self,file_name):
		self.fig.savefig(file_name)	

	def callback_refresh(self, widget, data=None):
		self.update_graph()
		

	def callback_close(self, widget, data=None):
		self.hide()
		return True

	def callback_hide_key(self, widget, data=None):
		self.show_key=not self.show_key
		self.draw_graph()

	def callback_save(self, widget, data=None):
		dialog = gtk.FileChooserDialog("Save as..",
                               None,
                               gtk.FILE_CHOOSER_ACTION_SAVE,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)

		filter = gtk.FileFilter()
		filter.set_name(".jpg")
		filter.add_pattern("*.jpg")
		dialog.add_filter(filter)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			file_name=dialog.get_filename()

			if os.path.splitext(file_name)[1]:
				self.save_image(file_name)
			else:
				filter=dialog.get_filter()
				self.save_image(file_name+filter.get_name())
			
		elif response == gtk.RESPONSE_CANCEL:
		    print 'Closed, no files selected'
		dialog.destroy()

	def callback_help(self, widget, data=None):
		cmd = 'firefox http://www.roderickmackenzie.eu/opvdm_wiki.html'
		os.system(cmd)

	def init(self):
		self.articles = []
		self.mesh_articles = []
		print "INIT!!"
		self.save_file_name="device_epitaxy.inp"

		self.fig = Figure(figsize=(5,4), dpi=100)
		self.ax1=None
		self.show_key=True
		self.hbox=gtk.HBox()
		self.exe_command , exe_name  =  set_exe_command()
		self.edit_list=[]
		self.line_number=[]
		gui_pos=0

		if os.path.isfile(self.save_file_name):
			f = open(self.save_file_name)
			self.lines = f.readlines()
			f.close()
			pos=0
			for i in range(0, len(self.lines)):
				self.lines[i]=self.lines[i].rstrip()

			n=0

			pos=0
			pos=pos+1	#first comment
			layers=int(self.lines[pos])

			for i in range(0, layers):
				pos=pos+1
				token=self.lines[pos]	#read label

				pos=pos+1
				layer_ticknes=self.lines[pos] 	#read thicknes

				self.articles.append([ token, str(layer_ticknes), True ])
				scan_item_add("device_epitaxy.inp",token,token,1)

			pos=pos+1
			pos=pos+1
			mesh_layers=int(self.lines[pos])

			for i in range(0, mesh_layers):
				pos=pos+1					#token
				token=self.lines[pos]
				scan_item_add("device_epitaxy.inp",token,"Mesh width"+str(i),1)
				pos=pos+1
				thicknes=self.lines[pos]	#read value

				pos=pos+1					#token
				token=self.lines[pos]
				scan_item_add("device_epitaxy.inp",token,"Mesh points"+str(i),1)

				pos=pos+1
				points=self.lines[pos] 		#read value

				self.mesh_articles.append([ str(thicknes), str(points), True ])

				n=n+1

		
		gui_pos=gui_pos+1

		self.draw_graph()
		canvas = FigureCanvas(self.fig)  # a gtk.DrawingArea
		#canvas.set_background('white')
		#canvas.set_facecolor('white')
		canvas.figure.patch.set_facecolor('white')
		canvas.set_size_request(500, 150)
		canvas.show()

		tooltips = gtk.Tooltips()

		toolbar = gtk.Toolbar()
		#toolbar.set_orientation(gtk.ORIENTATION_VERTICAL)
		toolbar.set_style(gtk.TOOLBAR_ICONS)
		toolbar.set_size_request(-1, 50)

		tool_bar_pos=0
		save = gtk.ToolButton(gtk.STOCK_SAVE)
		tooltips.set_tip(save, "Save image")
		save.connect("clicked", self.callback_save)
		toolbar.insert(save, tool_bar_pos)
		tool_bar_pos=tool_bar_pos+1

		hide_key = gtk.ToolButton(gtk.STOCK_INFO)
		tooltips.set_tip(hide_key, "Hide key")
		hide_key.connect("clicked", self.callback_hide_key)
		toolbar.insert(hide_key, tool_bar_pos)
		tool_bar_pos=tool_bar_pos+1

		image = gtk.Image()
   		image.set_from_file(find_data_file("gui/play.png"))
		save = gtk.ToolButton(image)
		tooltips.set_tip(save, "Run simulation")
		save.connect("clicked", self.callback_refresh)
		toolbar.insert(save, tool_bar_pos)
		tool_bar_pos=tool_bar_pos+1

		plot_toolbar = NavigationToolbar(canvas, self)
		plot_toolbar.show()
		box=gtk.HBox(True, 1)
		box.set_size_request(500,-1)
		box.show()
		box.pack_start(plot_toolbar, True, True, 0)
		tb_comboitem = gtk.ToolItem();
		tb_comboitem.add(box);
		tb_comboitem.show()
		toolbar.insert(tb_comboitem, tool_bar_pos)
		tool_bar_pos=tool_bar_pos+1

		sep = gtk.SeparatorToolItem()
		sep.set_draw(False)
		sep.set_expand(True)
		toolbar.insert(sep, tool_bar_pos)
		sep.show()
		tool_bar_pos=tool_bar_pos+1

		help = gtk.ToolButton(gtk.STOCK_HELP)
		toolbar.insert(help, tool_bar_pos)
		help.connect("clicked", self.callback_help)
		help.show()
		tool_bar_pos=tool_bar_pos+1

		close = gtk.ToolButton(gtk.STOCK_QUIT)
		close.connect("clicked", self.callback_close)
		toolbar.insert(close, tool_bar_pos)
		close.show()
		tool_bar_pos=tool_bar_pos+1

		toolbar.show_all()
		window_main_vbox=gtk.VBox()
		window_main_vbox.pack_start(toolbar, False, True, 0)
		#self.attach(toolbar, 0, 1, 0, 1)
		tool_bar_pos=tool_bar_pos+1




		self.hbox.pack_start(canvas, True, True, 0)
		#self.attach(canvas, 1, 3, 0, 1)


		#Layer editor
		self.layer_model = self.__create_model()
		self.mesh_model = self.__create_model_mesh()

		vbox = gtk.VBox(False, 2)
	

		frame = gtk.Frame()
		frame.set_label("Layers")
		vbox_layers = gtk.VBox(False, 2)
		treeview = gtk.TreeView(self.layer_model)
		treeview.set_size_request(200, 100)
		treeview.set_rules_hint(True)
		treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
		self.__add_columns(treeview)
		vbox_layers.pack_start(treeview, False, False, 0)
		treeview.show()

	

		if os.path.exists("./server.inp")==True:
			add_button = gtk.Button("Add",gtk.STOCK_ADD)
			add_button.connect("clicked", self.on_add_item_clicked, self.layer_model)
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
		frame.set_label("Mesh")
		vbox_mesh = gtk.VBox(False, 2)
		treeview = gtk.TreeView(self.mesh_model)
		treeview.set_size_request(200, 100)
		treeview.set_rules_hint(True)
		treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)
		self.__add_columns_mesh(treeview)
		vbox_mesh.pack_start(treeview, False, False, 0)
		treeview.show()

		gui_pos=3
		add_button = gtk.Button("Add",gtk.STOCK_ADD)
		add_button.connect("clicked", self.on_add_mesh_clicked, self.mesh_model)
		add_button.show()

		delete_button = gtk.Button("Delete",gtk.STOCK_DELETE)
		delete_button.connect("clicked", self.on_remove_from_mesh_click, treeview)
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
		self.hbox.pack_start(vbox, False, False, 0)
		#self.attach(vbox, 3, 4, 0, 1,gtk.SHRINK ,gtk.SHRINK)
		vbox.show()
		window_main_vbox.add(self.hbox)
		self.add(window_main_vbox)
		self.set_title("Electrical Mesh Editor - (www.opvdm.com)")
		self.set_icon_from_file(find_data_file("gui/mesh.png"))
		self.connect("delete-event", self.callback_close)
		self.set_position(gtk.WIN_POS_CENTER)


