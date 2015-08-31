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

import glib
import dbus
from threading import Thread
from dbus.mainloop.glib import DBusGMainLoop

class dbus_thread():

	def notifications(bus, message):
		print message.get_member()


	def foo(self,n):
		DBusGMainLoop(set_as_default=True)

		bus = dbus.SessionBus()
		bus.add_match_string_non_blocking("type='signal',interface='org.my.test'")
		bus.add_message_filter(self.notifications)

		#mainloop = glib.MainLoop()
		#mainloop.run()

	def start(self):
		#p = Thread(target=self.foo, args=(10,))
		#p.daemon = True
		#p.start()
		self.foo(10)

