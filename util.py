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

import sys
import os
import shutil
import signal
import subprocess
from tempfile import mkstemp
import logging
import zipfile
import re
from numpy import zeros
import hashlib
import glob
from win_lin import running_on_linux

if running_on_linux() == True:
	inp_dir='/usr/share/opvdm/'
else:
	inp_dir='c:\\opvdm\\'

def get_scan_dirs(scan_dirs,sim_dir):
	ls=os.listdir(sim_dir)

	for i in range(0, len(ls)):
		dir_name=os.path.join(sim_dir,ls[i])
		full_name=os.path.join(sim_dir,ls[i],"opvdm_gui_config.inp")
		if os.path.isfile(full_name):
			scan_dirs.append(dir_name)

def gui_print_path(text,path,length):
	remove=len(text)+len(path)-length
	if remove>0:
		ret=text+path[remove:]
	else:
		ret=text+path

	return ret

def join_path(one,two):
	output_file=os.path.join(one,two)

	if two[0]=='/':
		if one!="" :
			output_file=os.path.join(one,two[1:])

	return output_file
	
def read_data_2d(x_scale,y_scale,z,file_name):
	found,lines=zip_get_data_file(file_name)
	if found==True:
		x_max=0
		y_max=0
		y_pos=0
		z_store=[]
		for i in range(0, len(lines)):
			if (lines[i][0]!="#"):
				if lines[i]!="\n":

					temp=lines[i]
					temp=re.sub(' +',' ',temp)
					temp=re.sub('\t',' ',temp)
					temp=temp.rstrip()
					sline=temp.split(" ")
					if len(sline)==3:
						if x_max==0:
							y_scale.append(float(lines[i].split(" ")[1]))
						if y_pos==0:
							x_scale.append(float(lines[i].split(" ")[0]))

						z_store.append(float(lines[i].split(" ")[2]))
					y_pos=y_pos+1

					if x_max==0:
						y_max=y_max+1

				if lines[i]=="\n":
					x_max=x_max+1
					y_pos=0

		if  lines[len(lines)-1]!="\n":
			x_max=x_max+1

		#print "load 3d data",x_scale,y_scale

		pos=0
		for x in range(0, x_max):
			z.append([])
			for y in range(0, y_max):
				z[x].append(z_store[pos])
				pos=pos+1
		return True
	else:
		return False

def get_cache_path(path):
	m = hashlib.md5()
	m.update(path)
	cache_file=m.hexdigest()
	cache_path = os.path.expanduser("~")+"/cache/"+cache_file
	return cache_path

def copy_scan_dir(new_dir,old_dir):
	print "trying to copy",old_dir,new_dir
	if not os.path.exists(new_dir):
		os.makedirs(new_dir)
	for filename in glob.glob(os.path.join(old_dir, '*.*')):
		if os.path.isfile(filename):
			shutil.copy(filename, new_dir)

def delete_second_level_link_tree(path):
	for filename in os.listdir(path):
		full_name=os.path.join(path,filename)
		if os.path.isdir(full_name):
			print "Deleteing",full_name
			delete_link_tree(full_name)

	delete_link_tree(path)

def delete_link_tree(path):
	if os.path.islink(path):
		real_path=os.path.realpath(path)
		print "Deleting link:",path
		os.unlink(path)
		print "check",real_path,get_cache_path(path)
		if real_path==get_cache_path(path):	#only delete the cache directory if it is the one we are intending to delete 
			print "Delete tree",real_path
			shutil.rmtree(real_path)

	else:
		print "Deleting file:",path
		shutil.rmtree(path)

def numbers_to_latex(data):
	out=""
	number=False
	open_ten=False
	for i in range(0,len(data)):
		if str.isdigit(data[i])==True and number==False:
			out=out+""#$
			number=True

		if number==True:
			add=data[i]

			if number==True:
				if data[i]=="e":
					add="\\times10^{" 
					open_ten=True
				if str.isdigit(data[i])==True:
					add=data[i]
				else:
					if data[i]!="e" and data[i]!="-" and data[i]!="+" and data[i]!=".": 
						number=False
						add=""+data[i] #$
						if open_ten==True:
							add="}"+data[i] #$
							open_ten=False
			out=out+add
		else:
			out=out+data[i]
	if open_ten==True:
		out=out+"}"#$
		number=False

	if number==True:
		out=out+"" #$

	return out

def str2bool(v):
	if type(v) is bool:
		return v
	else:
		return v.lower() in ("yes", "true", "t", "1")

def pygtk_to_latex_subscript(in_string):
	out_string=in_string.replace("<sub>","_{")
	out_string=out_string.replace("</sub>","}")
	out_string=in_string.replace("<sup>","^{")
	out_string=out_string.replace("</sup>","}")
	return out_string

