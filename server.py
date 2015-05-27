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
from search import return_file_list
from util import find_data_file
from about import about_dialog_show
from util import str2bool
from used_files_menu import used_files_menu
from inp import inp_get_token_value
import threading
import gobject
import multiprocessing
import time
import glob
import socket
from time import sleep
from win_lin import running_on_linux
import subprocess
from util import gui_print_path

if running_on_linux()==True:
	import pyinotify
else:
	from welcome_windows import welcome_class	
	import win32file
	import win32con

	FILE_LIST_DIRECTORY = 0x0001

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
		self.notifier=False
 
	def onChange(self,ev):
		if running_on_linux()==True:
			file_name=os.path.basename(ev.pathname)
		else:
			file_name=os.path.basename(ev)

		file_name=file_name.rstrip()
		self.thread_data[0]
		self.thread_data[0]=file_name
		print "File changed!!!!!!!!!!!!!!!!!!!!!"
		self.emit("file_changed")

	def set_watch_path(self,path,thread_data):
		self.watch_path=path
		self.thread_data=thread_data

	def run(self):
		if running_on_linux()==True:
			wm = pyinotify.WatchManager()
			ret=wm.add_watch(self.watch_path, pyinotify.IN_CLOSE_WRITE, self.onChange,False,False)
			print ret
			print "notifyer!!!!!!!!!!!!!",self.notifier
			self.notifier = pyinotify.Notifier(wm)
			self.notifier.loop()
		else:
			hDir = win32file.CreateFile (self.watch_path,FILE_LIST_DIRECTORY,win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,None,win32con.OPEN_EXISTING,win32con.FILE_FLAG_BACKUP_SEMANTICS,None)

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
					full_filename = os.path.join (self.watch_path, file)
					self.onChange(full_filename)
	

	def stop(self):
		print "thread2:I have shutdown the thread!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",threading.currentThread()
		if running_on_linux()==True:
			self.notifier.stop()
			self.notifier=False
		print "thread:I have shutdown the thread!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",threading.currentThread()

