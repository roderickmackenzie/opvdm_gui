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


import sys
gui_dir='/usr/share/opvdm/gui/'
lib_dir='/usr/lib64/opvdm/'
sys.path.append('./gui/')
sys.path.append(lib_dir)

from command_args import command_args
command_args(len(sys.argv),sys.argv)


import pdb
import pygtk
import gtk
pygtk.require('2.0')
import os
import shutil
from scan_item import scan_items_clear
from scan import scan_class 
from tab import tab_class
from search import find_fit_error
from optics import class_optical
import signal
import subprocess
from inp import inp_update_token_value
from inp import inp_get_token_value
from inp import inp_isfile
from inp import inp_get_token_array
from util import set_exe_command
from util import get_orig_inp_file_path
from util import opvdm_clone
from export_as import export_as
from emesh import tab_electrical_mesh
from copying import copying
from hpc import hpc_class
from tab_homo import tab_bands
from tempfile import mkstemp
from plot_gen import plot_gen
from plot_gen import set_plot_auto_close
from import_archive import import_archive
from about import about_dialog_show
from util import find_data_file
from notice import notice
import os, fnmatch
import threading
import time
import gobject
import numpy
import matplotlib
import matplotlib.pyplot as plt
from used_files_menu import used_files_menu
from plot import load_graph
from scan_item import scan_item_add
from cmp_class import cmp_class
from plot_state import plot_state
import logging
from Queue import *
from util import check_is_config_file
from window_list import windows
from config import config
import random
from import_archive import delete_scan_dirs
from undo import undo_list_class
from splash import splash_window
from ver import ver
from win_lin import running_on_linux
import webbrowser
from debug import debug_mode

if running_on_linux()==True:
	import pyinotify
	import pynotify
	from welcome_linux import welcome_class
	from tab_terminal import tab_terminal
	if os.geteuid() == 0:
		exit("Don't run me as root!!")
	
else:
	from welcome_windows import welcome_class	
	import win32file
	import win32con
	#ACTIONS = {
	#  1 : "Created",
	#  2 : "Deleted",
	#  3 : "Updated",
	#  4 : "Renamed from something",
	#  5 : "Renamed to something"
	#}

	FILE_LIST_DIRECTORY = 0x0001


#def trace(frame, event, arg):
#    print "%s, %s:%d" % (event, frame.f_code.co_filename, frame.f_lineno)
#    return trace

#sys.settrace(trace)

#logging.basicConfig(filename='/tmp/opvdm.log', level=logging.INFO)

#logging.info(time.strftime("%c"))

print notice()

gobject.threads_init()

	
notebook = gtk.Notebook()

def process_events():
	while gtk.events_pending():
		gtk.main_iteration(False)

def set_active_name(combobox, name):
    logging.info('set_active_name'+name)
    liststore = combobox.get_model()
    for i in xrange(len(liststore)):
        if liststore[i][0] == name:
            combobox.set_active(i)

global thread_data

class _IdleObject(gobject.GObject):
	"""
	Override gobject.GObject to always emit signals in the main thread
	by emmitting on an idle handler
	"""
	def __init__(self):
		gobject.GObject.__init__(self)
	 
	def emit(self, *args):
		gobject.idle_add(gobject.GObject.emit,self,*args)

class _FooThread(threading.Thread, _IdleObject):
	__gsignals__ = {
		"file_changed": (
		gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [])
		}
	 
	def __init__(self, *args):
		threading.Thread.__init__(self)
		_IdleObject.__init__(self)
 
	def onChange(self,ev):
		if running_on_linux()==True:
			file_name=os.path.basename(ev.pathname)
		else:
			file_name=os.path.basename(ev)

		file_name=file_name.rstrip()
		global thread_data
		thread_data.put(file_name)
		self.emit("file_changed")

	def run(self):
		watch_path=os.getcwd()
		if running_on_linux()==True:
			wm = pyinotify.WatchManager()
			wm.add_watch(watch_path, pyinotify.IN_CLOSE_WRITE, self.onChange,False,False)
			self.notifier = pyinotify.Notifier(wm)
			self.notifier.loop()
		else:
			hDir = win32file.CreateFile (watch_path,FILE_LIST_DIRECTORY,win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,None,win32con.OPEN_EXISTING,win32con.FILE_FLAG_BACKUP_SEMANTICS,None)

			while 1:
				results = win32file.ReadDirectoryChangesW (hDir,1024,True,
				win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
				win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
				win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
				win32con.FILE_NOTIFY_CHANGE_SIZE |
				win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
				win32con.FILE_NOTIFY_CHANGE_SECURITY,
				None,
				None)

				for action, file in results:
					full_filename = os.path.join (watch_path, file)
					#print full_filename, ACTIONS.get (action, "Unknown")
					self.onChange(full_filename)

	def stop(self):
		self.notifier.stop()

