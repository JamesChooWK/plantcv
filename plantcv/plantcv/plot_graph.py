# -*- coding: utf-8 -*-
'''
Created on Thursday 19.12.2019
Copyright (©) CHOO WAI KEONG (James) 
Author: CHOO WAI KEONG (James) 
Email: james@adinnovations.nl
'''

import matplotlib.pyplot as plt
import numpy as np

def plot_graph(array, plot_label):
	""" plotting the array value for visualising.

	Inputs:
	array = peak value (numpy array)

	:param array: numpy array
	Returns:

	"""
	x_axis = np.arange(len(array))
	plt.plot(x_axis, array, label= str(plot_label))
	# plt.show()