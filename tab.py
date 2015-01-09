import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import shutil
from scan_item import scan_item
from scan_item import scan_item_add
from token_lib import tokens
from util import check_is_config_file
from inp import inp_update_token_value
from inp import inp_get_token_value
from undo import undo_list_class
import zipfile
import base64

class tab_class(gtk.VBox):
	
	lines=[]
	edit_list=[]
	file_name=""
	line_number=[]
	name=""
	visible=1

	def callback_edit(self, widget, data=None):
		#print self.file_name," ",data," ",type(widget)
		if type(widget)==gtk.Entry:
			a=undo_list_class()
			a.add([self.file_name, data, inp_get_token_value(self.file_name, data),widget])
			inp_update_token_value(self.file_name, data, widget.get_text())
			#print self.undo_list
		else:
			inp_update_token_value(self.file_name, data, widget.get_active_text())

	def init(self,filename,fullname,check_list):
		self.widget_type=[]
		self.file_name=filename
		self.edit_list=[]
		self.line_number=[]
		print "loading ",filename
		if check_is_config_file(filename)=="file":
			f = open(filename)
			self.lines = f.readlines()
			f.close()
		elif check_is_config_file(filename)=="archive":
			zf = zipfile.ZipFile('sim.opvdm', 'r')
			self.lines = zf.read(filename).split("\n")
			print self.lines
			zf.close()
		else:
			print "File not found"

		pos=0
		for i in range(0, len(self.lines)):
			self.lines[i]=self.lines[i].rstrip()

		n=0
		pos=0
		my_token_lib=tokens()
		height=27
		for i in range(0, len(self.lines)/2):

			show=False
			units="Units"
			token=self.lines[pos]
			result=my_token_lib.find(token)
			if result!=False:
				units=result.units
				text_info=result.info
				show=True
			pos=pos+1
			self.set_size_request(600,-1)
			if show == True :
				hbox=gtk.HBox()
				hbox.show()
				label = gtk.Label()
				label.set_size_request(400,height)
				label.set_markup(text_info)
				label.set_use_markup(True)
				hbox.pack_start(label, False, False, padding=1)
				label.show()

				self.line_number.append(pos)

				if result.opt[0]=="text":
					edit_box=gtk.Entry(max=0)
					edit_box.set_text(self.lines[pos]);
					edit_box.connect("changed", self.callback_edit, token)
					edit_box.show()
					self.widget_type.append("edit")
				else:
					edit_box=gtk.combo_box_new_text()
					index=0
					for i in range(0,len(result.opt)):
						edit_box.append_text(result.opt[i])
						if self.lines[pos]==result.opt[i]:
							index=i
					edit_box.set_active(index);
					
					edit_box.connect("changed", self.callback_edit, token)
					edit_box.show()
					self.widget_type.append("combo")
					print "Rod",self.widget_type[n],n,len(self.widget_type)
				edit_box.set_size_request(300,height)
				self.edit_list.append(edit_box)
				hbox.pack_start(edit_box, False, False, padding=1)
				#print "out -> %s %i",out_text,len(self.edit_list)

				label = gtk.Label()
				label.set_markup(units)
				label.set_use_markup(True)
				label.set_size_request(200,height)
				label.show()
				hbox.pack_start(label, False, False, padding=1)
				label.show()
				self.pack_start(hbox, False, False, padding=1)
				#self.add()
				scan_item_add(check_list,filename,token,text_info)
				
				n=n+1

			pos=pos+1
