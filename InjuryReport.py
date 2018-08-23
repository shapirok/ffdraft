import requests	
import pandas as pd
from bs4 import BeautifulSoup
import CommonFunctions as cf

URL = 'http://www.rotoworld.com/teams/injuries/nfl/all/'
RAW_FILE_NAME = 'RawData\\injuryreportraw.csv'
DATA_FILE_NAME = 'Data\\injuryreport.csv'

def df_from_html(tbl):
	rows = tbl.find_all('tr')
	header = rows[0].find_all('td')
	col_names=[]
	for col in header:
		col_names.append(col.get_text())
	col_names[1]='Summary'
	df = pd.DataFrame(columns=col_names)
	for row in rows[1:]:
		columns = row.find_all('td')
		info=[]
		for col in columns:
			info.append(col.get_text())
		df = df.append(dict(zip(col_names,info)),ignore_index=True)
	return df

def pull_data():
	try:
		page = requests.get(URL)
	except:
		return None
	soup =BeautifulSoup(page.content,'lxml')
	injury_report = soup.find('div', id = 'cp1_pnlInjuries')
	teams = injury_report.find_all('div',class_ = 'pb')
	df = pd.DataFrame()
	for team in teams:
		team_name = team.find('div', class_ = 'player').get_text()
		tbl = team.find('table')
		df_tmp = df_from_html(tbl)
		df_tmp['Team']=team_name
		df = df.append(df_tmp)
	df.to_csv(RAW_FILE_NAME,sep = '\t',index=False, encoding='utf-8')
	
	
def parse_names(data):
	team_data = pd.read_csv('Data\\Teams.csv',sep='\t')
	data = data.merge(team_data,how='left',left_on = 'Team',right_on='Teamname')
	position = data['POS'].str.extract('([^0-9]+)',expand=False)
	team = data['Shortname']
	player_name = data['Name'].str.split(' ')
	name_list = pd.concat(
		[
		player_name.str[0].rename('First'),
		player_name.str[1].rename('Last'),
		player_name.str[2].rename('Suffix'),
		position.rename('Position'),
		team.rename('Team')
		],
		axis=1
		)
	return name_list

def make_file():	
	
	data = pd.read_csv(RAW_FILE_NAME,sep = '\t',encoding='utf-8')
	data.columns = data.columns.str.strip()
	data.index = cf.getNameIndexFromNames(parse_names(data))
	data = data[['Status','Date','Returns','Summary']]
	data.to_csv(DATA_FILE_NAME,sep='\t', encoding='utf-8')
	return data
		
if __name__ == '__main__': make_file()


			
			
			
		
		
		
		
	
	
