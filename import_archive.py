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
import pygtk
from win_lin import running_on_linux

if running_on_linux()==True:
	inp_dir='/usr/share/opvdm/'
	gui_dir='/usr/share/opvdm/gui/'
	lib_dir='/usr/lib64/opvdm/'
else:
	inp_dir='c:\\opvdm\\'
	gui_dir='c:\\opvdm\\gui\\'
	lib_dir='c:\\opvdm\\'

sys.path.append('./gui/')
sys.path.append(lib_dir)

import os
import shutil
import signal
import subprocess
from util import get_scan_dirs 
from inp import inp_update_token_value
from util import replace_file_in_zip_archive
import os, fnmatch
import stat 
import zipfile
from util import zip_remove_file
from util import copy_scan_dir
from util import delete_second_level_link_tree
import tempfile

def copy_check_ver(orig,file_name,dest,only_over_write,clever):
	#remove the dest file if both exist ready to copy
	do_copy=True
	orig_ver=""
	dest_ver=""
	orig_file=os.path.join(orig,file_name)
	dest_file=os.path.join(dest,file_name)
	orig_zip_file=os.path.join(orig,"sim.opvdm")
	dest_zip_file=os.path.join(dest,"sim.opvdm")
	in_dest_zip_file=False
	orig_exists=False
	dest_exists=False
	orig_lines=[]
	dest_lines=[]

	#read in the src file where ever it may be
	if os.path.isfile(orig_file)==True:
		f = open(orig_file)
		lines = f.readlines()
		f.close()
		orig_exists=True
	elif os.path.isfile(orig_zip_file):
		zf = zipfile.ZipFile(orig_zip_file, 'r')
		items=zf.namelist()
		if items.count(file_name)>0:
			lines = zf.read(file_name).split("\n")
			orig_exists=True
		zf.close()
	else:
		orig_exists=False

	if orig_exists==True:
		for i in range(0, len(lines)):
			lines[i]=lines[i].rstrip()
			if lines[i]!="":
				orig_lines.append(lines[i])

		if orig_lines.count("#ver")>0:
			i=orig_lines.index('#ver')+1
			orig_ver=orig_lines[i]
	else:
		print "Warning: ",orig_file," no origonal file to copy"
		return

	#read in the dest file where ever it may be
	if os.path.isfile(dest_file)==True:
		f = open(dest_file)
		lines = f.readlines()
		f.close()
		dest_exists=True
		if file_name=="device.inp":
			print dest_lines
	elif os.path.isfile(dest_zip_file):
		zf = zipfile.ZipFile(dest_zip_file, 'r')
		items=zf.namelist()
		if items.count(file_name)>0:
			lines = zf.read(file_name).split("\n")
			in_dest_zip_file=True
			dest_exists=True
		zf.close()
	else:
		dest_exists=False



	if dest_exists==True:
		for i in range(0, len(lines)):
			lines[i]=lines[i].rstrip()
			if lines[i]!="":
				dest_lines.append(lines[i])

		if dest_lines.count('#ver')>0:
			i=dest_lines.index('#ver')+1
			dest_ver=dest_lines[i]



	#if we are only over writing only copy if dest file exists
	if (only_over_write==True):
		if dest_exists==True:
			do_copy=True
		else:
			print "Warning: ", file_name," - only exists in the source"
			do_copy=False
			return

	if orig_ver!=dest_ver:
		print "Warning: Verstion numbers do not match for files",orig_file,orig_ver,dest+file_name,dest_ver
		if clever==False:
			return

	if clever==True:
		for i in range(0,len(dest_lines)):
			if dest_lines[i].startswith("#") and dest_lines[i]!="#ver" and dest_lines[i]!="#end":
				lookfor=dest_lines[i]
				found=False
				for ii in range(0,len(orig_lines)):
					if orig_lines[ii]==lookfor:
						#print "Found",dest_lines[i],orig_lines[ii]
						dest_lines[i+1]=orig_lines[ii+1]
						found=True
						break
				if found==False:
					print "Warning: token ",lookfor, " in ",file_name," not found in archive" 
	else:
		dest_lines=orig_lines



	if (do_copy==True):
		if in_dest_zip_file==True:
			#print "Updating archive",file_name,dest_lines
			replace_file_in_zip_archive(dest_zip_file,file_name,dest_lines)
		else:
			#if it is in the dest file remove it
			zip_remove_file(dest_zip_file,file_name)
			a = open(dest_file, "w")
			for i in range(0,len(dest_lines)):
				a.write(dest_lines[i]+"\n")
			a.close()

			return


def import_archive(file_name,dest_dir,only_over_write):
	if file_name.endswith('.tar.gz')==True:
		tmp_dir=os.path.join(tempfile.gettempdir(), "opvdm")

		if os.path.exists(tmp_dir):
			shutil.rmtree(tmp_dir)

		if not os.path.exists(tmp_dir):
			os.makedirs(tmp_dir)

		cmd = 'tar -xzf '+file_name+' -C '+tmp_dir+'/'
		os.system(cmd)

		pattern='sim.opvdm'
		path=tmp_dir
		res=""
		for root, dirs, files in os.walk(path):
			for name in files:
				if fnmatch.fnmatch(name, pattern):
					res=os.path.join(root, name)
					break
			if res!="":
				break

		sim_path=os.path.dirname(res)

	else:
		sim_path=file_name

	files=[ "sim.inp", "device.inp", "stark.inp" ,"shg.inp" ,"dos0.inp", "dos1.inp"  ,"jv.inp" ,"celiv.inp" , "optics.inp", "math.inp",  "dump.inp" , "light.inp", "tpv.inp", "otrace.inp", "server.inp", "pulse_voc.inp","pulse.inp","light_exp.inp","time_mesh_config.inp" ]

	for i in files:
		copy_check_ver(sim_path,i,dest_dir,only_over_write,True)

	files=[ "device_epitaxy.inp", "optics_epitaxy.inp", "fit.inp", "constraints.inp","duplicate.inp", "thermal.inp","lumo0.inp","homo0.inp" ]

	for i in files:
		copy_check_ver(sim_path,i,dest_dir,only_over_write,False)

	import_scan_dirs(dest_dir,sim_path)

def import_scan_dirs(dest_dir,src_dir):
	sim_dirs=[]
	get_scan_dirs(sim_dirs,src_dir)
	for my_file in sim_dirs:
		dest=os.path.join(dest_dir,os.path.basename(my_file))
		print "copy scan dir",my_file,"to",dest

		if os.path.exists(dest):
			delete_second_level_link_tree(dest)

		copy_scan_dir(dest,my_file)

def delete_scan_dirs(path):
	sim_dirs=[]
	get_scan_dirs(sim_dirs,path)

	for my_file in sim_dirs:
		print "Deleteing ",my_file
		shutil.rmtree(my_file)

def clean_scan_dirs(path):
	sim_dirs=[]
	get_scan_dirs(sim_dirs,path)

	for my_dir in sim_dirs:
		print "cleaning ",my_dir
		files = os.listdir(my_dir)
		for file in files:
			file_name=os.path.join(my_dir,file)
			if file_name.endswith(".dat"):
				print "Remove",file_name
				os.remove(file_name)
			if os.path.isdir(file_name):
				print "remove dir",file_name
				shutil.rmtree(file_name)



