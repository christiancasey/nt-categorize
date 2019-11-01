#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 13:24:47 2019

@author: christiancasey
"""
import os
import glob
import re
import pandas

#%% Load categories data files

# Basic categories (index corresponds to category number - 1)
with open('categories.dat', 'r') as f:
	vCategories = f.read().split('\n')
	f.close()
nCategories = len(vCategories)

#%% Extract book entries with categories
dfBooks = pandas.DataFrame(columns =['Book', 'CategoryID']) 
for iCatID in range(1,nCategories+1):
	strFilename = 'books_in_categories/%i – %s.txt' % (iCatID, vCategories[iCatID-1])
	with open(strFilename, 'r') as f:
		strBooks = f.read()
		f.close()
	
	# Loop through all the entries marked off by <p> tags
	vMatches = re.finditer( r'<p.*?>(.*?)</p>', strBooks )
	for reMatch in vMatches:
		strBibEntry = reMatch.groups()[0]
		strBibEntry = strBibEntry.strip()
		
		# If there are no <b> tags, then the entry doesn't contain a title and is not a book entry
		vMatchesTitles = re.findall( r'<b.*?>(.*?)</b>', strBibEntry )
		if len(vMatchesTitles) < 1:
			continue
		
		# Remove all non-book-related stuff to verify that this is a book entry
		strBibEntryAlpha = strBibEntry
		strBibEntryAlpha = re.sub( r'[Bb]ack to top', '', strBibEntryAlpha )
		strBibEntryAlpha = re.sub( r'<([\/]*)(\w+)(.*?)>', r' ', strBibEntryAlpha )
		strBibEntryAlpha = re.sub( r'[^\w]', ' ', strBibEntryAlpha )
		strBibEntryAlpha = re.sub( r'\s+', r' ', strBibEntryAlpha )
		strBibEntryAlpha = strBibEntryAlpha.strip()
		
		# If you remove all the HTML stuff and it's now very short, it's not a book
		if len(strBibEntryAlpha) < 1:
			continue
		
		# Now we know that strBibEntry contains a book title
		