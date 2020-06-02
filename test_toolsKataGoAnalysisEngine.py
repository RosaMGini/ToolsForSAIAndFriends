import sys

sys.path.append('') # indicate the path of the toolsKataGoAnalysisEngine.py file
from toolsKataGoAnalysisEngine import sgf2list
from toolsKataGoAnalysisEngine import sgf2text
from toolsKataGoAnalysisEngine import interfaceKataGoAnalysisEngine

model = '' # a KataGo net
KGengine = '' # the KataGo engine (must be 1.4.2 or higher)
config = 'analysis_example.cfg' # a configuration file for the KataGoEngine

REFEREE = interfaceKataGoAnalysisEngine(KGengine,model,config,'-analysis-threads 1' )

# TYPICAL USAGE OF LOW-LEVEL METHOD launchQueryAndReturn()
line='{"id":"foo","initialStones":[["B","Q4"],["B","C4"]],"moves":[["W","P5"],["B","P6"]],"rules":"tromp-taylor","komi":7.5,"boardXSize":19,"boardYSize":19,"analyzeTurns":[2]}'
result=REFEREE.launchQueryAndReturn(line)
print('At turn',result['turnNumber'],'winrate is estimated to be',result['rootInfo']['winrate'], 'with score',result['rootInfo']['scoreLead'])

# TYPICAL USAGE OF METHOD analyse_listOfLists()
list_of_lists=[["W","P5"],["B","P6"]]
result=REFEREE.analyse_listOfLists(list_of_lists,2,'test_id',7.5,"tromp-taylor","WHITE")
print('At turn',result['turnNumber'],'winrate is estimated to be',result['rootInfo']['winrate'], 'with score',result['rootInfo']['scoreLead'])

# TYPICAL USAGE OF METHOD analyse_sgf()
fileSGF = '' # name of a sgf file
numTurn = 2 # turn that you want to be analysed in the sgf file 
result=REFEREE.analyse_sgf(fileSGF,numTurn,'test_id',7.5,"tromp-taylor","WHITE")
print('At turn',result['turnNumber'],'winrate is estimated to be',result['rootInfo']['winrate'], 'with score',result['rootInfo']['scoreLead'])