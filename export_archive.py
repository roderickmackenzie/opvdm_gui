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
import glob

def export_archive(target):
	for path, dirs, files in os.walk(directory):
		
		for file_name in files:
			whole_file_name=os.path.join(path,file_name)
			#print whole_file_name,"rod",self.ip_address[node]
			sendfile = open(whole_file_name, 'rb')
			data = sendfile.read()
			data_zip=data.encode("zlib")
			sendfile.close()
			sock.sendall(encode_for_tcp(whole_file_name)+encode_for_tcp(len(data_zip)))
			sock.sendall(data_zip)

	zf = zipfile.ZipFile(abs_path, 'w')

	for file_name in os.listdir(os.getcwd()):
		if file_name.endswith(".inp"):
			
			build='\n'.join(lines)
			zf.writestr(target, build)

	zf.close()



