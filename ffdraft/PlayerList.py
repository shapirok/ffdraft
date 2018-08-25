import pandas as pd
import CommonFunctions as cf
import ESPN as intake

DATA_FILE_NAME = 'Data/nameList.csv'

def main(rawFile= intake.RAW_FILE_NAME,parser=intake.parse_names):
	rawData = pd.read_csv(rawFile,sep = '\t')
	rawData.columns = rawData.columns.str.strip()
	nameList = parser(rawData)[['First','Last','Suffix','Team','Position']]
	nameList.index = cf.getNameIndexFromNames(nameList)
	nameList.to_csv(DATA_FILE_NAME,sep = '\t')
	return nameList






