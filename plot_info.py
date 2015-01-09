class plot_info():
	file_name=""
	x_label=""
	y_label=""
	y_units=""
	other_file=""
	x_mul=1.0
	y_mul=1.0
	logscale_x=0
	logscale_y=0
	title=""
	type=""
	def __init__(self,a,b,l,c,j,d,e,f,g,h,i):
		self.file_name=a
		self.x_label=b
		self.y_label=c
		self.x_mul=d
		self.y_mul=e
		self.other_file=f
		self.logscale_x=g
		self.logscale_y=h
		self.title=i
		self.y_units=j
		self.x_units=l
		self.type="xy"
