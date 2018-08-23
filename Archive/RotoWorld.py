#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests	
import pandas as pd
import nameIndex as nm
import nameList as nl

RAW_FILE_NAME = 'RawData\\RWRawData.csv'
DATA_FILE_NAME = 'Data\\RWBlurbs.csv'


def df_from_html(tbl):
	header = tbl.find("thead").find_all("th")
	colNames=[]
	for col in header:
		colNames.append(col.get_text())
	
	df = pd.DataFrame(columns=colNames)
	
	rows = tbl.find("tbody").find_all("tr")
	for row in rows:
		columns = row.find_all("td")
		info=[]
		for col in columns:
			info.append(col.get_text())
		df = df.append(dict(zip(colNames,info)),ignore_index=True)
	print(df)
	return df

def pullBlurbs():

	#nameList = pd.read_csv(nl.dataFile,sep='\t',index_col=0)
	
	url = 'http://www.rotoworld.com/articles/nfl/64532/57/rotopat-fantasy-top-50s'
	try:
		page = requests.get(url)
	except:
		return None
		
	soup =BeautifulSoup(page.content.decode('utf-8','ignore'),'lxml')
	start = soup.find("div",id="artpart")
	position = ""
	df = pd.DataFrame()
	for line in start.findAll("p",dir="ltr")[2:]:
		#print(line.prettify('utf8'))
		strong = line.find("strong")
		if not strong: 
			playerLink = line.find("a")
			player = playerLink.get_text()
			link = playerLink['href']
			text = line.get_text()
			# print(player)
			# print(link)
			# print(text)
			info = {'Player Name':player,'Position':position,'Blurb':text,'Link':link}
			# print(info)
			df = df.append(info,ignore_index=True)
		else:
			positionText = strong.get_text()
			if "RUNNING BACK" in positionText.upper():
				position = "RB"
			elif "RECEIVER" in positionText.upper():
				position = "WR"
			elif "QUARTER" in positionText.upper():
				position = "QB"
			elif "TIGHT" in positionText.upper():
				position = "TE"
			else:
				continue
				
	#print(df)
	df.to_csv(RAW_FILE_NAME,sep = "\t",index=False, encoding='utf-8')
	return df
		
def parseNames(rawData):
	nameList = pd.read_csv(nl.DATA_FILE_NAME,sep = '\t',index_col=0)
	position = rawData['Position'].rename('Position')
	names = rawData['Player Name'].str.split(" ")
	first = names.str[0].rename('First')
	last = names.str[1].rename('Last')
	#suffix = names.str[2].rename('Suffix')
	
	search = first.str[0]+" "+last.str[:3]+" "+position
	search = search.str.upper().str.strip()
	names = pd.DataFrame()
	for s in search:
		name = nameList.loc[(nameList.index.str.find(sub=s)!=-1)]
		if len(name)==0:
			name = pd.DataFrame(columns=names.columns.name, index = [s])
		elif len(name)>1:
			name = name.iloc[0]
			nameList=nameList.drop(name.name)
		else:
			nameList=nameList.drop(name.index)
		names = names.append(name)
	return names.reset_index()

def makeFile():
	
	data = pd.read_csv(RAW_FILE_NAME,sep = '\t',encoding='utf-8')
	data.columns = data.columns.str.strip()
	names = parseNames(data)
	data = pd.concat([data,names[['First','Last','Suffix','Team']]],axis=1)
	data.index = nm.getNameIndex(data)
	data = data[['First','Last','Suffix','Position','Team','Blurb','Link']]
	data = data.loc[data.Team.notnull()]
	data.to_csv(DATA_FILE_NAME,sep="\t",encoding='utf-8')
	return data

def pullPlayerNews(url):
	
	try:
		page = requests.get(url)
	except:
		return None
	
	soup =BeautifulSoup(page.content.decode('utf-8','ignore'),'lxml')
	df = pd.DataFrame()
	for line in soup.findAll("div",class_="playernews"):
		#print(line.prettify('utf8'))
		report = line.find("div",class_="report")
		impact =  line.find("div",class_="impact")
		date = impact.find("span",class_="date")
		
		news = report.get_text()+"\n"+impact.get_text()
		
		info = {'Date':date.get_text(),'News':news}
		df=df.append(info,ignore_index=True)
	return df
	
	

if __name__ == "__main__": makeFile()