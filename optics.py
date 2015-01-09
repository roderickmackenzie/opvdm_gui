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
from inp import inp_update_token_value
from inp import inp_get_token_value
from matplotlib.figure import Figure
from numpy import arange, sin, pi
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
import gobject
import os, fnmatch
from plot_gen import plot_gen
from util import find_data_file
import zipfile
import glob

#   columns
(
  COLUMN_LAYER,
  COLUMN_THICKNES,
  COLUMN_MATERIAL,
  COLUMN_DEVICE,
  COLUMN_EDITABLE
) = range(5)

# data
articles = []

def find_modes(path):
	result = []
	if os.path.isfile("./light_dump.zip"):
		zf = zipfile.ZipFile("./light_dump.zip", 'r')

		for file in zf.filelist:
		    if file.filename.startswith("light_1d_"):
			if file.filename.endswith("_photons_norm.dat"):
				store = file.filename[:-17]
				s=store.split("light_1d_")
				store = s[1]
				result.append(store)

		zf.close()
	return result

def find_models():
	ret=[]
	if os.path.isfile("./light/exp.so"):
		path="./light/"
	else:
		path="/usr/lib64/opvdm/"

	for file in glob.glob(path+"*.so"):
		ret.append(os.path.splitext(os.path.basename(file))[0])

	return ret

class scan_item(gtk.CheckButton):
	name=""
	token=""
	filename=""
	line=""

