from distutils.core import setup
import py2exe
import os
import sys
import matplotlib
import shutil
import glob

dest_path=os.path.join(os.getcwd(),"dist")

#if os.path.isdir(dest_path):
#	shutil.rmtree(dest_path)

includes =['cairo', 'pango', 'pangocairo','atk', 'gobject', 'gio',"matplotlib.backends",  "matplotlib.backends.backend_tkagg"]
pack  =[  'gtk','gtk.keysyms']
setup(
		console=['opvdm.py'],
        options={
				"py2exe":{
				'packages': pack,
				"includes": includes}
				},
		data_files=matplotlib.get_py2exe_datafiles()
)

if os.path.isdir(os.path.join(os.getcwd(),"dist","etc"))==False:
	dist=os.path.join(os.getcwd(),"dist","etc")
	print "copying",dist
	shutil.copytree("c:\\Python27\\Lib\\site-packages\\gtk-2.0\\runtime\\etc", dist)

	dist=os.path.join(dest_path,"lib")
	print "copying",dist
	shutil.copytree("c:\\Python27\\Lib\\site-packages\\gtk-2.0\\runtime\\lib", dist)

	dist=os.path.join(dest_path,"share")
	print "copying",dist
	shutil.copytree("c:\\Python27\\Lib\\site-packages\\gtk-2.0\\runtime\\share", dist)

print "copying from z:\\auto_dep\\"
for file in glob.glob("z:\\auto_dep\\*"):
	print file,os.getcwd()
	shutil.copy(file, os.getcwd())
	print file,dest_path+"\\"
	shutil.copy(file, dest_path+"\\")


path_to_del=os.path.join(dest_path,"share","gtk-doc")
if os.path.isdir(path_to_del)==True:
	print "Delete",path_to_del
	shutil.rmtree(path_to_del)

path_to_del=os.path.join(dest_path,"share","locale")
if os.path.isdir(path_to_del)==True:
	print "Delete",path_to_del
	shutil.rmtree(path_to_del)

path_to_del=os.path.join(dest_path,"share","man")
if os.path.isdir(path_to_del)==True:
	print "Delete",path_to_del
	shutil.rmtree(path_to_del)


path_to_del=os.path.join(dest_path,"share","doc")
if os.path.isdir(path_to_del)==True:
	print "Delete",path_to_del
	shutil.rmtree(path_to_del)

path_to_del=os.path.join(dest_path,"share","gtk-2.0")		#only contains a demo folder
if os.path.isdir(path_to_del)==True:
	print "Delete",path_to_del
	shutil.rmtree(path_to_del)

path_to_del=os.path.join(dest_path,"share","pub","gui","dist","tcl","tk8.5","demos")
if os.path.isdir(path_to_del)==True:
	print "Delete",path_to_del
	shutil.rmtree(path_to_del)

path_to_del=os.path.join(dest_path,"share","pub","gui","dist","tcl","tk8.5","images")
if os.path.isdir(path_to_del)==True:
	print "Delete",path_to_del
	shutil.rmtree(path_to_del)

path_to_del=os.path.join(dest_path,"share","mpl-data","sample_data")
if os.path.isdir(path_to_del)==True:
	print "Delete",path_to_del
	shutil.rmtree(path_to_del)

path_to_del=os.path.join(dest_path,"share","icons","Tango","scalable")
if os.path.isdir(path_to_del)==True:
	print "Delete",path_to_del
	shutil.rmtree(path_to_del)