class NotebookExample:

	icon_theme = gtk.icon_theme_get_default()
	plot_after_run=False
	plot_after_run_file=""
	electrical_mesh=None
	scan_window=None
	cluster_window=None
	exe_command , exe_name  =  set_exe_command()
	#print exe_command

	def check_model_error(self):
			logging.info('check_model_error')
			print "Thread ID=",threading.currentThread()
			f = open("error.dat")
			lines = f.readlines()
			f.close()
			read_lines=lines[0].strip()
			read_lines_split=read_lines.split()
			if (read_lines_split.count('License')==0):
				message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
				message.set_markup(lines[0].strip())
				message.run()
				message.destroy()
			else:
				c=copying()
				c.wow(self.exe_command)

	def goto_terminal_page(self):
		for i in range(0,len(notebook.get_children())):
    			if notebook.get_nth_page(i).name=="Terminal":
				if notebook.get_nth_page(i).visible==1:
					notebook.set_current_page(i)
					break

	def gui_sim_start(self):
		self.notebook_active_page=notebook.get_current_page()

		self.goto_terminal_page()

		self.spin.start()
		self.statusicon.set_from_stock(gtk.STOCK_NO) 

	def gui_sim_stop(self,text):
		self.progress.hide()

		message=""
		notebook.set_current_page(self.notebook_active_page)
		self.spin.stop()
		self.statusicon.set_from_stock(gtk.STOCK_YES)
		if os.path.isfile("signal_stop.dat")==True:
			f = open('signal_stop.dat')
			lines = f.readlines()
			f.close()
			message=lines[0].rstrip()

		if text!="":
			message=text

		if running_on_linux()==True:
			if message!="":
				pynotify.init ("opvdm")
				Hello=pynotify.Notification ("opvdm:",message,find_data_file("gui/application-opvdm.svg"))
				print find_data_file("gui/icon.png")
				Hello.set_timeout(2000)
				Hello.show ()



	def user_callback(self,object):
		#logging.info('user_callback')
		global thread_data
		file_name=thread_data.get()
		if (file_name=="signal_start.dat"):
			self.gui_sim_start()

		if (file_name=="signal_stop.dat"):
			#print "stopping!\n"
			self.gui_sim_stop("")
			if self.plot_after_run==True:
				if self.plot_after_run_file!="":
					plot_gen([self.plot_after_run_file,"old.dat"],[],None,"","")

		if (file_name=="signal_plot.dat"):
			#print "stopping!\n"
			self.gui_sim_plot()

		if (file_name=="error.dat"):
			print "GUI found error"
			self.check_model_error()

		thread_data.task_done()

	def make_menu(self,event_button, event_time, data=None):
		menu = gtk.Menu()
		#open_item = gtk.MenuItem("Open App")
		close_item = gtk.MenuItem("Quit")
		#Append the menu items
		#menu.append(open_item)
		menu.append(close_item)
		#add callbacks
		#open_item.connect_object("activate", open_app, "Open App")
		close_item.connect_object("activate", self.callback_close_window, "Quit")
		#Show the menu items
		#open_item.show()
		close_item.show()
		#Popup the menu
		menu.popup(None, None, None, event_button, event_time)

	def on_status_icon_right_click(self,data, event_button, event_time):
		self.make_menu(event_button, event_time)

	def notebook_load_pages(self):
		global thread_data
		thread_data = Queue(maxsize=0)
		
		#logging.info('notebook_load_pages')
		self.progress.show()
		self.finished_loading=False
		self.rod=[]
		self.number_of_tabs=0

		self.optics_window=class_optical()
		self.optics_window.init()
		if self.optics_window.enabled==True:
			self.optics_window.wow(self.exe_command)
			self.optics_window.hide()

		if (os.path.exists("sim.opvdm")==True) and (os.getcwd()!="C:\\opvdm"):
			self.play.set_sensitive(True)
			self.stop.set_sensitive(True)
			self.mesh.set_sensitive(True)
			self.examine.set_sensitive(True)
			self.param_scan.set_sensitive(True)
			self.optics_button.set_sensitive(True)
			self.plot_select.set_sensitive(True)
			self.undo.set_sensitive(True)
			self.save_sim.set_sensitive(True)

			f = open("./device_epitaxy.inp")
			lines = f.readlines()
			f.close()
			pos=0
			for i in range(0, len(lines)):
				lines[i]=lines[i].rstrip()

			dos_files=int(lines[1])

			visible = []
			names = []
			files = []

			try:
				f = open("./gui_config.inp")
				lines = f.readlines()
				f.close()

				for i in range(0, len(lines)):
					lines[i]=lines[i].rstrip()

				i=0
				while i<len(lines) :
					visible.append(lines[i])
					i=i+1

					files.append(lines[i])

					i=i+1
					names.append(lines[i])
					i=i+1
			except:
				print "No gui_config.inp file found\n"

			internal_names = ["Device","JV Curve","JV simple","Light","Output","CELIV","Numerics", "ToF", "stark", "Bands", "Pulse","Pulse voc", "imps","Exp. Optical Model","Terminal","Sun voc","TPC","fit","Thermal"]
			internal_files = ["device.inp","jv.inp","jv_simple.inp","light.inp","dump.inp","celiv.inp","math.inp","tof.inp","stark.inp","lumo0.inp","server.inp","pulse_voc.inp","imps.inp","light_exp.inp","terminal.inp","sun_voc.inp","tpc.inp","fit.inp","thermal.inp"]

			i=0
			while i<len(internal_names) :
				if (files.count(internal_files[i])==0):
					visible.append("1")
					files.append(internal_files[i])
					names.append(internal_names[i])
				i=i+1

			for i in range(0, dos_files):
				dos_file='dos'+str(i)+'.inp'
				if files.count(dos_file) == 0:
					visible.append("1")
					files.append(dos_file)
					names.append('DoS layer '+str(i))

			for i in range(0, len(names)):
				self.progress.set_fraction(float(i)/float(len(names)))
				process_events()
				cur_file=files[i]
				cur_name=names[i]
				cur_visible=int(visible[i])
				add_to_menu=False


				if running_on_linux()==True:
					if cur_file=="terminal.inp":
						hello=tab_terminal()
						add_to_menu=True
						self.rod.append(hello)
						self.rod[self.number_of_tabs].visible=cur_visible
						self.rod[self.number_of_tabs].wow(os.getcwd())
						self.rod[self.number_of_tabs].name=cur_name
						self.rod[self.number_of_tabs].file_name=cur_file
						self.terminal=hello.terminal
				else:
					self.terminal=None

				if cur_file=="lumo0.inp":
					hello=tab_bands()
					hello.update()
					if hello.enabled==True:
						add_to_menu=True
						self.rod.append(hello)
						self.rod[self.number_of_tabs].visible=cur_visible
						self.rod[self.number_of_tabs].wow()
						self.rod[self.number_of_tabs].name=cur_name
						self.rod[self.number_of_tabs].file_name=cur_file

				elif check_is_config_file(cur_file)!="none":
					add_to_menu=True
					self.rod.append(tab_class())
					self.rod[self.number_of_tabs].visible=cur_visible
					self.rod[self.number_of_tabs].init(cur_file,cur_name)
					self.rod[self.number_of_tabs].name=cur_name
					self.rod[self.number_of_tabs].file_name=cur_file


				if add_to_menu==True:
					hbox=gtk.HBox()
					hbox.set_size_request(-1, 25)
					mytext=cur_name
					#logging.info('Adding page'+mytext)
					if len(mytext)<10:
						for i in range(len(mytext),10):
							mytext=mytext+" "

					label=gtk.Label(mytext)
					label.set_justify(gtk.JUSTIFY_LEFT)
					hbox.pack_start(label, False, True, 0)

					button = gtk.Button()
					close_image = gtk.Image()
					close_image.set_from_file(find_data_file("gui/close.png"))
					print find_data_file("gui/close.png")
					close_image.show()
					# a button to contain the image widget
					button = gtk.Button()
					button.add(close_image)



					button.props.relief = gtk.RELIEF_NONE
					button.connect("clicked", self.callback_close_button,cur_name)
					button.set_size_request(25, 25)
					button.show()
					

					hbox.pack_end(button, False, False, 0)
					hbox.show_all()

					notebook.append_page(self.rod[self.number_of_tabs],hbox )

					if (cur_visible==True):
						self.rod[self.number_of_tabs].show()


					notebook.set_tab_reorderable(self.rod[self.number_of_tabs],True)
					a = (( "/View/"+cur_name,  None, self.callback_view_toggle, 0, "<ToggleItem>" ),   )
					self.item_factory.create_items( a, )
					myitem=self.item_factory.get_item("/View/"+cur_name)
					myitem.set_active(cur_visible)
					self.number_of_tabs=self.number_of_tabs+1
		else:
			self.play.set_sensitive(False)
			self.stop.set_sensitive(False)
			self.mesh.set_sensitive(False)
			self.examine.set_sensitive(False)
			self.param_scan.set_sensitive(False)
			self.optics_button.set_sensitive(False)
			self.plot_select.set_sensitive(False)
			self.undo.set_sensitive(False)
			self.save_sim.set_sensitive(False)


		hello=welcome_class()
		hello.wow(find_data_file("gui/image.jpg"))
		hello.show()
		notebook.append_page(hello, gtk.Label("Information"))
		self.finished_loading=True
		self.progress.hide()
		self.progress.set_fraction(0.0)
		logging.info('Added all pages to notebook')

	def callback_plot_after_run_toggle(self, widget, data):
		self.plot_after_run=data.get_active()
		self.config.set_value("#plot_after_simulation",data.get_active())

	def callback_set_plot_auto_close(self, widget, data):
		set_plot_auto_close(data.get_active())
		self.config.set_value("#one_plot_window",data.get_active())

	def toggle_tab_visible(self,name):
		logging.info('toggle_tab_visible '+str(self.finished_loading))
		if self.finished_loading==True:
			for i in range(0, self.number_of_tabs):
				if self.rod[i].name==name:
					widget=self.item_factory.get_widget("/View/"+name)
					if self.rod[i].visible==0:
						widget.set_active(True)
						self.rod[i].show()
						self.rod[i].visible=1
					else:
						widget.set_active(False)
						self.rod[i].hide()
						self.rod[i].visible=0


	 		a = open("./gui_config.inp", "w")
			for i in range(0, self.number_of_tabs):
				a.write(str(self.rod[i].visible)+"\n")
				a.write(self.rod[i].file_name+"\n")
				a.write(self.rod[i].name+"\n")

			a.close()

	def callback_close_button(self, widget, data):
		self.toggle_tab_visible(data)


	def callback_view_toggle(self, widget, data):
		self.toggle_tab_visible(data.get_label())


	def gui_sim_plot(self):

		#cmd = self.exe_command + ' --1fit\n'
		#self.terminal.feed_child(cmd)
		#ret= os.system(cmd)
		#if ret!=0 :
		#	message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
		#	message.set_markup("Error in solver")
		#	message.run()
		#	message.destroy()
		#else:
		print "Hello"
		#load_graph("./one.plot")

	def callback_run_scan(self, widget, data=None):
		if self.scan_window!=None:
			self.scan_window.callback_run_simulation(None)
		#try:
		#	os.rename("error_sun_voc0_sim.dat", "old.dat")
		#except:
		#	pass
		#
		#cmd = "cd "+self.sim_dir+";"+self.exe_command + ' --1fit\n'
		#self.terminal.feed_child(cmd)


	def callback_simulate(self, widget, data=None):

		#self.spin.start()
		if self.plot_after_run==True:
			try:
				ret= os.system("cp "+self.plot_after_run_file+" old.dat")
			except:
				pass

		if running_on_linux()==True:
			cmd = "cd "+self.sim_dir+" \n"
			self.terminal.feed_child(cmd)

			cmd = self.exe_command+" &\n"
			self.terminal.feed_child(cmd)
		else:
			cmd = self.exe_command
			subprocess.Popen([cmd])
			#ret= os.system(cmd)

		#




		#self.spin.stop()
	
	def callback_start_cluster_server(self, widget, data=None):
		self.goto_terminal_page()

		cmd = "cd "+self.sim_dir+" \n"
		#self.terminal.feed_child(cmd)

		cmd = "./opvdm --server &\n"

		#self.terminal.feed_child(cmd)


		#self.spin.stop()

	def callback_simulate_stop(self, widget, data=None):
		cmd = 'killall '+self.exe_name
		ret= os.system(cmd)
		self.spin.stop()

	def callback_run_fit(self, widget, data=None):
		if running_on_linux()==True:
			cmd = "cd "+self.sim_dir+" \n"
			self.terminal.feed_child(cmd)

			cmd = self.exe_command+" --1fit&\n"
			self.terminal.feed_child(cmd)
		else:
			cmd = self.exe_command+" --1fit"
			subprocess.Popen([cmd])

	def callback_cluster(self, widget, data=None):
		if self.cluster_window==None:
			self.cluster_window=hpc_class()
			self.cluster_window.init(self.hpc_root_dir,self.exe_dir,self.terminal)

		print self.cluster_window.get_property("visible")

		if self.cluster_window.get_property("visible")==True:
			self.cluster_window.hide()
		else:
			self.cluster_window.show()


	def callback_scan(self, widget, data=None):
		logging.info('callback_scan')
		self.tb_run_scan.set_sensitive(True)

		if self.scan_window==None:
			self.scan_window=scan_class(gtk.WINDOW_TOPLEVEL)
			self.scan_window.init(self.exe_name,self.exe_command,self.progress,self.gui_sim_start,self.gui_sim_stop,self.terminal)


		if self.scan_window.get_property("visible")==True:
			self.scan_window.hide()
		else:
			self.scan_window.show()



	def callback_plot_select(self, widget, data=None):
		logging.info('callback_plot_select')
		dialog = gtk.FileChooserDialog("Open graph..",
                               None,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)

		filter = gtk.FileFilter()
		filter.set_name("dat files")
		filter.add_pattern("*.dat")
		dialog.add_filter(filter)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			self.plot_open.set_sensitive(True)

			plot_token=plot_state()
			plot_token.path=os.path.dirname(dialog.get_filename())
			plot_token.file0=os.path.basename(dialog.get_filename())
			plot_token.tag0=""
			plot_token.file1=""
			plot_token.tag1=""
			plot_gen([dialog.get_filename()],[],plot_token,"auto","")

			self.plotted_graphs.refresh()
			self.plot_after_run_file=dialog.get_filename()
		elif response == gtk.RESPONSE_CANCEL:
		    print 'Closed, no files selected'
		dialog.destroy()

	def callback_plot_open(self, widget, data=None):
		plot_data=plot_state()
		plot_gen([self.plot_after_run_file],[],plot_data,"","")

	def callback_last_menu_click(self, widget, data):
		self.plot_open.set_sensitive(True)
		file_to_load=os.path.join(data.path,data.file0)
		plot_gen([file_to_load],[],data,"auto","")
		self.plot_after_run_file=file_to_load

	def callback_plot_fit_erros(self, widget, data=None):
		find_fit_error()	
		load_graph("./plot/fit_errors.plot")

	def callback_plot_converge(self, widget, data=None):
		load_graph("./plot/converge.plot")

	def callback_plot_matrix(self, widget, data=None):
		plot_gen(["matrix.dat"],[],None,"","")

	def callback_import(self, widget, data=None):
		logging.info('callback_import')
		dialog = gtk.FileChooserDialog("Import..",
                               None,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)

		filter = gtk.FileFilter()
		filter.set_name(".tar.gz")
		filter.add_pattern("*.tar.gz")
		dialog.add_filter(filter)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			import_archive(dialog.get_filename(),"./",False)
			self.change_dir_and_refresh_interface(os.getcwd())
		elif response == gtk.RESPONSE_CANCEL:
		    print 'Closed, no files selected'
		dialog.destroy()

	def change_sim_dir(self,new_dir):
		logging.info('change_sim_dir')
		print "Changing directory to ",new_dir
		os.chdir(new_dir)
		self.sim_dir=os.getcwd()
		try:
			self.thread.stop()
			self.thread = _FooThread()
			self.thread.connect("file_changed", self.user_callback)
			self.thread.daemon = True
			self.thread.start()
		except:
			print "Can't stop start thread"

	def callback_new(self, widget, data=None):
		logging.info('callback_new')
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

			self.change_sim_dir(dialog.get_filename())
			opvdm_clone()

			self.change_dir_and_refresh_interface(dialog.get_filename())

		elif response == gtk.RESPONSE_CANCEL:
		    print 'Closed, no dir selected'
		dialog.destroy()
		logging.info('Leaving callback callback_new')

	def change_dir_and_refresh_interface(self,new_dir):
		logging.info('change_dir_and_refresh_interface')
		#if os.path.isfile("ver.inp")==True:
		#	f = open("ver.inp")
		#	lines = f.readlines()
		#	f.close()
		#	for i in range(0, len(lines)):
		#		lines[i]=lines[i].rstrip()
		#
		#	if lines[1]!=version:
		#		myerror="I can only load files from opvdm version "+ver()+" current version "+lines[1]+"\n."
		#		logging.info(os.getcwd())
		#		logging.info(myerror)
		#		message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
		#		message.set_markup(myerror)
		#		message.run()
		#		message.destroy()
		#		sys.exit(myerror) 
		
		scan_items_clear()

		self.change_sim_dir(new_dir)
		self.config.load(self.sim_dir)
		self.exe_command , self.exe_name = set_exe_command()
		self.status_bar.push(self.context_id, os.getcwd())
		self.plot_open.set_sensitive(False)
		for child in notebook.get_children():
    			notebook.remove(child)

		self.notebook_load_pages()
		self.plotted_graphs.init(os.getcwd(),self.callback_last_menu_click)

		set_active_name(self.light, inp_get_token_value("light.inp", "#Psun"))
		set_active_name(self.sim_mode, inp_get_token_value("sim.inp", "#simmode"))

		scan_item_add("sim.inp","#simmode","sim mode",1)
		scan_item_add("light.inp","#Psun","light intensity",1)


		if self.scan_window!=None:
			logging.info('Del scan_window')
			del self.scan_window
			self.scan_window=None


		if self.electrical_mesh!=None:
			logging.info('Del scan_window')
			del self.electrical_mesh
			self.electrical_mesh=tab_electrical_mesh()
			self.electrical_mesh.init()

		myitem=self.item_factory.get_item("/Plots/One plot window")
		myitem.set_active(self.config.get_value("#one_plot_window",False))
		myitem=self.item_factory.get_item("/Plots/Plot after simulation")
		myitem.set_active(self.config.get_value("#plot_after_simulation",False))

		logging.info('Finished change_dir_and_refresh_interface')

	def callback_open(self, widget, data=None):
		logging.info('callback_open')
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
			self.change_dir_and_refresh_interface(dialog.get_filename())

		elif response == gtk.RESPONSE_CANCEL:
		    print 'Closed, no files selected'
		dialog.destroy()

	def callback_export(self, widget, data=None):
		logging.info('callback_export')
		dialog = gtk.FileChooserDialog("Save as..",
                               None,
                               gtk.FILE_CHOOSER_ACTION_SAVE,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)

		filter = gtk.FileFilter()
		filter.set_name(".tar.gz")
		filter.add_pattern("*.tar.gz")
		dialog.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name(".pdf")
		filter.add_pattern("*.pdf")
		dialog.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name(".jpg")
		filter.add_pattern("*.jpg")
		dialog.add_filter(filter)

		filter = gtk.FileFilter()
		filter.set_name(".tex")
		filter.add_pattern("*.tex")
		dialog.add_filter(filter)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			file_name=dialog.get_filename()
			mode=self.sim_mode.get_active_text()

			if os.path.splitext(file_name)[1]:
				export_as(file_name)
			else:
				filter=dialog.get_filter()
				export_as(file_name+filter.get_name())
			
		elif response == gtk.RESPONSE_CANCEL:
		    print 'Closed, no files selected'
		dialog.destroy()


	def callback_edit_file(self, widget, data=None):
		logging.info('callback_edit_file')
		page = notebook.get_current_page()
		cmd = 'gnome-open '+self.rod[page].file_name
		os.system(cmd)

	def callback_wiki(self, widget, data=None):
		page = notebook.get_current_page()
		webbrowser.open('http://www.roderickmackenzie.eu/wiki/index.php?title='+self.rod[page].file_name)

	def callback_about_dialog(self, widget, data=None):
		about_dialog_show()

	def callback_help(self, widget, data=None):
		webbrowser.open('http://www.opvdm.com/man/index.html')

	def callback_on_line_help(self, widget, data=None):
		webbrowser.open('www.opvdm.com')

	def callback_new_window(self, widget, data=None):
		if self.window2.get_property("visible")==True:
			self.window2.hide()
		else:
			self.window2.show()

	def callback_close_window2(self, widget, data=None):
		self.window2.hide()
		return True


	def callback_close_window(self, widget, data=None):
		self.win_list.update(self.window,"main_window")
		print "quiting"
		gtk.main_quit()


	def callback_examine(self, widget, data=None):
		mycmp=cmp_class()
		ret=mycmp.init(self.sim_dir,self.exe_command)
		if ret==False:
			md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_WARNING,  gtk.BUTTONS_CLOSE, "Re-run the simulation with 'dump all slices' set to one to use this tool.")
        		md.run()
        		md.destroy()
			return

	def callback_edit_mesh(self, widget, data=None):
		if self.electrical_mesh.get_property("visible")==True:
			self.electrical_mesh.hide_all()
		else:
			self.electrical_mesh.show_all()

	def callback_undo(self, widget, data=None):
		l=self.undo_list.get_list()
		if len(l)>0:
			#print l[len(l)-1][0]
			#print l[len(l)-1][1]
			value=l[len(l)-1][2]
			w_type=l[len(l)-1][3]

			if type(w_type)==gtk.Entry:
				self.undo_list.disable()
				w_type.set_text(value)
				self.undo_list.enable()

			l.pop()

