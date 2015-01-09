import pygtk
pygtk.require('2.0')
import gtk
import sys
import os
import shutil
import logging

class scan_item:
	name=""
	token=""
	filename=""

def scan_item_add(check_list,file_name,token,text_info):
	logging.info('scan_item_add')
	check_list.append(scan_item())
	listpos=len(check_list)-1
	check_list[listpos].name=os.path.splitext(file_name)[0]+'/'+text_info
	check_list[listpos].filename=file_name
	check_list[listpos].token=token
