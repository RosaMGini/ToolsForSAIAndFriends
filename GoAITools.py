import os
from os import  O_NONBLOCK 
import subprocess
from fcntl import fcntl, F_GETFL, F_SETFL
import time
class GoAITools:
    """
    GoAITools is a class providing low-level tools to interact with an AI capable to play Go.

    Author: Rosa Gini
    Date: 15 Aug 2020
    Version: 0.1
    Fork from GoGameAI.py


    Args: 
        AI: executable that will be used for the net
        typeAI: type of AI, currently supported: 'LZ' for leeelazero, 'SAI' for SAI, and 'KG' for Katago
        player: net that is going to be managed (with complete path)  

    Attributes:
        # none
        
   
    """
    #constructor
    def __init__(self, AI, typeAI, player):
        self.AI=AI
        self.typeAI=typeAI
        self.player=player
    # info to be printed
    def __str__(self):
        return "The AI net " + self.player + " can be launched with " + self.AI
    #METHODS WHICH PROVIDE INTERFACES TO ASSIGNED LEELAZ PROCESSES
    #method opening a leelaz process using a specified set of parameters, and importing the currentBoard
    def AIProcess(self,literal,currentBoard=''): 
        """
        AIProcess is a method opening a process of the software AI of type typeAI, using a specified set of parameters, and importing the currentBoard, if any; it returns an instance of subprocess.Popen()

        Args: 
            literal (str): string containing parameters to be used when opening the process

        Returns:
            processPlayer: an instance of subprocess.Popen()
        Throws:
            exception if typeAI is not supported
            
        """
        if self.typeAI!='SAI' and self.typeAI!='LZ' and self.typeAI!='KG':
            errormessage = "ERROR: the types of AI currently supported are SAI, LZ and KG: "+self.typeAI+" is not supported"
            raise Exception(errormessage)
        if self.typeAI=='SAI' or self.typeAI=='LZ':
            #clean literal
            literalsplit = literal.split(' ')
            checkq=False
            checkg=False
            literalnew=[]
            for word in literalsplit:
                if word!='-q':
                    literalnew.append(word)
                if word=='-q':
                    checkq=True
                if word=='-g' :
                    checkg=True 
            literalclean=literal
            if checkq:
                print("WARNING: the '-q' switch is incompatible with the functionalities of GoAITools with SAI or LZ; I am dropping it")
            if checkg==False:
                print("WARNING: the '-g' switch is necessary for the functionalities of GoAITools with SAI or LZ; I am adding it")
                literalnew.append('-g')
            literalclean=" ".join(literalnew)    
            lineLeela=self.AI+" -w "+ self.player+" "+ literalclean
            print('opening process of leelaz for a net of type',self.typeAI,'with command:',lineLeela)
            # processPlayer=subprocess.Popen(lineLeela,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,shell=True)
            processPlayer=subprocess.Popen(lineLeela,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,shell=True)
        if self.typeAI=='KG':
            lineKG= self.AI+' gtp -model '+self.player+' -config default_gtp.cfg -override-config '+literal
            print('opening process of katago for a net of type',typeAI,'with command:',lineKG)
            processPlayer=subprocess.Popen(lineKG,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,shell=True)
        if currentBoard!='':
            line='loadsgf '+currentBoard+'\n'
            processPlayer.stdin.write(line)
            processPlayer.stdin.flush()
        return processPlayer
    #method emptying the stderr of a AI process
    def emptystderrAIProcess(self,AIProcess):
        """
        emptystderrAIProcess is a method managing an instance of subprocess.Popen(): it empties the stderr  (uses features of subprocess.open())

        Args: 
            AIProcess (instance of subprocess.open()): the process whose stderr is going to be emptied
        Returns:
            nothing
        Throws:
            nothing
            
        """
        #makes the stderr of the process non-blocking when reading, in order to avoid deadlock when we empty stderr
        flags=fcntl(AIProcess.stderr,F_GETFL)
        fcntl(AIProcess.stderr,F_SETFL,flags | O_NONBLOCK)
        #read stderr until empty line is found
        while True:
            ln=AIProcess.stderr.readline() #[0:-1]
            if not ln:
                break
        # make stderr blocking again
        fcntl(AIProcess.stderr,F_SETFL,flags)
    #method emptying the stdout of a leelaz process
    def emptystdoutAIProcess(self,AIProcess):
        """
        emptystdoutAIProcess is a method managing an instance of subprocess.Popen(): it empties the stdout  (uses features of subprocess.open())

        Args: 
            AIProcess (instance of subprocess.open()): the process whose stdout is going to be emptied
        Returns:
            nothing
        Throws:
            nothing
            
        """
        #makes the stdout of the process non-blocking when reading, in order to avoid deadlock when we empty stdout
        flags=fcntl(AIProcess.stdout,F_GETFL)
        fcntl(AIProcess.stdout,F_SETFL,flags | O_NONBLOCK)
        #read stdout until empty line is found
        while True:
            ln=AIProcess.stdout.readline() #[0:-1]
            if not ln:
                break
        # make stdout blocking again
        fcntl(AIProcess.stdout,F_SETFL,flags)
    #method closing a AI process 
    def closeAIProcess(self,AIProcess):
        """
        closeAIProcess is a method managing a leelaz process: it closes it (passes a GTP command)

        Args: 
            AIProcess (instance of subprocess.open()): the process which is going to be closed
        Returns:
            nothing
        Throws:
            nothing
            
        """
        print('quitting process', AIProcess)
        line='quit\n'
        AIProcess.stdin.write(line)
        AIProcess.stdin.flush()
    #method having a process generate a move
    def generateMove(self,AIProcess,color):
        """
        generateMove has a leelaz process generate a move of a specified color (passes a GTP command)

        Args: 
            AIProcess (instance of subprocess.open()): the process which is going to generate a move
            color (str): the color whose move is going to be generated ('W' or 'B')
        Returns:
            move (str): a string containng a valid GTP move (e.g. 'J17')
        Throws:
            nothing
            
        """
        # empty stderr to avoid deadlock due to stderr too full; since generateMove is launched very often, this solves the problem
        self.emptystderrAIProcess(AIProcess)
        line='genmove '+color+'\n'
        print('command:',line)
        AIProcess.stdin.write(line)
        AIProcess.stdin.flush()
        while True:
            # check=AIProcess.stdout.readline()[0:-1]
            # print('capturing check: ---',check,"---")
            move=AIProcess.stdout.readline()[2:-1]
            # print('capturing output: ---',move,"---")
            if len(move)>1:
                break
        if len(move)>3 and move!="resign" and move!="pass":
            print('error!!! move returned:',move)
            return "error"
        #print the move
        print('move', move)
        return move
    #method incorporating a move in a AI process
    def incorporateMove(self,AIProcess,move,colorMove):
        """
        incorporateMove has a leelaz process incorporate a move of a specified color (passes a GTP command)

        Args: 
            AIProcess (instance of subprocess.open()): the process which is going to incorporate the move
            colorMove (str): the color whose move is going to be incorporated ('W' or 'B')
            move (str): a string containing a valid GTP move (e.g. 'J17', or 'resign')
        Returns:
            nothing
        Throws:
            nothing
            
        """
        line="play "+colorMove+" "+move+'\n'
        # print('incorporate:',move,'for player',colorMove,'in process',AIProcess)
        print('command:',line)
        AIProcess.stdin.write(line)
        AIProcess.stdin.flush()
    #method setting komi in a leelaz process
    def setKomi(self,AIProcess,komi):
        """
        setKomi has a AI process set the komi value (passes a GTP command)

        Args: 
            AIProcess (instance of subprocess.open()): the process which is going to incorporate the move
            komi (float): the value of komi to be set
        Returns:
            nothing
        Throws:
            nothing
            
        """
        line="komi "+str(komi)+'\n'
        # print('set komi:',str(komi))
        print('command:',line)
        AIProcess.stdin.write(line)
        AIProcess.stdin.flush()
    #method having an AI process show the board
    def showBoard(self,AIProcess):
        """
        showBoard has a AI process show the board (passes a GTP command and captures output)

        Args: 
            AIProcess (instance of subprocess.open()): the process which is going to show the board
            
        Returns:
            nothing
        Throws:
            nothing
            
        """
        line="showboard\n"
        print("Current board")
        AIProcess.stdin.write(line)
        AIProcess.stdin.flush()
        step=1
        step2=1
        if self.typeAI=="SAI" or self.typeAI=="LZ": 
            while True:
                row=AIProcess.stderr.readline()[:-1]
                if "a b c" in row:
                    step=2
                if step>=2:
                    print(row)
                    step2=step2+1
                if "a b c" in row and step2>2:
                    break
        if self.typeAI=="KG":
            while True:
                row=AIProcess.stdout.readline()[:-1]
                if "A B C" in row:
                    step=2
                if step>=2:
                    print(row)
                    step2=step2+1
                if "Next" in row and step2>=2:
                    break
            self.emptystdoutAIProcess(AIProcess)
    #method having a AI process store the heatmap of the current board and the current player (works both with a SAI and a LZ net)
    def heatmapCurrentBoard(self,AIProcess):
        """
        heatmapCurrentBoard has a leelaz process generate the heatmap of the current board

        Args: 
            AIProcess (instance of subprocess.open()): the process which is going to generate the heatmap of the current board
        Returns:
            outputHeatmap (str): a string contaning the output of the heatmap command
        Throws:
            nothing
            
        """
        # empty stderr to avoid reading older stuff
        self.emptystderrAIProcess(AIProcess)
        #send heatmap command
        line='heatmap'+'\n'
        print('command:',line)
        AIProcess.stdin.write(line)
        AIProcess.stdin.flush()
        #capture output
        outputHeatmap=['list containing heatmap output']
        while True:
            line=AIProcess.stderr.readline() #[:-1]
            # print('line heatmap:',line)
            outputHeatmap.append(line)
            # #CAUTION!!!! in this version the output of heatmap to stderr contains 'pass', the 1 row (ending with 'value') if it's a LZ net, or 3 rows (last ending with 'komi') if it's SAI; if this changes the code must be updated
            if line.find('pass')>=0:
                line=AIProcess.stderr.readline() #[:-1]
                outputHeatmap.append(line)
                if line.find('value')>=0:                    
                    break
                else:
                    while True:
                        line=AIProcess.stderr.readline()
                        outputHeatmap.append(line)
                        if line.find('komi')>=0:
                            break
                break
        #print('outputHeatmap',outputHeatmap)
        return outputHeatmap
    #method having a leelaz process parse the output of heatmap to find parameters
    def extractParametersCurrentBoard(self,AIProcess):
        """
        extractParametersCurrentBoard extracts from the result of the method heatmapCurrentBoard() a set of parameters and stores them in a dictionary. Only works for typeAI LZ or SAI

        Args: 
            AIProcess (instance of subprocess.open()): the process which is used to invoke the method heatmapCurrentBoard
        Returns:
            parameters (dictionary): a dictionary contaning the output of the heatmap command under the following keys: 'alpha','beta', 'alpkt', 'komi', 'winrate','lambda','mu','x_bar','x_base','value','pass','illegal', 'winrate is for'
        Throws:
            nothing
            
        """
        outputHeatmap=self.heatmapCurrentBoard(AIProcess)
        #print(outputHeatmap)
        lastLinesHeatmap=outputHeatmap[-15:]
        strLastLinesHeatmap = ' '.join(lastLinesHeatmap)
        parameters={}
        for par in ['alpha','beta', 'alpkt', 'komi', 'winrate','lambda','mu','x_bar','x_base','value','pass','illegal']:
            # print(par)
            parpos=strLastLinesHeatmap.find(par)
            if parpos>-1:
                remaining=strLastLinesHeatmap[parpos:]
                #print(remaining)
                word=remaining.split(" ",2)[1]
                word=word.replace(',', "")
                word=word.replace('%', "")
                word=word.replace('\n', "")
                # print(par,word)
                parameters[par]=float(word)
                # print('parameter for '+par+" is: ",parameters[par])
