#!/usr/bin/env python
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

import sys
import pygtk
inp_dir='/usr/share/opvdm/'
gui_dir='/usr/share/opvdm/gui/'
sys.path.append('./gui/')
sys.path.append(gui_dir)
pygtk.require('2.0')
import gtk

import os
import shutil
from scan import scan_class
from tab import tab_class
from search import find_fit_log
from tab_optical import tab_optical
import signal
import subprocess
from util import replace
from util import get_token_value
from tab_emesh import tab_electrical_mesh
from welcome import welcome_class
from tab_homo import tab_bands
from tempfile import mkstemp

if os.geteuid() == 0:
	exit("Don't run me as root!!")

check_list=[]
rod=[]

def find_data_file(name):
	local_file="./"+name
	if os.path.isfile(local_file)==True:
		ret=local_file
	else:
		ret=inp_dir+"/"+name
	return ret
	
exe_name='not set'
exe_command='not set'
notebook = gtk.Notebook()

def set_exe_command():
	global exe_command
	global exe_name

	if os.path.isfile("./go.o")==True:
		exe_command="./go.o"
		exe_name="go.o"
	else:
		exe_command="opvdm_core"
		exe_name="opvdm_core"

def notebook_load_pages():

	if os.path.exists("device.inp")==True:
		hello=tab_electrical_mesh()
		hello.wow()
		hello.show()
		notebook.append_page(hello, gtk.Label("Electrical Mesh"))

		hello=tab_optical()
		if hello.enabled==True:
			hello.wow()
			hello.show()
			notebook.append_page(hello, gtk.Label("Optics Epitaxy"))

		hello=tab_bands()
		if hello.enabled==True:
			hello.wow()
			hello.show()
			notebook.append_page(hello, gtk.Label("Bands"))

		f = open("./device_epitaxy.inp")
		lines = f.readlines()
		f.close()
		pos=0
		for i in range(0, len(lines)):
			lines[i]=lines[i].rstrip()

		for i in range(0, int(lines[1])):
			dos_file='dos'+str(i)+'.inp'
			dos_name='DoS layer '+str(i)
			if os.path.exists(dos_file)==True:
				rod.append(tab_class(8, 2, True))
				rod[pos].wow(dos_file,dos_name,check_list)

				rod[pos].show()

				notebook.append_page(rod[pos], gtk.Label(dos_name))
				pos=pos+1

		names = ["Device","JV Curve","Light","Output","CELIV","Numerics","Optics", "ToF"]
		files = ["device.inp","jv.inp","light.inp","dump.inp","celiv.inp","math.inp","optics.inp","tof.inp"]

	
		for i in range(0, len(names)):
			bufferf = "Append Frame %d" % (i+1)
			bufferl = "Page %d" % (i+1)
			if os.path.exists(files[i])==True:
				rod.append(tab_class(8, 2, True))
				rod[pos].wow(files[i],names[i],check_list)

				rod[pos].show()


				notebook.append_page(rod[pos], gtk.Label(names[i]))
				pos=pos+1
	else:
		hello=welcome_class()
		hello.wow(find_data_file("gui/image.jpg"))
		hello.show()
		notebook.append_page(hello, gtk.Label("Welcome"))



def set_active_name(combobox, name):
    liststore = combobox.get_model()
    for i in xrange(len(liststore)):
        if liststore[i][0] == name:
            combobox.set_active(i)

