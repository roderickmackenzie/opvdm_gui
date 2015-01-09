import pygtk
pygtk.require('2.0')
import gtk
import re
import sys
import os
import shutil
from token_lib import tokens
from numpy import *
from util import pango_to_gnuplot
from plot import plot_data
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
from plot_export import plot_export 
from numpy import arange, sin, pi, zeros
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas
from matplotlib.backends.backend_gtkagg import NavigationToolbar2GTKAgg as NavigationToolbar
from matplotlib.figure import Figure
from plot_info import plot_info
from util import zip_get_data_file
from util import read_xy_data
import matplotlib.ticker as ticker
from util import dlg_get_text

class plot_widget(gtk.VBox):

	def on_key_press_event(self,widget, event):
		keyname = gtk.gdk.keyval_name(event.keyval)
		#print "Key %s (%d) was pressed" % (keyname, event.keyval)
		if keyname=="a":
			self.do_plot()

		if keyname=="g":
			if self.grid==False:
				for i in range(0,len(self.ax)):
					self.ax[i].grid(True)
				self.grid=True
			else:
				for i in range(0,len(self.ax)):
					self.ax[i].grid(False)
				self.grid=False
		if keyname=="r":
			if self.lx==None:
				for i in range(0,len(self.ax)):
					self.lx = self.ax[i].axhline(color='k')
					self.ly = self.ax[i].axvline(color='k')
			self.lx.set_ydata(self.ydata)
			self.ly.set_xdata(self.xdata)

		if keyname=="l":
			if self.logy==True:
				self.logy=False
				for i in range(0,len(self.ax)):
					self.ax[i].set_yscale("linear")
			else:
				self.logy=True
				for i in range(0,len(self.ax)):
					self.ax[i].set_yscale("log")

		if keyname=="L":
			if self.logx==True:
				self.logx=False
				for i in range(0,len(self.ax)):
					self.ax[i].set_xscale("linear")
			else:
				self.logx=True
				for i in range(0,len(self.ax)):
					self.ax[i].set_xscale("log")

		if keyname=="q":
			self.win.destroy()

		if keyname == "c":
			if event.state == gtk.gdk.CONTROL_MASK:
				self.do_clip()

		self.fig.canvas.draw()

	def do_clip(self):
		snap = self.canvas.get_snapshot()
		pixbuf = gtk.gdk.pixbuf_get_from_drawable(None, snap, snap.get_colormap(),0,0,0,0,snap.get_size()[0], snap.get_size()[1])
		clip = gtk.Clipboard()
		clip.set_image(pixbuf)



	def mouse_move(self,event):
		#print event.xdata, event.ydata
		self.xdata=event.xdata
		self.ydata=event.ydata
	
		#self.fig.canvas.draw()

		#except:
		#	print "Error opening file ",file_name

	def read_data_2d(self,x,y,z,file_name):
		found,lines=zip_get_data_file(file_name)
		if found==True:

			for i in range(0, len(lines)):
				lines[i]=re.sub(' +',' ',lines[i])
				lines[i]=re.sub('\t',' ',lines[i])
				lines[i]=lines[i].rstrip()
				sline=lines[i].split(" ")
				if len(sline)==2:
					if (lines[i][0]!="#"):
						x.append(float(lines[i].split(" ")[0]))
						y.append(float(lines[i].split(" ")[1]))
						z.append(float(lines[i].split(" ")[2]))
			return True
		else:
			return False


	def sub_zero_frame(self,t,s,i):
		tt=[]
		ss=[]
		#print self.zero_frame_enable
		if self.zero_frame_enable==True:
			if read_xy_data(tt,ss,self.zero_frame_list[i])==True:
				for ii in range(0,len(t)):
					s[ii]=s[ii]-ss[ii]
	def do_plot(self):
		plot_number=0
		test_file=self.input_files[0]
		for i in range(0,len(self.input_files)):
			if os.path.isfile(self.input_files[i]):
				test_file=self.input_files[i]
		self.fig.clf()
		self.fig.subplots_adjust(bottom=0.2)
		self.fig.subplots_adjust(bottom=0.2)
		self.fig.subplots_adjust(left=0.1)
		self.fig.subplots_adjust(hspace = .001)
		if self.plot_title=="":
			self.fig.suptitle(self.mygraph.read.title)
		else:
			self.fig.suptitle(self.plot_title)

		self.ax=[]
		number_of_plots=max(self.plot_id)+1
		if number_of_plots>1:
			yloc = plt.MaxNLocator(4)
		else:
			yloc = plt.MaxNLocator(10)

		self.mygraph.find_file(test_file,self.plot_token)


		for i in range(0,number_of_plots):
			self.ax.append(self.fig.add_subplot(number_of_plots,1,i+1, axisbg='white'))
			#Only place label on bottom plot
			if i==number_of_plots-1:
				self.ax[i].set_xlabel(self.mygraph.read.x_label+" ("+self.mygraph.read.x_units+")")

			else:
				self.ax[i].tick_params(axis='x', which='both', bottom='off', top='off',labelbottom='off') # labels along the bottom edge are off

			#Only place y label on center plot
			if self.normalize==True:
				y_text="Normalized "+self.mygraph.read.y_label
				y_units="au"
			else:
				y_text=self.mygraph.read.y_label
				y_units=self.mygraph.read.y_units
			if i==math.trunc(number_of_plots/2):
				self.ax[i].set_ylabel(y_text+" ("+y_units+")")

			if self.logx==True:
				self.ax[i].set_xscale("log")

			if self.logy==True:
				self.ax[i].set_yscale("log")


		lines=[]
		files=[]

		my_max=1.0

		if self.mygraph.read.type=="xy":
			#print self.input_files
			if self.normalize==True:
				looking_for=0
				my_max=[]
				local_max=1
				for i in range(0, len(self.input_files)):
					if self.plot_id[i]==0:
						t=[]
						s=[]
						if read_xy_data(t,s,self.input_files[i])==True:
							self.sub_zero_frame(t,s,i)

							if self.invert_y==True:
								for ii in range(0,len(s)):
									s[ii]=-s[ii]

							if self.subtract_first_point==True:
								val=s[0]
								for ii in range(0,len(t)):
									s[ii]=s[ii]-val

							local_max=s[0]

							for ii in range(0,len(t)):
								value=s[ii]*self.mygraph.read.y_mul

								if local_max<value:
									local_max=value
							my_max.append(local_max)
							looking_for=looking_for+1
						else:
							return
					else:
						my_max.append(local_max)

				#print "my_max=",my_max

			for i in range(0, len(self.input_files)):
				#t,s = loadtxt(self.input_files[i], unpack=True)
				t=[]
				s=[]
				if read_xy_data(t,s,self.input_files[i])==True:

					if self.invert_y==True:
						for ii in range(0,len(s)):
							s[ii]=-s[ii]					

					if self.subtract_first_point==True:
						val=s[0]
						for ii in range(0,len(s)):
							s[ii]=s[ii]-val

					self.sub_zero_frame(t,s,i)

					for ii in range(0,len(t)):
						t[ii]=t[ii]*self.mygraph.read.x_mul
						s[ii]=s[ii]*self.mygraph.read.y_mul
						if self.normalize==True:
							s[ii]=s[ii]/my_max[i]

					plot_number=self.plot_id[i]
					#print plot_number, number_of_plots,self.plot_id
					if self.ymax!=-1:
						self.ax[plot_number].set_ylim((self.ymin,self.ymax))

					Ec, = self.ax[plot_number].plot(t,s, linewidth=3 ,alpha=1.0,color=self.color[i],marker=self.marker[i])

					if number_of_plots>1:
						self.ax[plot_number].yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1e'))
						if min(s)!=max(s):
							self.ax[plot_number].yaxis.set_ticks(arange(min(s), max(s), (max(s)-min(s))/4.0 ))

					if self.labels[i]!="":
						files.append(self.labels[i]+" "+self.key_units)
						lines.append(Ec)

			self.lx = None
			self.ly = None
			legend=self.fig.legend(lines, files, self.legend_pos)
		else:
			x=[]
			y=[]
			z=[]

			if self.read_data_2d(x,y,z,self.input_files[0])==True:
				maxx=-1
				maxy=-1
				for i in range(0,len(z)):
					if x[i]>maxx:
						maxx=x[i]

					if y[i]>maxy:
						maxy=y[i]

				maxx=maxx+1
				maxy=maxy+1

				data = zeros((maxy,maxx))


				for i in range(0,len(z)):
					data[y[i]][x[i]]= random.random()+5
					self.ax[0].text(x[i], y[i]+float(maxy)/float(len(z))+0.1,'%.1e' %  z[i], fontsize=12)

				#fig, ax = plt.subplots()
				self.ax[0].pcolor(data,cmap=plt.cm.Blues)

				self.ax[0].invert_yaxis()
				self.ax[0].xaxis.tick_top()

		#self.fig.tight_layout(pad=0.0, w_pad=0.0, h_pad=0.0)
		self.fig.canvas.draw()

	def callback_plot_save(self, widget, data=None):
		dialog = gtk.FileChooserDialog("Directory to make a gnuplot script..",
                               None,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_NEW, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		dialog.set_action(gtk.FILE_CHOOSER_ACTION_CREATE_FOLDER)

		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		dialog.add_filter(filter)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			plot_export(dialog.get_filename(),self.input_files,self.mygraph)

		elif response == gtk.RESPONSE_CANCEL:
		    print 'Closed, no dir selected'

		dialog.destroy()

	def load_data(self,input_files,plot_id,labels,plot_token):
		self.labels=labels
		self.plot_id=plot_id
		if len(input_files)!=len(labels):
			return
		self.input_files=input_files
		self.plot_token=plot_token
		self.mygraph=plot_data()
		self.mygraph.find_file(self.input_files[0],self.plot_token)

		#print "Rod",input_files
		title=self.mygraph.read.title
		self.win.set_title(title+" - www.opvdm.com")

		if (self.mygraph.read.logscale_x==1):
			self.logx=True
	
		if (self.mygraph.read.logscale_y==1):
			self.logy=True

		self.do_plot()

	def gen_colors_black(self,repeat_lines):
		#make 100 black colors
		marker_base=["","x","o"]
		c_tot=[]
		base=[[0.0,0.0,0.0]]
		self.marker=[]
		self.color=[]
		for i in range(0,100):
			for n in range(0,repeat_lines):
				self.color.append([base[0][0],base[0][1],base[0][2]])
				self.marker.append(marker_base[n])

	def gen_colors(self,repeat_lines):
		base=[[0.0,0.0,1.0],[0.0,1.0,0.0],[1.0,0.0,0.0],[0.0,1.0,1.0],[1.0,1.0,0.0],[1.0,0.0,1.0]]
		c_tot=[]
		self.marker=[]
		marker_base=["","x","o"]
		mul=1.0
		self.color=[]
		for i in range(0,len(base)):
			for n in range(0,repeat_lines):
				c_tot.append([base[i][0]*mul,base[i][1]*mul,base[i][2]*mul])
				self.marker.append(marker_base[n])
		mul=0.5
		for i in range(0,len(base)):
			for n in range(0,repeat_lines):
				c_tot.append([base[i][0]*mul,base[i][1]*mul,base[i][2]*mul])
				self.marker.append(marker_base[n])

		mul=0.7
		for i in range(0,len(base)):
			for n in range(0,repeat_lines):
				c_tot.append([base[i][0]*mul,base[i][1]*mul,base[i][2]*mul])
				self.marker.append(marker_base[n])

		mul=0.25
		for i in range(0,len(base)):
			for n in range(0,repeat_lines):
				c_tot.append([base[i][0]*mul,base[i][1]*mul,base[i][2]*mul])
				self.marker.append(marker_base[n])

		self.color=c_tot

	def callback_black(self, data, widget):
		self.gen_colors_black(1)
		self.do_plot()

	def callback_rainbow(self, data, widget):
		self.gen_colors(1)
		self.do_plot()

	def callback_key(self, data, widget):
		self.legend_pos=widget.get_label()
		self.do_plot()

	def callback_units(self, data, widget):
		units=dlg_get_text( "Units:", "Suns")
		if units!=None:
			self.key_units=units
		self.do_plot()


	def callback_autoscale_y(self, data, widget):
		if widget.get_active()==True:
			self.ymax=-1
			self.ymin=-1
		else:
			xmin, xmax, ymin, ymax = self.ax[0].axis()
			self.ymax=ymax
			self.ymin=ymin

	def callback_normtoone_y(self, data, widget):
		if widget.get_active()==True:
			self.normalize=True
		else:
			self.normalize=False
		self.do_plot()



	def callback_toggle_log_scale_y(self, widget, data):
		self.logy=data.get_active()
		self.do_plot()

	def callback_toggle_log_scale_x(self, widget, data):
		self.logy=data.get_active()
		self.do_plot()

	def callback_toggle_invert_y(self, widget, data):
		self.invert_y=data.get_active()
		self.do_plot()

	def callback_toggle_subtract_first_point(self, widget, data):
		self.subtract_first_point=data.get_active()
		self.do_plot()

	def callback_refresh(self, widget, data=None):
		self.do_plot()

	def init(self,in_window):
		self.key_units=""
		self.zero_frame_enable=False
		self.zero_frame_list=[]
		#print type(in_window)
		self.plot_title=""
		self.gen_colors(1)
		#self.color =['r','g','b','y','o','r','g','b','y','o']
		self.win=in_window
		self.grid=False
		self.show_pointer=False
		self.logy=False
		self.logx=False
		self.invert_y=False
		self.normalize=False
		self.subtract_first_point=False
		self.legend_pos="lower right"
		self.toolbar = gtk.Toolbar()
		self.toolbar.set_style(gtk.TOOLBAR_ICONS)
		self.toolbar.set_size_request(-1, 50)
		self.toolbar.show()
		self.ymax=-1
		self.ymin=-1
		self.pack_start(self.toolbar, False, True, 0)	

		self.fig = Figure(figsize=(2.5,2), dpi=100)

		self.canvas = FigureCanvas(self.fig)  # a gtk.DrawingArea

		self.fig.canvas.mpl_connect('motion_notify_event', self.mouse_move)

		self.item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", None)

		menu_items = (
		    ( "/_Key",         None,         None, 0, "<Branch>" ),
		    ( "/_Key/upper right",  None,         self.callback_key , 0, None ),
		    ( "/_Key/upper left",  None,         self.callback_key , 0, None ),
		    ( "/_Key/lower left",  None,         self.callback_key , 0, None ),
		    ( "/_Key/lower right",  None,         self.callback_key , 0, None ),
		    ( "/_Key/right",  None,         self.callback_key , 0, None ),
		    ( "/_Key/center right",  None,         self.callback_key , 0, None ),
		    ( "/_Key/lower center",  None,         self.callback_key , 0, None ),
		    ( "/_Key/upper center",  None,         self.callback_key , 0, None ),
		    ( "/_Key/center",  None,         self.callback_key , 0, None ),
		    ( "/_Key/Units",  None,         self.callback_units , 0, None ),
		    ( "/_Color/Black",  None,         self.callback_black , 0, None ),
		    ( "/_Color/Rainbow",  None,         self.callback_rainbow , 0, None ),
		    ( "/_Axis/_Autoscale y",     None, self.callback_autoscale_y, 0, "<ToggleItem>", "gtk-save" ),
		    ( "/_Axis/_Set log scale y",     None, self.callback_toggle_log_scale_y, 0, "<ToggleItem>", "gtk-save" ),
		    ( "/_Axis/_Set log scale x",     None, self.callback_toggle_log_scale_x, 0, "<ToggleItem>", "gtk-save" ),

		    ( "/_Math/_Subtract first point",     None, self.callback_toggle_subtract_first_point, 0, "<ToggleItem>", "gtk-save" ),
		    ( "/_Math/_Invert y-axis",     None, self.callback_toggle_invert_y, 0, "<ToggleItem>", "gtk-save" ),
		    ( "/_Math/_Norm to 1.0 y",     None, self.callback_normtoone_y, 0, "<ToggleItem>", "gtk-save" ),
		    )


		self.item_factory.create_items(menu_items)


		menubar=self.item_factory.get_widget("<main>")
		menubar.show_all()
		self.pack_start(menubar, False, True, 0)



		pos=0
		plot_toolbar = NavigationToolbar(self.canvas, self.win)
		plot_toolbar.show()
		box=gtk.HBox(True, 1)
		box.set_size_request(400,-1)
		box.show()
		box.pack_start(plot_toolbar, True, True, 0)
		tb_comboitem = gtk.ToolItem();
		tb_comboitem.add(box);
		tb_comboitem.show_all()

		self.toolbar.add(tb_comboitem)
		pos=pos+1

		self.plot_save = gtk.ToolButton(gtk.STOCK_SAVE)
		self.plot_save.connect("clicked", self.callback_plot_save)
		self.toolbar.add(self.plot_save)
		pos=pos+1

		refresh = gtk.ToolButton(gtk.STOCK_REFRESH)
		refresh.connect("clicked", self.callback_refresh)
		self.toolbar.insert(refresh, pos)
		pos=pos+1

		self.toolbar.show_all()


		self.canvas.figure.patch.set_facecolor('white')
		self.canvas.set_size_request(650, 400)
		self.pack_start(self.canvas, True, True, 0)	

		#self.fig.canvas.draw()

		self.canvas.show()

		self.win.connect('key_press_event', self.on_key_press_event)
