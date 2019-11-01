#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 10:23:56 2019

@author: christiancasey

This script processes the scraped data from the ISAW New Titles pages
and creates a new set of files with only book entries grouped by category.
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

# Messy categories used in HTML and mapping to category number
dfCategoryMap = pandas.read_csv('category_map.csv')
dCategoryMap = dict(zip(dfCategoryMap['Category'], dfCategoryMap['Number']))


#%% Get a list of unique categories as they appear in the HTML
## There is no need to do this again, all categories are now loaded from files above
#vCategoriesMessy = []
#vFiles = glob.glob('pages/*')
#vFiles.sort()
#
#for strFilename in vFiles:
#	with open(strFilename, 'r') as f:
#		strPage = f.read()
#		f.close()
#		
#	strRegex = re.compile('<a name="(?P<name>.*?)" id="(?P<id>.*?)">')
#	vMatches = re.findall(strRegex, strPage)
#	
#	# Deal with the fact that some files have links without a name attribute
#	# Some have only one link with a name attribute
#	# Any file with fewer than 4 matches needs to be researched
#	if len(vMatches) <= 3:
#		strRegex = re.compile('<a id="(?P<id>.*?)">')
#		vMatches = re.findall(strRegex, strPage)
#	
#	
#	print('%i - %s' % (len(vMatches), strFilename) )
#	
#	for vMatch in vMatches:
#		if isinstance(vMatch, str):
#			vMatch = [vMatch];
#		vCategoriesMessy.append(vMatch[0])
#		
#print()
#vCategoriesMessy = list(set(vCategoriesMessy))
#vCategoriesMessy.sort()

#%% Get list of files and mark categories
# Replace the category HTML string with a clear formatted marker, 
# which maps all the various category names to a single unique identifier
vFiles = glob.glob('pages/*')
vFiles.sort()


vBooksInCat = [''] * nCategories 		# Empty container for all book lists grouped by category
	
for strFilename in vFiles:
	with open(strFilename, 'r') as f:
		strPage = f.read()
		f.close()
	
	# Replace <strong> with <b> for consistency across files
	strPage = re.sub( r'<([\/]*)strong>', r'<\1b>', strPage )
	
	strRegex = re.compile('<a .*?id="(.*?)">')
	vMatches = re.findall(strRegex, strPage)
#	print('• %i - %s' % (len(vMatches), strFilename) )
	
	# Go through the matching category ids and map them to an set integer value
	iPrev = -1;
	for strMatch in vMatches:
		# Some matched strings in this looser search are not in the dict, use .get()
		# 0 refers to no match or an erroneous one (e.g. "Top")
		iCatID = dCategoryMap.get(strMatch, 0)
		
		# Only encode the category when a match is found
		if not (iCatID == 0):
			# Replace the match with a unambiguous string containing category number
			strPage = re.sub( re.compile('<a .*?id="%s">' % strMatch), '\n\n•Category¶%i§\n\n' % (iCatID), strPage )
		
		
		# Use iPrev to ensure that category numbers are always ascending
		if iCatID > 0 and iCatID < iPrev:
			raise Warning('Categories are not in ascending order: %s', strFilename)
		iPrev = iCatID
	
	# Loop through the categories and clean up the page
	for iCatID in range(1,nCategories+1):
		
		# Keep only the last category identifier
		# The last category heading is the one preceeding the books
		strCategoryLabel = '•Category¶%i§' % (iCatID)
		iLastCategoryInstance = strPage.rfind( strCategoryLabel )
		# Delete all category labels except the last one
		strPage = strPage[:iLastCategoryInstance].replace( strCategoryLabel, '' ) + strPage[iLastCategoryInstance:]
	
	# Get the locations of all category labels
	vMatches = re.finditer('•Category¶\d',strPage)
	vMatchStart = [ reMatch.start() for reMatch in vMatches ]
	
	# Use this random comment in the HTML to mark the end of the last category
	# It appears in every file in the same place, right after the last category
	iEOF = strPage.find('<!-- AddThis Button BEGIN -->')
	
	# Raise a warning if the EOF signal is not found
	if iEOF == -1:
		raise Warning('No EOF signal found in file: %s' % strFilename)
	
	# Put the end of file index for the last category
	vMatchStart.append(iEOF)
		
	# Loop through categories in file and extract content
	vMatches = re.finditer('•Category¶\d',strPage)
	for iMatch, reMatch in enumerate(vMatches):
		iCatID = int(reMatch.group()[-1])
		strBooksInCat = strPage[vMatchStart[iMatch]:vMatchStart[iMatch+1]]
		strBooksInCat = '%s\n\n%s\n\n\n\n%s\n' % (strFilename,strBooksInCat, '~'*80) 					# Add some whitespace
		vBooksInCat[iCatID-1] = vBooksInCat[iCatID-1] + strBooksInCat
	
#%% Save books in category to text files
for iCatID in range(1,nCategories+1):
	strFilename = 'books_in_categories/%i – %s.txt' % (iCatID, vCategories[iCatID-1])
	with open(strFilename, 'w') as f:
		f.write(vBooksInCat[iCatID-1])
		f.close()



















