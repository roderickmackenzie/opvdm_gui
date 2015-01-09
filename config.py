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

import sys
import pdb
import pygtk
pygtk.require('2.0')
import gtk

import os

class config_item:
	tag=""
	value=""


class config():
	tag_list=[]
	path=""
	def set_value(self,tag,value):
		found=False

		for i in range(0,len(self.tag_list)):
			if self.tag_list[i].tag==tag:
				self.tag_list[i].value=value
				found=True
				break

		if found==False:
			a=config_item()
			a.tag=tag
			a.value=value
			self.tag_list.append(a)
			pos=len(self.tag_list)-1

		print "Saved as",self.path+"config.inp"
		a = open(self.path+"config.inp", "w")
		a.write(str(len(self.tag_list))+"\n")
		for i in range(0,len(self.tag_list)):
			a.write(self.tag_list[i].tag+"\n")
			a.write(str(self.tag_list[i].value)+"\n")

		a.close()

	def get_value(self,tag,default):
		ret=default
		for i in range(0,len(self.tag_list)):
			if self.tag_list[i].tag==tag:
				ret=self.tag_list[i].value
				if ret=="True":
					ret=True
				elif ret=="False":
					ret=False
		return ret

	def load(self,path):
		self.tag_list=[]
		self.path=path
		try:
			f = open(self.path+"config.inp")
			lines = f.readlines()
			f.close()

			for i in range(0, len(lines)):
				lines[i]=lines[i].rstrip()

			number=int(lines[0])
			for i in range(0,number):
				a=config_item()
				a.tag=lines[i*2+1]
				a.value=lines[i*2+2]
				self.tag_list.append(a)
		except:
			pass

