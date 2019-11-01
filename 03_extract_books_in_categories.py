#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 13:24:47 2019

@author: christiancasey

This script processes the book entries to create a pandas dataframe with only
the book titles and category IDs.
It also downloads the New Titles data from the Google sheet as a dataframe.
It saves both for later use.
"""

import os
import glob
import re
import pandas
from tqdm import tqdm

#%% Load categories data files

# Basic categories (index corresponds to category number - 1)
with open('categories.dat', 'r') as f:
	vCategories = f.read().split('\n')
	f.close()
nCategories = len(vCategories)

#%% Extract book entries with categories

dfBooks = pandas.DataFrame(columns = ['CategoryID', 'BookHTML', 'BookAlpha'])
for iCatID in tqdm(range(1,nCategories+1)):
	
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
		
		# If it is already in the dataframe, skip it
		if ( dfBooks['BookHTML'].str.find(strBibEntry) > -1 ).any():
			continue;
		
		
		# Now we know that strBibEntry contains a NEW book title
		
		# Put the whole thing in the dataframe
		dfBook = pandas.DataFrame({'CategoryID': [iCatID],
																														'BookHTML': [strBibEntry], 
																														'BookAlpha': [strBibEntryAlpha]})
		
		dfBooks = dfBooks.append(dfBook, ignore_index=True)


#%% Get the current data from the CSV file that Gabriel is editing
dfSheet = pandas.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vQJKa50tuO654jw8quDaMRlKJbDIkV3FYQPESrQ60IfspMZQynqs1tEA99x6lNm_L9t8fikw8LdAwY4/pub?gid=1471928200&single=true&output=csv')

# Rename one column because it causes problems for SQL
dfSheet.rename( columns = {'Controlled heading (Pleiades, TGN, LCSH, or FAST)': 'Controlled heading'}, inplace = True)

		
#%% Save the output for use in the next script

dfBooks.to_pickle('books_categories.pkl')
dfSheet.to_pickle('books_sheet.pkl')
