class server:
	def __init__(self):
		self.running=False
		self.thread_data=[""]
		self.enable_gui=False

	def init(self,sim_dir):
		self.terminate_on_finish=False
		self.mylock=False
		self.cpus=multiprocessing.cpu_count()
		self.jobs=[]
		self.status=[]
		self.jobs_running=0
		self.jobs_run=0
		self.sim_dir=sim_dir
		self.cluster=str2bool(inp_get_token_value("server.inp","#cluster"))
		self.server_ip=inp_get_token_value("server.inp","#server_ip");
		self.errors=""

	def start_threads(self):
		if self.cluster==False:
			self.thread = _FooThread()
			self.thread.set_watch_path(self.sim_dir,self.thread_data)
			self.thread.connect("file_changed", self.callback)
			self.thread.daemon = True
			print "I am watching!!!!!!!!!!!!!!!!!!!!!!!!!!!!",self.sim_dir
			if self.running==True:
				#print "thread:I'm still running!!!!!!!!!!!!!"
				self.stop()
			self.thread.start()

		else:
			if self.running==False:
				try:
					self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

					# Open TPC port to server
					server_address = (self.server_ip, 10002)
					print >>sys.stderr, 'connecting to %s port %s' % server_address
					self.tcp_sock.connect(server_address)

					self.tcp_sock.sendall("open_tpc")
				except:
					return -1

				self.mylock=False
				self.thread = threading.Thread(target = self.listen)
				self.thread.daemon = True
				self.thread.start()

		return 0

	def set_terminal(self,terminal):
		self.terminal=terminal
	def gui_sim_start(self):
		self.errors=""
		s=gtk.gdk.screen_get_default()
		w,h=self.progress_window.get_size()

		x=s.get_width()-w
		y=0

		self.progress_window.move(x,y)

		self.progress_window.show()
		self.spin.start()

		self.extern_gui_sim_start()

	def gui_sim_stop(self):
		self.progress_window.hide()
		self.spin.stop()
		self.extern_gui_sim_stop("Finished simulation")
		if self.errors!="":
			message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
			message.set_markup(self.errors)
			message.run()
			message.destroy()
		self.errors=""

	def setup_gui(self,extern_gui_sim_start,extern_gui_sim_stop):
		self.enable_gui=True
		self.extern_gui_sim_start=extern_gui_sim_start
		self.extern_gui_sim_stop=extern_gui_sim_stop
		self.progress_window=gtk.Window()
		self.progress_window.set_decorated(False)
		self.progress_window.set_title("opvdm progress")
		self.progress_window.set_size_request(400, 50)
		self.progress_window.set_position(gtk.WIN_POS_CENTER)
		self.progress_window.set_keep_above(True)
		main_hbox = gtk.HBox(False, 5)
		main_hbox.set_border_width(1)
		main_hbox.show()

		self.progress = gtk.ProgressBar(adjustment=None)
		self.progress.show()

		main_hbox.pack_start(self.progress, True, True, 0)

		self.spin=gtk.Spinner()
		self.spin.set_size_request(32, 32)
		self.spin.show()
		self.spin.stop()

		main_hbox.pack_start(self.spin, False, False, 0)


		main_vbox = gtk.VBox(False, 5)
		main_vbox.show()
		main_vbox.pack_start(main_hbox, True, True, 0)

		self.progress_array = []
		for i in range(0,10):
			self.progress_array.append(gtk.ProgressBar(adjustment=None))
			self.progress_array[i].hide()
			self.progress_array[i].set_size_request(-1, 15)
			self.progress_array[i].modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse("green"))
			main_vbox.pack_end(self.progress_array[i], True, False, 0)

		self.label=gtk.Label("Running...")
		#label.set_justify(gtk.JUSTIFY_LEFT)
		self.label.show()

		main_vbox.pack_start(main_hbox, True, True, 0)
		main_vbox.pack_start(self.label, True, True, 4)


		self.progress_window.add(main_vbox)

		#self.progress_window.show()

		#self.gtk.Window.set_keep_above

	def add_job(self,command):
		if self.cluster==False:
			self.jobs.append(command)
			self.status.append(0)
		else:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			port = 8888;
			s.sendto("addjobs#"+command, (self.server_ip, port))
			s.close()

	def wake_nodes(self):
		if self.cluster==True:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			port = 8888;
			s.sendto("wake_nodes", (self.server_ip, port))
			s.close()

	def clear_cache(self):
		if self.cluster==True:
			if self.running==True:
				print "Clear cache on server"
				self.mylock=True
				s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				port = 8888;
				s.sendto("clear_cache#", (self.server_ip, port))
				s.close()
				print "I should be waiting for mylock"
				self.wait_lock()
				print "I have finished waiting"


	def start(self,exe_command):
		if self.enable_gui==True:
			self.progress_window.show()
			self.gui_sim_start()
		#self.statusicon.set_from_stock(gtk.STOCK_NO) 
		self.exe_command=exe_command
		self.running=True
		self.run_jobs()



	def listen(self):
		print "thread !!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
		self.running=True
		try:
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		except socket.error:
			print 'Failed to create socket'
			sys.exit()

		self.socket.bind(('', 8889))

		while(1):
			d = self.socket.recvfrom(1024)
			data = d[0]
			addr = d[1]
			print data
			print "command=",data
			if data.startswith("percent"):
				command=data.split("#")
				percent=float(command[1])
				self.progress.set_fraction(percent/100.0)
			if data.startswith("job_finished"):
				command=data.split("#")
				self.label.set_text(gui_print_path("Finished:  ",command[1],60))
			if data.startswith("finished"):
				self.stop()
				sys.exit()
			if data.startswith("ok"):
				self.mylock=False
			if data.startswith("node_error"):
				command=data.split("#")
				self.errors=self.errors+"Node error!!! "+command[1]
				#self.mylock.set()
			if data.startswith("load"):
				if data.count("#")>1:
					command=data.split("#")
					items=len(command)
					height=50
					for i in range(1,len(command)):
						print command[i]
						height=height+15
						percent=float(command[i])
						if self.progress_array[i].get_property("visible")==False:
							self.progress_array[i].show()
						self.progress_array[i].set_fraction(percent)

					window_height=self.progress_window.get_size()
					window_height=window_height[1]
					if window_height!=height:
						self.progress_window.set_size_request(400, height)
			if data.startswith("server_quit"):
				self.stop()
				print "Server quit!"

	def set_wait_bit(self):
		self.opp_finished=False

	
	def print_jobs(self):
		for i in range(0, len(self.jobs)):
			print self.jobs[i],self.status[i]

	def killall(self):
		if self.cluster==True:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			port = 8888;
			s.sendto("killall", (self.server_ip, port))
			s.close()
		else:
			exe_name=os.path.basename(self.exe_command)
			cmd = 'killall '+exe_name
			ret= os.system(cmd)

		self.stop()

	def print_jobs(self):
		if self.cluster==True:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			port = 8888;
			s.sendto("print_jobs", (self.server_ip, port))
			s.close()


	def sleep(self):
		if self.cluster==True:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			port = 8888;
			s.sendto("sleep", (self.server_ip, port))
			s.close()	

	def poweroff(self):
		if self.cluster==True:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			port = 8888;
			s.sendto("poweroff", (self.server_ip, port))
			s.close()	

	def get_data(self):
		if self.cluster==True:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			port = 8888;
			s.sendto("get_data", (self.server_ip, port))
			s.close()	


	def wait_lock(self):
		print "Waiting for cluster..."
		while(self.mylock==True):
			sleep(0.1)


	def run_jobs(self):
		if self.cluster==True:
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			port = 8888;
			self.mylock=True
			s.sendto("set_master_ip", (self.server_ip, port))
			self.wait_lock()

			self.mylock=True
			s.sendto("set_exe#"+self.exe_command, (self.server_ip, port))
			self.wait_lock()

			#self.mylock.clear()
			s.sendto("run", (self.server_ip, port))
			#self.mylock.wait(1000)

			s.close()
		else:
			if (len(self.jobs)==0):
				return

			for i in range(0, len(self.jobs)):
				if (self.jobs_running<self.cpus):
					if self.status[i]==0:
						self.status[i]=1
						print "Running job",self.jobs[i]
						if self.enable_gui==True:
							self.label.set_text("Running job"+self.jobs[i])

						self.jobs_running=self.jobs_running+1
						if running_on_linux()==True:
							cmd="cd "+self.jobs[i]+";"
							cmd=cmd+self.exe_command+" --lock "+os.path.join(self.sim_dir,"lock"+str(i)+".dat")+" &\n"
							print "command="+cmd
							if self.enable_gui==True:
								self.terminal.feed_child(cmd)
							else:
								print cmd
								os.system(cmd)
							
						else:
		
							#print "thread: forked"
							#if os.fork() == 0:
							#os.chdir(self.jobs[i])
							cmd=self.exe_command+" --lock "+os.path.join(self.sim_dir,"lock"+str(i)+".dat")+" &\n"
							print cmd,self.jobs[i]
							subprocess.Popen(cmd,cwd=self.jobs[i])
							#os.system(cmd)

							#sys.exit()

	def stop(self):
		if self.cluster==False:
			self.thread.stop()
			self.running=False
		else:
			self.socket.close()
			self.tcp_sock.close()


		self.jobs=[]
		self.status=[]
		self.jobs_running=0
		self.jobs_run=0
		self.gui_sim_stop()
		self.progress.set_fraction(0.0) 
		self.running=False
		ls=os.listdir(self.sim_dir)

		for i in range(0, len(ls)):
			if ls[i][:4]=="lock" and ls[i][-4:]==".dat":
				del_file=os.path.join(self.sim_dir,ls[i])
				print "delete file:",del_file
				os.remove(del_file)
	
		print "thread: I have shut down the server."


	def simple_run(self,exe_command):
		self.exe_command=exe_command
		ls=os.listdir(self.sim_dir)
		for i in range(0, len(ls)):
			if ls[i][:4]=="lock" and ls[i][-4:]==".dat":
				del_file=os.path.join(self.sim_dir,ls[i])
				print "delete file:",del_file
				os.remove(del_file)
		self.run_jobs()

		while(1):
			ls=os.listdir(self.sim_dir)
			for i in range(0, len(ls)):
				if ls[i][:4]=="lock" and ls[i][-4:]==".dat":
					lock_file=ls[i]
					os.remove(os.path.join(self.sim_dir,lock_file))
					self.jobs_run=self.jobs_run+1
					self.jobs_running=self.jobs_running-1
			self.run_jobs()
			time.sleep(0.1)

			if self.jobs_run==len(self.jobs):
				break
				
	def callback(self,object):
		print "File!!!!!!!!!!!! changed"
		file_name=self.thread_data[0]
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

