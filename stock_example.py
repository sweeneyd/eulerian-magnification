# -*- coding: utf-8 -*-
"""

Created on Mon Sep 22 23:02:04 2014

@author: Dan
"""

from eulerian_magnify import eulerian_magnification, show_frequencies

video_name = '/Users/Dan/Movies/Mitosis in 2D - HeLa cell undergoes mitosis-HD.mp4'
show_frequencies(video_name)
eulerian_magnification(video_name, image_processing='gaussian', pyramid_levels=3, freq_min=50.0 / 60.0, freq_max=1.0, amplification=50)

#show_frequencies('media/baby.mp4')
#eulerian_magnification('media/baby.mp4', image_processing='laplacian', pyramid_levels=5, freq_min=0.45, freq_max=1, amplification=50)