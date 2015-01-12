import sys
import os
import shutil
from util import opvdm_clone
from export_as import export_as
from import_archive import import_archive
from util import find_data_file
from util import opvdm_copy_src
import fnmatch
import logging
import time
from import_archive import delete_scan_dirs
from import_archive import clean_scan_dirs
from ver import ver
from import_archive import import_scan_dirs
from udp_server import udp_server
from udp_client import udp_client
from make_man import make_man
from scan_util import tree_load_program
from scan_util import tree_gen
from scan_item import scan_item_load
from scan_item import scan_items_index_item
from server import server
from util import set_exe_command
import gtk 
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
			print "\t--clean\t\tcleans the current simulation directory deleting .dat files and scan dirs"
			print "\t--dump-tab (output file)\t\tdumps simulation parameters as jpg"
			print "\t--import-scandirs\t\tOnly imports the scan directories"
			print "\t--clean-scandirs\t\tDeletes the content of all scan dirs"

			print ""
			print "Additional information about opvdm is available at http://www.opvdm.com."
			print ""
			print "Report bugs to: roderick.mackenzie@nottingham.ac.uk"
			sys.exit(0)
		if argv[1]=="--version":
			print ver()
			sys.exit(0)
		if argv[1]=="--import-scandirs":
			import_scan_dirs("./",argv[2])
			exit(0)
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
		if argv[1]=="--clone-src":
			opvdm_copy_src(argv[2])
			sys.exit(0)

		if argv[1]=="--file_info":
			data=plot_data()
			data.dump_file()
			sys.exit(0)
		if argv[1]=="--clean":
			delete_scan_dirs("./")
			if os.path.isdir("./pub"):
				print "Deleteing pub"
				shutil.rmtree("./pub")
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
		if argv[1]=="--clean-scandirs":
			clean_scan_dirs(os.getcwd())
			sys.exit(0)

		if argv[1]=="--server":
			obj=udp_server()
			obj.start()

		if argv[1]=="--client":
			client=udp_client()
			client.init()

		if argv[1]=="--make-man":
			make_man()
			sys.exit(0)

		if argv[1]=="--run-scan":
			program_list=[]
			exe_command , exe_name  =  set_exe_command()
			print scan_items_index_item("imps/Modulation frequency")
			scan_item_load("./suns/scan_items.inp")
			tree_load_program(program_list,"./suns/")
			print program_list
			watch_dir=os.path.join(os.getcwd())+"/suns/"
			commands=tree_gen(program_list,os.getcwd(),os.path.join(os.getcwd(),"suns"))
			myserver=server()
			myserver.init(watch_dir)
			myserver.clear_cache()
			for i in range(0, len(commands)):
				myserver.add_job(commands[i])
				print "Adding job"+commands[i]
			myserver.simple_run(exe_command)

			sys.exit(0)