#		self.file_name, data, widget.get_text(),widget


	def callback_optics_sim(self, widget, data=None):
		if self.optics_window.get_property("visible")==True:
			self.optics_window.hide()
		else:
			self.optics_window.show()

	def callback_make(self, widget, data=None):
		cmd = 'make clean'
		os.system(cmd)

		cmd = 'make'
		os.system(cmd)

	def call_back_sim_mode_changed(self, widget, data=None):
		mode=self.sim_mode.get_active_text()
		inp_update_token_value("sim.inp", "#simmode", mode,1)

	def call_back_light_changed(self, widget, data=None):
		light_power=self.light.get_active_text()
		print light_power
		inp_update_token_value("light.inp", "#Psun", light_power,1)


	def get_main_menu(self, window):
		logging.info('get_main_menu')
		accel_group = gtk.AccelGroup()


		item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)

		item_factory.create_items(self.menu_items)

	        #import_image = gtk.Image()
   		#import_image.set_from_file(find_data_file("gui/document-import-2.png"))
		#myitem=item_factory.get_widget("/File/Import")
		#myitem.set_image(import_image)

		if os.path.exists("./server.inp")==False:
			item_factory.delete_item("/Plots/Fit")


		window.add_accel_group(accel_group)

		self.item_factory = item_factory

		return item_factory.get_widget("<main>")


		#cmd = ['/bin/echo', 'File', ev.pathname, 'changed']
	    #subprocess.Popen(cmd).communicate()
		

	def __init__(self):
		splash=splash_window()
		splash.init()
		self.undo_list=undo_list_class()
		self.undo_list.init()
		self.sim_dir=os.getcwd()
		self.statusicon = gtk.StatusIcon()
		self.statusicon.set_from_stock(gtk.STOCK_YES) 
		#self.statusicon.connect("popup-menu", self.right_click_event)
		self.statusicon.set_tooltip("opvdm")
		self.statusicon.connect('popup-menu', self.on_status_icon_right_click)

		logging.info('__init__')
		self.exe_dir= os.path.dirname(os.path.abspath(__file__))
		self.hpc_root_dir= os.path.dirname(os.path.abspath(__file__))+'/../'

		print "opvdm exe in "+self.exe_dir
		print "current directory "+os.getcwd()

		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_border_width(10)
		self.window.set_title("Organic Photovoltaic Device Model (www.opvdm.com)")

		self.win_list=windows()
		self.win_list.load()

		self.config=config()
		#table = gtk.Table(3,6,False)

		self.window.set_icon_from_file(find_data_file("gui/image.jpg"))

		

		self.show_tabs = True
		self.show_border = True

		self.menu_items = (
		    ( "/_File",         None,         None, 0, "<Branch>" ),
			("/File/_New", "<control>N", self.callback_new, 0, "<StockItem>", "gtk-new" ),
			("/File/_Open", "<control>O", self.callback_open, 0, "<StockItem>", "gtk-open" ),
		    ( "/File/_Save...",     None, self.callback_export, 0, "<StockItem>", "gtk-save" ),
		    ( "/File/Import",     None, self.callback_import, 0 , "<StockItem>", "gtk-harddisk"),
		    ( "/File/Quit",     "<control>Q", gtk.main_quit, 0, "<StockItem>", "gtk-quit" ),
		    ( "/_Edit/Edit file",   None,         self.callback_edit_file, 0, None ),
		    ( "/_Simulate",      None,         None, 0, "<Branch>" ),
		    ( "/Simulate/Run",  None,         self.callback_simulate, 0, "<StockItem>", "gtk-media-play" ),
		    ( "/Simulate/Parameter scan",  None,         self.callback_scan , 0, None ),
		    ( "/Simulate/Start cluster server",  None,         self.callback_start_cluster_server , 0, None ),
		    ( "/_View",      None,         None, 0, "<Branch>" ),
		    ( "/_Plots",      None,         None, 0, "<Branch>" ),
		    ( "/Plots/Open plot file",  None,         self.callback_plot_select, 0, "<StockItem>", "gtk-open"),
		    ( "/_Plots/",     None, None, 0, "<Separator>" ),
		    ( "/Plots/Numerics",  None,         None, 0, "<Branch>" ),
		    ( "/Plots/Numerics/Converge",  None,         self.callback_plot_converge, 0, None ),
		    ( "/Plots/Numerics/Matrix",  None,         self.callback_plot_matrix, 0, None ),
		    ( "/Plots/Fit",      None,         None, 0, "<Branch>" ),
		    ( "/Plots/Fit/Fit errors",  None,         self.callback_plot_fit_erros, 0, None ),
		    ( "/_Plots/",     None, None, 0, "<Separator>" ),
		    ( "/_Help",         None,         None, 0, "<LastBranch>" ),
			( "/_Help/Help Index",   None,         self.callback_help, 0, "<StockItem>", "gtk-help"  ),
		    ( "/_Help/Help about this tab",   None,         self.callback_wiki, 0, None  ),
			

		    ( "/_Help/About",   None, self.callback_about_dialog, 0, "<StockItem>", "gtk-about" ),
		    )
		pos=0

		self.menubar = self.get_main_menu(self.window)

		a = (( "/Plots/Plot after simulation",  None, self.callback_plot_after_run_toggle, 0, "<ToggleItem>" ),   )
		self.item_factory.create_items( a, )


		a = (( "/Plots/One plot window",  None, self.callback_set_plot_auto_close, 0, "<ToggleItem>" ),   )
		self.item_factory.create_items( a, )

		#table.show()
		self.window.connect("destroy", gtk.main_quit)

		self.tooltips = gtk.Tooltips()

		#window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		#window.connect("destroy", lambda w: gtk.main_quit())
		#window.set_title("Item Factory")
		self.window.set_size_request(-1, -1)
		main_vbox = gtk.VBox(False, 5)
		main_vbox.set_border_width(1)
		self.window.add(main_vbox)
		#window.add(table)
		main_vbox.show()


		toolbar = gtk.Toolbar()
		toolbar.set_style(gtk.TOOLBAR_ICONS)
		toolbar.set_size_request(-1, 50)

		toolbar2 = gtk.Toolbar()
		toolbar2.set_style(gtk.TOOLBAR_ICONS)
		toolbar2.set_size_request(-1, 30)

		#newtb = gtk.ToolButton(gtk.STOCK_NEW)
		#opentb = gtk.ToolButton(gtk.STOCK_OPEN)

		open_sim = gtk.ToolButton(gtk.STOCK_OPEN)
		self.tooltips.set_tip(open_sim, "Open a simulation")
		toolbar.insert(open_sim, pos)
		pos=pos+1

		self.save_sim = gtk.ToolButton(gtk.STOCK_SAVE)
		self.tooltips.set_tip(self.save_sim, "Save a simulation")
		toolbar.insert(self.save_sim, pos)
		pos=pos+1

		new_sim = gtk.ToolButton(gtk.STOCK_NEW)
		self.tooltips.set_tip(new_sim, "Make a new simulation")
		toolbar.insert(new_sim, pos)
		pos=pos+1

		sep_lhs = gtk.SeparatorToolItem()
		sep_lhs.set_draw(True)
		sep_lhs.set_expand(False)
		toolbar.insert(sep_lhs, pos)
		pos=pos+1

		self.undo = gtk.ToolButton(gtk.STOCK_UNDO)
		self.tooltips.set_tip(self.undo, "Undo")
		toolbar.insert(self.undo, pos)
		self.undo.connect("clicked", self.callback_undo)
		pos=pos+1

		sep_lhs = gtk.SeparatorToolItem()
		sep_lhs.set_draw(True)
		sep_lhs.set_expand(False)
		toolbar.insert(sep_lhs, pos)
		pos=pos+1

	        image = gtk.Image()
   		image.set_from_file(find_data_file("gui/play.png"))
		self.play = gtk.ToolButton(image)
		self.tooltips.set_tip(self.play, "Run the simulation")
		toolbar.insert(self.play, pos)
		self.play.connect("clicked", self.callback_simulate)
		pos=pos+1

		image = gtk.Image()
   		image.set_from_file(find_data_file("gui/forward.png"))
		self.tb_run_scan = gtk.ToolButton(image)
		self.tb_run_scan.connect("clicked", self.callback_run_scan)
		self.tooltips.set_tip(self.tb_run_scan, "Run parameter scan")
		toolbar.insert(self.tb_run_scan, pos)
		self.tb_run_scan.set_sensitive(False)
		pos=pos+1

		if debug_mode()==True:
			image = gtk.Image()
	   		image.set_from_file(find_data_file("gui/fit.png"))
			self.tb_run_fit = gtk.ToolButton(image)
			self.tb_run_fit.connect("clicked", self.callback_run_fit)
			self.tooltips.set_tip(self.tb_run_fit, "Run a fit command")
			toolbar.insert(self.tb_run_fit, pos)
			self.tb_run_fit.set_sensitive(True)
			pos=pos+1

	        image = gtk.Image()
   		image.set_from_file(find_data_file("gui/pause.png"))
		self.stop = gtk.ToolButton(image )
		self.tooltips.set_tip(self.stop, "Stop the simulation")
		self.stop.connect("clicked", self.callback_simulate_stop)
		toolbar.insert(self.stop, pos)
		pos=pos+1

		sep = gtk.SeparatorToolItem()
		sep.set_draw(True)
		sep.set_expand(False)
		toolbar.insert(sep, pos)
		pos=pos+1

	        image = gtk.Image()
   		image.set_from_file(find_data_file("gui/scan.png"))
		self.param_scan = gtk.ToolButton(image)
		self.param_scan.connect("clicked", self.callback_scan)
		self.tooltips.set_tip(self.param_scan, "Parameter scan")
		toolbar.insert(self.param_scan, pos)
		pos=pos+1

		sep = gtk.SeparatorToolItem()
		sep.set_draw(True)
		sep.set_expand(False)
		toolbar.insert(sep, pos)
		pos=pos+1

	        image = gtk.Image()
   		image.set_from_file(find_data_file("gui/plot.png"))
		self.plot_select = gtk.MenuToolButton(image,"hello")
		self.tooltips.set_tip(self.plot_select, "Find a file to plot")
		self.plotted_graphs = used_files_menu()
		self.plot_select.set_menu(self.plotted_graphs.menu)
		toolbar.insert(self.plot_select, pos)
		self.plot_select.connect("clicked", self.callback_plot_select)
		self.plot_select.set_sensitive(False)
		pos=pos+1

	        image = gtk.Image()
   		image.set_from_file(find_data_file("gui/refresh.png"))
		self.plot_open = gtk.ToolButton(image)
		self.tooltips.set_tip(self.plot_open, "Replot the graph")
		toolbar.insert(self.plot_open, pos)
		self.plot_open.set_sensitive(False)
		pos=pos+1

	        image = gtk.Image()
   		image.set_from_file(find_data_file("gui/plot_time.png"))
		self.examine = gtk.ToolButton(image)
		self.tooltips.set_tip(self.examine, "Examine results in time domain")
		self.examine.connect("clicked", self.callback_examine)
		toolbar.insert(self.examine, pos)
		pos=pos+1

		sep = gtk.SeparatorToolItem()
		sep.set_draw(True)
		sep.set_expand(False)
		toolbar.insert(sep, pos)
		pos=pos+1

	        image = gtk.Image()
   		image.set_from_file(find_data_file("gui/mesh.png"))
		self.mesh = gtk.ToolButton(image)
		self.tooltips.set_tip(self.mesh, "Edit the electrical mesh")
		self.mesh.connect("clicked", self.callback_edit_mesh)
		toolbar.insert(self.mesh, pos)
		pos=pos+1

		if os.path.isfile(find_data_file("optics_epitaxy.inp")):
			image = gtk.Image()
	   		image.set_from_file(find_data_file("gui/optics.png"))
			self.optics_button = gtk.ToolButton(image)
			self.tooltips.set_tip(self.optics_button, "Optical simulation")
			self.optics_button.connect("clicked", self.callback_optics_sim)
			toolbar.insert(self.optics_button, pos)
			pos=pos+1


		if debug_mode()==True:
			image = gtk.Image()
	   		image.set_from_file(find_data_file("gui/server.png"))
			cluster = gtk.ToolButton(image)
			cluster.connect("clicked", self.callback_cluster)
			self.tooltips.set_tip(cluster, "Configure cluster")
			toolbar.insert(cluster, pos)
			cluster.show()
			pos=pos+1


		sep2 = gtk.SeparatorToolItem()
		sep2.set_draw(False)
		sep2.set_expand(True)
		toolbar.insert(sep2, pos)
		pos=pos+1


		help = gtk.ToolButton(gtk.STOCK_HELP)
		self.tooltips.set_tip(help, "Help")
		help.connect("clicked", self.callback_help)
		toolbar.insert(help, pos)
		pos=pos+1


		quittb = gtk.ToolButton(gtk.STOCK_QUIT)
		self.tooltips.set_tip(quittb, "Quit")
		toolbar.insert(quittb, pos)
		quittb.connect("clicked", gtk.main_quit)
		pos=pos+1

		new_sim.connect("clicked", self.callback_new)
		open_sim.connect("clicked", self.callback_open)
		self.save_sim.connect("clicked", self.callback_export)

		self.plot_open.connect("clicked", self.callback_plot_open)

		self.sim_mode = gtk.combo_box_entry_new_text()

		f = open(find_data_file("sim_menu.inp"))
		lines = f.readlines()
		f.close()

		for i in range(0, len(lines)):
			self.sim_mode.append_text(lines[i].rstrip())

		self.sim_mode.child.connect('changed', self.call_back_sim_mode_changed)
		set_active_name(self.sim_mode, inp_get_token_value("sim.inp", "#simmode"))

		lable=gtk.Label("Simulation mode:")
		#lable.set_width_chars(15)
		lable.show
	        hbox = gtk.HBox(False, 2)
        	
	        hbox.pack_start(lable, False, False, 0)
	        hbox.pack_start(self.sim_mode, False, False, 0)

		tb_comboitem = gtk.ToolItem();
		tb_comboitem.add(hbox);
		tb_comboitem.show_all()
		toolbar2.insert(tb_comboitem, 0)
		logging.info('__init__5')

		self.light = gtk.combo_box_entry_new_text()
		sun_values=["0.0","0.01","0.1","1.0","10"]
		token=inp_get_token_value("light.inp", "#Psun")
		if sun_values.count(token)==0:
			sun_values.append(token)

		for i in range(0,len(sun_values)):
			self.light.append_text(sun_values[i])

		self.light.child.connect('changed', self.call_back_light_changed)
		set_active_name(self.light, token)

		ti_light = gtk.ToolItem();
		lable=gtk.Label("Light intensity:")
		lable.show
	        hbox = gtk.HBox(False, 2)
	        hbox.pack_start(lable, False, False, 0)
	        hbox.pack_start(self.light, False, False, 0)

		ti_light.add(hbox)
		ti_light.show_all()
		toolbar2.insert(ti_light, 1)

		sep = gtk.SeparatorToolItem()
		sep.set_draw(False)
		sep.set_expand(True)
		sep.show_all()
		toolbar2.insert(sep, 2)

		ti_progress = gtk.ToolItem()
		hbox = gtk.HBox(False, 2)

		logging.info('__init__6')
		#hbox.set_child_packing(self.progress, False, False, 0, 0)

		self.spin=gtk.Spinner()
		self.spin.set_size_request(32, 32)
		self.spin.show()
		self.spin.stop()

		logging.info('__init__6.1')
		gap=gtk.Label(" ")
		hbox.add(gap)
		hbox.add(self.spin)	
		#hbox.set_child_packing(self.spin, False, False, 0, 0)



		gap.show()
		hbox.show()
		logging.info('__init__6.2')
		ti_progress.add(hbox)
		toolbar2.insert(ti_progress, 3)
		ti_progress.show()


		toolbar.show_all()
		toolbar2.show()


		main_vbox.pack_start(self.menubar, False, True, 0)
		handlebox = gtk.HandleBox()
		handlebox.set_snap_edge(gtk.POS_LEFT)
		handlebox.show()

		toolbar.set_size_request(1000, -1)
		toolbar2.set_size_request(900, -1)
		tb_vbox=gtk.VBox()
		tb_vbox.add(toolbar)
		tb_vbox.add(toolbar2)
		tb_vbox.show()



		handlebox.add(tb_vbox)

		main_vbox.pack_start(handlebox, False, False, 0)
		self.progress = gtk.ProgressBar(adjustment=None)

		self.progress.hide()

		main_vbox.pack_start(self.progress, False, False, 0)#add(self.progress)





		self.window.connect("delete-event", self.callback_close_window) 

		logging.info('__init__7')
		self.win_list.set_window(self.window,"main_window")



		self.menubar.show()

		self.make_window2(main_vbox)

		self.window.show()

		process_events()		

		self.electrical_mesh=tab_electrical_mesh()
		self.electrical_mesh.init()

		logging.info('__init__6.5')
		self.thread = _FooThread()
		self.thread.connect("file_changed", self.user_callback)
		self.thread.daemon = True
		self.thread.start()
		logging.info('__init__6.6')


	def make_window2(self,main_vbox):
		notebook.set_tab_pos(gtk.POS_TOP)
		notebook.show()
		notebook.set_current_page(1)

		box=gtk.HBox()
		self.status_bar = gtk.Statusbar()      
		self.context_id = self.status_bar.get_context_id("Statusbar example")
		self.status_bar.push(self.context_id, os.getcwd())

		box.add(self.status_bar)

		self.window2_box=gtk.VBox()
		self.window2_box.add(notebook)
		self.window2_box.add(box)
		self.window2_box.set_child_packing(box, False, False, 0, 0)
		self.window2_box.set_size_request(-1, 550)
		self.window2 = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window2.set_border_width(10)

		self.window2.set_title("Organic Photovoltaic Device Model (www.opvdm.com)")
		self.window2.connect("delete-event", self.callback_close_window2)

		self.window2.set_icon_from_file(find_data_file("gui/image.jpg"))
		if main_vbox==None:
			self.window2.add(self.window2_box)
		else:
			main_vbox.add(self.window2_box)			



		box.show()
		self.status_bar.show()
		self.window2_box.show()

		self.change_dir_and_refresh_interface(os.getcwd())
		if main_vbox==None:
			self.window2.show()

def main():
	gtk.main()
	return 0

if __name__ == "__main__":

	NotebookExample()
	main()

