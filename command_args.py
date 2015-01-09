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
import shutil
from scan import scan_class
from tab import tab_class
from search import find_fit_error
from optics import class_optical
import signal
import subprocess
from inp import inp_update_token_value
from inp import inp_get_token_value
from inp import inp_isfile
from util import set_exe_command
from util import get_orig_inp_file_path
from util import opvdm_clone
from export_as import export_as
from emesh import tab_electrical_mesh
from welcome import welcome_class
from copying import copying
from hpc import hpc_class
from tab_homo import tab_bands
from tempfile import mkstemp
from plot_gen import plot_gen
from plot_gen import set_plot_auto_close
from import_archive import import_archive
from about import about_dialog_show
from util import find_data_file
from notice import notice
import os, fnmatch
import pyinotify
import pynotify
import threading
import time
import gobject
import numpy
import logging
import time
from util import check_is_config_file
from window_list import windows
from config import config
from plot import plot_data
from import_archive import delete_scan_dirs
from undo import undo_list_class
from ver import ver
def command_args(argc,argv):
	if argc>=2:
		if argv[1]=="--help":
			print "Usage: opvdm [option] src_file dest_file"
			print ""
			print "Options:"
			print "\t--version\tdisplays the current version"
			print "\t--help\t\tdisplays the help"
			print "\t--export\texport a simulation to a gz file"
			print "\t--import\timport a simulation from a gz file or a directory"
			print "\t\t\tusage --import abc.gz ./path/to/output/ "
			print "\t--patch\t\tpatch a simulation with an archived simulation"
			print "\t--clone\t\tgenerate a clean simulation in the current directory"
			print "\t--clean\t\tcleans the current simulation directory"
			print "\t--dump-tab (output file)\t\tdumps simulation parameters as jpg"

			print ""
			print "Additional information about opvdm is available at http://www.opvdm.com."
			print ""
			print "Report bugs to: roderick.mackenzie@nottingham.ac.uk"
			sys.exit(0)
		if argv[1]=="--version":
			print ver()
			sys.exit(0)
		if argv[1]=="--export":
			export_as(argv[2])
			sys.exit(0)
		if argv[1]=="--dump-tab":
			export_as(argv[2])
			sys.exit(0)
		if argv[1]=="--import":
			import_archive(argv[2],"./",False)
			sys.exit(0)
		if argv[1]=="--patch":
			import_archive(argv[2],argv[3],True)
			sys.exit(0)
		if argv[1]=="--clone":
			opvdm_clone()
			sys.exit(0)
		if argv[1]=="--file_info":
			data=plot_data()
			data.dump_file()
			sys.exit(0)
		if argv[1]=="--clean":
			delete_scan_dirs("./")
			files = os.listdir("./")
			for file in files:
				remove=False
				if file.endswith(".txt"):
					remove=True
				if file.endswith("~"):
					remove=True
				if file.endswith(".dat"):
					remove=True
				if file.endswith(".o"):
					remove=True
				if file.endswith(".orig"):
					remove=True
				if file.endswith(".back"):
					remove=True
				if file.endswith(".bak"):
					remove=True
				if file.endswith("gmon.out"):
					remove=True
				if remove==True:
					print file
					os.remove(file)
			sys.exit(0)
