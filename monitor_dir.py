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
import threading
import gobject
import multiprocessing
import glob
import socket
from time import sleep
from win_lin import running_on_linux
import subprocess
from util import gui_print_path

if running_on_linux()==True:
	import pyinotify
else:
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
		print "thread: file changed"
		self.emit("file_changed")

	def set_watch_path(self,path,thread_data):
		self.watch_path=path
		self.thread_data=thread_data

	def run(self):
		if running_on_linux()==True:
			print "thread: start"
			wm = pyinotify.WatchManager()
			print "wathcing path",self.watch_path
			ret=wm.add_watch(self.watch_path, pyinotify.IN_CLOSE_WRITE, self.onChange,False,False)
			print ret
			print "thread: start notifyer",self.notifier
			self.notifier = pyinotify.Notifier(wm)
			try:
				while 1:
					self.notifier.process_events()
					if self.notifier.check_events():
						self.notifier.read_events()
			#self.notifier.loop()
			except:
				print "error in notify",sys.exc_info()[0]
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
		print "thread: stop been called",threading.currentThread()
		if running_on_linux()==True:
			self.notifier.stop()
			self.notifier=False
			print "thread:I have shutdown the notifyer",threading.currentThread()
