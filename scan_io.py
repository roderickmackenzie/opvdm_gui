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
import gc
import gtk
import sys
import os
import shutil
from util import delete_link_tree

def scan_delete_simulations(dirs_to_del):
	for i in range(0, len(dirs_to_del)):
		delete_link_tree(dirs_to_del[i])

def scan_list_simulations(dirs_to_del,dir_to_search):
	ls=os.listdir(dir_to_search)
	print ls
	for i in range(0, len(ls)):
		full_name=os.path.join(dir_to_search,ls[i])
		if os.path.isdir(full_name):
			if os.path.isfile(os.path.join(full_name,'scan.inp')):
				dirs_to_del.append(full_name)

def scan_clean_dir(dir_to_clean):
		dirs_to_del=[]
		scan_list_simulations(dirs_to_del,dir_to_clean)
		print dirs_to_del,dir_to_clean

		if (len(dirs_to_del)!=0):

			settings = gtk.settings_get_default()
			settings.set_property('gtk-alternative-button-order', True)

			dialog = gtk.Dialog()
			cancel_button = dialog.add_button(gtk.STOCK_YES, gtk.RESPONSE_YES)

			ok_button = dialog.add_button(gtk.STOCK_NO, gtk.RESPONSE_NO)
			ok_button.grab_default()

			help_button = dialog.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)

			text_del_dirs=""
			if len(dirs_to_del)>30:
				for i in range(0,30,1):
					text_del_dirs=text_del_dirs+dirs_to_del[i]+"\n"
				text_del_dirs=text_del_dirs+"and "+str(len(dirs_to_del)-30)+" more."
			else:
				for i in range(0,len(dirs_to_del)):
					text_del_dirs=text_del_dirs+dirs_to_del[i]+"\n"

			label = gtk.Label("Should I delete the old simualtions first?:\n"+"\n"+text_del_dirs)
			dialog.vbox.pack_start(label, True, True, 0)
			label.show()

			dialog.set_alternative_button_order([gtk.RESPONSE_YES, gtk.RESPONSE_NO,
						       gtk.RESPONSE_CANCEL])

			#dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_QUESTION,  gtk.BUTTONS_YES_NO, str("Should I delete the old simualtions first?:\n"+"\n".join(dirs_to_del)))
			response = dialog.run()
			
			if response == gtk.RESPONSE_YES:
					scan_delete_simulations(dirs_to_del)
			elif response == gtk.RESPONSE_NO:
				print "Not deleting"
			elif response == gtk.RESPONSE_CANCEL:
				run=False
				print "Cancel"

			dialog.destroy()
