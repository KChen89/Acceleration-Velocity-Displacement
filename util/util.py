'''
utility function to read data, integration, and plot
@author: Kemeng Chen
'''

import os
import sys
import numpy as np 
import math
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy import signal
from mpl_toolkits.mplot3d import Axes3D

def read_data(file_path, columns):
	'''
	read files according to file_path and columns
	args:
		file_path, columns (list)
	return:
		data (numpy array)
	'''
	if not os.path.isfile(file_path):
		raise AssertionError(file_path, 'not found')
	mode='r'
	with open (file_path, mode) as f:
		lines=f.readlines()
		num_rows=len(lines)
		print(str(num_rows), ' rows')
		num_cols=len(columns)
		data=np.zeros([num_rows, num_cols])
		for indice, line in enumerate(lines[3:]):
			row=line.rstrip().split('\t')
			# print(row)
			for ii, i in enumerate(columns):
				data[indice,ii]=row[i]
		# data[:,2]-=10
		# for i in range(3):
		# 	data[:,i]=calibration(data[:,i])
	f.close()
	return data

def median_filter(data, f_size):
	lgth, num_signal=data.shape
	f_data=np.zeros([lgth, num_signal])
	for i in range(num_signal):
		f_data[:,i]=signal.medfilt(data[:,i], f_size)
	return f_data

def freq_filter(data, cutoff):
	pass

def coeffs_interp(coeffs, s_lgth):
	'''
	interpolation of coefficients
	Args:
		coeffs: coeffs (list)
		s_lgth: expected length after interpolation
	Returns:
		ucoeffs: coefficients after interpolation
	'''
	level=len(coeffs)
	ucoeffs=list()
	r_index=np.linspace(0, s_lgth, s_lgth, endpoint=False)
	for i in range(level):
		w_data=coeffs[i]
		temp_index=np.linspace(0, s_lgth, w_data.shape[0], endpoint=True)
		intep_f=interp1d(temp_index, w_data)
		intep_data=intep_f(r_index)
		ucoeffs.append(intep_data)
	return ucoeffs

def data_wavelets_plot(data, ws=128, mw='db4', lev=7):
	lgth, num_signal=data.shape
	label=['x', 'y', 'z']
	for i in range(num_signal):
		signal=np.pad(data[:,i], math.floor(ws/2), 'edge')
		coeffs=wavedec(data, wavelet=mw, level=lev, mode='symmetric')
		ucoeffs=coeffs_interp(coeffs, lgth)
		plot_wavelets(ucoeffs, label[i])

def plot_wavelets(coeffs, title):
	'''
	plot coefficients of each level
	Args:
		coeffs: coefficients in list
	Returns:
		none
	'''
	level=len(coeffs)
	fig, axes=plt.subplots(level, 1)
	for i in range(level):
		axes[level-i-1].plot(coeffs[i])
		axes[level-i-1].set_xlim([0, len(coeffs[i])-1])
		if i==level-1:
			title='cA'+str(i)
		else:
			title='cD'+str(i+1)
		axes[i].set_title(title)

def fft_plot(data, fs):
	lgth, num_signal=data.shape
	fqy=np.zeros([lgth,num_signal])
	fqy[:,0]=np.abs(fft(data[:,0]))
	fqy[:,1]=np.abs(fft(data[:,1]))
	fqy[:,2]=np.abs(fft(data[:,2]))
	index=np.arange(int(lgth/2))/(int(lgth/2)/(fs/2))
	fig, ax=plt.subplots()
	labels=['x','y','z']
	color_map=['r', 'g', 'b']
	for i in range(3):
		ax.plot(index, fqy[0:int(lgth/2),i], color_map[i], label=labels[i])
	ax.set_xlim([0, fs/2])
	ax.set_xlabel('Hz')
	ax.set_title('Frequency spectrum')
	ax.legend()

def plot_lines(data, fs):
	num_rows, num_cols=data.shape
	if num_cols!=3:
		raise ValueError('Not 3D data')
	fig, ax=plt.subplots()
	labels=['x','y','z']
	color_map=['r', 'g', 'b']
	index=np.arange(num_rows)/fs
	for i in range(num_cols):
		ax.plot(index, data[:,i], color_map[i], label=labels[i])
	ax.set_xlim([0,num_rows/fs])
	ax.set_xlabel('Time [sec]')
	ax.set_title('Time domain')
	ax.legend()

def acc_integration(data):
	num_rows, num_cols=data.shape
	int_data=np.zeros(data.shape)
	for i in range(num_cols):
		int_data[:,i]=TZ_integration(data[:,i])
	return int_data

def plot3D(data):
	fig=plt.figure()
	ax=fig.add_subplot(111, projection='3d')
	ax.plot(xs=data[:,0], ys=data[:,1], zs=data[:,2], zdir='z')

def calibration(signal):
	inc_eng=np.sum(np.clip(signal, a_min=0, a_max=None))
	der_eng=-1*np.sum(np.clip(signal, a_max=0, a_min=None))
	if inc_eng==0 or der_eng==0:
		raise ValueError('Calibration rule does NOT hold')

	if inc_eng>der_eng:
		beta_p=1
		beta_n=inc_eng/der_eng
		c_signal=(beta_n-1)*np.clip(signal, a_max=0, a_min=None)+signal
	elif der_eng>inc_eng:
		beta_n=1
		beta_p=der_eng/inc_eng
		c_signal=(beta_p-1)*np.clip(signal, a_min=0, a_max=None)+signal
	else:
		c_signal=signal
	return c_signal

def TZ_integration(in_signal):
	lgth=in_signal.shape
	integral=np.zeros(lgth)
	c=0
	for indice, s in enumerate(in_signal):
		if indice==0:
			integral[indice]=c+in_signal[indice]
		else:
			integral[indice]=integral[indice-1]+in_signal[indice]
	return integral

