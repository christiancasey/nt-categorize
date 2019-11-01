import pandas as pd

import urllib
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy import create_engine


#%% Get the current data from the CSV file that Gabriel is editing
nt = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vQJKa50tuO654jw8quDaMRlKJbDIkV3FYQPESrQ60IfspMZQynqs1tEA99x6lNm_L9t8fikw8LdAwY4/pub?gid=1471928200&single=true&output=csv')

# Rename one column because it causes problems for SQL
nt.rename( columns = {'Controlled heading (Pleiades, TGN, LCSH, or FAST)': 'Controlled heading'}, inplace = True)


#%% Delete the existing old_data table and replace it with the new data from the CSV

# Drop the old table
psqlConn = psycopg2.connect("dbname=newtitles user=postgres password=postgres")
psqlConn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
psqlCursor = psqlConn.cursor()
psqlCursor.execute('DROP TABLE IF EXISTS old_data;')
psqlCursor.close()
psqlConn.close()

# Create a new table with CSV data
engine = create_engine('postgresql://postgres:postgres@localhost:5432/newtitles')
nt.to_sql('old_data', engine)


#%%
vTitles = nt['Title and author'].str.strip()
print(vTitles)

#%% Categorize using Naive Bayes -- Come  back  to this
#from categorize_nt import predict_categories
#predict_categories(vTitles) 

# Go through pages and link categories to book info
# Match up book info from pages with info in the dataframe
# Create a new column with category values

v = None


psqlConn = psycopg2.connect("dbname=newtitles user=postgres password=postgres")
psqlConn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT);
psqlCursor = psqlConn.cursor()
psqlCursor.execute('SELECT * FROM old_data;')
v = psqlCursor.fetchall()
psqlCursor.close()
psqlConn.close()
















