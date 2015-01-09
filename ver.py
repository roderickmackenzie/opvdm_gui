import sys
import pdb
import pygtk
pygtk.require('2.0')
import gtk
from util import find_data_file
from inp import inp_load_file

def ver():
	lines=[]
	inp_load_file(lines,find_data_file("ver.inp"))
	ver_string="core: Version "+lines[1]+", gui: Version "+lines[3]+", materials: Version "+lines[5]

	string=ver_string
	return string
