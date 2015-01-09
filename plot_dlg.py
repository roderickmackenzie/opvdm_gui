import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import shutil
import signal
import subprocess
from tempfile import mkstemp
from plot_command import plot_command_class


class plot_dlg_class(gtk.Window):

	def populate_combo_box_using_input_file(self,combobox,input_file):
		try:
			f = open(self.path+"/"+input_file)
			lines = f.readlines()
			f.close()

			for i in range(0, len(lines) ,2):
				lines[i]=lines[i].rstrip()
				combobox.append_text(lines[i])

			combobox.set_active(0)
		except:
		
			combobox.get_model().clear()

	def callback_edit0(self, widget):
		print "Edit"
		self.populate_combo_box_using_input_file(self.token0,self.file0.get_text())

	def callback_edit1(self, widget):
		print "Edit"
		self.populate_combo_box_using_input_file(self.token1,self.file1.get_text())

	def callback_click(self, widget,button,data):
		if button == "ok":
			data.file0=self.file0.get_text().decode('utf8')
			data.tag0=self.token0.get_active_text().decode('utf8')
			data.file1=self.file1.get_text().decode('utf8')
			data.tag1=self.token1.get_active_text().decode('utf8')
			self.ret=True
		else:
			self.ret=False

		gtk.main_quit()

	def my_init(self,data):
		self.path=os.path.dirname(data.example_file0)
		self.ret=False
		self.set_title("xy plot www.opvdm.com")
		self.set_keep_above(True)
		l=gtk.Label("x-axis:")
		l.show()
		vbox=gtk.VBox()
		hbox=gtk.HBox()
		self.file0 = gtk.Entry()
		self.file0.set_text(data.file0)
		self.file0.connect("changed", self.callback_edit0)
		self.file0.show()
		hbox.add(self.file0)


		self.token0 = gtk.combo_box_new_text()
		self.token0.set_wrap_width(5)
		self.populate_combo_box_using_input_file(self.token0, os.path.basename(data.example_file0))
		self.token0.show()
		hbox.add(self.token0)

		hbox.show()

		vbox.add(l)
		vbox.add(hbox)

		l=gtk.Label("y-axis:")
		l.show()

		hbox=gtk.HBox()
		self.file1 = gtk.Entry()
		self.file1.set_text(data.file0)
		self.file1.connect("changed", self.callback_edit1)
		self.file1.show()
		hbox.add(self.file1)

		self.token1 = gtk.combo_box_new_text()
		self.token1.set_wrap_width(5)
		self.populate_combo_box_using_input_file(self.token1,os.path.basename(data.example_file1))
		self.token1.show()
		hbox.add(self.token1)

		hbox.show()
		vbox.add(l)
		vbox.add(hbox)
		button_box=gtk.HBox()

		button_cancel=gtk.Button(stock=gtk.STOCK_CANCEL)
		button_cancel.show()
		button_box.add(button_cancel)
		button_cancel.connect("clicked",self.callback_click,"cancel",data)

		button_ok=gtk.Button(stock=gtk.STOCK_OK)
		button_ok.show()
		button_ok.connect("clicked",self.callback_click,"ok",data)
		button_box.add(button_ok)

		button_box.show()

		vbox.add(button_box)
		vbox.show()
		self.add(vbox)
		self.show()

	def my_run(self,data):
		self.show_all()

		gtk.main()
		self.destroy()
		return self.ret

