import pandas as pd
import numpy as np
import PlayerList as pl
import InjuryReport as ir
import FantasyPros as fp
import ESPN as espn
from sklearn.linear_model import LinearRegression
import RotoWorld as rw
import sys

pd.options.display.max_colwidth=500

DATA_FILE_NAME = 'Data\\ffCheatSheet.csv'

def upsideIndicator(fpData):
	avg = fpData['Avg'].reshape(-1,1)
	stdev = fpData['Std Dev'].reshape(-1,1)
	upsideRaw = pow(stdev,2)/avg
	model = LinearRegression()
	model.fit(avg,upsideRaw)
	exp = model.predict(avg)	
	upside = upsideRaw-exp
	upside = upside.reshape(-1)
	upside= (upside/np.linalg.norm(upside)*100).round()
	#upside = min(max(-10.0,upside),10.0)
	#upside_indicator = avg*(1+upside/100)
	# plt.scatter(avg, upside,  color='black')
	# plt.xticks(())
	# plt.yticks(())
	# plt.show()
	
	
	df = pd.Series(upside,index=fpData.index).rename('Upside')
	return df


def main():
	espnData = espn.make_file()
	espnData = espnData['Rank']
	espnData.name= 'ESPNRank'
	cheatSheet = pl.main(espn.RAW_FILE_NAME,espn.parse_names).drop('Suffix',axis=1)
	cheatSheet = pd.concat([cheatSheet,espnData], axis=1)
	
	fpData = fp.make_file()
	cheatSheetWithFPRanks = cheatSheet.merge(fpData, how="left",left_index=True,right_index=True)
	noDNoK = cheatSheetWithFPRanks.loc[(cheatSheetWithFPRanks.Position !="DEF") 
									   & (cheatSheetWithFPRanks.Position !="K")
									   & (cheatSheetWithFPRanks['Avg'].notnull())]
	upside = upsideIndicator(noDNoK)
	fpData = pd.concat([fpData,upside],axis=1)
	fpData = fpData[['Rank','Upside']]
	fpData.rename(columns={'Rank':'FPRank'},inplace=True)
	cheatSheet = cheatSheet.merge(fpData, how="left",left_index=True,right_index=True)
	
	ir.pull_data()	
	irData = ir.make_file()
	irData = irData[['Returns']]
	irData.rename(columns={'Returns':'Injury Status'},inplace=True)
	cheatSheet = cheatSheet.merge(irData, how="left",left_index=True,right_index=True)
	
	rw.pull_data()
	rwData = rw.makeFile()
	rwData = rwData[['Blurb']]
	rwData.Blurb = rwData.Blurb.str.encode(sys.stdout.encoding,"replace").str.decode(sys.stdout.encoding)
	cheatSheet = cheatSheet.merge(rwData, how="left",left_index=True,right_index=True)

	cheatSheet = cheatSheet.sort_values(by='FPRank')
	
	cheatSheet.to_csv(DATA_FILE_NAME,sep = '\t',encoding='utf-8')
	return cheatSheet
	
if __name__ == "__main__": main()

