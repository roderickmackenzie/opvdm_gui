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
from search import return_file_list
from plot import plot_data
from plot import plot_info
from util import find_data_file
from about import about_dialog_show
from used_files_menu import used_files_menu
import threading
import gobject
import pyinotify
import multiprocessing
import time
import glob

class _IdleObject(gobject.GObject):

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
		file_name=os.path.basename(ev.pathname)
		file_name=file_name.rstrip()
		self.thread_data[0]
		self.thread_data[0]=file_name
		self.emit("file_changed")

	def set_watch_path(self,path,thread_data):
		self.watch_path=path
		self.thread_data=thread_data

	def run(self):
		wm = pyinotify.WatchManager()
		ret=wm.add_watch(self.watch_path, pyinotify.IN_CLOSE_WRITE, self.onChange,False,False)
		print ret
		self.notifier = pyinotify.Notifier(wm)
		self.notifier.loop()
		

	def stop(self):
		print "thread2:I have shutdown the thread!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",threading.currentThread()
		self.notifier.stop()
		print "thread:I have shutdown the thread!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",threading.currentThread()

class server:
	def __init__(self):
		self.running=False
		self.thread_data=[""]

	def init(self):
		self.cpus=multiprocessing.cpu_count()
		self.jobs=[]
		self.status=[]
		self.jobs_running=0
		self.jobs_run=0

	def set_terminal(self,terminal):
		self.terminal=terminal

	def setup_gui(self,progress,gui_sim_start,gui_sim_stop):
		self.progress=progress
		self.gui_sim_start=gui_sim_start
		self.gui_sim_stop=gui_sim_stop

	def add_job(self,command):
		self.jobs.append(command)
		self.status.append(0)

	def start(self,sim_dir,exe_command):
		self.progress.show()
		self.gui_sim_start()
		#self.statusicon.set_from_stock(gtk.STOCK_NO) 
		self.sim_dir=sim_dir
		self.exe_command=exe_command
		self.thread = _FooThread()
		self.thread.set_watch_path(self.sim_dir,self.thread_data)
		self.thread.connect("file_changed", self.callback)
		self.thread.daemon = True
		if self.running==True:
			print "thread:I'm still running!!!!!!!!!!!!!"
			self.stop()

		self.running=True
		self.thread.start()
		self.run_jobs()


	def print_jobs(self):
		for i in range(0, len(self.jobs)):
			print self.jobs[i],self.status[i]

	def run_jobs(self):
		if (len(self.jobs)==0):
			return

		for i in range(0, len(self.jobs)):
			if (self.jobs_running<self.cpus):
				if self.status[i]==0:
					self.status[i]=1
					self.jobs_running=self.jobs_running+1
					print "Running job",self.jobs[i]
					#print "thread: forked"
					#if os.fork() == 0:
					#os.chdir(self.jobs[i])
					cmd="cd "+self.jobs[i]+";"
					cmd=cmd+self.exe_command+" --zip_results --lock "+self.sim_dir+"lock"+str(i)+".dat &\n"
					#os.system(cmd)
					self.terminal.feed_child(cmd)
					#print "Finished",self.jobs[i]
					#f = open(self.sim_dir+"lock"+str(i)+".dat",'w')
					#f.write("hello")
					#f.close()

					#sys.exit()

	def stop(self):
		self.thread.stop()
		self.jobs=[]
		self.status=[]
		self.jobs_running=0
		self.jobs_run=0
		self.gui_sim_stop("Simulations finished")
		self.progress.set_fraction(0.0) 
		self.running=False
		ls=os.listdir(self.sim_dir)

		for i in range(0, len(ls)):
			if ls[i][:4]=="lock" and ls[i][-4:]==".dat":
				del_file=self.sim_dir+'/'+ls[i]
				print "delete file:",del_file
				os.remove(del_file)

		print "thread: I have shut down the server."

	def callback(self,object):
		file_name=self.thread_data[0]
		print file_name		
		if str(file_name)>4:
			test=file_name[:4]
			if test=="lock":
				rest=file_name[4:]
				finished=int(os.path.splitext(rest)[0])
				#print self.jobs[finished]
				#self.print_jobs()
				self.jobs_run=self.jobs_run+1
				self.jobs_running=self.jobs_running-1
				self.progress.set_fraction(float(self.jobs_run)/float(len(self.jobs)))
				self.run_jobs()
				if (self.jobs_run==len(self.jobs)):
					self.stop()

