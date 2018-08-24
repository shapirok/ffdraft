import sys
import numpy as np
import pandas as pd
import Draft as d
import RotoWorld as rw
from numpy import rank
from IPython.display import clear_output
from threading import Thread

class ConsoleDraftRunner():
	def __init__(self, draft,runContinuous=False):
		self.draft=draft
		self.run(runContinuous)
		#Thread.__init__(self)
		#self.start()
		
	def run(self,runContinuous):
		result = ""
		while True:
			user_input = input("Input (C=CheatSheet,D=Draft,\n\tU=Undo,Q=Quit,P=Picks,R=Roster,N=News):").upper().strip()
			result = self.parse_user_input(user_input)
			clear_output()
			print(result)
			if (str(result).strip() == "Quit") | (runContinuous ==False):
				break
		return None
			
	def parse_user_input(self,user_input):
		draft = self.draft
		try:
			option = user_input[0]
			ext = user_input[2:]
			if option == "Q":
				result = "Quit"
			elif option == "P":
				result = draft.get_picks()
			elif option =="R":
				if not ext:
					r = draft.my_pick
				else:
					r = int(ext)
				result = draft.get_roster(r)
			elif option == "C":
				result = draft.get_cheatsheet(ext,20)
			elif option == "A":
				result = draft.utility_adjusted_cheatsheet('FPRank',draft.my_pick)[:20].reset_index(drop=True)
			elif option =="D":
				i = getCorrectName(ext,draft.undrafted_players())
				if i is not None:
					name = draft.add_player(i)
					if name.Roster == draft.my_pick :
						result = "Added "+ name['First']+" " + name['Last']+" " + name['Position']+" " + name['Team']+" to your roster, pick " + str(name['Pick'])
					else:
						result = "Team " + str(name['Roster']) +" added "+ name['First']+" " + name['Last']+" " + name['Position']+" " + name['Team']+", pick " + str(name['Pick'])
				else: 
					result = "No player found"
			elif option == "U":
				if draft.draftList.empty:
					result = "No picks made"
				else:
					if not ext:
						pick= max(draft.draftList.Pick)+1
						i = draft.draftList.loc[draft.draftList.Pick==(pick-1)].index.values[0]
					else:
						i=getCorrectName(ext,draft.draftList)
					if i is not None:
						name = draft.undo_pick(i)
						result = "Undid draft back to "+name.First+" " + name.Last+" " + name.Position+" " + name.Team
					else:
						result = "No player found"
			elif option =="I":
				i = getCorrectName(ext,draft.playerList)
				if i is not None:
					result=""
					try:
						result += draft.rotoWorld.loc[i,"Blurb"]
						result += "\n\n" 
					except:
						result += ""
					try:
						result +=draft.injuryReport.loc[i,"Summary"]
					except:
						result+=""
				else: 
					result = "No player found"
			elif option == "N":
				i = getCorrectName(ext,draft.playerList.loc[draft.rotoWorld.loc[draft.rotoWorld.Link.notnull()].index])
				if i is not None:
					url = draft.rotoWorld.loc[i,"Link"]
					news = rw.pullPlayerNews(url)
					result = ""
					for j,n in news.iterrows():
						result+=n.Date +"\n"
						result+=n.News+"\n"+"\n"
				else: 
					result = "No player found"
			else: 
				result = "Invalid command"
		except Exception as e: result = "Got an error for command " + user_input  + ": " +str(e)
		if isinstance(result,str):
			result = "\n"+result+"\n\n"
			result = result.encode(sys.stdout.encoding,"replace").decode(sys.stdout.encoding)
		else: 
			result = result	
		draft.save_draft()
		return result


def getCorrectName(s, nameList):
	if not s:
		return None
	matches = nameList.loc[nameList.index.str.contains(s)]
	if len(matches) ==0:
		return None
	elif len(matches) == 1:
		return matches.index.values[0]
	else:
		for i,name in matches.iterrows():
			option = "\nDid you mean "+ name['First']+" " + name['Last']+" " + name['Position']+" " + name['Team'] + "(Y/N)?"
			user_input = input(option)
			if user_input.upper() == "Y":
				return i
	return None


def main():
	return ConsoleDraftRunner(dr.main())
	
if __name__ == "__main__": main()
