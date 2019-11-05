#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 15:24:52 2019

@author: christiancasey

This script matches the titles in the Google Sheet (prepared by Gabriel) 
to the results from scraping the webpage
"""

import os
import glob
import re
import pandas
from tqdm import tqdm

#%% Function definitions

# Returns a new dataframe with each word separated into a new column
def BreakOutWords(df, strColumn, nWords = 5):
	dfWords = pandas.DataFrame(columns = list(range(1,nWords+1))) 
	
	for strText in df[strColumn]:
		vWords = strText.split()
		vWords = vWords[:min(len(vWords),nWords)]
		dfRow = pandas.DataFrame(columns = range(1,len(vWords)+1))
		dfRow.loc[0] = vWords
		dfWords = dfWords.append(dfRow)
		
	return dfWords

def FindMatchesInColumn( dfColumn, strWord ):
	vMatches = dfColumn.str.lower().find(strWord.lower()) > -1
	vMatches = [ int(x) for x in vMatches ]
	return vMatches

def PadBSN( strBSN ):
	if len(strBSN) >= 9:
		return strBSN
	strBSN = '0'*(9-len(strBSN)) + strBSN
	return strBSN

#%% Load categories data files

# Basic categories (index corresponds to category number - 1)
with open('categories.dat', 'r') as f:
	vCategories = f.read().split('\n')
	f.close()
nCategories = len(vCategories)

#%% Initialize dataframes
dfBooks = pandas.read_pickle('books_categories.pkl')
dfBooks.insert(0, 'Index', dfBooks.index.tolist() ) 			# Add an index to include in match below

# Get the current data from the CSV file that Gabriel is editing
dfSheet = pandas.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vQJKa50tuO654jw8quDaMRlKJbDIkV3FYQPESrQ60IfspMZQynqs1tEA99x6lNm_L9t8fikw8LdAwY4/pub?gid=1471928200&single=true&output=csv')

# Rename one column because it causes problems for SQL
dfSheet.rename( columns = {'Controlled heading (Pleiades, TGN, LCSH, or FAST)': 'Controlled heading'}, inplace = True)

# Cludge to fix the fact that this formatted date field is interpreted as a float on import
dfSheet['DATE_ADDED'] = dfSheet['DATE_ADDED'].astype(str)
dfSheet['DATE_ADDED'] = dfSheet['DATE_ADDED'].apply(lambda x: x.replace('.0', ''))

nBooks = len(dfBooks)
nSheet = len(dfSheet)

#vSheetTitles = dfSheet['Title and author'].str.lower().to_list()
vSheetTitles = dfBooks['BookAlpha'].str.lower().to_list()
vSheetTitles = [ re.sub( r'[^\w]', '', s ) for s in vSheetTitles ]

#%% Matching -- match Google Sheets data (dfSheets) to list of books scraped from site (dfBooks)

dfBooksMatches = pandas.DataFrame(columns = ['MatchedTitle', 'MatchIndex', 'Category', 'CategoryID', 'Score'])


# Loop through each title in the books dataframe and find its best match in the sheet

for iRow in tqdm(range(0, nSheet)):
	
#	strTitle = dfBooks['BookAlpha'].iloc[iRow].lower().strip()
	strTitle = dfSheet['Title and author'].iloc[iRow].lower().strip()
#	iAuthorStart = strTitle.find(' // ')
#	if(iAuthorStart > 1):
#		strTitle = strTitle[:iAuthorStart-1].strip()
	strTitle = re.sub( r'[^\w]', '', strTitle )
	
	strBSN = PadBSN( dfSheet['BSN'].iloc[iRow] )
	dfBSNMatch = dfBooks.query('BSN == "'  + strBSN + '"')
	
	# If there is a BSN match, make the connection and skip the title matching
	if len(dfBSNMatch) == 1:
		
		strTitle = dfBSNMatch['BookAlpha'].iloc[0]
		iMaxIndex = dfBSNMatch['Index'].iloc[0]
		iCatID = dfBSNMatch['CategoryID'].iloc[0]
		iMaxScore = 1000          #  Just make it bigger than anything in the title matches
		dfBooksMatchesRow = pandas.DataFrame( {'MatchedTitle': [ dfBSNMatch['BookAlpha'] ],
																																										'MatchIndex': [ iMaxIndex ],
																																										'Category': [ vCategories[iCatID-1] ],
																																										'CategoryID': [ iCatID ],
																																										'Score': [ iMaxScore ]} )
		dfBooksMatches = dfBooksMatches.append(dfBooksMatchesRow, ignore_index=True)
	
	else:
		# Compare the title in the book entry to the titles column in the sheet 
		# and find the best match
	#	vSumRow = [0]*nSheet
		vSumRow = [0]*nBooks
		for iSheet, strSheetTitle in (enumerate(vSheetTitles)):
			iMaxLen = min( len(strTitle), len(strSheetTitle) )
			vSumRow[iSheet] = iMaxLen
			for i in range(1,iMaxLen):
				if not strTitle[:i] == strSheetTitle[:i]:
					vSumRow[iSheet] = i
					break
		
		
		iMaxScore = max(vSumRow)
		vMaxIndices = [i for i, iValue in enumerate(vSumRow) if iValue == iMaxScore]
		iMaxIndex = vMaxIndices[0]
	#	print(vMaxIndices)
		iCatID = dfBooks['CategoryID'].iloc[iMaxIndex]
		
		# Use score 10 as threshold for adding
		if iMaxScore >= 10:
			dfBooksMatchesRow = pandas.DataFrame( {'MatchedTitle': [ dfBooks['BookAlpha'].iloc[iMaxIndex] ],
																																											'MatchIndex': [ iMaxIndex ],
																																											'Category': [ vCategories[iCatID-1] ],
																																											'CategoryID': [ iCatID ],
																																											'Score': [ iMaxScore ]} )
		else:
			dfBooksMatchesRow = pandas.DataFrame( {'MatchedTitle': [ '' ],
																																											'MatchIndex': [ -1 ],
																																											'Category': [ '' ],
																																											'CategoryID': [ -1 ],
																																											'Score': [ iMaxScore ]} )
		dfBooksMatches = dfBooksMatches.append(dfBooksMatchesRow, ignore_index=True)
		
																																								

#%% Join the new link dataframe with the old

dfSheetToBooks = dfSheet.join(dfBooksMatches)

#%% Count number of matches

df = dfSheetToBooks.query('`Score` >= 10')

print( 'Percent matched entries: %0.2f%%' % (len(df)/len(dfSheetToBooks)*100) )
print( 'Unmatched entries: %i' % (len(dfSheetToBooks) - len(df)) )

#%% Save the new matched dataframe

dfSheetToBooks.to_pickle('books_categories_messy.pkl')
