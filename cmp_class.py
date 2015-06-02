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
from inp import inp_update_token_value
from scan_item import scan_item
from scan_item import scan_item_add
from util import find_data_file
from numpy import *
from matplotlib.figure import Figure
from numpy import arange, sin, pi
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib import ticker
import matplotlib.cm as cm
from matplotlib.mlab import griddata
import glob
from matplotlib import rcParams
from util import time_with_units
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
from plot_widget import plot_widget
from util import zip_get_data_file
from window_list import windows
from plot_state import plot_state
from plot_io import plot_load_info

class cmp_class(gtk.Window):
	mix_y=None
	max_y=None
	max_z=1e24
	icon_theme = gtk.icon_theme_get_default()
	def check_2d_file(self,name):
		mapfiles=["pt_map","nt_map"]
		filename=os.path.basename(name)
		for i in range(len(filename)-1,0,-1):
			if filename[i]=="_":
				break
		data=filename[:i]
		count=mapfiles.count(data)
		if count==1:
			return True
		else:
			return False

	def callback_close(self, widget, data=None):
		self.win_list.update(self,"cmp_class")
		return False

	def load_data_file(self):
		found, self.lines = zip_get_data_file(os.path.join(self.entry0.get_active_text(),"dump_slice_info.dat"))
		if found==False:
			found, self.lines = zip_get_data_file(os.path.join(self.entry1.get_active_text(),"dump_slice_info.dat"))

		if found==False:
			self.lines=["none"]
			print "Can not open","dump_slice_info.dat"
			return False

		for i in range(0, len(self.lines)):
			self.lines[i]=self.lines[i].rstrip()

		self.adj1.set_upper(len(self.lines))
		return True

	def do_clip(self):

		snap = self.canvas.get_snapshot()
		pixbuf = gtk.gdk.pixbuf_get_from_drawable(None, snap, snap.get_colormap(),0,0,0,0,snap.get_size()[0], snap.get_size()[1])
		clip = gtk.Clipboard()
		clip.set_image(pixbuf)


	def on_key_press_event(self,widget, event):
		keyname = gtk.gdk.keyval_name(event.keyval)
		if gtk.gdk.keyval_name(event.keyval) == "c":
			if event.state == gtk.gdk.CONTROL_MASK:
				self.do_clip()

	def callback_set_min_max(self, data, widget):

		path0=self.entry0.get_active_text()
		my_max=-1e40
		my_min=1e40
		print "Rod",self.file_names
		for ii in range(0,len(self.file_names)):
			for i in range(0,len(self.lines)):
				self.update(i)
				t=[]
				s=[]
				z=[]
				if self.plot.read_data_file(t,s,z,ii) == True:
					temp_max=max(s)
					temp_min=min(s)

					if temp_max>my_max:
						my_max=temp_max

					if temp_min<my_min:
						my_min=temp_min

		self.plot.ymax=my_max
		self.plot.ymin=my_min

	def update(self,value):
		
		files=self.entry2.get_text().split()
		value=int(value)

		if value>len(self.lines) or self.lines[0]=="none":
			return


		plus=files[0].count("%")


		path0=self.entry0.get_active_text()
		path1=self.entry1.get_active_text()
		self.file_names=[]
		labels=[]
		zero_frame=[]

		if plus==0:
			title=self.lines[value].split()
			self.plot.plot_title="Voltage="+title[0]+" time="+time_with_units(float(title[1]))
			for i in range(0,len(files)):
				self.file_names.append(os.path.join(path0,files[i]+"_"+str(int(value))+".dat"))
				zero_frame.append(os.path.join(path0,files[i]+"_0.dat"))
				labels.append(files[i])

				self.file_names.append(os.path.join(path1,files[i]+"_"+str(int(value))+".dat"))
				zero_frame.append(os.path.join(path1,files[i]+"_0.dat"))
				labels.append("")
		else:
			for i in range(0,len(files)):
				if files[i].count("%")!=1:
					break
				base_name, frame= files[i].split("%")
				pos=int(frame)+value
				if pos<len(self.lines):
					title=time_with_units(float(self.lines[pos].split()[1]))
				else:
					title=""

				self.file_names.append(os.path.join(path0,base_name+"_"+str(int(pos))+".dat"))
				zero_frame.append(os.path.join(path0,base_name+"_0.dat"))
				labels.append(title)

		plot_id=[]
		if self.multi_plot==False:
			for i in range(0,len(self.file_names)):
				plot_id.append(0)
		else:
			for i in range(0,len(self.file_names)):
				plot_id.append(i)
		
		exp_files=self.entry3.get_text().split()
		for i in range(0,len(exp_files)):
			self.file_names.append(exp_files[i])
			zero_frame.append("")
			labels.append("")
			plot_id.append(i)
		self.plot.zero_frame_list=zero_frame

		print self.file_names
		print plot_id
		self.plot.plot_labels(labels)
		self.plot.set_plot_ids(plot_id)
		self.plot.load_data(self.file_names,self.plot_token,"","")



	def callback_scale(self, adj):
		print "here",type(self.plot.plot_token.key_units)

		plot_load_info(self.plot_token,self.file_names[0])
		print "here1",type(self.plot.plot_token.key_units)
		self.update(self.adj1.value)
		print "here2",type(self.plot.plot_token.key_units)
		self.plot.do_plot()


	def callback_edit(self,data):
		print os.getcwd() 
		a = open(os.path.join(self.sim_dir,"gui_cmp_config.inp"), "w")
		a.write(self.entry0.get_active_text()+"\n")
		a.write(self.entry1.get_active_text()+"\n")
		a.write(self.entry2.get_text()+"\n")
		a.write(self.entry3.get_text()+"\n")
		a.close()
		self.plot.gen_colors(2)
		self.load_data_file()
		print "Saved"

	def config_load(self):
		try:
	 		f = open(os.path.join(self.sim_dir,"gui_cmp_config.inp"), "r")
			lines = f.readlines()
			f.close()

			for i in range(0, len(lines)):
				lines[i]=lines[i].rstrip()

			if self.snapshot_list.count(lines[0])!=0:
				self.entry0.set_active(self.snapshot_list.index(lines[0]))
			else:
				self.entry0.set_active(0)

			if self.snapshot_list.count(lines[1])!=0:
				self.entry1.set_active(self.snapshot_list.index(lines[1]))
			else:
				self.entry1.set_active(0)

			self.entry2.set_text(lines[2])
			self.entry3.set_text(lines[3])
		except:
			self.entry0.set_active(0)
			self.entry1.set_active(0)
			self.entry2.set_text("n p")
			self.entry3.set_text("")

	def save_image(self,file_name):
		fileName, ext = os.path.splitext(file_name)

		if (ext==".jpg"):
			self.canvas.figure.savefig(file_name)
		elif ext==".avi":
			out_file=os.path.join(os.getcwd(),"snapshots")
			jpgs=""
			for i in range(0,int(self.adj1.get_upper())):
				self.update(i)
				self.plot.do_plot()
				image_name=os.path.join(out_file,"image_"+str(i)+".jpg")
				self.canvas.figure.savefig(image_name)
				jpgs=jpgs+" mf://"+image_name

			os.system("mencoder "+jpgs+" -mf type=jpg:fps=1.0 -o "+file_name+" -ovc lavc -lavcopts vcodec=mpeg1video:vbitrate=800")
			#msmpeg4v2
		else:
			print "Unknown file extention"

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

		filter = gtk.FileFilter()
		filter.set_name(".avi")
		filter.add_pattern("*.avi")
		dialog.add_filter(filter)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			dialog.hide()
			file_name=dialog.get_filename()

			#print os.path.splitext(file_name)[1]
			if os.path.splitext(file_name)[1]:
				self.save_image(file_name)
			else:
				filter=dialog.get_filter()
				self.save_image(os.path.join(file_name,filter.get_name()))
			
		elif response == gtk.RESPONSE_CANCEL:
		    print 'Closed, no files selected'
		dialog.destroy()

	def callback_help(self, widget, data=None):
		webbrowser.open('http://www.roderickmackenzie.eu/opvdm_wiki.html')


	def callback_toggle_subtract(self, widget, data):
		self.plot.zero_frame_enable=data.get_active()
		self.update(self.adj1.value)
		print "CONVERTh!!!!!!!!!!!",type(self.plot.plot_token.key_units)
		self.plot.do_plot()

	def callback_multi_plot(self, data, widget):
		if widget.get_active()==True:
			self.multi_plot=True
		else:
			self.multi_plot=False
		self.update(self.adj1.value)
		print "CONVERTi!!!!!!!!!!!",type(self.plot.plot_token.key_units)
		self.plot.do_plot()

	def update_snapshots_dir(self):

		matches = []
		for root, dirnames, filenames in os.walk(self.sim_dir, followlinks=True):
			for filename in dirnames:
				mydir=os.path.join(root,filename)
				if mydir.endswith("snapshots")==True:
					matches.append(os.path.join(root, filename))

		return matches

	def init(self,sim_dir,exe_command):
		self.plot_token=plot_state()
		self.sim_dir=sim_dir
		self.win_list=windows()
		self.win_list.load()
		self.win_list.set_window(self,"cmp_class")

		self.snapshot_list=self.update_snapshots_dir()
		vbox=gtk.VBox()

		self.multi_plot=False

		self.log_scale_y="auto"

		self.plot=plot_widget()
		self.plot.init(self)

		accel_group = gtk.AccelGroup()
		item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)

		menu_items = (
		    ( "/_Options",         None,         None, 0, "<Branch>" ),
		    ( "/Options/_Subtract 0th frame",     None, self.callback_toggle_subtract, 0, "<ToggleItem>", "gtk-save" ),
		    ( "/_Axis/_Multiplot",     None, self.callback_multi_plot, 0, "<ToggleItem>", "gtk-save" ),
		    ( "/_Axis/_Set y axis to maximum",     None, self.callback_set_min_max, 0, "<ToggleItem>", "gtk-save" ),
		    )

		self.plot.item_factory.create_items(menu_items)


		#self.add_accel_group(accel_group)

		#menubar=item_factory.get_widget("<main>")
		#menubar.show_all()
		#vbox.pack_start(menubar, False, True, 0)



	        image = gtk.Image()
   		image.set_from_file(self.icon_theme.lookup_icon("video", 32, 0).get_filename())
		self.video = gtk.ToolButton(image)
		self.plot.toolbar.add(self.video)
		self.video.show()
		self.video.connect("clicked", self.callback_save)

	        image = gtk.Image()
   		image.set_from_file(find_data_file(os.path.join("gui","scale.png")))
		self.scale = gtk.ToolButton(image)
		self.plot.toolbar.add(self.scale)
		#self.scale.connect("clicked", self.callback_auto_scale)


		sep = gtk.SeparatorToolItem()
		sep.set_draw(False)
		sep.set_expand(True)
		self.plot.toolbar.add(sep)
		sep.show()


		help = gtk.ToolButton(gtk.STOCK_HELP)
		self.plot.toolbar.add(help)
		help.connect("clicked", self.callback_help)
		help.show()

		close = gtk.ToolButton(gtk.STOCK_QUIT)
		close.connect("clicked", self.callback_close)
		self.plot.toolbar.add(close)
		close.show()

		self.connect("delete-event", self.callback_close) 

		self.plot.toolbar.show_all()


		self.canvas=self.plot.canvas 
		self.plot.show()
		vbox.add(self.plot)

		#adjust
		self.adj1 = gtk.Adjustment(0.0, 0.0, 100, 1, 1.0, 1.0)
		self.adj1.connect("value_changed", self.callback_scale)
		vscale = gtk.HScale(self.adj1)
		vscale.set_update_policy(gtk.UPDATE_CONTINUOUS)
		vscale.set_digits(1)
		vscale.set_value_pos(gtk.POS_TOP)
		vscale.set_draw_value(True)
		vscale.set_size_request(200, 40)
		vscale.set_digits(0)
		vbox.pack_start(vscale, False, False, 10)


		sim_vbox=gtk.VBox()
		primary_hbox=gtk.HBox()

		text=gtk.Label("Primary dir")
		primary_hbox.add(text)

		self.entry0 = gtk.combo_box_entry_new_text()
		self.entry0.show()


		for i in range(0,len(self.snapshot_list)):
			self.entry0.append_text(self.snapshot_list[i])

		primary_hbox.add(self.entry0)
		sim_vbox.add(primary_hbox)

		secondary_hbox=gtk.HBox()

		text=gtk.Label("Secondary dir")
		secondary_hbox.add(text)

		self.entry1 = gtk.combo_box_entry_new_text()
		self.entry1.show()

		for i in range(0,len(self.snapshot_list)):
			self.entry1.append_text(self.snapshot_list[i])

		secondary_hbox.add(self.entry1)
		sim_vbox.add(secondary_hbox)

		sim_vbox.show()
		#hbox.set_size_request(-1, 30)
		vbox.pack_start(sim_vbox, False, False, 0)

		hbox2=gtk.HBox()
		text=gtk.Label("Files to plot")
		hbox2.add(text)
		self.entry2 = gtk.Entry()
		self.entry2.set_text("pt_map nt_map")
		self.entry2.show()
		hbox2.add(self.entry2)
		hbox2.set_size_request(-1, 30)
		vbox.pack_start(hbox2, False, False, 0)

		hbox3=gtk.HBox()
		text=gtk.Label("Exprimental data")
		hbox3.add(text)
		self.entry3 = gtk.Entry()
		self.entry3.set_text("")
		self.entry3.show()
		hbox3.add(self.entry3)
		hbox3.set_size_request(-1, 30)
		vbox.pack_start(hbox3, False, False, 0)

		self.update_button = gtk.Button()
		self.update_button.set_label("Update")
		self.update_button.show()
		self.update_button.connect("clicked", self.callback_scale)
		vbox.add(self.update_button)

		self.config_load()
		slice_info_file=os.path.join(self.entry0.get_active_text(),"dump_slice_info.dat")
		print "Rod==",slice_info_file
		found, lines = zip_get_data_file(slice_info_file)
		if found==False:
			md = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION,  gtk.BUTTONS_YES_NO, "No slice data has been written to disk.  You need to re-run the simulation with the dump_slices set to 1.  Would you like to do this now?  Note: This generates lots of files and will slow down the simulation.")

#gtk.MessageDialog(self, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, 
		# gtk.BUTTONS_CLOSE, "Should I remove the simulation directory "+dir_to_del)
			response = md.run()

			if response == gtk.RESPONSE_YES:
				inp_update_token_value("dump.inp", "#dump_1d_slices", "1",1)
				cmd = exe_command
				ret= os.system(cmd)

			md.destroy()




		self.load_data_file()

		self.entry0.connect("changed", self.callback_edit)
		self.entry1.connect("changed", self.callback_edit)
		self.entry2.connect("changed", self.callback_edit)
		self.entry3.connect("changed", self.callback_edit)



		vbox.show_all()
		self.add(vbox)

		ret=self.load_data_file()
		
		self.update(0)
		if ret==True:
			self.plot.do_plot()
			print "CONVERTj!!!!!!!!!!!",type(self.plot.plot_token.key_units)
		#["Ec","Ev","Fn","Fp"]
		self.set_border_width(10)
		self.set_title("Compare")
		self.set_icon_from_file(find_data_file(os.path.join("gui/image.jpg")))

		self.connect('key_press_event', self.on_key_press_event)

		self.show()
		

