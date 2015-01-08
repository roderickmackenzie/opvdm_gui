import sys
import os
import shutil
from token_lib import tokens
from util import pango_to_gnuplot
from plot_info import plot_info
from util import zip_get_data_file

def load_graph(path):
	cmd = '/usr/bin/gnuplot -persist '+path
	print cmd
	os.system(cmd)

def check_info_file(search_string):
	files=["dos0.inp","dos1.inp","photokit_ri.dat","photokit_real.dat","photokit_imag.dat","jv_psun_voc.dat","jv_voc_nt.dat","jv_voc_pt.dat","jv_psun_nf_nt.dat","jv_psun_pf_pt.dat","jv_psun_np_tot.dat","sim_info.dat","light.inp"]
	if files.count(search_string)> 0:
		return True
	else:
		return False

def file_name_to_latex(in_string):
	out_string=in_string.replace("_","\\_")
	return out_string

def get_plot_file_info(output,file_name):
	found,lines=zip_get_data_file(file_name)
	if found==False:
		return False

	for i in range(0, len(lines)):
		lines[i]=lines[i].rstrip()
	if len(lines)>1:
		if lines[0]=="#opvdm":
			for i in range(0, len(lines)):
				if (lines[i][0]!="#"):
					break
				else:
					command=lines[i].split(" ",1)
					if len(command)<2:
						command.append("")
					if (command[0]=="#x_mul"):
						output.x_mul=float(command[1])
					if (command[0]=="#y_mul"):
						output.y_mul=float(command[1])
					if (command[0]=="#x_label"):
						output.x_label=command[1]
					if (command[0]=="#y_label"):
						output.y_label=command[1]
					if (command[0]=="#x_units"):
						output.x_units=command[1]
					if (command[0]=="#y_units"):
						output.y_units=command[1]
					if (command[0]=="#logscale_x"):
						output.logscale_x=bool(int(command[1]))
					if (command[0]=="#logscale_y"):
						output.logscale_y=bool(int(command[1]))
					if (command[0]=="#type"):
						output.type=command[1]
					if (command[0]=="#title"):
						output.title=command[1]
					if (command[0]=="#section_one"):
						output.section_one=command[1]
					if (command[0]=="#section_two"):
						output.section_two=command[1]

			#print "Data read from file"
			return True

	return False

class plot_data:

	
	pos=0
	def __init__(self):
		print "init"

	def find_file(self,file_name,plot_token):
		self.local=plot_info("","","","","",1.0,1.0,"none",0,0,"","","")
		ret=get_plot_file_info(self.local,file_name)
		print "ret====",ret
		if ret==True:
			self.read=self.local
			return True

		#check to see if I have been provided with a token

		if plot_token!=None:
			my_token_lib=tokens()
			result0=my_token_lib.find(plot_token.tag0)
			result1=my_token_lib.find(plot_token.tag1)
			print "one=",plot_token.tag0,result0
			print "two=",plot_token.tag1,result1
			if result0!=False:
				ret=plot_info("","","","","",1.0,1.0,"none",0,0,"","","")
				ret.x_label=result0.info
				ret.x_units=result0.units
				ret.y_label=result1.info
				ret.y_units=result1.units
				ret.title=result0.info+" "+result1.info

				print "Found tokens",plot_token.tag0,plot_token.tag1
				self.read=ret
				return True
			else:
				print "Tokens not found",plot_token.tag0,plot_token.tag1

		return False
	
