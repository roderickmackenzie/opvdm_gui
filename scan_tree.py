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


import gc
import sys
import os
import shutil
import glob

from inp import inp_update_token_value
from scan_item import scan_items_get_list
from scan_item import scan_items_index_item
from inp import inp_get_token_value
from inp import inp_get_token_array

def tree_load_program(program_list,sim_dir):
	file_name=os.path.join(sim_dir,'opvdm_gui_config.inp')

	if os.path.isfile(file_name)==True:
		f=open(file_name)
		config = f.readlines()
		f.close()

		for ii in range(0, len(config)):
			config[ii]=config[ii].rstrip()

		pos=0
		mylen=int(config[0])
		pos=pos+1
		for i in range(0, mylen):
			program_list.append([config[pos], config[pos+1], config[pos+2]])
			pos=pos+3

def tree_gen(program_list,base_dir,sim_dir):
	sim_dir=os.path.abspath(sim_dir)	# we are about to traverse the directory structure better to have the abs path
	commands=[]
	print "here",program_list
	tree_items=[[],[],[]]
	for i in range(0,len(program_list)):
		print i,program_list[i][0],program_list[i][1],program_list[i][2]
		if program_list[i][2]=="scan":
			tree_items[0].append(program_list[i][0])
			tree_items[1].append(program_list[i][1])
			tree_items[2].append(program_list[i][2])

	print "tree items=",tree_items
	tree(program_list,tree_items,commands,base_dir,0,sim_dir,"","")
	return commands

def tree_apply_mirror(program_list):
	param_list=scan_items_get_list()
	for i in range(0, len(program_list)):
		for ii in range(0, len(program_list)):
			if program_list[i][2]==program_list[ii][0]:
				#I have found two matching IDs
				pos_mirror_src=scan_items_index_item(program_list[i][2])
				pos_mirror_dest=scan_items_index_item(program_list[i][0])
				src_value=inp_get_token_value(param_list[pos_mirror_src].filename, param_list[pos_mirror_src].token)
				#pull out of the file the value
				if program_list[i][1]!="mirror":
					#find value in list
					orig_list=program_list[i][1].split()
					look_up=program_list[ii][1].split()
					src_value=orig_list[look_up.index(src_value.rstrip())]

				inp_update_token_value(param_list[pos_mirror_dest].filename, param_list[pos_mirror_dest].token, src_value,param_list[pos_mirror_dest].line)

def tree_apply_constant(program_list):
	param_list=scan_items_get_list()
	for i in range(0, len(program_list)):
		if program_list[i][2]=="constant":
			pos_mirror_dest=scan_items_index_item(program_list[i][0])
			inp_update_token_value(param_list[pos_mirror_dest].filename, param_list[pos_mirror_dest].token, program_list[i][1],param_list[pos_mirror_dest].line)
			print os.getcwd()
			print "Replace",param_list[pos_mirror_dest].filename,param_list[pos_mirror_dest].token,program_list[i][1]

def copy_simulation(base_dir,cur_dir):
	param_list=scan_items_get_list()
	cache=int(inp_get_token_value("server.inp","#use_cache"))
	print "cache status",cache
	if cache==True:
		cache_path=get_cache_path(cur_dir)
		d = os.path.dirname(cache_path)

		if os.path.isdir(cache_path)==True:
			shutil.rmtree(cache_path)		#if there is something in the cache with this name remove it

		if not os.path.exists(cache_path):
			os.makedirs(cache_path)			#make the folder in the cache

		if os.path.isdir(cur_dir):
			os.rmdir(cur_dir)			#if the target exists remove it

		print cache_path, cur_dir

		os.symlink(cache_path, cur_dir)


	#copy fit dirs
	fit_file=os.path.join(base_dir, "fit.inp")
	if os.path.isfile(fit_file):
		fit_array=inp_get_token_array(fit_file, "#fitnames")
		do_fit=inp_get_token_array(fit_file, "#do_fit")
		if (int(fit_array[0])>0) and (do_fit==1):
			exp_dir=os.path.join(cur_dir,"exp")
			if not os.path.exists(exp_dir):
				os.makedirs(exp_dir)

			for i in range(1,len(fit_array)):
				shutil.copytree(os.path.join(base_dir,"exp",fit_array[i]), os.path.join(exp_dir,fit_array[i]))

	f_list=glob.iglob(os.path.join(base_dir, "*.inp"))
	for inpfile in f_list:
		shutil.copy(inpfile, cur_dir)

	shutil.copy(os.path.join(base_dir, "sim.opvdm"), cur_dir)

def tree(program_list,tree_items,commands,base_dir,level,path,var_to_change,value_to_change):
		param_list=scan_items_get_list()
		print level,tree_items
		i=tree_items[1][level]
		words=i.split()
		pass_var_to_change=var_to_change+" "+str(scan_items_index_item(tree_items[0][level]))
		print pass_var_to_change
		for ii in words:
			cur_dir=os.path.join(path,ii)

			if not os.path.exists(cur_dir):
				os.makedirs(cur_dir)

			pass_value_to_change=value_to_change+" "+ii

			if ((level+1)<len(tree_items[0])):
					tree(program_list,tree_items,commands,base_dir,level+1,cur_dir,pass_var_to_change,pass_value_to_change)
			else:
				new_values=pass_value_to_change.split()
				pos=pass_var_to_change.split()
				
				copy_simulation(base_dir,cur_dir)

				os.chdir(cur_dir)
				
				for i in range(0, len(pos)):
					inp_update_token_value(param_list[int(pos[i])].filename, param_list[int(pos[i])].token, new_values[i],param_list[int(pos[i])].line)
				
				tree_apply_constant(program_list)
				tree_apply_mirror(program_list)

				
				inp_update_token_value("physdir.inp", "#physdir", os.path.join(base_dir,"phys"),1)
				inp_update_token_value("dump.inp", "#plot", "0",1)

				commands.append(os.getcwd())

			if level==0:
				f = open(os.path.join(cur_dir,'scan.inp'),'w')
				f.write("data")
				f.close()
