# -*- coding: utf-8 -*-
"""
EULERSLICK MODULE (eulerSlick.py)
Eulerian Video Magnification Algorithm
Originally created by: Dana Silver
Forked from: https://github.com/brycedrennan/eulerian-magnification/blob/master/eulerian_magnify.py
GitHub: 
Modified by: Dan Sweeney (Sun Oct  5 14:37:19 2014)
@author: Dan
"""

import cv2
import os
import sys

import numpy as np
import pylab
import scipy.signal
import scipy.fftpack

import cv2.cv as cv

class eulerSlick(object):
    def __init__(self, video_filepath):
        pyramid_levels = 4
        amplification = 50
        pyramid_type = 'laplacian'
        lo_cutoff, hi_cutoff = [0.833, 1]
        
        # Load video and get fps
        video_buffer, fps = self.loadVideo(video_filepath)
        
        # Decompose video into frequency pyramid
        pyramid_buffer = self.generatePyramid(video_buffer, pyramid_type, pyramid_levels)
        
        # Apply bandpass filter to video
        filtered_buffer = self.temporalBandpass(pyramid_buffer, fps, lo_cutoff, hi_cutoff)
        
        # Amplify filtered video
        amplified_buffer = self.amplify(filtered_buffer, amplification)
        
        # Collapse amplified pyramid and add to original video
        collapsed_buffer = self.collapsePyramid(amplified_buffer, video_buffer, pyramid_levels) 
        
            
    def loadVideo(self, video_filepath):
        print "Loading " + video_filepath
        
        # Load video and get basic properties
        capture = cv2.VideoCapture(video_filepath)
        frame_count = int(capture.get(cv.CV_CAP_PROP_FRAME_COUNT))
        width, height = get_capture_dimensions(capture)
        fps = int(capture.get(cv.CV_CAP_PROP_FPS))
        
        # Generate a height x width x frame_count matrix for video
        x = 0
        video_buffer = np.zeros((frame_count, height, width, 3), dtype='uint8')
        while True:
            _, frame = capture.read()
    
            if frame == None or x >= frame_count:
                break
            video_buffer[x] = frame
            x += 1
        capture.release()

        return video_buffer, fps

        
    def generatePyramid(self, video, pyramidType, levels):
        if pyramidType == 'gaussian':
            pyramid_buffer = self.gaussianPyramid(video, levels)
        elif pyramidType == 'laplacian':
            pyramid_buffer = self.laplacianPyramid(video, levels)
        else:
            print "ERROR: INCORRECT PYRAMID TYPE\nUnable to generate pyramid of type " + str(pyramidType)
        return pyramid_buffer
 
       
    def laplacianPyramid(self, video, levels):
        vid_data = None
        for x in range(0, video.shape[0]):
            frame = video[x]
            copy = np.ndarray(shape=frame.shape, dtype="float")
            copy[:] = frame
    
            for i in range(levels):
                prev_copy = copy[:]
                copy = cv2.pyrDown(copy)
    
            laplacian = prev_copy - cv2.pyrUp(copy)
    
            if x == 0:
                vid_data = np.zeros((video.shape[0], laplacian.shape[0], laplacian.shape[1], 3))
            vid_data[x] = laplacian
        return vid_data
  
              
    def gaussianPyramid(self, video, levels):
        vid_data = None
        for x in range(0, video.shape[0]):
            frame = video[x]
            copy = np.ndarray(shape=frame.shape, dtype="float")
            copy[:] = frame
            for i in range(levels):
                copy = cv2.pyrDown(copy)
    
            gaussian = copy
    
            if x == 0:
                vid_data = np.zeros((video.shape[0], gaussian.shape[0], gaussian.shape[1], 3))
            vid_data[x] = gaussian
        return vid_data
  
      
    def temporalBandpass(self, video, fps, lo_cutoff = 0.833, hi_cutoff = 1, axis = 0):
        print "Applying bandpass between " + str(lo_cutoff) + " and " + str(hi_cutoff) + " Hz"
        
        # Apply Fourier transform for frequency-domain filtering
        fft = scipy.fftpack.fft(video, axis=axis)
        frequencies = scipy.fftpack.fftfreq(video.shape[0], d=1.0 / fps)
        
        # Find bounding frequencies for bandpass filter
        bound_low = (np.abs(frequencies - lo_cutoff)).argmin()
        bound_high = (np.abs(frequencies - hi_cutoff)).argmin()
        
        # Generate bandpass within FFT
        fft[:bound_low] = 0
        fft[bound_high:-bound_high] = 0
        fft[-bound_low:] = 0
        
        # Inverse FFT to return filtered signal
        filtered_buffer = scipy.fftpack.ifft(fft, axis=0)
        return filtered_buffer
        
        
    def amplify(self, video_buffer, amplification):
        print "Amplifying signal by factor of " + str(amplification)
        video_buffer *= amplification
        return video_buffer
        
        
    def collapsePyramid(self, mod_buffer, video_buffer, pyramid_levels, fps):
        """Combine a gaussian video representation with the original and save to file"""
        # ISOLATE THE PRAMID COLLAPSE AND REOPENING THE PYRAMID
        width, height = get_frame_dimensions(video_buffer[0])
        fourcc = cv.CV_FOURCC('M', 'J', 'P', 'G')
        writer = cv2.VideoWriter(save_filename, fourcc, fps, (width, height), 1)
        for x in range(0, mod_buffer.shape[0]):
            img = np.ndarray(shape=mod_buffer[x].shape, dtype='float')
            img[:] = mod_buffer[x]
            for i in range(pyramid_levels):
                img = cv2.pyrUp(img)
    
            img[:height, :width] = img[:height, :width] + video_buffer[x]
            res = cv2.convertScaleAbs(img[:height, :width])
            writer.write(res)
            
if __name__ == "__main__":
    apple = eulerSlick('/Users/Dan/Movies/Mitosis_in_2D_-_HeLa_cell_undergoes_mitosis-HD.avi')