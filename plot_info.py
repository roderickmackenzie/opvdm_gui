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

class plot_info():
	file_name=""
	x_label=""
	y_label=""
	y_units=""
	other_file=""
	x_mul=1.0
	y_mul=1.0
	logscale_x=0
	logscale_y=0
	title=""
	type=""
	def __init__(self,a,b,l,c,j,d,e,f,g,h,i):
		self.file_name=a
		self.x_label=b
		self.y_label=c
		self.x_mul=d
		self.y_mul=e
		self.other_file=f
		self.logscale_x=g
		self.logscale_y=h
		self.title=i
		self.y_units=j
		self.x_units=l
		self.type="xy"
