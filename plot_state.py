class plot_state():
	def __init__(self):
		self.grid=False
		self.show_pointer=False
		self.logy=False
		self.logx=False
		self.label_data=False
		self.invert_y=False
		self.normalize=False
		self.norm_to_peak_of_all_data=False
		self.subtract_first_point=False
		self.add_min=False
		self.legend_pos="lower right"
		self.ymax=-1
		self.ymin=-1
		self.x_label=""
		self.y_label=""
		self.x_units=""
		self.y_units=""
		self.x_mul=1.0
		self.y_mul=1.0
		self.key_units=""