def lines_to_xyz(x,y,z,lines):
	for i in range(0, len(lines)):
		lines[i]=re.sub(' +',' ',lines[i])
		lines[i]=re.sub('\t',' ',lines[i])
		lines[i]=lines[i].rstrip()
		sline=lines[i].split(" ")
		if len(sline)==2:
			if (lines[i][0]!="#"):
				x.append(float(sline[0]))
				y.append(float(sline[1]))
				z.append("")
		if len(sline)==3:
			if (lines[i][0]!="#"):
				x.append(float(sline[0]))
				y.append(float(sline[1]))
				z.append(sline[2])

def read_xyz_data(x,y,z,file_name):
	found,lines=zip_get_data_file(file_name)
	if found==True:
		lines_to_xyz(x,y,z,lines)
		#print "here z=,",z,x,file_name
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
	if (time<1000e-15):
		ret=str(time*1e15)+" fs"
	elif (time<1000e-12):
		ret=str(time*1e12)+" ps"
	elif (time<1000e-9):
		ret=str(time*1e9)+" ns"
	elif (time<1000e-6):
		ret=str(time*1e6)+" us"
	elif (time<1000e-3):
		ret=str(time*1e3)+" ms"
	else:
		ret=str(time)+" s"
	return ret

def fx_with_units(fx):
	ret=str(fx)
	if (fx<1e3):
		ret=str(fx*1)+" Hz"
	elif (fx<1e6):
		ret=str(fx/1e3)+" kHz"
	elif (fx<1e9):
		ret=str(fx/1e6)+" MHz"

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

def pango_to_gnuplot(data):
	one=""
	data.replace("<sub>", "_{")
	data.replace("</sub>", "}")

def find_data_file(name):

	local_file=os.path.join(os.getcwd(),name)
	if os.path.isfile("main.c")==True:
		ret=local_file
	else:
		ret=os.path.join(inp_dir,name)
	return ret

def opvdm_copy_src(new_dir):
	pwd=os.getcwd()
	file_list=glob.glob(os.path.join(pwd,"*"))

	if not os.path.exists(new_dir):
		os.makedirs(new_dir)
	print file_list
	for name in file_list:
		gui_file_name=os.path.join(name,"opvdm_gui_config.inp")
		
		if os.path.isfile(gui_file_name)==False:
			fname=os.path.basename(name)
			out=os.path.join(new_dir,fname)
			if os.path.isfile(name):
				 shutil.copy(name, out)
			else:
				print "Copy dir:", name
				shutil.copytree(name, out,symlinks=True)
		else:
			print "I will not copy",name





def opvdm_clone():
	src=get_orig_inp_file_path()
	source = os.listdir(src)
	pwd=os.getcwd()
	destination=pwd
	for files in source:
		if files.endswith(".inp"):
			print "copying",files,destination
			shutil.copy(os.path.join(src,files),destination)

	shutil.copy(os.path.join(src,"sim.opvdm"),destination)

	if os.path.isdir(os.path.join(src,"plot")):
		shutil.copytree(os.path.join(src,"plot"), os.path.join(pwd,"plot"))

	if os.path.isdir(os.path.join(src,"exp")):
		shutil.copytree(os.path.join(src,"exp"), os.path.join(pwd,"exp"))

	shutil.copytree(os.path.join(src,"phys"), os.path.join(pwd,"phys"))

def set_exe_command():
	if running_on_linux() == True:
		if os.path.isfile("./go.o")==True:
			exe_command=os.path.join(os.getcwd(), "go.o")
			exe_name="go.o"
		elif os.path.isfile("./main.c")==True:
			exe_command=os.path.join(os.getcwd(), "go.o")
			exe_name="go.o"
		else:
			exe_command="opvdm_core"
			exe_name="opvdm_core"
		return exe_command, exe_name
	else:
		if os.path.isfile("opvdm.exe")==True:
			exe_command=os.path.join(os.getcwd(), "opvdm.exe")
			exe_name="opvdm.exe"
		else:
			exe_command="c:\\opvdm\\opvdm.exe"
			exe_name="opvdm.exe"
		return exe_command, exe_name

def get_orig_inp_file_path():
	if running_on_linux() == True:
		if os.path.isfile("opvdm.py")==True:
			path=os.getcwd()
		else:
			path="/usr/share/opvdm/"
		return path
	else:
		if os.path.isfile("opvdm.py")==True:
			path=os.path.join(os.getcwd(), "\\")
		else:
			path="c:\\opvdm\\"
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


