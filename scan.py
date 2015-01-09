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

class scan_class:

	check_list=[]

	def __init__(self,check_list_in):
		self.check_list=check_list_in
		print "constructur"

	def callback_edit(self, widget, data=None):
		sim_dir=os.getcwd()+'/'+self.text.get_text()
		self.status_bar.push(self.context_id, sim_dir)

	def callback_edit_param(self, widget, data=None):
		f = open('opvdm_gui_config.inp','w')
		f.write(self.scan_values.get_text())
		f.close()


	def callback_plot_jv(self, widget, data):
		base_dir=os.getcwd()
		sim_dir=base_dir+'/'+self.text.get_text()

		values=self.scan_values.get_text()

		cmd = 'gnuplot -persist '+sim_dir+'/jv.plot'
		os.system(cmd)

	def callback_plot_charge(self, widget, data=None):
		base_dir=os.getcwd()
		sim_dir=base_dir+'/'+self.text.get_text()

		values=self.scan_values.get_text()

		cmd = 'gnuplot -persist '+sim_dir+'/opvdm_charge.plot'
		os.system(cmd)

	def callback_simulate(self, widget, data=None):
		base_dir=os.getcwd()
		sim_dir=base_dir+'/'+self.text.get_text()
		self.status_bar.push(self.context_id, sim_dir)

		cmd = 'mkdir '+sim_dir
		os.system(cmd)
		values=self.scan_values.get_text()
		for i in values.split():
			sim_sim_dir = sim_dir+'/'+i
			print "making ",sim_sim_dir
			cmd='mkdir '+sim_sim_dir	
			os.system(cmd)

			cmd = 'cp *.inp '+sim_sim_dir+'/'
			os.system(cmd)

			cmd = 'cp *.inp '+sim_sim_dir+'/'
			os.system(cmd)

			os.chdir(sim_sim_dir)

			replace("physdir.inp", "#physdir", "../../phys/")
			replace("dump.inp", "#plot", "0")

			for ii in range(0, len(self.check_list)):
				if self.check_list[ii].get_active() == True:
					replace(self.check_list[ii].filename, self.check_list[ii].token, i)	
			cmd=exe_name	
			os.system(cmd)

			os.chdir(base_dir)

		f = open(sim_dir+'/opvdm_jv.plot','w')
		f.write("set xlabel 'Applied voltage (V)'\n")
		f.write("set ylabel 'Current (A)'\n")
		f.write("plot \\\n")

		n=0
		mylen=len(values.split())-1
		for i in values.split():
			sim_sim_dir = sim_dir+'/'+i
			f.write("'"+sim_sim_dir+"/ivexternal.dat'")
			if n != mylen:
				f.write(",\\\n")
			n=n+1

		f.close()

		f = open(sim_dir+'/opvdm_charge.plot','w')
		f.write("set xlabel 'Applied voltage (V)'\n")
		f.write("set ylabel 'Charge density (m^{-3})'\n")
		f.write("plot \\\n")

		n=0
		mylen=len(values.split())-1
		for i in values.split():
			sim_sim_dir = sim_dir+'/'+i
			f.write("'"+sim_sim_dir+"/charge.dat'")
			if n != mylen:
				f.write(",\\\n")
			n=n+1

		f.close()
		#cmd = 'mv charge.dat charge_last.dat'
		#os.system(cmd)

		#cmd = 'opvdm_core'
		#os.system(cmd)

	def get_main_menu(self, window):
		accel_group = gtk.AccelGroup()


		item_factory = gtk.ItemFactory(gtk.MenuBar, "<main>", accel_group)


		item_factory.create_items(self.menu_items)


		window.add_accel_group(accel_group)

		self.item_factory = item_factory

		return item_factory.get_widget("<main>")

	def open_window(self):

		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_border_width(2)
		window.set_title("Parameter scan - opvdm")

		table = gtk.Table(3,6,False)
		#window.add(table)
		n=0

		label = gtk.Label("Simulation name")
		table.attach(label, 0, 1, n, n+1)
		label.show()

		self.text = gtk.Entry()
		self.text.set_text("scan1")
		self.text.connect("changed", self.callback_edit, n)
		table.attach(self.text, 1, 2, n, n+1)
		self.text.show()
		n=n+1
		items=0
		titles= [ "Parameter to scan" ]
		one=gtk.CList(1,titles)
		one.clear()
		one.set_size_request(150, 300)
		table.attach(one, 0, 2, n, n+5)
		one.show()
		n=n+5

		for i in range(0, len(self.check_list)):
			if self.check_list[i].get_active() == True:

				one.set_selection_mode(gtk.SELECTION_SINGLE)
				one.set_column_width(0, 150)
				one.append([self.check_list[i].name])
				items=items+1


		label = gtk.Label("Enter scan values")
		table.attach(label, 0, 1, n, n+1)
		label.show()

		self.scan_values = gtk.Entry()
		self.scan_values.connect("changed", self.callback_edit_param)
		try:
   			f=open('opvdm_gui_config.inp')
			config = f.readlines()
			self.scan_values.set_text(config[0])
			f.close()
		except IOError:
			self.scan_values.set_text("1e-6 1e-5 1e-4")


		table.attach(self.scan_values, 1, 2, n, n+1)
		self.scan_values.show()
		n=n+1

		self.status_bar = gtk.Statusbar()      

		self.status_bar.show()

		self.context_id = self.status_bar.get_context_id("Statusbar example")

		table.attach(self.status_bar, 0, 2, n, n+1)
		self.status_bar.push(self.context_id, os.getcwd())

		table.show()

		self.menu_items = (
		    ( "/_File",         None,         None, 0, "<Branch>" ),
		    ( "/File/Quit",     "<control>Q", gtk.main_quit, 0, None ),
		    ( "/_Scan",      None,         None, 0, "<Branch>" ),
		    ( "/Scan/Run",  None,         self.callback_simulate, 0, None ),
		    ( "/_Plots",      None,         None, 0, "<Branch>" ),
		    ( "/Plots/JV Curve",  None,         None, 0, "<Branch>" ),
		    ( "/Plots/JV Curve/J - V",  None,         self.callback_plot_jv, 0, None ),
		    ( "/Plots/JV Curve/Charge",  None,         self.callback_plot_charge, 0, None ),
		    ( "/_Help",         None,         None, 0, "<LastBranch>" ),
		    ( "/_Help/opvdm Help",   None,         None, 0, None ),
		    ( "/_Help/About",   None,         None, 0, None ),
		    )

		main_vbox = gtk.VBox(False, 2)
		main_vbox.set_border_width(1)
		window.add(main_vbox)
		#window.add(table)
		main_vbox.show()

		menubar = self.get_main_menu(window)

		main_vbox.pack_start(menubar, False, True, 0)
		main_vbox.add(table)
		menubar.show()



		window.show()

		if items == 0:
			message = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, buttons=gtk.BUTTONS_OK)
			message.set_markup("You have not selected any parameters to scan through - tick the check box in the main window.")
			message.run()
			message.destroy()
			window.destroy()
