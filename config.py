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

