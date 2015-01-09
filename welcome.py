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
import commands

class welcome_class(gtk.HBox):
	
	lines=[]
	edit_list=[]
	file_name=""
	line_number=[]
	save_file_name=""

	# This callback quits the program
	def delete_event(self, widget, event, data=None):
		gtk.main_quit()
		return False


	def wow(self,image_name):
		print "Welcome"

		output=str(commands.getstatusoutput('opvdm --version')[1])
		label = gtk.Label()
		label.set_markup("<big><b>Organic photovoltaic device model</b>\n"+
				 "(<a href=\"http://www.opvdm.com\" "+
                         "title=\"Click to find out more\">www.opvdm.com</a>)\n\n"
				+"To make a new simulation directory click <i>new</i> in the <i>file</i> menu\n"
				+"or to open an existing simulation click on the <i>open</i> button.\n"
				+"There is more help on the <a href=\"http://www.opvdm.com/opvdm_wiki.html\">Wiki</a>.  "

				+"Please report bugs to\nroderick.mackenzie@nottingham.ac.uk.\n\n"
				+"Rod\n18/10/13\n"
				+"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n\n\n"
				+output+"</big>")
		self.add(label)
	        image = gtk.Image()
   		image.set_from_file(image_name)
		self.add(image)

   		image.show()
		label.show()


		

