import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import shutil
from util import find_data_file

def notice():
	ret="opvdm (Organic Photovoltaic Device Model)\n"
	ret=ret+"Copyright Roderick MacKenzie 2012, all rights reserved\n"
	return ret
