import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import shutil
import signal
import subprocess
from tempfile import mkstemp

class plot_command_class:
	file0=""
	tag0=""
	file1=""
	tag1=""
	file2=""
	tag2=""
	example_file0=""
	example_file1=""
	example_file2=""
