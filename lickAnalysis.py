####################################
## FUNCTIONS
####################################

import pandas as  pd
import glob
import os
import scipy.io
import logging

def quickConversion(tmp, myCol=None):
    tmp = tmp.reset_index()
    if tmp.columns.nlevels > 1:
        tmp.columns = ['_'.join(col) for col in tmp.columns] 
    tmp.columns = tmp.columns.str.replace('[_]','')
    if myCol:
        tmp = tmp.rename(columns={np.nan: myCol})
    return tmp

class matExtraction:

	def __init__(self, matfileName):
		self.filename_mat = matfileName
		self.sID = matfileName.split(os.sep)[-3]
		self.session = matfileName.split(os.sep)[-2]
		self.filenamepd = glob.glob(os.path.dirname(matfileName)+os.sep+'*.csv')[0]
		self.geno = 'toget' ## TODO add genotype and combination with genotype

	def extractMatfile(self):
		'''
		definition to extract the matrix to be able to read the mat file and have a workable output
		on the matfile
		'''
		mat = scipy.io.loadmat(self.filename_mat, mat_dtype=False)
		mat = list(mat.items())
		mat = mat[-1][-1]

		allDat = []
		for i in range(len(mat)):
			# print(i)
			tmp = pd.DataFrame(mat[i][-1])
			tmp = tmp.iloc[:,:-2]
			tmp.columns = ["state.mat1","lick.trigg","time.s","state.mat2"]
			tmp["Trial"] = i+1
			tmp["trial.total.per.session"] = len(tmp)
			allDat.append(tmp)
		allDat = pd.concat(allDat)

		return allDat

	def combineFiles(self):
		'''
		reading of the corresponding csv file giving the output if correct or not
		'''
		tmp = pd.read_csv(self.filenamepd)
		matflo = self.extractMatfile()
		dat = pd.merge(matflo, tmp, on='Trial')
		dat['sID'] = self.sID
		dat['session'] = self.session

		### get the category 
		### --------------------------------------------------------------------------
		dat.loc[(dat['GoNoGo']==1) & (dat['Correct']==1), 'category'] = 'Hit'
		dat.loc[(dat['GoNoGo']==1) & (dat['Correct']==0), 'category'] = 'Miss'
		dat.loc[(dat['GoNoGo']==0) & (dat['Correct']==0), 'category'] = 'FA'
		dat.loc[(dat['GoNoGo']==0) & (dat['Correct']==1), 'category'] = 'CR'

		return dat

	def getResponseTime(self):

		'''
		Function to exclusively get the response time
		'''

		dat = self.combineFiles()

		### response time start
		###----------------------------------------------------------------------------
		resp = dat.loc[(dat['state.mat1']==7) & (dat['state.mat2']==8), ['sID','session','Trial', 'time.s', 'category']]
		resp.rename(columns = {'time.s':'timeStart'}, inplace = True)

		respEnd = dat.loc[(dat['state.mat1']==8) & (dat['state.mat2']==9) & (dat['lick.trigg']==1), ['sID','session','Trial', 'time.s']]
		respEnd.rename(columns = {'time.s':'timeEnd'}, inplace = True)

		respTime = pd.merge(resp, respEnd, on=['sID','Trial','session'])
		respTime['respTime'] = respTime['timeEnd']-respTime['timeStart']

		return respTime

	def getTheLickCount(self):
		### the table can be simplified
		### in the state matrix only the lick.trigg == 1 corresponds to lick

		dat = self.combineFiles()
		dat = dat[dat['lick.trigg']==1]

		### custom dat category based on the definition of pre and post
		dat.loc[(dat['state.mat1']>=3) & (dat['state.mat1']<=5), 'stateCategory'] = 'pre'
		## there are issue with the 0 see
		 ### 'Y:\\Sheldon\\pole_localization\\.PoleLocalization001\\PoleLocalization_coh1_licks\\1035\\20220901\\202291122147.mat'
		 ## trial 142
		dat.loc[(dat['state.mat1']==1) | (dat['state.mat1']==2) | (dat['state.mat1']==11), 'stateCategory'] = 'post'
		dat.loc[(dat['state.mat1']==10), 'stateCategory'] = 'drinking'

		### get the lick count information
		dat = dat[['sID', 'session', 'Trial', 'category', 'stateCategory']]
		summary = dat.groupby(['sID', 'session', 'Trial', 'category', 'stateCategory']).agg({'Trial':['count']})
		summary = quickConversion(summary)

		return summary

		### get the lick interval by category
		### can think of adding this if it may be relevant/useful

####################################
## INPUT
####################################

# get the files from the main folder
mpath = r'Y:\Sheldon\pole_localization\.PoleLocalization001\PoleLocalization_coh1_licks'
allFiles = glob.glob(mpath+'/**/*.mat', recursive = True)

# check for error and duplicates 
# the destination folder needs to be specified
fullList = [x.split(os.sep)[-3]+os.sep+x.split(os.sep)[-2] for x in allFiles]
duplicates = [x for x in fullList if fullList.count(x) > 1]
pd.DataFrame(duplicates).to_csv(r'C:\git\WDIL_lick\output'+os.sep+'duplicates.csv')

## create a log file for error during the loop
logging.basicConfig(filename=r'C:\git\WDIL_lick\output\lick.log', filemode='w', level=logging.INFO)


#### combine this for all the files
allrespTime = []
allLickCount = []

for i,j in enumerate(allFiles):
	print(str(i)+'/'+str(len(allFiles)))
	print(j)

	try:
		t = matExtraction(j)
		tmpART = t.getResponseTime()
		tmpALC = t.getTheLickCount()

		allrespTime.append(tmpART)
		allLickCount.append(tmpALC)
	except:
		logging.info(j)

allrespTime = pd.concat(allrespTime)
allLickCount = pd.concat(allLickCount)

## save data to specific destination folder
allrespTime.to_csv(r'C:\git\WDIL_lick\output'+os.sep+'respTime.csv')
allLickCount.to_csv(r'C:\git\WDIL_lick\output'+os.sep+'lickCount.csv')


### TROUBLESHOOTING
'''
allLickCount[allLickCount['Trialcount']>20]

[x for x in allFiles if '20220829' in x]

t = matExtraction(j)
a = t.extractMatfile()
a.to_csv(r'C:\git\WDIL_lick\output'+os.sep+'troubleShoot.csv')'''