#        parameters['winrate is for']=self.nextColor
        return parameters
    #method setting a parameter in a leelaz process
    def setOption(self,AIProcess,OptionName,NumericValue):
        """
        setOption sets an option in a leelaz process to a value. Only works for typeAI SAI or LZ 

        Args: 
            AIProcess (instance of subprocess.open()): the process which received the command
            OptionName (str): the name of the option that is set
            NumericValue (float): the value to which OptionName is set

        Returns:
            nothing
        Throws:
            nothing
            
        """
        line='lz-setoption name '+OptionName+' value '+str(NumericValue)+'\n'
        #print('command:',line)
        AIProcess.stdin.write(line)
        AIProcess.stdin.flush()  
    #method having a leelaz process print the current state of the game in the sgf file
    def printSGF(self,AIProcess):
        """
        printSGF has a AI process print the current board to the SGF file fileSGF (passes a GTP command)

        Args: 
            AIProcess (instance of subprocess.open()): the process which received the command

        Returns:
            nothing
        Throws:
            nothing
            
        """
        print('printing',fileSGF)
        with open(fileSGF,"w") as sgf: 
            AIProcess.stdin.write("printsgf\n")
            AIProcess.stdin.flush()
            emptylines=0
            if self.typeAI=='SAI' or self.typeAI=='LZ':
                while True:
                    line=AIProcess.stdout.readline()
                    #print('line pre is: ',line)
                    parpos=line.find('=')
                    #print('parpos is: ',parpos)
                    if parpos==0:
                        line=line[1:]
                        #print('line post is: ',line)
                    sgf.write(line)
                    if line=="\n":
                        emptylines=emptylines+1
                    else:
                        emptylines=0
                    if emptylines>1:
                        break
            if self.typeAI=='KG':
                while True:
                    line=AIProcess.stdout.readline()
                    #print('line pre is: ',line)
                    parpos=line.find('=')
                    #print('parpos is: ',parpos)
                    if parpos==0:
                        line=line[1:]
                        #print('line post is: ',line)
                    sgf.write(line)
                    if line=="\n":
                        break
