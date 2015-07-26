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



import gtk
import os

COL_PATH = 0
COL_PIXBUF = 1
COL_IS_DIRECTORY = 2

class opvdm_open(gtk.Dialog): 


	def init(self,path):
		self.file_path=""
		self.set_default_response(gtk.RESPONSE_OK)
		self.set_title("Open file - opvdm")
		self.set_flags(gtk.DIALOG_DESTROY_WITH_PARENT)
		#self.add_buttons("OK",True,"Cancel",False)

		self.set_size_request(800, 400)
		self.set_position(gtk.WIN_POS_CENTER)

		self.dir = path
		self.root_dir= path

		vbox = gtk.VBox(False, 0);

		toolbar = gtk.Toolbar()
		vbox.pack_start(toolbar, False, False, 0)

		self.up_button = gtk.ToolButton(gtk.STOCK_GO_UP);
		self.up_button.set_is_important(True)
		self.up_button.set_sensitive(False)
		toolbar.insert(self.up_button, -1)

		home_button = gtk.ToolButton(gtk.STOCK_HOME)
		home_button.set_is_important(True)
		toolbar.insert(home_button, -1)



		self.text= gtk.Entry()
		self.text.show()
		self.text.set_text(self.dir)
		self.text.set_size_request(500, -1)
		tb_path = gtk.ToolItem()
		tb_path.add(self.text)
		tb_path.show_all()
		toolbar.insert(tb_path, -1)



		self.fileIcon = self.get_icon(gtk.STOCK_FILE)
		self.dirIcon = self.get_icon(gtk.STOCK_DIRECTORY)

		sw = gtk.ScrolledWindow()
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		vbox.pack_start(sw, True, True, 0)

		self.store = self.create_store()
		self.fill_store()

		icon_view = gtk.IconView(self.store)
		icon_view.set_selection_mode(gtk.SELECTION_MULTIPLE)

		self.up_button.connect("clicked", self.on_up_clicked)
		home_button.connect("clicked", self.on_home_clicked)

		icon_view.set_text_column(COL_PATH)
		icon_view.set_pixbuf_column(COL_PIXBUF)

		icon_view.connect("item-activated", self.on_item_activated)
		sw.add(icon_view)
		icon_view.grab_focus()
		icon_view.set_spacing(0)
		icon_view.set_row_spacing(0)
		icon_view.set_column_spacing(0)

		self.vbox.pack_start( vbox)
		self.show_all()

	def get_icon(self, name):
		theme = gtk.icon_theme_get_default()
		return theme.load_icon(name, 48, 0)
    

	def create_store(self):
		store = gtk.ListStore(str, gtk.gdk.Pixbuf, bool)
		store.set_sort_column_id(COL_PATH, gtk.SORT_ASCENDING)
		return store

	def get_filename(self):
		return self.file_path

	def fill_store(self):
		self.store.clear()

		for fl in os.listdir(self.dir):
			file_name=os.path.join(self.dir, fl)
			if os.path.isdir(file_name):
			    self.store.append([fl, self.dirIcon, True])
			else:
				append=False
				if (file_name.endswith(".dat")==True):
					f = open(file_name, 'r')
					text = f.readline()
					f.close()
					print text
					text=text.rstrip()
					if text=="#opvdm":
						append=True

				if (file_name.endswith(".inp")==True):
					append=True


				if append==True:
					self.store.append([fl, self.fileIcon, False])

	def on_home_clicked(self, widget):
		self.dir = self.root_dir
		self.fill_store()
        
    
	def on_item_activated(self, widget, item):

		model = widget.get_model()
		path = model[item][COL_PATH]
		isDir = model[item][COL_IS_DIRECTORY]

		if isDir==False:
			self.file_path=os.path.join(self.dir, path)
			self.response(True)
		    	return
		    
		self.dir = os.path.join(self.dir, path)
		self.change_path()

	def change_path(self):
		self.text.set_text(self.dir)

		self.fill_store()
		sensitive = True
		print self.dir,self.root_dir
		if self.dir == self.root_dir:
			sensitive = False

		self.up_button.set_sensitive(sensitive)

	def on_up_clicked(self, widget):
		self.dir = os.path.dirname(self.dir)
		self.change_path()

