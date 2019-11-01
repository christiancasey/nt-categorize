#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 10:23:56 2019

@author: christiancasey

This script downloads all of the pages in the ISAW New Titles part of the website.
"""

import urllib
import os
import glob
import pandas


#%% Clean out directory for new files

vFiles = glob.glob('pages/*')
for strFilename in vFiles:
	os.remove(strFilename)


#%% Load list of URLs for old New Titles pages
	
dfURLs = pandas.read_csv('URLs.csv')
vURLs = [strURL for strURL in dfURLs['URL']]


#%% Loop through URL list and download all files

iPage = 0
for strURL in vURLs:
	print(strURL)
	
	i = strURL.rfind('/')
	strName = strURL[i+1:]
	
	strPage = urllib.request.urlopen(strURL).read().decode('utf-8')
	
	# Save filename with name in URL and an index number for proper sorting
	# Separate index and name with ~ for easy parsing later if necessary
	iPage += 1
	f = open( ('pages/%02i ~ ' % iPage) + strName + '.html', 'w')
	f.write(strPage)
	f.close()
	








