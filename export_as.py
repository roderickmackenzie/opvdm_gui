#!/usr/bin/env python
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
import pygtk
inp_dir='/usr/share/opvdm/'
gui_dir='/usr/share/opvdm/gui/'
lib_dir='/usr/lib64/opvdm/'
sys.path.append('./gui/')
sys.path.append(lib_dir)

import os
import shutil
import signal
import subprocess
from inp import inp_get_token_value
from inp import inp_load_file
import os, fnmatch
import stat
from token_lib import tokens
from util import pygtk_to_latex_subscript
import glob
def to_exp(data):
	ret=data
	if (ret.count('e')!=0):
		data=float(ret)
		ret="%1.1e" % data
		a,b=ret.split('e')
		ret=a+"\\e{"+b+"}"
	return ret

def to_nm(data):
	ret=str(float(data)*1e9)
	return ret

def to_mev(data):
	temp=float(data)
	temp=temp*1000.0
	ret=str(temp)
	if (ret.count('e')!=0):
		a,b=ret.split('e')
		ret=a+"\\e{"+b+"}"
	return ret

def export_as(output):
	ext= os.path.splitext(output)[1]
	line=""
	if (ext==".pdf") or (ext==".jpg") or (ext==".tex"):

		lines=[]
		line=line+"\\documentclass{article}\n"
		line=line+"\\providecommand{\\e}[1]{\\ensuremath{\\times 10^{#1}}}\n"
		line=line+"\\begin{document}\n"
		line=line+"\\pagenumbering{gobble}\n"
		line=line+"\n"
		files=[]

		f_list=glob.iglob(os.path.join("./", "dos*.inp"))
		for in_file in f_list:
                         files.append(in_file)
		print files
		line=line+"\\begin{table}[H]\n"
		line=line+"\\begin{center}\n"
		line=line+"  \\begin{tabular}{lll}\n"
		line=line+"  \\hline\n"     
		line=line+"  Parameter & label & unit \\\\\n"
		line=line+"  \\hline\n"
		dos_lines=[]
		for i in range(0,len(files)):
			lines=[]
			inp_load_file(lines,files[i])
			dos_lines.append(lines)

		t=tokens()
		for i in range(0,len(dos_lines[0]),2):
			my_token=t.find(dos_lines[0][i])

			if my_token!=False:
				number=""
				if my_token.number_type=="e":
					for ii in range(0,len(files)):

						if len(files)>0:
							sub="_{"+str(ii)+"}"
						else:
							sub=""

						if dos_lines[0][i+1]!=dos_lines[ii][i+1] or ii==0:
							number=to_exp(dos_lines[ii][i+1])
							line=line+my_token.info+sub+" & $"+number+"$ & $"+pygtk_to_latex_subscript(my_token.units)+"$"+" \\\\\n"
		line=line+"  \\hline\n"
		line=line+"\\end{tabular}\n"
		line=line+"\\end{center}\n"
		line=line+"\\caption{Density of states}\n"
		line=line+"\\end{table}\n"
		line=line+"\n"

		files=["./device.inp"]
		names=["Device"]
		for cur_file in range(0,len(files)):
			line=line+"\\begin{table}[H]\n"
			line=line+"\\begin{center}\n"
			line=line+"  \\begin{tabular}{lll}\n"
			line=line+"  \\hline\n"     
			line=line+"  Parameter & label & unit \\\\\n"
			line=line+"  \\hline\n"
			inp_load_file(lines,files[cur_file])
			t=tokens()
			for i in range(0,len(lines),2):
				my_token=t.find(lines[i])
				if my_token!=False:
					number=""
					if my_token.number_type=="e":
						number=to_exp(lines[i+1])
						line=line+my_token.info+" & $"+number+"$ & $"+pygtk_to_latex_subscript(my_token.units)+"$"+" \\\\\n"
			line=line+"  \\hline\n"
			line=line+"\\end{tabular}\n"
			line=line+"\\end{center}\n"
			line=line+"\\caption{"+names[cur_file]+"}\n"
			line=line+"\\end{table}\n"
			line=line+"\n"

		line=line+"\\end{document}\n"

		text_file = open("doc.tex", "w")
		text_file.write(line)
		text_file.close()

		if (ext==".pdf"):
			os.system("latex -interaction=batchmode doc")
			os.system("dvipdf doc.dvi")
			os.system("mv doc.pdf "+output)

		if (ext==".jpg"):
			os.system("latex -interaction=batchmode doc")
			os.system("convert -trim -bordercolor White -border 20x10 +repage -density 300 doc.dvi doc.jpg")
			os.system("mv doc.jpg "+output)

		if (ext==".tex"):
			os.system("mv doc.tex "+output)

	elif (ext==".gz"):
		cmd = 'tar -czvf '+output+' ./*.inp ./sim.opvdm ./*.dat '
		os.system(cmd)



