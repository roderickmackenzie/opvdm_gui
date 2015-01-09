import sys
import pdb
import pygtk
pygtk.require('2.0')
import gtk

import os

class window_item:
	name=""
	x=0.0
	y=0.0

wlist=[]

class windows():
	def update(self,window,name):
		global wlist
		pos=-1
		x,y=window.get_position()

		for i in range(0,len(wlist)):
			if wlist[i].name==name:
				pos=i
				wlist[i].x=x
				wlist[i].y=y
				break

		if pos==-1:
			a=window_item()
			a.name=name
			a.x=x
			a.y=y
			wlist.append(a)
			pos=len(wlist)-1


		a = open("window_list.inp", "w")
		a.write(str(len(wlist))+"\n")
		for i in range(0,len(wlist)):
			a.write(wlist[i].name+"\n")
			a.write(str(wlist[i].x)+"\n")
			a.write(str(wlist[i].y)+"\n")

		a.close()

	def set_window(self,window,name):
		global wlist
		for i in range(0,len(wlist)):
			if wlist[i].name==name:
				s=gtk.gdk.screen_get_default()
				w,h=window.get_size()
				x=int(wlist[i].x)
				y=int(wlist[i].y)
				if (x+w>s.get_width()):
					x=0
					print "Reset with"
				if (y+h>s.get_height()):
					y=0
					print "Reset height"

				window.move(x,y)
				break
	def load(self):
		global wlist
		wlist=[]
		try:
			f = open("window_list.inp")
			lines = f.readlines()
			f.close()

			for i in range(0, len(lines)):
				lines[i]=lines[i].rstrip()

			number=int(lines[0])
			for i in range(0,number):
				a=window_item()
				a.name=lines[i*3+1]
				a.x=lines[i*3+2]
				a.y=lines[i*3+3]
				wlist.append(a)
		except:
			pass

