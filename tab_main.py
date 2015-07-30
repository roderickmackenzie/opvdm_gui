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
import math
import random
from layer_widget import layer_widget

class tab_main(gtk.VBox):

	def update(self,object):
		self.darea.queue_draw()

	def init(self):
		main_hbox=gtk.HBox()
		self.darea = gtk.DrawingArea()
		self.darea.connect("expose-event", self.expose)
		#darea.show()

		self.frame=layer_widget()
		main_hbox.pack_start(self.frame, False, False, 0)
		main_hbox.pack_start(self.darea, True, True, 0)

		self.frame.connect("refresh", self.update)

		self.add(main_hbox)
		self.show_all()

	def draw_box(self,x,y,z,r,g,b,text):
		self.cr.set_source_rgb(r,g,b)

		points=[(x,y), (x+200,y), (x+200,y+z), (x,y+z)]
		print points
		self.cr.move_to(x, y)
		for px,py in points:
			self.cr.line_to(px, py)
		self.cr.fill()

		r=r*0.5
		g=g*0.5
		b=b*0.5
		self.cr.set_source_rgb(r,g,b)

		points=[(x+200,y-0),(x+200,y+z), (x+200+80,y-60+z),(x+200+80,y-60)]
		print points
		self.cr.move_to(points[0][0], points[0][1])
		for px,py in points:
			self.cr.line_to(px, py)
		self.cr.fill()

		r=r*0.5
		g=g*0.5
		b=b*0.5
		self.cr.set_source_rgb(r,g,b)

		points=[(x,y),(x+200,y), (x+200+80,y-60), (x+100,y-60)]
		self.cr.move_to(points[0][0], points[0][1])
		print points
		self.cr.move_to(x, y)
		for px,py in points:
			self.cr.line_to(px, py)
		self.cr.fill()
		self.cr.set_font_size(14)
		self.cr.move_to(x+200+80+20, y-60+z/2)
		self.cr.show_text(text)
		
	def draw(self,articles):
		tot=0
		for i in range(0,len(articles)):
			tot=tot+float(articles[i][1])

		pos=0.0
		for i in range(0,len(articles)):
			thick=200.0*float(articles[i][1])/tot
			pos=pos+thick
			print "Draw"
			self.draw_box(-400,100.0-pos,thick*0.9,random.uniform(0, 1),random.uniform(0, 1),random.uniform(0, 1),articles[i][2])

	def expose(self, widget, event):

		self.cr = widget.window.cairo_create()

		self.cr.set_line_width(9)
		self.cr.set_source_rgb(0.7, 0.2, 0.0)
		        
		w = self.allocation.width
		h = self.allocation.height

		self.cr.translate(w/2, h/2)

		self.draw(self.frame.articles)


