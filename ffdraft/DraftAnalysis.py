import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

class Analyze():
	def __init__(self,Draft):
		self.draft = Draft
		self.teams = Draft.teams
		self.roster_spots = {'RB':2.5,'WR':2.5,'TE':1,'QB':1,'DEF':0,'K':0} #Used by the draft analysis tool.  Doesn't deal with flex players yet, so I'm sticking in 2.5s for RB and WR.  Not going to try to analyze kickers and def.  Assuming always at replacement value.
		self.roster_size = Draft.roster_size -2 #Subtracting 2 for kickers and def
		self.replacement_level = self.replacement_level_rank()
		self.first_pick_PAR = 5 #how many points above replacement the first pick will get you.  This is just used to level set and make the Points above replacement at the right order of magnitude
		self.trade_value = 0.5 #you can get 50% of a player's utility value if you trade them, so it might be worthwhile to draft an 8th WR if they're good value
		self.vol =0.25
	
	def replacement_level_rank(self):
		return round(self.teams*(self.roster_size)*0.9) 
		
		#translate ranking into points above replacement
	def pick_to_PAR(self,pick):
		rv = self.replacement_level
		fpv = self.first_pick_PAR
		k = np.log(0.99)
		PAR =exponential(pick, fpv, rv, k)
		PAR = max(PAR,0)
		return PAR
	
	
	#make a guess on what % of the season the player will be on your starting roster (and thus provide utility)
	# this is without taking into consideration the other players you drafted, and is only based on their rank
	def prob_startable(self,pick):
		PAR = self.pick_to_PAR(pick)
		marginal = self.pick_to_PAR(sum(self.roster_spots.values())*self.teams)
		util = exponential_2(PAR, self.first_pick_PAR, 0.95,marginal,0.45)
		return util
	
	#This works in tandem with the previous function to determine how likely an additional player is to make the active roster, taking into consideration ateam's other draft picks
	def roster_utility(self,position,r):
		roster = self.draft.get_roster(r)
		spots = self.roster_spots[position]
		util = 0
		for pick in roster.loc[roster.Position==position,'Pick']:
			util += self.prob_startable(pick)
		try: roster_utility = logistic(util,spots-1,0.85,spots,0.2) 
		except: roster_utility = 0
		return roster_utility
		
		#retuns a dictionary of how to adjust a player's rank for each positon
	def utility(self,r):
		util = {}
		for position in self.roster_spots.keys():
			roster_utility = self.roster_utility(position,r)
			trade_utility = (1-roster_utility)*self.trade_value
			utility = roster_utility+trade_utility
			util[position] = round(utility,2)
		return util

#get the upside of a set of players given their average and standard deviation

def upsideIndicator(avg: pd.Series,stdev: pd.Series):
	avgArr = avg.reshape(-1,1)
	stdevArr = stdev.reshape(-1,1)
	upsideRaw = pow(stdevArr,2)/avgArr
	model = LinearRegression()
	model.fit(avgArr,upsideRaw)
	exp = model.predict(avgArr)	
	upside = upsideRaw-exp
	upside = upside.reshape(-1)
	upside= (upside/np.linalg.norm(upside)*100).round()
	return pd.Series(upside,index=avg.index).rename('Upside')
#some math functions used for the stats above
	
def logistic(x,x1,y1,x2,y2):
	g1 = np.log(y1/(1-y1))
	g2 = np.log(y2/(1-y2))
	b = (g2-g1)/(x2-x1)
	a = g1-b*x1
	return np.exp(a+b*x)/(1+np.exp(a+b*x))

def exponential(x,y_intercept,x_intercept,k):
	return -y_intercept*np.exp(k*x_intercept)/(np.exp(k*x_intercept)-1)*np.exp(k*(x-x_intercept-1))+y_intercept/(np.exp(k*x_intercept)-1)+y_intercept

def exponential_2(x,x1,y1,x2,y2):
	k=np.log(y2/y1)/(x2-x1)
	a = y1/np.exp(k*x1)
	return a*np.exp(k*x)


