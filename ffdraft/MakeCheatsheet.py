import pandas as pd
import numpy as np
import PlayerList as pl
import InjuryReport as ir
import FantasyPros as fp
import ESPN as espn
import DraftAnalysis as da
import RotoWorld as rw
import sys

DATA_FILE_NAME = 'Data\\ffCheatSheet.csv'

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
	upside = da.upsideIndicator(avg = noDNoK['Avg'],stdev = noDNoK['Std Dev'])
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

