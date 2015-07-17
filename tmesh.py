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
from inp import inp_load_file
from inp import inp_read_next_item
from gui_util import dlg_get_text
from inp import inp_get_token_value
import matplotlib.mlab as mlab
from debug import debug_mode
from inp import inp_write_lines_to_file

(
SEG_LENGTH,
SEG_DT,
SEG_VOLTAGE,
SEG_MUL,
SEG_SUN,
SEG_LASER
) = range(6)

mesh_articles = []

class tab_time_mesh(gtk.Window):
	lines=[]
	edit_list=[]

	line_number=[]
	save_file_name=""

	file_name=""
	name=""
	visible=1

	def save_data(self):
		out_text=[]
		out_text.append("#start_time")
		out_text.append(str(float(self.start_time)))
		out_text.append("#fs_laser_time")
		out_text.append(str(float(self.fs_laser_time)))
		out_text.append("#time_segments")
		out_text.append(str(int(len(self.store))))
		i=0
		for line in self.store:
			out_text.append("#time_segment"+str(i)+"_len")
			out_text.append(str(line[SEG_LENGTH]))
			out_text.append("#time_segment"+str(i)+"_dt")
			out_text.append(str(line[SEG_DT]))
			out_text.append("#time_segment"+str(i)+"_voltage")
			out_text.append(str(line[SEG_VOLTAGE]))
			out_text.append("#time_segment"+str(i)+"_mul")
			out_text.append(str(line[SEG_MUL]))
			out_text.append("#time_segment"+str(i)+"_sun")
			out_text.append(str(line[SEG_SUN]))
			out_text.append("#time_segment"+str(i)+"_laser")
			out_text.append(str(line[SEG_LASER]))
			i=i+1

		out_text.append("#ver")
		out_text.append("1.0")
		out_text.append("#end")
		
		inp_write_lines_to_file(os.path.join(os.getcwd(),"time_mesh_config.inp"),out_text)

	def callback_add_section(self, widget, treeview):
		data=["0.0", "0.0", "0.0", "0.0", "0.0", "0.0"]
		selection = treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
			self.store.insert(path+1,data)
		else:
			self.store.append(data)

		self.update_mesh()
		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def callback_remove_item(self, button, treeview):

		selection = treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
			model.remove(iter)

		self.update_mesh()
		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def callback_move_down(self, widget, treeview):

		selection = treeview.get_selection()
		model, iter = selection.get_selected()

		if iter:
			path = model.get_path(iter)[0]
 			self.store.move_after( iter,self.store.iter_next(iter))

		self.update_mesh()
		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def callback_start_time(self, widget, treeview):
		new_time=dlg_get_text( "Enter the start time of the simulation", str(self.start_time))

		if new_time!=None:
			self.start_time=float(new_time)
			self.update_mesh()
			self.draw_graph()
			self.fig.canvas.draw()
			self.save_data()


	def callback_laser(self, widget, treeview):
		new_time=dlg_get_text( "Enter the time at which the laser pulse will fire (-1) to turn it off", str(self.fs_laser_time))

		if new_time!=None:
			self.fs_laser_time=float(new_time)
			self.update_mesh()
			self.draw_graph()
			self.fig.canvas.draw()
			self.save_data()

	def on_cell_edited_length(self, cell, path, new_text, model):
		model[path][SEG_LENGTH] = new_text
		self.update_mesh()
		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def on_cell_edited_dt(self, cell, path, new_text, model):
		print "Rod",path
		model[path][SEG_DT] = new_text
		self.update_mesh()
		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def on_cell_edited_voltage(self, cell, path, new_text, model):
		model[path][SEG_VOLTAGE] = new_text
		self.update_mesh()
		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def on_cell_edited_sun(self, cell, path, new_text, model):
		model[path][SEG_SUN] = new_text
		self.update_mesh()
		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def on_cell_edited_laser(self, cell, path, new_text, model):
		model[path][SEG_LASER] = new_text
		self.update_mesh()
		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def on_cell_edited_mul(self, cell, path, new_text, model):
		model[path][SEG_MUL] = new_text
		self.update_mesh()
		self.draw_graph()
		self.fig.canvas.draw()
		self.save_data()

	def update_graph(self):
		cmd = self.exe_command+' --onlypos'
		ret= os.system(cmd)
		self.fig.clf()
		self.draw_graph()
		self.fig.canvas.draw()

	def gaussian(self,x, mu, sig):
		return exp(-power(x - mu, 2.) / (2 * power(sig, 2.)))

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

		self.ax1.set_ylabel('Magnitude (au)')
		#ax2.set_ylabel('Energy (eV)')
		self.ax1.set_xlabel('Time (s)')
		sun, = self.ax1.plot(self.time,self.sun, 'go-', linewidth=3 ,alpha=1.0)
		laser, = self.ax1.plot(self.time,self.laser, 'bo-', linewidth=3 ,alpha=1.0)

		if self.fs_laser_time!=-1:
			if len(self.time)>2:
				dt=(self.time[len(self.time)-1]-self.time[0])/100
				start=self.fs_laser_time-dt*5
				stop=self.fs_laser_time+dt*5
				x = linspace(start,stop,100)
				y=self.gaussian(x,self.fs_laser_time,dt)
				#print y
				fs_laser, = self.ax1.plot(x,y, 'g-', linewidth=3 ,alpha=1.0)

		self.ax1.ticklabel_format(style='sci', axis='x', scilimits=(0,0))

		self.ax2 = self.ax1.twinx()
		voltage, = self.ax2.plot(self.time,self.voltage, 'ro-', linewidth=3 ,alpha=1.0)
		self.ax2.set_ylabel('Voltage (Volts)')
		self.fig.legend((voltage, sun, laser), ('Voltage', 'Sun', 'Laser'), 'upper right')


	def save_image(self,file_name):
		self.fig.savefig(file_name)	
		

	def callback_close(self, widget, data=None):
		self.hide()
		return True

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

	def create_model(self):
		store = gtk.ListStore(str, str, str, str, str, str)

		for line in self.list:
			store.append([str(line[SEG_LENGTH]), str(line[SEG_DT]), str(line[SEG_VOLTAGE]), str(line[SEG_MUL]), str(line[SEG_SUN]), str(line[SEG_LASER])])

		return store

	def create_columns(self, treeview):

		model=treeview.get_model()
		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited_length, model)
		renderer.set_property('editable', True)
		column = gtk.TreeViewColumn("Length", renderer, text=SEG_LENGTH)
		column.set_sort_column_id(SEG_LENGTH)
		treeview.append_column(column)

		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited_dt, model)
		column = gtk.TreeViewColumn("dt", renderer, text=SEG_DT)
		renderer.set_property('editable', True)
		column.set_sort_column_id(SEG_DT)
		treeview.append_column(column)

		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited_voltage, model)
		column = gtk.TreeViewColumn("Voltage", renderer, text=SEG_VOLTAGE)
		renderer.set_property('editable', True)
		column.set_sort_column_id(SEG_VOLTAGE)
		treeview.append_column(column)

		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited_mul, model)
		renderer.set_property('editable', True)
		column = gtk.TreeViewColumn("Multiply", renderer, text=SEG_MUL)
		column.set_sort_column_id(SEG_MUL)
		treeview.append_column(column)

		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited_sun, model)
		renderer.set_property('editable', True)
		column = gtk.TreeViewColumn("Sun", renderer, text=SEG_SUN)
		column.set_sort_column_id(SEG_SUN)
		if debug_mode()==False:
			column.set_visible(False)
		treeview.append_column(column)

		renderer = gtk.CellRendererText()
		renderer.connect("edited", self.on_cell_edited_laser, model)
		renderer.set_property('editable', True)
		column = gtk.TreeViewColumn("Laser", renderer, text=SEG_LASER)
		column.set_sort_column_id(SEG_LASER)
		if debug_mode()==False:
			column.set_visible(False)
		treeview.append_column(column)

	def load_data(self):
		lines=[]
		inp_load_file(lines,"time_mesh_config.inp")

		pos=0
		token,value,pos=inp_read_next_item(lines,pos)
		self.start_time=float(value)

		token,value,pos=inp_read_next_item(lines,pos)
		self.fs_laser_time=float(value)

		token,value,pos=inp_read_next_item(lines,pos)
		self.segments=int(value)

		self.list=[]
		for i in range(0, self.segments):
			token,length,pos=inp_read_next_item(lines,pos)
			token,dt,pos=inp_read_next_item(lines,pos)
			token,voltage,pos=inp_read_next_item(lines,pos)
			token,mul,pos=inp_read_next_item(lines,pos)
			token,sun,pos=inp_read_next_item(lines,pos)
			token,laser,pos=inp_read_next_item(lines,pos)
			self.list.append((length,dt,voltage,mul,sun,laser))

		print self.list

	def update_mesh(self):
		self.laser=[]
		self.sun=[]
		self.voltage=[]
		self.time=[]
		self.fs_laser=[]
		pos=self.start_time
		fired=False

		laser_pulse_width=float(inp_get_token_value("optics.inp", "#laser_pulse_width"))


		for line in self.store:
			end_time=pos+float(line[SEG_LENGTH])
			dt=float(line[SEG_DT])
			voltage=float(line[SEG_VOLTAGE])
			mul=float(line[SEG_MUL])
			sun=float(line[SEG_SUN])
			laser=float(line[SEG_LASER])

			if dt!=0.0 and mul!=0.0:
				while(pos<end_time):
					self.time.append(pos)
					self.laser.append(laser)
					self.sun.append(sun)
					self.voltage.append(voltage)
					self.fs_laser.append(0.0)
					pos=pos+dt

					if fired==False:
						if pos>self.fs_laser_time:
							fired=True
							self.fs_laser[len(self.fs_laser)-1]=laser_pulse_width/dt

					dt=dt*mul

		a = open("time_mesh.inp", "w")
		a.write(str(len(self.time))+"\n")
		for i in range(0,len(self.time)):

			a.write(str(self.time[i])+" "+str(self.laser[i])+" "+str(self.sun[i])+" "+str(self.voltage[i])+" "+str(self.fs_laser[i])+"\n")

		a.close()
	def init(self):
		self.fig = Figure(figsize=(5,4), dpi=100)
		self.ax1=None
		self.show_key=True
		self.hbox=gtk.HBox()
		self.exe_command , exe_name  =  set_exe_command()
		self.edit_list=[]
		self.line_number=[]
		gui_pos=0

		self.list=[]

		self.load_data()

		gui_pos=gui_pos+1

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

		self.store = self.create_model()
		treeview = gtk.TreeView(self.store)

		tool_bar_pos=0
		save = gtk.ToolButton(gtk.STOCK_SAVE)
		tooltips.set_tip(save, "Save image")
		save.connect("clicked", self.callback_save)
		toolbar.insert(save, tool_bar_pos)
		tool_bar_pos=tool_bar_pos+1

		add_section = gtk.ToolButton(gtk.STOCK_ADD)
		tooltips.set_tip(add_section, "Add section")
		add_section.connect("clicked", self.callback_add_section,treeview)
		toolbar.insert(add_section, tool_bar_pos)
		tool_bar_pos=tool_bar_pos+1

		add_section = gtk.ToolButton(gtk.STOCK_CLEAR)
		tooltips.set_tip(add_section, "Add section")
		add_section.connect("clicked", self.callback_remove_item,treeview)
		toolbar.insert(add_section, tool_bar_pos)
		tool_bar_pos=tool_bar_pos+1

		move_down = gtk.ToolButton(gtk.STOCK_GO_DOWN)
		tooltips.set_tip(move_down, "Move down")
		move_down.connect("clicked", self.callback_move_down,treeview)
		toolbar.insert(move_down, tool_bar_pos)
		tool_bar_pos=tool_bar_pos+1

		if debug_mode()==True:
			image = gtk.Image()
	   		image.set_from_file(find_data_file("gui/laser.png"))
			laser = gtk.ToolButton(image)
			tooltips.set_tip(laser, "Laser start time")
			laser.connect("clicked", self.callback_laser,treeview)
			toolbar.insert(laser, tool_bar_pos)
			tool_bar_pos=tool_bar_pos+1

			image = gtk.Image()
	   		image.set_from_file(find_data_file("gui/start.png"))
			start = gtk.ToolButton(image)
			tooltips.set_tip(start, "Simulation start time")
			start.connect("clicked", self.callback_start_time,treeview)
			toolbar.insert(start, tool_bar_pos)
			tool_bar_pos=tool_bar_pos+1

		plot_toolbar = NavigationToolbar(canvas, self)
		plot_toolbar.show()
		box=gtk.HBox(True, 1)
		box.set_size_request(500,-1)
		box.show()
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
		self.vbox=gtk.VBox()
		self.vbox.pack_start(toolbar, False, True, 0)
		self.vbox.pack_start(toolbar, True, True, 0)
		tool_bar_pos=tool_bar_pos+1



		canvas.set_size_request(700,400)
		self.vbox.pack_start(canvas, True, True, 0)


		treeview.set_rules_hint(True)

		self.create_columns(treeview)

		self.vbox.pack_start(treeview, False, False, 0)
		#treeview.show()

		self.vbox.show()

		self.update_mesh()
		self.draw_graph()

		self.save_data()

		self.add(self.vbox)
		self.set_title("Time domain mesh editor - (www.opvdm.com)")
		self.set_icon_from_file(find_data_file("gui/time.png"))
		self.connect("delete-event", self.callback_close)
		self.set_position(gtk.WIN_POS_CENTER)


