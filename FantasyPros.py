import pandas as pd
import numpy as np
import CommonFunctions as cf
import re

RAW_FILE_NAME = 'RawData\\fantasypros_2018_Draft_Overall_Rankings.csv'
DATA_FILE_NAME = 'Data\\fpRanks.csv'

	
def parse_names(data):
	position = data['Pos'].str.extract('([^0-9]+)',expand=False).rename('Position')
	team = data['Team']
	names = data['Overall'].str.split(" ")

	name_list = pd.concat([
			names.str[0].rename('First'),
			names.str[1].rename('Last'),
			names.str[2].rename('Suffix'),
			position,
			team
			]
		,axis=1
		)

	name_list.loc[
		name_list.Position == 'DST',
		['Position']
		] = 'DEF'
	name_list.loc[
		name_list.Position == 'DEF', 
		['Last','First','Suffix']
		] = np.nan

	return name_list
	
def make_file():	
	data = pd.read_csv(RAW_FILE_NAME)
	data.columns = data.columns.str.strip()
	data.index = cf.getNameIndexFromNames(parse_names(data))
	data = data.drop(['Overall','WSID','Pos','Team','Bye','vs. ADP'],axis=1)
	data.to_csv(DATA_FILE_NAME,sep='\t',encoding='utf-8')
	return data
	
if __name__ == "__main__": make_data()

