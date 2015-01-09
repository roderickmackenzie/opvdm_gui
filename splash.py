import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import shutil
import glib
from token_lib import tokens
from numpy import *
from util import pango_to_gnuplot
from plot import plot_data
from util import find_data_file
from ver import ver
from notice import notice

class splash_window():
	def timer_cb(self):
		self.window.destroy()
		return False

	def destroy(self):
		self.window.destroy()

	def callback_destroy(self,widget):
		self.destroy()

	def show_cb(self,widget, data=None):
		glib.timeout_add(1500, self.timer_cb)

	def init(self):
		self.window = gtk.Window()
		self.window.connect("show", self.show_cb)

		self.window.set_decorated(False)
		self.window.set_border_width(10)
		self.window.set_keep_above(True)
		fixed = gtk.Fixed()
		image = gtk.Image()
		image_file=find_data_file("gui/splash.png")
		label = gtk.Label()
		label.set_use_markup(gtk.TRUE)
		label.set_markup('<span color="black" size="88000"><b>opvdm</b></span>')
		label.show()
		image.set_from_file(image_file)
		image.show()
		#fixed.put(image, 0, 0)
		fixed.put(label,40,40)

		label = gtk.Label()
		label.set_use_markup(gtk.TRUE)
		label.set_markup(notice()+"\n"+ver())
		label.show()

		fixed.put(label,40,200)

		self.window.add(fixed)
		self.window.set_position(gtk.WIN_POS_CENTER)
		self.window.show_all()
		self.window.connect("destroy", self.callback_destroy)


