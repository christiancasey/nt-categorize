#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 15:24:52 2019

@author: christiancasey

This script imports the 
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

#%% Load categories data files

# Basic categories (index corresponds to category number - 1)
with open('categories.dat', 'r') as f:
	vCategories = f.read().split('\n')
	f.close()
nCategories = len(vCategories)

#%% Initialize dataframes


nWords = 20

dfBooks = pandas.read_pickle('books_categories.pkl')

# Get the current data from the CSV file that Gabriel is editing
dfSheet = pandas.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vQJKa50tuO654jw8quDaMRlKJbDIkV3FYQPESrQ60IfspMZQynqs1tEA99x6lNm_L9t8fikw8LdAwY4/pub?gid=1471928200&single=true&output=csv')
# Rename one column because it causes problems for SQL
dfSheet.rename( columns = {'Controlled heading (Pleiades, TGN, LCSH, or FAST)': 'Controlled heading'}, inplace = True)


nBooks = len(dfBooks)
nSheet = len(dfSheet)

#vSheetTitles = dfSheet['Title and author'].str.lower().to_list()
vSheetTitles = dfBooks['BookAlpha'].str.lower().to_list()
vSheetTitles = [ re.sub( r'[^\w]', '', s ) for s in vSheetTitles ]

#%%

dfBooksMatches = pandas.DataFrame(columns = ['MatchedTitle', 'MatchIndex', 'Category', 'CategoryID', 'Score'])


# Loop through each title in the books dataframe and find its best match in the sheet

for iRow in tqdm(range(0, nSheet)):
#	strTitle = dfBooks['BookAlpha'].iloc[iRow].lower().strip()
	strTitle = dfSheet['Title and author'].iloc[iRow].lower().strip()
#	iAuthorStart = strTitle.find(' // ')
#	if(iAuthorStart > 1):
#		strTitle = strTitle[:iAuthorStart-1].strip()
	strTitle = re.sub( r'[^\w]', '', strTitle )
#	strTitle = re.sub( r' \w{1,5} ', ' ', strTitle )
	
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
		
		
		
#		vMatches = FindMatchesInColumn( dfSheet['Title and author'], strWord )
#		vSumRow = [ x + y for x, y in zip(vSumRow, vMatches) ]
	
	
	iMaxScore = max(vSumRow)
	vMaxIndices = [i for i, iValue in enumerate(vSumRow) if iValue == iMaxScore]
	iMaxIndex = vMaxIndices[0]
#	print(vMaxIndices)
	iCatID = dfBooks['CategoryID'].iloc[iMaxIndex]
	
	dfBooksMatchesRow = pandas.DataFrame( {'MatchedTitle': [ dfBooks['BookAlpha'].iloc[iMaxIndex] ],
																																									'MatchIndex': [ iMaxIndex ],
																																									'Category': [ vCategories[iCatID-1] ],
																																									'CategoryID': [ iCatID ],
																																									'Score': [ iMaxScore ]} )
	dfBooksMatches = dfBooksMatches.append(dfBooksMatchesRow, ignore_index=True)
																																								

#	print('\n\n%s\n%s\n' % ('~'*40, strTitle))
#	for i in vMaxIndices:
#		print('|||||')
#		print( vSheetTitles[i] )
#		print()
#	print()
#	print(iMax)
#	vSum.sort(reverse = True)

##%% Join the new link dataframe with the old

dfSheetToBooks = dfSheet.join(dfBooksMatches)

#%%

df = dfSheetToBooks.query('`Score` > 10')#.query( '`CategoryID` == 2' )

df2 = dfSheet['Coordinates'].str.split(',', expand=True)

df[['Latitude', 'Longitude']] = df['Coordinates'].str.split(',', expand=True)
df['Latitude'] = df['Latitude'].str.strip()
df['Longitude'] = df['Longitude'].str.strip()
#df[['First','Last']] = df.Name.str.split(expand=True) 


df2 = df[['Latitude', 'Longitude', 'CategoryID']]
df2.to_csv('EarthTest.csv')
#v=dfSheetToBooks['Score'].to_list()
#w = [ int(x>10) for x in v ]
#sum(w)

#%%
print(vSumRow[2222])


vSheetTitles[1734]


print( vSheetTitles[90] )