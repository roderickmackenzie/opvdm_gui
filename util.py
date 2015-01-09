import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import shutil
import signal
import subprocess
from tempfile import mkstemp
import logging
import zipfile
import re
from encode import encode_now
from encode import inp_set_encode
from encode import inp_unset_encode

inp_dir='/usr/share/opvdm/'
def pygtk_to_latex_subscript(in_string):
	out_string=in_string.replace("<sub>","_{")
	out_string=out_string.replace("</sub>","}")
	out_string=in_string.replace("<sup>","^{")
	out_string=out_string.replace("</sup>","}")
	return out_string

def read_xy_data(x,y,file_name):
	found,lines=zip_get_data_file(file_name)
	if found==True:

		xmul=1.0
		ymul=1.0

		for i in range(0, len(lines)):
			lines[i]=re.sub(' +',' ',lines[i])
			lines[i]=re.sub('\t',' ',lines[i])
			lines[i]=lines[i].rstrip()
			sline=lines[i].split(" ")
			if len(sline)==2:
				if (lines[i][0]!="#"):
					x.append(float(sline[0]))
					y.append(float(sline[1]))
		return True
	else:
		return False

def zip_get_data_file(file_name):
	found=False
	lines=[]
	zip_file=os.path.dirname(file_name)+".zip"
	name=os.path.basename(file_name)
	if os.path.isfile(file_name)==True:
		f = open(file_name)
		lines = f.readlines()
		f.close()
		found=True

	if os.path.isfile(zip_file) and found==False:
		zf = zipfile.ZipFile(zip_file, 'r')
		items=zf.namelist()
		if items.count(name)>0:
			lines = zf.read(name).split("\n")
			found=True
		zf.close()

	return [found,lines]

def time_with_units(time):
	ret=str(time)
	if (time<1000e-9):
		ret=str(time*1e9)+" ns"
	elif (time<1000e-6):
		ret=str(time*1e6)+" us"
	elif (time<1000e-3):
		ret=str(time*1e3)+" ms"
	else:
		ret=str(time)+" s"
	return ret

def check_is_config_file(name):
	found="none"
	if os.path.isfile(name)==True:
		found=True
		return "file"
	if os.path.isfile("sim.opvdm"):
		zf = zipfile.ZipFile('sim.opvdm', 'r')
		items=zf.namelist()
		if items.count(name)>0:
			found="archive"
		zf.close()

	return found

def dlg_get_text( message, default=''):

	d = gtk.MessageDialog(None,
	          gtk.DIALOG_MODAL ,
	          gtk.MESSAGE_QUESTION,
	          gtk.BUTTONS_OK_CANCEL,
	          message)
	entry = gtk.Entry()
	entry.set_text(default)
	entry.show()
	d.vbox.pack_end(entry)
	entry.connect('activate', lambda _: d.response(gtk.RESPONSE_OK))
	d.set_default_response(gtk.RESPONSE_OK)

	r = d.run()
	text = entry.get_text().decode('utf8')
	d.destroy()
	if r == gtk.RESPONSE_OK:
		return text
	else:
		return None

def pango_to_gnuplot(data):
	one=""
	data.replace("<sub>", "_{")
	data.replace("</sub>", "}")

def find_data_file(name):
	local_file=os.getcwd()+"/"+name
	if os.path.isfile("main.c")==True:
		ret=local_file
	else:
		ret=inp_dir+"/"+name
	return ret

def opvdm_clone():
	logging.info('opvdm_clone')
	src=get_orig_inp_file_path()
	source = os.listdir(src)
	destination = "./"
	for files in source:
		if files.endswith(".inp"):
			print "copying",files,destination
			shutil.copy(src+files,destination)

	shutil.copy(src+"/sim.opvdm",destination)

	shutil.copytree(src+"/plot", "./plot")
	shutil.copytree(src+"/exp", "./exp")
	shutil.copytree(src+"/phys", "./phys")

def set_exe_command():

	if os.path.isfile("./go.o")==True:
		exe_command=os.getcwd()+"/go.o"
		exe_name="go.o"
	else:
		exe_command="opvdm_core"
		exe_name="opvdm_core"
	return exe_command, exe_name

def get_orig_inp_file_path():

	if os.path.isfile("main.c")==True:
		path=os.getcwd()+"/"
	else:
		path="/usr/share/opvdm/"
	return path

def replace_file_in_zip_archive(zip_file_name,target,lines):
	fh, abs_path = mkstemp()
	source = zipfile.ZipFile(zip_file_name, 'r')
	zf = zipfile.ZipFile(abs_path, 'w')

	for file in source.filelist:
	    if not file.filename.startswith(target):
		zf.writestr(file.filename, source.read(file))

	source.close()

	build=""
	for i in range(0,len(lines)):
		build=build+lines[i]+"\n"

	build=encode_now(build,True)

	zf.writestr(target, build)

	zf.close()
	os.close(fh)
	shutil.move(abs_path, zip_file_name)

def zip_remove_file(zip_file_name,target):
	if os.path.isfile(zip_file_name):
		source = zipfile.ZipFile(zip_file_name, 'r')
		if source.filelist.count(target)>0:
			fh, abs_path = mkstemp()
			zf = zipfile.ZipFile(abs_path, 'w')

			for file in source.filelist:
			    if not file.filename.startswith(target):
				zf.writestr(file.filename, source.read(file))
			zf.close()
			os.close(fh)
		source.close()

		if source.filelist.count(target)>0:
			shutil.move(abs_path, zip_file_name)


