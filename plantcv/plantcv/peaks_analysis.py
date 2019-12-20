# -*- coding: utf-8 -*-
'''
Created on Thursday 19.12.2019
Copyright (©) CHOO WAI KEONG (James) 
Author: CHOO WAI KEONG (James) 
Email: james@adinnovations.nl
'''

import numpy as np 


def peaks_analysis(array, daxis):
	""" Calculate the total value of each axis and return an array

	Inputs:
	array = numpy array of the RGB or Gray image
	daxis = x or y direction ( x = 1, y = 0)

	Returns:
	peaks_array = array of peaks value

	:param array: numpy.ndarray
	:param daxis: int
	:return peaks_array: numpy.ndarray
	"""
	peaks_array = np.sum(array, axis=daxis)

	return peaks_array