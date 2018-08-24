#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests	
import pandas as pd
import CommonFunctions as cf
import PlayerList as pl
import re

RAW_FILE_NAME = 'RawData\\RWRawData.csv'
DATA_FILE_NAME = 'Data\\RWBlurbs.csv'



def pull_data():
	url1 = 'http://www.rotoworld.com/articles/nfl/81539/57/silvas-preseason-top-150'
	url2 = 'http://www.rotoworld.com/articles/nfl/81539/57/silvas-preseason-top-150?pg=2'
	try:
		page1 = requests.get(url1)
		page2 = requests.get(url2)
	except:
		return None
    
	soup = BeautifulSoup(page1.content.decode('utf-8','ignore'),'lxml')
	playerHTMLBlock1_1 = soup.find("div",id="artpart").findAll("p")[2]
	playerHTMLSplitIntoParagraphs1_1 = BeautifulSoup(str(playerHTMLBlock1_1).replace("<br/> ","</p> <p>"),'lxml').findAll("p")
	playerHTMLBlock1_2 = soup.find("div",id="artpart").findAll("p")[6]
	playerHTMLSplitIntoParagraphs1_2 = BeautifulSoup(str(playerHTMLBlock1_2).replace("<br/> ","</p> <p>"),'lxml').findAll("p")
	soup2 =BeautifulSoup(page2.content.decode('utf-8','ignore'),'lxml')
	playerHTMLBlock2 = soup2.find("div",id="artpart").findAll("p")[0]
	playerHTMLSplitIntoParagraphs2 = BeautifulSoup(str(playerHTMLBlock2).replace("<br/> ","</p> <p>"),'lxml').findAll("p")[1:]
	df = parseRotoworldBlock(playerHTMLSplitIntoParagraphs1_1 + playerHTMLSplitIntoParagraphs1_2 + playerHTMLSplitIntoParagraphs2)

	df.to_csv(RAW_FILE_NAME,sep = "\t",index=False, encoding='utf-8')
	return df
		
def parseRotoworldBlock(playerHTMLSplitIntoParagraphs):
	df = pd.DataFrame()
	for line in playerHTMLSplitIntoParagraphs: 
		playerLink = line.find("a")
		if playerLink is None :
			player = line.find("strong").get_text() 
			link = ""
		else :
			player = playerLink.get_text()
			link = playerLink['href']
		text = line.get_text()
		position = re.search('(?<=[(])\D+(?=\d+[)])',text).group(0)
		blurb = re.search('(?<= – ).*',text).group(0)
		info = {'Player Name':player,'Position':position,'Blurb':blurb,'Link':link}
		df = df.append(info,ignore_index=True)
	return df
	
		
def parse_names(rawData):
	nameList = pd.read_csv(pl.DATA_FILE_NAME,sep = '\t',index_col=0)
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
	names = parse_names(data)
	data = pd.concat([data,names[['First','Last','Suffix','Team']]],axis=1)
	data.index = cf.getNameIndexFromNames(data)
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