import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import shutil
from util import find_data_file
from ver import ver
from notice import notice
def about_dialog_show():
	about = gtk.AboutDialog()
	about.set_program_name("opvdm")
	about.set_version("")
	#about.set_copyright("The GUI for opvdm, Copyright Roderick MacKenzie 2014")
	about.set_comments(ver()+"\n"+notice())
	about.set_website("http://www.opvdm.com")

	image=find_data_file("gui/image.jpg")
	about.set_logo(gtk.gdk.pixbuf_new_from_file(image))
	about.run()
	about.destroy()
