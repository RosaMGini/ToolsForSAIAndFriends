import sys

sys.path.append('') # indicate the path of the toolsKataGoAnalysisEngine.py file
from toolsKataGoAnalysisEngine import sgf2list
from toolsKataGoAnalysisEngine import sgf2text
from toolsKataGoAnalysisEngine import interfaceKataGoAnalysisEngine


fileSGF = '' # name of a sgf file
numTurn = 2 # turn that you want to be analysed
model = '' # a KataGo net
KGengine = '' # the KataGo engine (must be 1.4.2 or higher)
config = 'analysis_example.cfg' # a configuration file for the KataGoEngine

REFEREE = interfaceKataGoAnalysisEngine(KGengine,model,config,'-analysis-threads 1' )
result=REFEREE.analyse_sgf(fileSGF,numTurn,'test_id',7.5,"tromp-taylor","WHITE")
print('At turn',result['turnNumber'],'winrate is estimated to be',result['rootInfo']['winrate'], 'with score',result['rootInfo']['scoreLead'])