class NotebookExample:


	def callback_plot_doping(self, widget, data=None):
		self.load_graph(0,"x_Nad.plot")

	def callback_simulate_all_exp(self, widget, data=None):

		cmd = exe_command + ' --1fit'
		ret= os.system(cmd)
		if ret!=0 :
			message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
			message.set_markup("Error in solver")
			message.run()
			message.destroy()
		else:
			self.p_plot_fit=self.load_graph(self.p_plot_fit,"fit.plot")

	def callback_simulate(self, widget, data=None):

		#cmd = 'mv ivexternal.dat ivexternal_last.dat'
		#os.system(cmd)

		#cmd = 'mv charge.dat charge_last.dat'
		#os.system(cmd)

		cmd = exe_command + ' &'
		ret= os.system(cmd)
		if ret!=0 :
			message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
			message.set_markup("Error in solver")
			message.run()
			message.destroy()

	def callback_simulate_stop(self, widget, data=None):
		cmd = 'killall '+exe_name
		ret= os.system(cmd)

	def callback_scan(self, widget, data=None):
		a=scan_class(check_list)
		a.open_window()

	def load_graph(self, pid ,data):
		print pid,"in"
		#if pid!=0:
		#	#p.kill()
		#	os.killpg(pid, signal.SIGTERM)
		#	print "Killing graph"

		plot_dir=self.simulation_dir+'/plot/'
		print "Plot dir="+plot_dir
		cmd = '/usr/bin/gnuplot -persist '+plot_dir+data
		print cmd
		#os.system(cmd)
		p = subprocess.Popen(['/usr/bin/gnuplot', '-persist', plot_dir+data], stdout=subprocess.PIPE, shell=False)
		#print p.pid,"out"
		return p.pid

	def callback_plot_jv(self, widget, data=None):
		self.load_graph(0,"jv.plot")

	def callback_plot_fit(self, widget, data=None):
		self.p_plot_fit=self.load_graph(self.p_plot_fit,"fit.plot")
		

	def callback_plot_charge(self, widget, data=None):
		self.load_graph(0,"charge.plot")

	def callback_plot_converge(self, widget, data=None):
		self.load_graph(0,"converge.plot")

	def callback_plot_i_time(self, widget, data=None):
		self.load_graph(0,"gui_celiv_i_time.plot")

	def callback_import(self, widget, data=None):
		dialog = gtk.FileChooserDialog("Import..",
                               None,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)

		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		dialog.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name("Images")
		filter.add_mime_type("image/png")
		filter.add_mime_type("image/jpeg")
		filter.add_mime_type("image/gif")
		filter.add_pattern("*.png")
		filter.add_pattern("*.jpg")
		filter.add_pattern("*.gif")
		filter.add_pattern("*.tif")
		filter.add_pattern("*.xpm")
		dialog.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
		dialog.add_filter(filter)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			cmd = './opvdm_import '+dialog.get_filename()+'/'
			os.system(cmd)
		elif response == gtk.RESPONSE_CANCEL:
		    print 'Closed, no files selected'
		dialog.destroy()

	def callback_new(self, widget, data=None):
		dialog = gtk.FileChooserDialog("Make new opvdm simulation dir..",
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
			if not os.path.exists(dialog.get_filename()):
				os.makedirs(dialog.get_filename())

			self.simulation_dir=dialog.get_filename()+'/'
			print self.simulation_dir
			os.chdir(self.simulation_dir)
			set_exe_command()
			self.status_bar.push(self.context_id, self.simulation_dir)
			os.system("opvdm_clone")

			check_list=[]
			for child in notebook.get_children():
            			notebook.remove(child)

			notebook_load_pages()
		elif response == gtk.RESPONSE_CANCEL:
		    print 'Closed, no dir selected'
		dialog.destroy()

	def callback_open(self, widget, data=None):
		dialog = gtk.FileChooserDialog("Open..",
                               None,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)
		dialog.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)

		filter = gtk.FileFilter()
		filter.set_name("All files")
		filter.add_pattern("*")
		dialog.add_filter(filter)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			self.simulation_dir=dialog.get_filename()+'/'
			print "New simulation dir="+self.simulation_dir
			os.chdir(self.simulation_dir)
			set_exe_command()
			self.status_bar.push(self.context_id, self.simulation_dir)
			check_list=[]
			for child in notebook.get_children():
            			notebook.remove(child)

			notebook_load_pages()
		elif response == gtk.RESPONSE_CANCEL:
		    print 'Closed, no files selected'
		dialog.destroy()

	def callback_save(self, widget, data=None):
		dialog = gtk.FileChooserDialog("Save..",
                               None,
                               gtk.FILE_CHOOSER_ACTION_SAVE,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)

		filter = gtk.FileFilter()
		filter.set_name("gz files")
		filter.add_pattern("*.gz")
		dialog.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name("Archive")
		#filter.add_mime_type("image/png")
		#filter.add_mime_type("image/jpeg")
		#filter.add_mime_type("image/gif")
		filter.add_pattern("*.gz")

		dialog.add_filter(filter)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			cmd = 'tar -czvf '+dialog.get_filename()+'.tar.gz ./*.inp ./*.dat '
			os.system(cmd)
		elif response == gtk.RESPONSE_CANCEL:
		    print 'Closed, no files selected'
		dialog.destroy()

	def callback_edit_file(self, widget, data=None):
		page = notebook.get_current_page()
		cmd = 'gnome-open '+rod[page].file_name
		os.system(cmd)

	def callback_wiki(self, widget, data=None):
		page = notebook.get_current_page()
		cmd = 'firefox http://www.opvdm.com/wiki/index.php?title='+rod[page].file_name
		os.system(cmd)

	def callback_help(self, widget, data=None):
		cmd = 'firefox http://www.opvdm.com/opvdm_wiki.html'
		os.system(cmd)

	def callback_about_dialog_show(self, widget, data=None):
		about = gtk.AboutDialog()
		about.set_program_name("opvdm V1.0")
		about.set_version("")
		about.set_copyright("Released under GPL v2, (c) Roderick MacKenzie")
		about.set_comments("Organic photovoltaic device model")
		about.set_website("http://www.opvdm.com")

		image=find_data_file("gui/image.jpg")
		about.set_logo(gtk.gdk.pixbuf_new_from_file(image))
		about.run()
		about.destroy()


	def callback_on_line_help(self, widget, data=None):
		cmd = 'firefox www.opvdm.com'
		os.system(cmd)

	def callback_make(self, widget, data=None):
		cmd = 'make clean'
		os.system(cmd)

		cmd = 'make'
		os.system(cmd)

	def callback_hpc_check_load(self, widget, data=None):
		curdir=os.getcwd()
		os.chdir(self.hpc_root_dir)
		cmd = './hpc_check_load.sh'
		os.system(cmd)
		os.chdir(curdir)

	def callback_hpc_get_data(self, widget, data=None):
		curdir=os.getcwd()
		os.chdir(self.hpc_root_dir)
		cmd = './from_hpc.sh'
		os.system(cmd)
		os.chdir(curdir)

	def callback_hpc_run_once(self, widget, data=None):
		curdir=os.getcwd()
		os.chdir(self.hpc_root_dir)
		cmd = './autoonefit.sh'
		os.system(cmd)
		os.chdir(curdir)

	def callback_hpc_make_images(self, widget, data=None):
		curdir=os.getcwd()
		os.chdir(self.hpc_root_dir)
		cmd = './makeimages.sh'
		os.system(cmd)
		os.chdir(curdir)

	def callback_hpc_view_images(self, widget, data=None):
		cmd = 'gnome-open '+self.exe_dir+'../'
		os.system(cmd)

	def callback_hpc_build_job_local(self, widget, data=None):
		curdir=os.getcwd()
		os.chdir(self.hpc_root_dir)
		try:
			shutil.rmtree('./hpc')
		except: 
	  		print "No hpc dir to delete"

		cmd = './buildforhpc.sh'
		os.system(cmd)
		os.chdir(curdir)
		print "Build job"

	def callback_hpc_send_to_hpc(self, widget, data=None):
		curdir=os.getcwd()
		os.chdir(self.hpc_root_dir)
		print self.hpc_root_dir
		cmd = './to_hpc.sh'
		os.system(cmd)
		os.chdir(curdir)

	def callback_hpc_build_jobs(self, widget, data=None):
		curdir=os.getcwd()
		os.chdir(self.hpc_root_dir)
		cmd = './hpc_make_sim.sh'
		os.system(cmd)
		os.chdir(curdir)

	def call_back_sim_mode_changed(self, widget, data=None):
		mode=self.sim_mode.get_active_text()
		replace(find_data_file("sim.inp"), "#simmode", mode)

	def call_back_light_changed(self, widget, data=None):
		light_power=self.light.get_active_text()
		print light_power
		replace(find_data_file("light.inp"), "#Psun", light_power)


	def callback_hpc_clean_nodes(self, widget, data=None):
		curdir=os.getcwd()
		os.chdir(self.hpc_root_dir)
		cmd = './hpc_remove_from_nodes.sh'
		os.system(cmd)
		os.chdir(curdir)

	def callback_hpc_copy_to_nodes(self, widget, data=None):
		curdir=os.getcwd()
		os.chdir(self.hpc_root_dir)
		cmd = './hpc_copy_to_nodes.sh'
		os.system(cmd)
		os.chdir(curdir)

	def callback_hpc_kill_jobs(self, widget, data=None):
		curdir=os.getcwd()
		os.chdir(self.hpc_root_dir)
		cmd = './hpc_kill_jobs.sh'
		os.system(cmd)
		os.chdir(curdir)

	def callback_hpc_run_jobs(self, widget, data=None):
		curdir=os.getcwd()
		os.chdir(self.hpc_root_dir)
		cmd = './hpc_run_jobs.sh'
		os.system(cmd)
		os.chdir(curdir)

	def callback_hpc_fitlog_plot(self, widget, data=None):
		find_fit_log()
		cmd = 'gnuplot -persist '+self.exe_dir+'plot/hpc_fitlog.plot'
		os.system(cmd)

	def get_main_menu(self, window):
		accel_group = gtk.AccelGroup()


		item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)

		item_factory.create_items(self.menu_items)
		if os.path.exists("./server.inp")==False:
			item_factory.delete_item("/HPC")
			item_factory.delete_item("/Build")

		window.add_accel_group(accel_group)

		self.item_factory = item_factory

		return item_factory.get_widget("<main>")

	def __init__(self):
		self.p_plot_fit=0
		self.simulation_dir=os.path.dirname(os.path.abspath(__file__))+'/'
		self.exe_dir= os.path.dirname(os.path.abspath(__file__))+'/'
		self.hpc_root_dir= os.path.dirname(os.path.abspath(__file__))+'/../'

		print "Running in "+self.exe_dir
		print "Simulation directory "+self.simulation_dir

		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_border_width(10)
		window.set_title("Organic Photovoltaic Device Model (www.opvdm.com)")

		table = gtk.Table(3,6,False)

		image=gui_dir+"/image.jpg"
		if os.path.isfile(image)==False:
			image=self.exe_dir+"gui/image.jpg"
		window.set_icon_from_file(image)

		
		notebook.set_tab_pos(gtk.POS_TOP)
		table.attach(notebook, 0,6,0,1)
		notebook.show()
		self.show_tabs = True
		self.show_border = True

		notebook_load_pages()

		self.status_bar = gtk.Statusbar()      

		self.status_bar.show()

		self.context_id = self.status_bar.get_context_id("Statusbar example")

		table.attach(self.status_bar, 2,3,1,2)
		self.status_bar.push(self.context_id, self.simulation_dir)

		notebook.set_current_page(1)
		table.show()
		window.connect("destroy", gtk.main_quit)

		self.menu_items = (
		    ( "/_File",         None,         None, 0, "<Branch>" ),
			("/File/_New", "<control>N", self.callback_new, 0, "<StockItem>", "gtk-new" ),
			("/File/_Open", "<control>O", self.callback_open, 0, "<StockItem>", "gtk-open" ),
		    ( "/File/_Save",     "<control>S", self.callback_save, 0, "<StockItem>", "gtk-save" ),
		    ( "/File/Import",     None, self.callback_import, 0, None ),
		    ( "/File/Quit",     "<control>Q", gtk.main_quit, 0, "<StockItem>", "gtk-quit" ),
		    ( "/_Edit/Edit file",   None,         self.callback_edit_file, 0, None ),
		    ( "/_Simulate",      None,         None, 0, "<Branch>" ),
		    ( "/Simulate/Run",  None,         self.callback_simulate, 0, "<StockItem>", "gtk-media-play" ),
		    ( "/Simulate/Parameter scan",  None,         self.callback_scan , 0, None ),
		    ( "/_Plots",      None,         None, 0, "<Branch>" ),
		    ( "/Plots/Doping",  None,          self.callback_plot_doping, 0, None ),
		    ( "/Plots/Fit to exp",  None,         self.callback_plot_fit, 0, None ),
		    ( "/_Plots/",     None, None, 0, "<Separator>" ),
		    ( "/Plots/JV Curve",  None,         None, 0, "<Branch>" ),
		    ( "/Plots/JV Curve/J - V",  None,         self.callback_plot_jv, 0, None ),
		    ( "/Plots/JV Curve/Charge density",  None,         self.callback_plot_charge, 0, None ),
		    ( "/Plots/Numerics",  None,         None, 0, "<Branch>" ),
		    ( "/Plots/Numerics/Converge",  None,         self.callback_plot_converge, 0, None ),
		    ( "/Plots/CELIV",  None,         None, 0, "<Branch>" ),
		    ( "/Plots/CELIV/i-time",  None,         self.callback_plot_i_time, 0, None ),
		    ( "/_Build",      None,         None, 0, "<Branch>" ),
		    ( "/_Build/Rebuild model",     None, self.callback_make, 0, None ),
		    ( "/_HPC",      None,         None, 0, "<Branch>" ),
			( "/_HPC/Check load",     None, self.callback_hpc_check_load, 0, None ),
			( "/_HPC/",     None, None, 0, "<Separator>" ),
		    ( "/_HPC/Download",      None,         None, 0, "<Branch>" ),
		    ( "/_HPC/Download/Get Data",     None, self.callback_hpc_get_data, 0, None ),
		    ( "/_HPC/Download/Run all downloaded jobs",     None, self.callback_hpc_run_once, 0, None ),
		    ( "/_HPC/Download/Make images",     None, self.callback_hpc_make_images, 0, None ),

		    ( "/_HPC/Download/View images",     None, self.callback_hpc_view_images, 0, None ),
		    ( "/_HPC/Download/Plot Convergence",     None, self.callback_hpc_fitlog_plot, 0, None ),
		    ( "/_HPC/Upload",      None,         None, 0, "<Branch>" ),
		    ( "/_HPC/Upload/Build job for HPC",     None, self.callback_hpc_build_job_local, 0, None ),

		    ( "/_HPC/Upload/Send to HPC",     None, self.callback_hpc_send_to_hpc, 0, None ),
		    ( "/_HPC/Upload/Clean nodes",     None, self.callback_hpc_clean_nodes, 0, None ),
		    ( "/_HPC/Upload/Build Jobs on HPC",     None, self.callback_hpc_build_jobs, 0, None ),
		    ( "/_HPC/Upload/Copy to nodes",     None, self.callback_hpc_copy_to_nodes, 0, None ),
		    ( "/_HPC/Upload/Kill Jobs",     None, self.callback_hpc_kill_jobs, 0, None ),


		    ( "/_HPC/Upload/Run on cluster",     None, self.callback_hpc_run_jobs, 0, None ),
		    ( "/_Help",         None,         None, 0, "<LastBranch>" ),
			( "/_Help/Help Index",   None,         self.callback_help, 0, "<StockItem>", "gtk-help"  ),
		    ( "/_Help/Help about this tab",   None,         self.callback_wiki, 0, None  ),
		    ( "/_Help/Web page",   None,         self.callback_on_line_help, 0, None ),
			

		    ( "/_Help/About",   None,         self.callback_about_dialog_show, 0, "<StockItem>", "gtk-about" ),
		    )
		#window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		#window.connect("destroy", lambda w: gtk.main_quit())
		#window.set_title("Item Factory")
		window.set_size_request(800, -1)

		main_vbox = gtk.VBox(False, 4)
		main_vbox.set_border_width(1)
		window.add(main_vbox)
		#window.add(table)
		main_vbox.show()

		toolbar = gtk.Toolbar()
		toolbar.set_style(gtk.TOOLBAR_ICONS)

		toolbar2 = gtk.Toolbar()
		toolbar2.set_style(gtk.TOOLBAR_ICONS)

		#newtb = gtk.ToolButton(gtk.STOCK_NEW)
		#opentb = gtk.ToolButton(gtk.STOCK_OPEN)
		open_sim = gtk.ToolButton(gtk.STOCK_OPEN)
		new_sim = gtk.ToolButton(gtk.STOCK_NEW)
		play = gtk.ToolButton(gtk.STOCK_MEDIA_PLAY)
		play_exp = gtk.ToolButton(gtk.STOCK_DND_MULTIPLE)
		stop = gtk.ToolButton(gtk.STOCK_MEDIA_STOP)
		help = gtk.ToolButton(gtk.STOCK_HELP)

		plot = gtk.ToolButton(gtk.STOCK_PAGE_SETUP)
		sep = gtk.SeparatorToolItem()
		sep.set_draw(False)
		sep.set_expand(True)

		sep_lhs = gtk.SeparatorToolItem()
		sep_lhs.set_draw(True)
		sep_lhs.set_expand(False)

		quittb = gtk.ToolButton(gtk.STOCK_QUIT)
		
		pos=0
		toolbar.insert(open_sim, pos)
		pos=pos+1
		toolbar.insert(new_sim, pos)
		pos=pos+1
		toolbar.insert(sep_lhs, pos)
		pos=pos+1
		toolbar.insert(play, pos)
		pos=pos+1
		toolbar.insert(play_exp, pos)
		pos=pos+1
		toolbar.insert(stop, pos)
		pos=pos+1
		toolbar.insert(plot, pos)
		pos=pos+1
		toolbar.insert(help, pos)
		pos=pos+1
		toolbar.insert(sep, pos)
		pos=pos+1
		toolbar.insert(quittb, pos)
		pos=pos+1

		new_sim.connect("clicked", self.callback_new)
		open_sim.connect("clicked", self.callback_open)
		play.connect("clicked", self.callback_simulate)
		play_exp.connect("clicked", self.callback_simulate_all_exp)
		plot.connect("clicked", self.callback_plot_fit)
		stop.connect("clicked", self.callback_simulate_stop)
		help.connect("clicked", self.callback_help)
		quittb.connect("clicked", gtk.main_quit)

		self.sim_mode = gtk.combo_box_entry_new_text()

		f = open(find_data_file("sim_menu.inp"))
		lines = f.readlines()
		f.close()

		for i in range(0, len(lines)):
			self.sim_mode.append_text(lines[i].rstrip())

		self.sim_mode.child.connect('changed', self.call_back_sim_mode_changed)
		set_active_name(self.sim_mode, get_token_value(find_data_file("sim.inp"), "#simmode"))

		lable=gtk.Label("Simulation mode:")
		#lable.set_width_chars(15)
		lable.show
	        hbox = gtk.HBox(False, 2)
        
	        hbox.pack_start(lable, False, False, 0)
	        hbox.pack_start(self.sim_mode, False, False, 0)
	        #hbox.add(self.)
		tb_comboitem = gtk.ToolItem();
		tb_comboitem.add(hbox);
		toolbar2.insert(tb_comboitem, 0)


		self.light = gtk.combo_box_entry_new_text()
		self.light.append_text('0.0')
		self.light.append_text('1.0')
		self.light.append_text('10.0')
		self.light.append_text('100.0')
		self.light.append_text('1000.0')
		self.light.child.connect('changed', self.call_back_light_changed)
		set_active_name(self.light, get_token_value(find_data_file("light.inp"), "#Psun"))

		ti_light = gtk.ToolItem();
		lable=gtk.Label("Light intensity:")
		lable.show
	        hbox = gtk.HBox(False, 2)
        
	        hbox.pack_start(lable, False, False, 0)
	        hbox.pack_start(self.light, False, False, 0)

		ti_light.add(hbox);
		toolbar2.insert(ti_light, 1)




		toolbar.show_all()
		toolbar2.show_all()



		menubar = self.get_main_menu(window)

		main_vbox.pack_start(menubar, False, True, 0)
		main_vbox.add(toolbar)
		main_vbox.add(toolbar2)
		main_vbox.add(table)
		menubar.show()


		window.show()

def main():


	set_exe_command()
	gtk.main()
	return 0

if __name__ == "__main__":
	argc = len(sys.argv)
	if argc==2:
		if sys.argv[1]=="--help":
			print "opvdm - The GUI for Organic Photovoltaic Device Model"
			print "Copyright Roderick MacKenzie 2012, released under GPLv2"
			print ""
			print "Usage: opvdm [options]"
			print ""
			print "Options:"
			print "\t--version\tdisplays the current version"
			print "\t--help\t\tdisplays the help"
			print ""
			print "Additional information about opvdm is available at http://www.opvdm.com."
			print ""
			print "Report bugs to: roderick.mackenzie@nottingham.ac.uk"
			sys.exit(0)
		if sys.argv[1]=="--version":
			print "opvdm, Version 1.0"
			print "Copyright and written by Roderick MacKenzie 2012, Releced under GPLv2"
			print ""
			print "This is free software; see the source code for copying conditions."
			print "There is ABSOLUTELY NO WARRANTY; not even for MERCHANTABILITY or"
			print "FITNESS FOR A PARTICULAR PURPOSE."
			sys.exit(0)
	NotebookExample()
	main()