class class_optical(gtk.Window):

	icon_theme = gtk.icon_theme_get_default()

	dump_dir="./light_dump/"
	lines=[]
	edit_list=[]

	line_number=[]

	file_name=""
	name=""
	visible=1

	def init(self):
		self.config_file="optics_epitaxy.inp"
		self.enabled=os.path.exists(self.config_file)
		
	def onclick(self, event):
		print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
		event.button, event.x, event.y, event.xdata, event.ydata)
		for i in range(0,len(self.layer_end)):
			if (self.layer_end[i]>event.xdata):
				break
		
		plot_gen(["./phys/"+self.layer_name[i]+"/alpha.inp"],[],None)

	def update_cb(self):
		self.cb.handler_block(self.cb_id)
		thefiles=find_modes(self.dump_dir)
		thefiles.sort()
		files_short=thefiles[::2]
		model=self.cb.get_model()
		model.clear()
		#self.cb.clear()
		self.cb.append_text("all")
		for i in range(0, len(files_short)):
			self.cb.append_text(str(files_short[i])+" nm")
		self.cb.set_active(0)
		self.cb.handler_unblock(self.cb_id)

	def update_cb_model(self):
		models=find_models()
		for i in range(0, len(models)):
			self.cb_model.append_text(models[i])

		used_model=inp_get_token_value("light.inp", "#light_model")
		if models.count(used_model)==0:
			used_model="exp"
			inp_update_token_value("light.inp", "#light_model","exp")

		self.cb_model.set_active(models.index(used_model))

	def __create_model(self):

		# create list store
		model = gtk.ListStore(
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
			  COLUMN_DEVICE, item[COLUMN_DEVICE],
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

		# Device
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited, model)
		renderer.set_data("column", COLUMN_DEVICE)

		column = gtk.TreeViewColumn("Active layer", renderer, text=COLUMN_DEVICE,
				       editable=COLUMN_EDITABLE)
		treeview.append_column(column)

	def callback_save_image(self, widget):
		dialog = gtk.FileChooserDialog("Save plot",
                               None,
                               gtk.FILE_CHOOSER_ACTION_SAVE,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		dialog.set_action(gtk.FILE_CHOOSER_ACTION_CREATE_FOLDER)

		filter = gtk.FileFilter()
		filter.set_name("png")
		filter.add_pattern("*.png")
		dialog.add_filter(filter)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			self.fig.savefig(dialog.get_filename())

		elif response == gtk.RESPONSE_CANCEL:
		    print 'Closed'
		dialog.destroy()


	def on_add_item_clicked(self, button, treeview):
		new_item = ["#mat", "100e-9", "pcbm","0","1",True]

		selection = treeview.get_selection()
		model, iter = selection.get_selected()

		path = model.get_path(iter)[0]
		print path
		#model.remove(iter)

		#del articles[ path ]

		articles.insert(path, new_item) #append(new_item)

		iter = model.insert(path) #append()
		model.set (iter,
		    COLUMN_LAYER, new_item[COLUMN_LAYER],
		    COLUMN_THICKNES, new_item[COLUMN_THICKNES],
		    COLUMN_MATERIAL, new_item[COLUMN_MATERIAL],
		    COLUMN_DEVICE, new_item[COLUMN_DEVICE],
		    COLUMN_EDITABLE, new_item[COLUMN_EDITABLE]
		)
		self.save_model(model)
		self.update_graph(model)

	def save_model(self, model):
		print "Saved"
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

	def callback_close(self, widget, data=None):
		self.hide()
		return True

	def on_remove_item_clicked(self, button, treeview):

		selection = treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
			model.remove(iter)

			del articles[ path ]

			self.save_model(model)
			self.update_graph(model)


	def callback_refresh(self, button,treeview):

		selection = treeview.get_selection()
		model, iter = selection.get_selected()

		self.save_model(model)
		self.update_graph(model)
		self.update_cb()


	def gen_main_menu(self, window,vbox):
		accel_group = gtk.AccelGroup()


		item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)

		menu_items = (
		    ( "/_File",         None,         None, 0, "<Branch>" ),
		    ( "/File/_Save...",     None, self.callback_save_image, 0, "<StockItem>", "gtk-save" ),
		    ( "/File/Refresh",     None, self.callback_refresh, 0 , "<ImageItem>"),
		    ( "/File/Close",     "<control>Q", self.callback_close, 0, "<StockItem>", "gtk-quit" ),

		    )

		item_factory.create_items(menu_items)


		window.add_accel_group(accel_group)

		menubar=item_factory.get_widget("<main>")
		menubar.show_all()
		vbox.pack_start(menubar, False, True, 0)


	def on_key_press_event(self,widget, event):
		keyname = gtk.gdk.keyval_name(event.keyval)
		if keyname == "c":
			if event.state == gtk.gdk.CONTROL_MASK:
				self.do_clip()

		self.fig.canvas.draw()

	def update_graph(self,model):
		cmd = self.exe_command+' --optics --zip_results'
		print cmd
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

		if column == COLUMN_DEVICE:
			#old_text = model.get_value(iter, column)
			articles[path][COLUMN_DEVICE] = new_text

			model.set(iter, column, articles[path][COLUMN_DEVICE])

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

	def do_clip(self):
		snap = self.canvas.get_snapshot()
		pixbuf = gtk.gdk.pixbuf_get_from_drawable(None, snap, snap.get_colormap(),0,0,0,0,snap.get_size()[0], snap.get_size()[1])
		clip = gtk.Clipboard()
		clip.set_image(pixbuf)

	def draw_graph(self,model):

		print "Drawing graph"

		self.layer_end=[]
		self.layer_name=[]

		n=0
		self.fig.clf()
		ax1 = self.fig.add_subplot(111)
		ax2 = ax1.twinx()
		x_pos=0.0
		layer=0
		color =['r','g','b','y','o','r','g','b','y','o']
		start=0.0

		for item in model:
			if item[COLUMN_DEVICE]=="0":
				start=start-float(item[COLUMN_THICKNES])
			else:
				break
		start=start*1e9

		x_pos=start
		for item in model:

			label=item[COLUMN_LAYER]
			layer_ticknes=item[COLUMN_THICKNES]
			layer_material=item[COLUMN_MATERIAL]
			device=item[COLUMN_DEVICE]

			delta=float(layer_ticknes)*1e9
			print os.getcwd()
			mat_file='./phys/'+layer_material+'/mat.inp'
			print mat_file
			myfile = open(mat_file)
			self.mat_file_lines = myfile.readlines()
			myfile.close()
			
			for ii in range(0, len(self.mat_file_lines)):
				self.mat_file_lines[ii]=self.mat_file_lines[ii].rstrip()

			x = [x_pos,x_pos+delta,x_pos+delta,x_pos]
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
			self.layer_end.append(x_pos)
			self.layer_name.append(layer_material)
			ax2.fill(x,lumo_shape, color[layer],alpha=0.4)
			ax2.text(x_pos-delta/1.5, lumo-0.3, layer_material.upper())

			if homo!=0.0:
				homo_shape = [homo,homo,homo_delta,homo_delta]
				ax2.fill(x,homo_shape, color[layer],alpha=0.4)

			layer=layer+1

			n=n+1

		ax1.set_ylabel('Photon density')
		ax1.set_xlabel('Position (nm)')
		ax2.set_ylabel('Energy (eV)')
		ax2.set_xlim([start, x_pos])
		#ax2.axis(max=)#autoscale(enable=True, axis='x', tight=None)
		if os.path.isfile("./light_dump.zip"):
			zf = zipfile.ZipFile("./light_dump.zip", 'r')
			lines = zf.read(self.optical_mode_file).split("\n")

			zf.close()
			xx=[]
			yy=[]
			for i in range(0, len(lines)):
				if lines[i]!="":
					line=lines[i].split(" ")
					xx.append(float(line[0]))
					yy.append(float(line[1]))
			t = asarray(xx)
			s = asarray(yy)

			t=t*1e9
			ax1.plot(t,s, 'black', linewidth=3 ,alpha=0.5)


		self.fig.tight_layout()

	def on_changed(self, widget, model):
		cb_text=widget.get_active_text()
		print "Roderick=",cb_text
		if cb_text=="all":
			self.optical_mode_file="light_1d_photons_tot_norm.dat"
		else:
			self.optical_mode_file="light_1d_"+cb_text[:-3]+"_photons_norm.dat"
		print self.optical_mode_file
		self.draw_graph(model)
		self.fig.canvas.draw()

	def on_cb_model_changed(self, widget):
		cb_text=widget.get_active_text()
		inp_update_token_value("light.inp", "#light_model", cb_text)

	def callback_help(self, widget, data=None):
		cmd = 'firefox http://www.roderickmackenzie.eu/opvdm_wiki.html'
		os.system(cmd)

	def wow(self,exe_command):
		find_models()
		self.main_vbox=gtk.VBox()
		self.gen_main_menu(self,self.main_vbox)
		toolbar = gtk.Toolbar()

		toolbar.set_style(gtk.TOOLBAR_ICONS)
		toolbar.set_size_request(-1, 50)
		self.main_vbox.pack_start(toolbar, False, False, 0)


		#self.optical_mode_file=self.dump_dir+"/light_1d_photons_tot_norm.dat"
		self.optical_mode_file="light_1d_photons_tot_norm.dat"
		
		self.exe_command=exe_command
		self.edit_list=[]
		self.line_number=[]

		print "loading ",os.getcwd(),self.config_file
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
			device=self.lines[pos] 	#read thicknes

			articles.append([ label, str(layer_ticknes),str(layer_material),str(device), True ])

			layer=layer+1

			#print "out -> %s %i",out_text,len(self.edit_list)

			n=n+1

		model = self.__create_model()

		self.cb = gtk.combo_box_new_text()
		self.cb.set_wrap_width(5)
		self.cb_id=self.cb.connect("changed", self.on_changed,model)
		self.update_cb()


		self.cb_model = gtk.combo_box_new_text()
		self.cb_model.set_wrap_width(5)
		self.cb_model.connect("changed", self.on_cb_model_changed)
		self.update_cb_model()

		self.fig = Figure(figsize=(5,4), dpi=100)
		self.canvas = FigureCanvas(self.fig)  # a gtk.DrawingArea
	
		cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)

		self.canvas.figure.patch.set_facecolor('white')
		self.canvas.set_size_request(900, 400)
		self.canvas.show()
		self.main_vbox.pack_start(self.canvas, True, True, 0)
		self.connect('key_press_event', self.on_key_press_event)
		#attach(canvas, 0, 3, gui_pos, gui_pos+1)

		# create model

		gui_pos=gui_pos+1


		add_button = gtk.Button("Add layer",gtk.STOCK_ADD)
		add_button.show()

		delete_button = gtk.Button("Delete layer",gtk.STOCK_DELETE)
		delete_button.show()

		# create tree view
		treeview = gtk.TreeView(model)
		treeview.set_size_request(500, 150)
		treeview.set_rules_hint(True)
		treeview.get_selection().set_mode(gtk.SELECTION_SINGLE)

		tool_bar_pos=0
		save = gtk.ToolButton(gtk.STOCK_SAVE)
		save.connect("clicked", self.callback_save_image)
		toolbar.insert(save, tool_bar_pos)
		toolbar.show_all()
		tool_bar_pos=tool_bar_pos+1

		image = gtk.Image()
   		image.set_from_file(self.icon_theme.lookup_icon("media-playback-start", 32, 0).get_filename())
		refresh = gtk.ToolButton(image)
		refresh.connect("clicked", self.callback_refresh,treeview)
		toolbar.insert(refresh, tool_bar_pos)
		toolbar.show_all()
		tool_bar_pos=tool_bar_pos+1

		ti_light = gtk.ToolItem()
		lable=gtk.Label("Optical mode:")
		lable.show()
	        ti_hbox = gtk.HBox(False, 2)
		ti_hbox.show()
        
	        ti_hbox.pack_start(lable, False, False, 0)
	        ti_hbox.pack_start(self.cb, False, False, 0)
		self.cb.show()

		lable=gtk.Label("Optical model:")
		lable.show()
	        ti_hbox.pack_start(lable, False, False, 0)
		ti_hbox.pack_start(self.cb_model, False, False, 0)
		self.cb_model.show()
		

		ti_light.add(ti_hbox);
		toolbar.insert(ti_light, tool_bar_pos)
		ti_light.show()

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
		close.connect("clicked", self.callback_close,treeview)
		toolbar.insert(close, tool_bar_pos)
		close.show()
		tool_bar_pos=tool_bar_pos+1

	        hbox = gtk.HBox(False, 5)


	        hbox.pack_start(add_button, False, False, 0)
	        hbox.pack_start(delete_button, False, False, 0)
		hbox.show()
		#self.attach(hbox, 2, 4, gui_pos, gui_pos+1,gtk.SHRINK ,gtk.SHRINK)
		self.main_vbox.pack_start(hbox, False, False, 0)
		gui_pos=gui_pos+1



		add_button.connect("clicked", self.on_add_item_clicked, treeview)
		delete_button.connect("clicked", self.on_remove_item_clicked, treeview)


		self.__add_columns(treeview)

		#sw.add()
		
		#self.attach(treeview, 0, 3, gui_pos, gui_pos+1,gtk.SHRINK ,gtk.SHRINK)
		self.main_vbox.pack_start(treeview, False, False, 0)
		gui_pos=gui_pos+1

		self.connect("delete-event", self.callback_close) 

		treeview.show()
		self.add(self.main_vbox)
		self.main_vbox.show()
		self.draw_graph(model)
		self.set_icon_from_file(find_data_file("gui/image.jpg"))
		self.set_title("Optical Model - (www.opvdm.com)")
		self.set_position(gtk.WIN_POS_CENTER)



