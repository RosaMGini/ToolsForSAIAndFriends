# version 1.1
#

import os
import subprocess
from sgfmill import sgf_grammar
from sgfmill import sgf_moves
from sgfmill import sgf
import sgfmill
import json

def sgf2listOfLists(sgf_file):
    """From the input sgf file named -sgf_file- sgf2list returns the moves as a Python list of lists, each containing a position in the format [Color, vertex], e.g. [["W","P5"],["B","P6"]] """
    SGFstring = ''
    with open(sgf_file,"r") as myfile:
        SGFstring = myfile.read().replace('\n','')
    SGFobject = sgf.Sgf_game.from_string(SGFstring)
    moves=sgf_moves.get_setup_and_moves(SGFobject)[1]
    listmoves=[]
    for move in moves:
        Color=move[0].upper()
        vertex=sgfmill.common.format_vertex(move[1])
        list=[Color,vertex]
        listmoves.append(list)
    return listmoves

def sgf2list(sgf_file):
    """From the input sgf file named -sgf_file- sgf2list returns the moves as a Python list of strings, each containing a position in the format ["Color", "vertex"], e.g. ['["W","P5"]','["B","P6"]'] """
    SGFstring = ''
    with open(sgf_file,"r") as myfile:
        SGFstring = myfile.read().replace('\n','')
    SGFobject = sgf.Sgf_game.from_string(SGFstring)
    moves=sgf_moves.get_setup_and_moves(SGFobject)[1]
    listmoves=[]
    for move in moves:
        Color=move[0].upper()
        vertex=sgfmill.common.format_vertex(move[1])
        listmoves.append('["'+Color+'","'+vertex+'"]')
    return listmoves

def sgf2text(sgf_file):
    """From the input sgf file named -sgf_file- sgf2text returns the moves as a string in the format ["Color", "vertex"], e.g. '["W","P5"],["B","P6"]' """
    listmoves = sgf2list(sgf_file)
    stringmoves = ','.join(listmoves)
    return stringmoves

def sgf2board_size(sgf_file):
    """From the input sgf file named -sgf_file- sgf2board_size returns the boardsize"""
    SGFstring = ''
    with open(sgf_file,"r") as myfile:
        SGFstring = myfile.read().replace('\n','')
    SGFobject = sgf.Sgf_game.from_string(SGFstring)
    board_size = SGFobject.get_size()
    return board_size

