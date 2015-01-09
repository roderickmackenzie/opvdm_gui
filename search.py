#!/usr/bin/env python

import os, fnmatch
import glob


def find_fit_log():
	pattern='fitlog.dat'
	path='../'
	result = []
	for root, dirs, files in os.walk(path):
		for name in files:
			if fnmatch.fnmatch(name, pattern):
				result.append(os.path.join(root, name))
	files=result
	string="plot "
	for my_file in files:
		 string=string+"'"+my_file+"' using ($2) with lp,"
	string = string[:-1]
	text_file = open("./plot/hpc_fitlog.plot", "w")
	text_file.write(string)
	text_file.close()

def return_file_list(result,start_dir,file_name):
	print start_dir, file_name
	pattern=file_name
	path=start_dir
	for root, dirs, files in os.walk(path):
		for name in files:
			if fnmatch.fnmatch(name, pattern):
				result.append(os.path.join(root, name))

	for i in range(0, len(result)):
		result[i]=result[i].rstrip()



def find_fits():
	pattern='plot_file.dat'
	path='./'
	result = []
	for root, dirs, files in os.walk(path):
		for name in files:
			if fnmatch.fnmatch(name, pattern):
				result.append(os.path.join(root, name))
	files=result
	string="plot \\"

	for my_file in files:
		f = open(my_file)
		lines = f.readlines()
		f.close()

		for i in range(0, len(lines)):
			string=string+'\n'+lines[i].rstrip()
	string = string[:-2]

	text_file = open("./plot/fit.plot", "w")
	text_file.write(string)
	text_file.close()

def find_fit_error():
	path='./'
	result = []
	string="plot \\\n"
	i=0
	for name in glob.glob('error_*exp*.dat'):
		i=i+1
		string=string+"'"+name+"' with lp lt "+str(i)+",\\\n"

	i=0
	for name in glob.glob('error_*sim*.dat'):
		i=i+1
		string=string+"'"+name+"' with lp lt "+str(i)+",\\\n"

	string = string[:-3]

	text_file = open("./plot/fit_errors.plot", "w")
	text_file.write(string)
	text_file.close()



