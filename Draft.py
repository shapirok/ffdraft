import sys
import numpy as np
import pandas as pd
import RotoWorld as rw
import MakeCheatsheet as cs
import InjuryReport as ir
import PlayerList as pl
import DraftAnalysis as da
from numpy import rank
from IPython.display import clear_output

class Draft():
	def __init__(self, draftFile=None,teams = 12, roster_size=15,my_pick = 2):
		if draftFile == None:
			draftFile= "testdraft.csv"
			draftList = pd.read_csv( pl.DATA_FILE_NAME, sep= "\t", index_col	=0)[['First','Last','Position','Team']]
			draftList.columns = draftList.columns.str.strip()
			draftList["Pick"] = np.NaN
			draftList["Roster"] = np.NaN
			draftList
		else:
			draftList = pd.read_csv("Drafts\\"+draftFile, sep= "\t", index_col	=0)
		self.draftFile= draftFile
		self.draftList = draftList
		self.teams = max(1,teams)
		self.my_pick =min(max(1,my_pick),teams)
		self.roster_size = max(1,roster_size)
		self.cheatSheet = pd.read_csv(cs.DATA_FILE_NAME,sep = '\t',index_col=0)
		self.injuryReport = pd.read_csv(ir.DATA_FILE_NAME,sep = '\t',index_col = 0)
		self.rotoWorld = pd.read_csv(rw.DATA_FILE_NAME,sep = '\t',index_col = 0)
		self.save_draft()
		
	def add_player(self,index):
		pick =  sum(self.draftList.Pick.notnull())+1
		team = snake_order(pick,self.teams)
		self.draftList.loc[index,'Pick'] = pick
		self.draftList.loc[index,'Roster'] = team
		return self.draftList.loc[index]

	def undo_pick(self,index):
		name = self.draftList.loc[index]
		self.draftList.loc[self.draftList.Pick>=name.Pick,"Roster"] =np.NaN
		self.draftList.loc[self.draftList.Pick>=name.Pick,"Pick"] =np.NaN
		return self.draftList.loc[index]
		
	def get_roster(self,team):
		roster = self.draftList.loc[self.draftList.Roster==team]
		return roster.sort_values(by=["Position","Pick"]).reset_index(drop=True)

	def get_cheatsheet(self,position = None,l=20):
		if not position:
			remaining = self.cheatSheet.loc[self.draftList.Pick.isnull()]
		else:
			remaining = self.cheatSheet.loc[(self.draftList.Pick.isnull()) & (self.draftList.Position==position)]
		return remaining.sort_values(by=["FPRank"])[:l].reset_index(drop=True)
	
	def utility_adjusted_cheatsheet(self,ranking='FPRank',r = None):
		if not r: r = self.my_pick
		cs = self.cheatSheet.loc[self.draftList.Pick.isnull()]
		stripped = cs[['Position',ranking]].rename(columns={ranking:'Rank'})
		util_adjust = self.util_adjust(r,stripped)
		return pd.concat([cs,util_adjust],axis=1).sort_values(by=util_adjust.name)
		
	def get_picks(self):
		picked = self.draftList.loc[self.draftList.Pick.notnull()]
		return picked.sort_values(by=["Pick"]).reset_index(drop=True)
	
	def auto_draft(self,spotsToAutoDraft,rankingColumnToUse):
		for i in range(1,spotsToAutoDraft):
			roster = snake_order(i, self.teams)
			cs = self.utility_adjusted_cheatsheet(ranking=rankingColumnToUse, r=roster).sort_values(by='UtilRank')
			i = cs.index[0]
			self.add_player(i)
		self.save_draft()
		return self.get_picks().iloc[::-1][:spotsToAutoDraft-1].iloc[::-1]
	
	def save_draft(self):
		self.draftList.to_csv('Drafts\\'+self.draftFile,sep = '\t')
	
	def Analyze(self):
		return da.Analyze(self)
	
	def util_adjust(self,r,cs):
		a = self.Analyze()
		utility = a.utility(r)
		adjRank = pd.Series(index = cs.index, name = 'UtilRank')
		for i,p in cs.iterrows():
			rank = a.pick_to_PAR(p.Rank)
			adj =utility[p.Position] 
			arank = adj*rank
			if np.isnan(arank): arank = 0
			adjRank[i] = arank
		adjRanks = adjRank.rank(axis=0,method='first',ascending=False,na_option = 'top')
		return adjRanks
			
	
def snake_order(p,n):
	pick = ((p-1) % n)+1
	rnd = (p-pick)/n+1
	d = rnd%2
	if d: 
		roster = pick
	else:
		roster = n-pick+1
	return roster

def main():
	return Draft('csreporting.csv',10,16,1)
	
if __name__ == "__main__": main()