class interfaceKataGoAnalysisEngine:
    """
    interfaceKataGoAnalysisEngine is a class that supports interaction between the analysis engine of KataGo and Python. Reference for the analysis engine of KataGo: https://github.com/lightvector/KataGo/blob/master/docs/Analysis_Engine.md

    Authors: Rosa Gini, Maurizio Parton
    Date: 24 May 2020
    Version: 1.1
    changelog: added method analyse_list_of_moves
    
    Args: 
        KGengine: the string that launches the local KataGo engine
        model: the pathway to the net that is to be used
        configFile: the configuration file for the analysis engine
        other: a string of additional commands


    Attributes:
        KGProcess: an instance of subprocess.Popen()
   
    """
    #constructor
    def __init__(self,KGengine,model,configFile,other):
        lineKG= KGengine+' analysis -model '+model+' -config '+ configFile +' '+other
        print('opening process of katago with command:',lineKG,'\n')
        self.KGProcess=subprocess.Popen(lineKG,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,universal_newlines=True,shell=True,bufsize=0)
        
    # info to be printed
    def __str__(self):
        return "KataGo Analysis Engine using net " + model + "with config file " + configFile + " and parameters " + other +'\n'

    # method invoking KataGo with a json line and returning the result as a dictionary
    def launchQueryAndReturn(self,line):
        """
        launchQueryAndReturn is a method launching a query in KataGo's analysis engine and returning the result as a dictionary; only works if the line is correctly formatted, but does not check for this; the dictionary contains the result of the analysis of the first turn only

        Args: 
            line (str): a JSON line formatted for KataGo's analysis engine: format is documented in the engine documentation https://github.com/lightvector/KataGo/blob/v1.4.0/docs/Analysis_Engine.md

        Returns:
            the Python dictionary of the JSON response from KataGo's analysis engine: format is documented in the engine documentation https://github.com/lightvector/KataGo/blob/v1.4.0/docs/Analysis_Engine.md

        Throws:
            nothing
            
        """
        line=line+'\n'
        # print('launching the following query',line,'\n\n' )
        self.KGProcess.stdin.write(line)
        self.KGProcess.stdin.flush()
        while True:
            print('...analysing query, please wait...')
            analysis=self.KGProcess.stdout.readline()#[0:-1]
            if len(analysis)>1:
                break
        analysisJSON= analysis
        analysisPYTHON=json.loads(analysisJSON)
        print('the analysis is completed\n\n')
        return(analysisPYTHON)
    
    # method analysing a sgf file and capturing the output
    def analyse_sgf(self,sgf_file,turnToBeAnalysed,id,komi,rules,COLOR):
        """
        analyse_sgf is a method analysing the turn -turnToBeAnalysed- of the moves contained in the sgf file -sgf_file-. The moves are considered to be part of a game played with komi -komi- and rules -rules-. The analysis is conducted from the point of view of -COLOR-

        Args: 
            sgf_file (str): name of the sgf file
            turnToBeAnalysed (int): turn to be analysed
            id (str): identifier of the query
            komi (float): komi for the game
            rules (string or JSON): specify the rules for the game using either a shorthand string or a full JSON object
            COLOR (str): the color whose point of view is chosen for the analysis ('BLACK'|'WHITE')

        Returns:
            the Python dictionary of the JSON response from KataGo's analysis engine: format is documented in the engine documentation https://github.com/lightvector/KataGo/blob/v1.4.0/docs/Analysis_Engine.md

        Throws:
            nothing
            
        """
        board_size = sgf2board_size(sgf_file)
        overrideDic = {}
        overrideDic["reportAnalysisWinratesAs"] = COLOR 
        lineDic = {}
        lineDic['id'] = id
        lineDic['moves'] = sgf2listOfLists(sgf_file)
        lineDic['rules'] = rules
        lineDic['komi'] = komi
        lineDic['boardXSize'] = board_size
        lineDic['boardYSize'] = board_size
        lineDic['analyzeTurns'] = [turnToBeAnalysed]
        lineDic['overrideSettings'] = overrideDic
        line = json.JSONEncoder().encode(lineDic) #+'\n'
        # print('launching the following query with identifier',id,'\n',line,'\n\n' )
        analysisPYTHON=self.launchQueryAndReturn(line)
        print('the analysis',analysisPYTHON['id'],'is completed for turn',analysisPYTHON['turnNumber'],'from sgf file',sgf_file, 'with komi',str(komi), 'and rules', rules,'\n')
        return(analysisPYTHON)

    # method analysing a sgf file and capturing the output
    def analyse_listOfLists(self,list_of_lists,turnToBeAnalysed,id,komi,rules,COLOR,board_size=19):
        """
        analyse_listOfLists is a method analysing the turn -turnToBeAnalysed- of the moves contained in the list of lists -list_of_lists-. The moves are considered to be part of a game played with komi -komi- and rules -rules-. The analysis is conducted from the point of view of -COLOR-

        Args: 
            list_of_lists (list): list of lists of moves ["W","P6"]
            turnToBeAnalysed (int): turn to be analysed
            id (str): identifier of the query
            komi (float): komi for the game
            rules (string or JSON): specify the rules for the game using either a shorthand string or a full JSON object
            COLOR (str): the color whose point of view is chosen for the analysis ('BLACK'|'WHITE')

        Returns:
            the Python dictionary of the JSON response from KataGo's analysis engine: format is documented in the engine documentation https://github.com/lightvector/KataGo/blob/v1.4.0/docs/Analysis_Engine.md

        Throws:
            nothing
            
        """
        board_size = board_size
        overrideDic = {}
        overrideDic["reportAnalysisWinratesAs"] = COLOR 
        lineDic = {}
        lineDic['id'] = id
        lineDic['moves'] = list_of_lists
        lineDic['rules'] = rules
        lineDic['komi'] = komi
        lineDic['boardXSize'] = board_size
        lineDic['boardYSize'] = board_size
        lineDic['analyzeTurns'] = [turnToBeAnalysed]
        lineDic['overrideSettings'] = overrideDic
        line = json.JSONEncoder().encode(lineDic) #+'\n'
        # print('launching the following query with identifier',id,'\n',line,'\n\n' )
        analysisPYTHON=self.launchQueryAndReturn(line)
        print('the analysis',analysisPYTHON['id'],'is completed for turn',analysisPYTHON['turnNumber'],'with komi',str(komi), 'and rules', rules,'\n')
        return(analysisPYTHON)



