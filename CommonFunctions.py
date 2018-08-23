import pandas as pd
import numpy as np

def getNameIndexFromNames(nameList):
	index = nameList.First.str[:1].str.cat([nameList.Last.str[:3],nameList.Position,nameList.Team],sep=" ",na_rep="")
	index = index.str.upper().str.strip()
	index = index.rename('Index')
	return index

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