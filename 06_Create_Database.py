#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 16:49:43 2019

@author: christiancasey

This script uses the saved dataframe to create the `Books` table in the `New Titles` database
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

#%% Initialize dataframes
df = pandas.read_pickle('books_categories.pkl')


