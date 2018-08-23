from bs4 import BeautifulSoup
import requests	
import numpy as np
import pandas as pd
import CommonFunctions as cf

RAW_FILE_NAME  = 'RawData\\ESPNRawdata.csv'
DATA_FILE_NAME  = 'Data\\ESPNRanks.csv'

def pull_data():
	page = requests.get('http://www.espn.com/fantasy/football/story/_/page/18RanksPreseason300nonPPR/2018-fantasy-football-non-ppr-rankings-top-300')

	soup =BeautifulSoup(page.content,'lxml')

	for caption in soup.findAll("h2"):
		if "Top-300 Non-PPR Rankings For 2018" in caption.text:      
			break
	tbl = caption.parent

	reportDF = cf.df_from_html(tbl)
	reportDF.to_csv(RAW_FILE_NAME,sep = "\t",index=False)
	return reportDF
		
def parse_names(rawData):
	position = rawData['Pos'].rename('Position')
	team = rawData['Team'].rename('Team')
	names = rawData['Rank, Player'].str.split(" ")
	rank = names.str[0].str.extract('([0-9]+)',expand=False).rename('Rank')
	first = names.str[1].rename('First')
	last = names.str[2].rename('Last')
	suffix = names.str[3].rename('Suffix')

	nameList = pd.concat([first,last,suffix,position,team,rank],axis=1)

	nameList.loc[nameList.Position == 'DST', ['Position']] = 'DEF'
	nameList.loc[nameList.Position == 'DEF', ['Last']] = np.nan
	nameList.loc[nameList.Position == 'DEF', ['First','Suffix']] = np.nan
	return nameList

def make_file():	
	data = pd.read_csv(RAW_FILE_NAME,sep = '\t', encoding='utf-8')
	data.columns = data.columns.str.strip()
	data = pd.concat([data,parse_names(data)[['First','Last','Suffix','Position','Rank']]],axis=1)
	data.index = cf.getNameIndexFromNames(parse_names(data))
	data = data[['First','Last','Suffix','Position','Team','Rank']]
	data.to_csv(DATA_FILE_NAME,sep="\t")
	return data
		

if __name__ == "__main__": makeFile()


			
			
			
		
		
		
		
	
	
