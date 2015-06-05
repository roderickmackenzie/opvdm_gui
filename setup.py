from distutils.core import setup
import py2exe

setup(
	name = "opvdm",
	version = "2.8",
	description = "Organic photovoltaic device model (opvdm)",
	author = "Roderick MacKenzie",
	author_email = "roderick.mackenzie@nottingham.ac.uk",
	py_modules=['opvdm'],
	options = {
		'py2exe': {
		'packages': ['numpy','pycrypto','matplotlib','six','pyparsing','pywin32']
		}
	}
      )
