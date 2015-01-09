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
from plot import plot_data
from matplotlib import rcParams
from util import time_with_units
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
from plot_widget import plot_widget
from util import read_xy_data
from util import zip_get_data_file
class cmp_class(gtk.Window):
	mix_y=None
	max_y=None
	max_z=1e24
	mygraph=plot_data()
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
		self.hide()
		return True

	def load_data_file(self):
		found, self.lines = zip_get_data_file(self.entry0.get_text()+"dump_slice_info.dat")
		if found==False:
			found, self.lines = zip_get_data_file(self.entry1.get_text()+"dump_slice_info.dat")

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


	def update(self,files,value):
		value=int(value)
		if value>len(self.lines) or self.lines[0]=="none":
			#md = gtk.MessageDialog(self, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,  gtk.BUTTONS_CLOSE, "Re-run the simulation with 'dump all slices' set to one to use this tool.")
        		#md.run()
        		#md.destroy()
			return


		plus=files[0].count("+")


		path0=self.entry0.get_text()
		path1=self.entry1.get_text()
		file_names=[]
		labels=[]
		zero_frame=[]

		if plus==0:
			title=self.lines[value].split()
			self.plot.plot_title="Voltage="+title[0]+" time="+time_with_units(float(title[1]))
			for i in range(0,len(files)):
				file_names.append(path0+files[i]+"_"+str(int(value))+".dat")
				zero_frame.append(path0+files[i]+"_0.dat")
				labels.append(files[i])

				file_names.append(path1+files[i]+"_"+str(int(value))+".dat")
				zero_frame.append(path1+files[i]+"_0.dat")
				labels.append("")
		else:
			for i in range(0,len(files)):
				if files[i].count("+")!=1:
					break
				base_name, frame= files[i].split("+")
				pos=int(frame)+value
				if pos<len(self.lines):
					title=time_with_units(float(self.lines[pos].split()[1]))
				else:
					title=""

				file_names.append(path0+base_name+"_"+str(int(pos))+".dat")
				zero_frame.append(path0+base_name+"_0.dat")
				labels.append(title)

		plot_id=[]
		if self.multi_plot==False:
			for i in range(0,len(file_names)):
				plot_id.append(0)
		else:
			for i in range(0,len(file_names)):
				plot_id.append(i)

		exp_files=self.entry3.get_text().split()
		for i in range(0,len(exp_files)):
			file_names.append(exp_files[i])
			zero_frame.append("")
			labels.append("")
			plot_id.append(i)
		self.plot.zero_frame_list=zero_frame
		self.plot.load_data(file_names,plot_id,labels,None)



	def callback_scale(self, adj):
		self.update(self.entry2.get_text().split(),self.adj1.value)


	def callback_edit(self,data):
		print os.getcwd() 
		a = open("./gui_cmp_config.inp", "w")
		a.write(self.entry0.get_text()+"\n")
		a.write(self.entry1.get_text()+"\n")
		a.write(self.entry2.get_text()+"\n")
		a.write(self.entry3.get_text()+"\n")
		a.close()
		self.plot.gen_colors(2)
		self.load_data_file()
		#self.update(self.entry2.get_text().split(),self.adj1.value)
		print "Saved"

	def config_load(self):
		try:
	 		f = open("./gui_cmp_config.inp", "r")
			lines = f.readlines()
			f.close()

			for i in range(0, len(lines)):
				lines[i]=lines[i].rstrip()

			self.entry0.set_text(lines[0])
			self.entry1.set_text(lines[1])
			self.entry2.set_text(lines[2])
			self.entry3.set_text(lines[3])
		except:
			self.entry0.set_text("./snapshots/")
			self.entry1.set_text("./")
			self.entry2.set_text("n p")
			self.entry3.set_text("")

	def save_image(self,file_name):
		fileName, ext = os.path.splitext(file_name)

		if (ext==".jpg"):
			self.canvas.figure.savefig(file_name)
		elif ext==".avi":
			out_file="./snapshots/"
			jpgs=""
			for i in range(0,int(self.adj1.get_upper())):
				self.update(self.entry2.get_text().split(),i)
				image_name=out_file+"image_"+str(i)+".jpg"
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
				self.save_image(file_name+filter.get_name())
			
		elif response == gtk.RESPONSE_CANCEL:
		    print 'Closed, no files selected'
		dialog.destroy()

	def callback_help(self, widget, data=None):
		cmd = 'firefox http://www.roderickmackenzie.eu/opvdm_wiki.html'
		os.system(cmd)


	def callback_toggle_subtract(self, widget, data):
		self.plot.zero_frame_enable=data.get_active()
		self.update(self.entry2.get_text().split(),self.adj1.value)

	def callback_multi_plot(self, data, widget):
		if widget.get_active()==True:
			self.multi_plot=True
		else:
			self.multi_plot=False
		self.update(self.entry2.get_text().split(),self.adj1.value)

	def init(self,exe_command):

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
   		image.set_from_file(find_data_file("gui/scale.png"))
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


		hbox=gtk.HBox()
		text=gtk.Label("Primary dir")
		hbox.add(text)
		self.entry0 = gtk.Entry()
		self.entry0.set_text("./snapshots/")
		self.entry0.show()
		hbox.add(self.entry0)
		text=gtk.Label("Secondary dir")
		hbox.add(text)
		self.entry1 = gtk.Entry()
		self.entry1.set_text("./")
		self.entry1.show()
		hbox.add(self.entry1)

		self.update_button = gtk.Button()
		self.update_button.set_label("Update")
		self.update_button.show()
		self.update_button.connect("clicked", self.callback_scale)
		hbox.add(self.update_button)

		hbox.show()
		hbox.set_size_request(-1, 30)
		vbox.pack_start(hbox, False, False, 0)

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

		self.config_load()
		print self.entry0.get_text()+"dump_slice_info.dat"
		found, lines = zip_get_data_file(self.entry0.get_text()+"dump_slice_info.dat")
		if found==False:
			md = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION,  gtk.BUTTONS_YES_NO, "No slice data has been written to disk.  You need to re-run the simulation with the dump_slices set to 1.  Would you like to do this now?  Note: This generates lots of files and will slow down the simulation.")

#gtk.MessageDialog(self, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_QUESTION, 
		# gtk.BUTTONS_CLOSE, "Should I remove the simulation directory "+dir_to_del)
			response = md.run()

			if response == gtk.RESPONSE_YES:
				inp_update_token_value("dump.inp", "#dump_1d_slices", "1")
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

		self.update(self.entry2.get_text().split(),0)
		#["Ec","Ev","Fn","Fp"]
		self.set_border_width(10)
		self.set_title("Compare")
		self.set_icon_from_file(find_data_file("gui/image.jpg"))

		self.connect('key_press_event', self.on_key_press_event)

		self.show()
		

