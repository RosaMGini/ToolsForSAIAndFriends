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
    def AIProcess(self,literal,currentBoard='',startFromMove=''): 
        """
        AIProcess is a method opening a process of the software AI of type typeAI, using a specified set of parameters, and importing the currentBoard, if any, at move startFromMove, if indicated; it returns an instance of subprocess.Popen()

        Args: 
            literal (str): string containing parameters to be used when opening the process
            currentBoard (str): (optional) string containing the namefile of the SGF the game must start from
            startFromMove(str): (optional) string containing the number of the move of the SGF the game must start from, meaning the the first move played will be the next one to this

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
            print('opening process of katago for a net of type',self.typeAI,'with command:',lineKG)
            processPlayer=subprocess.Popen(lineKG,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True,shell=True)
        if currentBoard!='':
            startingFrom=''
            if startFromMove!='':
                if self.typeAI=='SAI' or self.typeAI=='LZ':
                    startingFrom=' '+str(int(startFromMove)+1)
                if self.typeAI=='KG':
                    startingFrom=' '+startFromMove
            line='loadsgf '+currentBoard+startingFrom+'\n'
            print(line)
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
    def generateMove(self,AIProcess,color,debugging=False):
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
            check=AIProcess.stdout.readline()[0:-1]
            if debugging==True:
                print('capturing check: ---',check,"---")
            # move=AIProcess.stdout.readline()[2:-1]
            move=check[2:]
            if debugging==True:
                print('capturing output: ---',move,"---")
            if len(move)>1:
                break
        if len(move)>3 and move!="resign" and move!="pass":
            print('error!!! move returned:',move)
            return "error"
        #print the move
        print('move', move)
        return move
    def generateMoveStdErr(self,AIProcess,color,debugging=False):
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
            check=AIProcess.stderr.readline()[0:-1]
            if debugging==True:
                print('capturing check: ---',check,"---")
            # move=AIProcess.stdout.readline()[2:-1]
            move=check[2:]
            if debugging==True:
                print('capturing output: ---',move,"---")
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
            parameters (dictionary): a dictionary contaning the output of the heatmap command under the following keys: 'alpha','beta', 'alpkt', 'komi', 'winrate','lambda','mu','x_bar','x_base','value','pass','illegal'
        Throws:
            exception if self.typeAI!='SAI' and self.typeAI!='LZ'
            
        """
        if self.typeAI!='SAI' and self.typeAI!='LZ':
            errormessage = "ERROR!!! only AIs of type 'SAI' or 'LZ' can use the method extractParametersCurrentBoard()"
            raise Exception(errormessage)
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
    def printSGF(self,AIProcess,fileSGF):
        """
        printSGF has a AI process print the current board to the SGF file fileSGF (passes a GTP command)

        Args: 
            AIProcess (instance of subprocess.open()): the process which received the command
            fileSGF (string): thr filename of the file to be printed

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


class GoGameAI:
    """
    GoGameAI is a class that manages Go games of a pair of nets for two AIs. In a typical use, an instance of the class is created, and is then used to invoke the methods playDefault() or playWithVariableAgent(). In a more refined use, lower level methods can be used directly.

    Authors: Rosa Gini, Maurizio Parton
    Date: 24 Aug 2020
    Version: 1.3
    Fork from GoGameSAI.py
    
    Track Change
    From 1.2: implement starting from move n-th of a provided SGF file in KataGo and in SAI/LZ: KataGo requires the move (n+1)th


    Args: 
        firstAI: executable that will be used for the first net firstPlayer
        secondAI: executable that will be used for the second net secondPlayer
        typeFirstAI: type of firstAI, currently supported: 'LZ' for leeelazero, 'SAI' for SAI, and 'KG' for Katago
        typeSecondAI: type of secondtAI, currently supported: as for typeFirstAI
        firstPlayer: net that will play first (with complete path)
        secondPlayer: net that will play second (with complete path)
        colorFirst: color that will play first ('W' if it's white, or 'B' if it's black)
        fileSGF: filename of the file where the sgf of the game will be saved
        startingBoard: filename of the sgf of the starting board (can be empty if the game starts from the empty board)
        startFromMove (string): (optional) number of the move of the SGF the game must start from

    Attributes:
        # stable attributes 
        playerOrdPlayer (dictionary of two strings): in playerOrdPlayer['1'] firstPlayer is stored; in playerOrdPlayer['2']' secondPlayer is stored
        colorOrdPlayer (dictionary of two strings): in colorOrdPlayer['1'] colorFirst is stored; in colorOrdPlayer['2'] the other color is stored
        AIOrdPlayer (dictionary of two strings): path and name of file containing the players
        typeAIOrdPlayer (dictionary of two strings): stores the two types of AI
        ToolsOrdPlayer (dictionary of two instances of GoAITools): the constructor crates two instances of GoAITools one for each player and stores them in a dictionary
        # to be updated at start game the game 
        processOrd (dictionary of two instances of subprocess.Popen()): initially empty, they are instantiated at game start by using the method AIprocess of GoAITools on both elements of ToolsOrdPlayer 
        # to be updated during the game 
        currentBoard (str): the filename of the board at the current moment if the game
        nextOrdPlayer (str): contains '1' if the next player is the first, '2' otherwise
        nextColor (str): color of next player ('W' or 'B')
        lastMoveIsPass (int): 1 if the last move was a pass, 0 otherwise
        gameStatus (str): 'ongoing' if the game is ongoing, 'completed' if it has ended
        # to store the result of the game at the end
        colorWhichHasResigned (str): 'undefined' until the end; when the game is completed it is 'W' or 'B' if one of the two colors has resigned, 'counting points' otherwise
        final_score (str): 'undefined' until the end; then it contains the result coded in the GTP format ('= B+R', '= W+2.5',...)
        winnerColor (str): 'undefined' until the end; then it contains the color of the winner ('B' or 'W', or 'none' if the game ended in a draw)
        gameWinner (str): 'undefined' until the end; then it contains '1' of the winner is firstPlayer, '2' if the winner if secondPlayer, 'draw' if the game ended in a draw
   
    """
    #constructor
    def __init__(self, firstAI, secondAI,typeFirstAI, typeSecondAI, firstPlayer,secondPlayer,colorFirst,fileSGF,startingBoard,startFromMove=''):
        #stable attributes 
        self.otherColor={'B':'W','W':'B'}
        self.otherOrdPlayer={'1':'2','2':'1'}
        self.colorOrdPlayer={}
        self.colorOrdPlayer['1']=colorFirst
        self.colorOrdPlayer['2']=self.otherColor[colorFirst]
        self.AIOrdPlayer={}
        self.AIOrdPlayer['1']=firstAI #path and name of file containing the first AI
        self.AIOrdPlayer['2']=secondAI #path and name of file containing the second AI
        self.typeAIOrdPlayer={}
        self.typeAIOrdPlayer['1']=typeFirstAI #type of the first AI
        self.typeAIOrdPlayer['2']=typeSecondAI #type of the second AI
        self.playerOrdPlayer={}
        self.playerOrdPlayer['1']=firstPlayer #path and name of file containing the weight of the SAI net which is going to move first
        self.playerOrdPlayer['2']=secondPlayer #path and name of file  containing the weight of the SAI net which is going to move second
        self.startingBoard=startingBoard #board at the beginning of the game
        self.startFromMove=startFromMove #move of the initial board the geme must restart from
        self.colorSecond=self.otherColor[colorFirst]
        self.fileSGF=fileSGF
        #attributes to be updated at game start
        self.processOrd={} #dictionary of the two processes that will be launched
        #attributes to be updated during the game
        self.currentBoard=startingBoard
        self.nextOrdPlayer='1'
        self.nextColor=colorFirst #color of next player
        self.gameStatus='ongoing'
        self.lastMoveIsPass=0
        #attributes to be updated at the end of the game
        self.colorWhichHasResigned='undefined'
        self.final_score='undefined'
        self.winnerColor='undefined'
        self.gameWinner='undefined'
        # open two instances of GoAITools
        self.ToolsOrdPlayer={}
        self.ToolsOrdPlayer['1']=GoAITools(firstAI,typeFirstAI,firstPlayer) 
        self.ToolsOrdPlayer['2']=GoAITools(secondAI,typeSecondAI,secondPlayer) 
    # info to be printed
    def __str__(self):
        return "First SAI net " + firstPlayer + ", playing as " + colorFirst + " and starting from " + startingBoard
    #METHODS WHICH OPERATE ON TWO SPECIFIC LEELAZ PROCESSES self.processOrd['1'] and self.processOrd['2']
    #method opening a leelaz process for one of the two players, using a specified set of parameters, and importing the currentBoard, and storing it in the dictionary self.processOrd[ordplayer] 
    def AIOrdProcess(self,ordplayer,literal): 
        """
        AIOrdProcess invokes AIProcess of ToolsOrdPlayer['1'] of ToolsOrdPlayer['2'], according to its argument

        Args: 
            ordplayer (str): must be either '1' or '2'
            literal (str): the literal to be used to open the process

        Returns:
            nothing
        Throws:
            exception if ordplayer is not '1' or '2'
            
        """
        if ordplayer!='1' and ordplayer!='2':
            errormessage = "ERROR!!! the first argument must be either '1' or '2'"
            raise Exception(errormessage)
        player=self.playerOrdPlayer[ordplayer]
        typeAI=self.typeAIOrdPlayer[ordplayer]
        AI=self.AIOrdPlayer[ordplayer]
        print(self.startingBoard)
        AIProcess=self.ToolsOrdPlayer[ordplayer].AIProcess(literal,self.startingBoard,self.startFromMove) 
        self.processOrd[ordplayer]=AIProcess
    #open two processes with assiged parameters, they are stored in the dictionary self.processOrd['1'] and self.processOrd['2'] and set the current board and the komi
    def startGame(self,literalFirst,literalSecond,komi):
        """
        startGame opens two processes and stores them in the dictionary processOrd

        Args: 
            literalFirst (str): the literal to be used to open the first process
            literalSecond (str): the literal to be used to open the second process
            komi (float): the komi to be set for the game
        Returns:
            nothing
        Throws:
            nothing
            
        """
        self.AIOrdProcess('1',literalFirst)
        self.AIOrdProcess('2',literalSecond)
        self.currentBoard=self.fileSGF
        self.ToolsOrdPlayer['1'].setKomi(self.processOrd['1'],komi)
        self.ToolsOrdPlayer['2'].setKomi(self.processOrd['2'],komi)
    # have the ordplayer process print the current board to the SGF file
    def printSGFOrdProcess(self,ordplayer):
        """
        printSGFOrdProcess has the ordplayer process print the current board to the SGF file fileSGF (passes a GTP command)

        Args: 
            ordplayer (str): must be either '1' or '2'

        Returns:
            nothing
        Throws:
            exception if ordplayer is neither '1' nor '2'
            exception if the dictionary processOrd is empty
            
        """
        if ordplayer!='1' and ordplayer!='2':
            errormessage = "ERROR!!! the first argument must be either '1' or '2'"
            raise Exception(errormessage)
        if self.processOrd=={}:
            errormessage = "ERROR!!! the process "+ordplayer+" is not active"
            raise Exception(errormessage)
        player=self.playerOrdPlayer[ordplayer]
        typeAI=self.typeAIOrdPlayer[ordplayer]
        AIProcess=self.processOrd[ordplayer]
        self.ToolsOrdPlayer[ordplayer].printSGF(AIProcess,self.fileSGF)
   #close the two players' processes
    def closeTwoPlayerProcesses(self):
        """
        closeTwoPlayerProcesses closes the two processes stored in the dictionary processOrd

        Args: 
            nothing
        Returns:
            nothing
        Throws:
            nothing
            
        """
        for ord in ['1','2']:
            self.ToolsOrdPlayer[ord].closeAIProcess(self.processOrd[ord])
    #method generating the next move and managing the output (regardless of whether the game terminates or not)
    def moveNext(self):
        """
        moveNext manages generation of the next move of a game: it has generateMove() generate it for the current player, incorporateMove incorporate it for the next player; then if the game is over it stores the result (using the GTP command final_score); otherwise it has current and next player and color updated

        Args: 
            nothing
        Returns:
            nothing
        Throws:
            nothing
            
        """
        thisOrdPlayer=self.nextOrdPlayer
        thisProcess=self.processOrd[thisOrdPlayer]
        thisColor=self.nextColor
        thisTypeAI=self.typeAIOrdPlayer[thisOrdPlayer]
        thisTool=self.ToolsOrdPlayer[thisOrdPlayer]
        print('player:',thisOrdPlayer)
        move=thisTool.generateMove(thisProcess,thisColor,debugging=False)
        if move=="resign":
            self.gameStatus='completed'
        if move=="pass" and self.lastMoveIsPass==1:
            self.gameStatus='completed'
        if move=="pass":
            self.lastMoveIsPass=1
        else:
            self.lastMoveIsPass=0
        #inform the other player of the move
        otherOrd=self.otherOrdPlayer[thisOrdPlayer]
        self.ToolsOrdPlayer[otherOrd].incorporateMove(self.processOrd[otherOrd],move,thisColor)
        #if the move terminated the game, set and return attributes referring to winner and result; otherwise, prepare the next move: switch nextOrdPlayer and nextColor
        if self.gameStatus=='completed':
            self.colorWhichHasResigned=thisColor if move=="resign" else 'counting points'
            thisProcess.stdin.write("final_score\n")
            thisProcess.stdin.flush()
            while True:
                outputFinalScore=thisProcess.stdout.readline()[:-1]
                print('reading score...',outputFinalScore)
                if len(outputFinalScore)>2:
                    break
            # print('final_score from leelaz',outputFinalScore)
            self.final_score=outputFinalScore if self.colorWhichHasResigned=='counting points' else '= '+self.otherColor[self.colorWhichHasResigned]+'+R'
            self.returnAllResults()
        else:
            self.nextOrdPlayer=self.otherOrdPlayer[thisOrdPlayer]
            self.nextColor=self.otherColor[thisColor]            
    #METHODS SETTING FINAL RESULTS (NO LEELAZ PROCESSES INVOLVED)
    #return gtp final score
    def returnfinal_score(self):
        """
        returnfinal_score  returns the GTP final score (it is probably redundant but is used in other methods); requires that gameStatus is 'completed'

        Args: 
            nothing
        Returns:
           final_score (str): the attribute containing the GTP result
        Throws:
            if the game is not completed but throws a warning 
            
        """
        if self.gameStatus!='completed':
            print('WARNING: the game is not completed')
        return self.final_score
    #method defining and exporting winnerColor (to be ran after returnfinal_score())
    def returnWinnerColor(self):
        """
        returnWinnerColor sets the attribute winnerColor and returns the color of the winner; requires that gameStatus is 'completed' and final_score!='undefined'

        Args: 
            nothing
        Returns:
            winnerColor (str): the color of the winner ('B', 'W', or 'none' if it is a draw)
        Throws:
            if the game is completed but the final score is undefined throws a warning 
            
        """
        if self.gameStatus=='completed' and self.final_score!='undefined':
            if self.final_score[2]=='B':
                self.winnerColor='B'
            elif self.final_score[2]=='W':
                self.winnerColor='W'
            else:
                self.winnerColor='none'
        elif self.gameStatus=='completed' and self.final_score=='undefined':
            print('WARNING: the game is completed but final_score was not set; run the method final_score() before assessing the color of the winner')
        return self.winnerColor
    #method defining and exporting gameWinner (to be ran after returnWinnerColor())
    def returnGameWinner(self):
        """
        returnGameWinner sets the attribute colorOrdPlayer and returns the order of the winner (requires that gameStatus is 'completed' and final_score!='undefined' and winnerColor!='undefined')

        Args: 
            nothing
        Returns:
            gameStatus (str): the order of the winner ('1', '2', or 'draw' if it is a draw)
        Throws:
            if the game is completed but either the final score is undefined or the coor of the winner is underfined, throws a warning 
            
        """
        if self.gameStatus=='completed' and self.final_score!='undefined' and self.winnerColor!='undefined':
            if self.colorOrdPlayer['1']==self.winnerColor:
                self.gameWinner='1'
            elif self.colorOrdPlayer['2']==self.winnerColor:
                self.gameWinner='2'
            else:    
                self.gameWinner='draw'
        elif self.gameStatus=='completed' and self.final_score=='undefined':
            print('WARNING: the game is completed but final_score and winnerColor were not set; run the method final_score() and the method winnerColor() before assessing the winner')
        elif self.gameStatus=='completed' and self.final_score!='undefined' and self.winnerColor!='undefined':
            print('WARNING: the game is completed and final_score was assessed, but winnerColor were not set; run the method winnerColor() before assessing the winner')
        return self.gameWinner
    #method returning all the results
    def returnAllResults(self):
        """
        returnAllResults invokes in a sequence the 3 methods returnfinal_score(), returnWinnerColor(). This sets the attributes colorOrdPlayer and winnerColor, and returns both them and final_score (requires that gameStatus is 'completed')

        Args: 
            nothing
        Returns:
            gameStatus (str): the order of the winner ('1', '2', or 'draw' if it is a draw)
        Throws:
            if the game is completed but either the final score is undefined or the color of the winner is underfined, throws a warning 
            
        """
        if self.gameStatus!='completed':
            print('WARNING: the game is not completed')
        self.returnfinal_score()
        self.returnWinnerColor()
        self.returnGameWinner()
    #METHODS PLAYING GAMES
    #method playing by default: assign once and for all a set of SAI parameters to each player and have them play until gameStatus is 'completed' 
    def playDefault(self,literalFirst,literalSecond,komi,verbose=False):
        """
        playDefault is the method managing a regular game, after assigning parameters to the two players, until the game is completed. At the end colorOrdPlayer, winnerColor, and final_score are assigned, printSGF() is invoked by the last playing process, and both processes are closed
        Args: 
            literalFirst (str): a sequence of parameters which is valid in the syntax of the executable leelaz, to be used by the first player
            literalSecond (str): a sequence of parameters which is valid in the syntax of the executable leelaz, to be used by the second player
            komi (float): the komi to be set for the game
        Returns:
            it invokes moveNext() until the game is completed, which implies that it sets the attributes and returns the results colorOrdPlayer, winnerColor, and final_score
        Throws:
            none 
            
        """
        print("****************************************************************************************" )
        print("A game starts between "+  self.playerOrdPlayer['1'] +" and "+  self.playerOrdPlayer['2'] )
        print( self.playerOrdPlayer['1']+" plays first" )
        print( "Komi is "+ str(komi) )
        print( "The first player plays "+ self.colorOrdPlayer['1'] )
        if self.startingBoard=='':
            print("The starting board is empty")
        else:
            print("The starting board is "+self.startingBoard)
            if self.startFromMove!='':
                print("Game starts from move number "+self.startFromMove)
        print("****************************************************************************************" )
        #start the game with the assigned parameters
        self.startGame(literalFirst,literalSecond,komi)
        if verbose==True:
            self.ToolsOrdPlayer['1'].showBoard(self.processOrd['1'])
        #make the processes move in turn
        while True:
            #pick the player
            thisOrdPlayer=self.nextOrdPlayer
            thisProcess=self.processOrd[thisOrdPlayer]
            thisColor=self.nextColor
            thisTool=self.ToolsOrdPlayer[thisOrdPlayer]
            #move
            move=self.moveNext()
            if verbose==True:
                thisTool.showBoard(thisProcess)
            if self.gameStatus=='completed':
                break      
        #print the SGF
        self.printSGFOrdProcess(thisOrdPlayer)
        #close the leelaz processes
        self.closeTwoPlayerProcesses()
    #method playing with variable agent: set a threshold for winrate and parameters mu and lambda for one of the players and have the two players play until gameStatus is 'completed' 
    #ordPlayerVariableAgent,threshold,parmu,parlambda are numbers; threshold is in percentage
    def playWithVariableAgent(self,literalFirst,literalSecond,ordPlayerVariableAgent,threshold,parmu,parlambda,komi,verbose=False):
        """
        playWithVariableAgent is the method managing a game where one of the players is SAI and plays with a variable agent. Parameters are assigned to the two players, as wll as the parameters of the variable agent, and the orded of the payer which plays with a viable agent. The game is played until it is completed; at the end colorOrdPlayer, winnerColor, and final_score are assigned, and printSGF() is invoked by the last playing process, and both processes are closed
        Args: 
            literalFirst (str): a sequence of parameters which is valid in the syntax of the executable leelaz, to be used by the first player
            literalSecond (str): a sequence of parameters which is valid in the syntax of the executable leelaz, to be used by the second player
            ordPlayerVariableAgent (str): order of the player which plays with variable agent; can be '1' o '2'
            threshold (int): perentage of winrate that triggers activation of the agent
            parmu (float): parameter mu of the agent (in [0,1])
            parlambda (float): parameter lambda of the agent (in [0,1])
            komi (float): the komi to be set for the game
        Returns:
            it invokes moveNext() until the game is completed, which implies that it sets the attributes and returns the results colorOrdPlayer, winnerColor, and final_score
        Throws:
            exception if typeAI[ordPlayerVariableAgent]!='SAI' 
        """
        print("****************************************************************************************" )
        print("A game starts between "+  self.playerOrdPlayer['1'] +" and "+  self.playerOrdPlayer['2'] )
        print( self.playerOrdPlayer['1']+" plays first ")
        print( "The first player plays "+ self.colorOrdPlayer['1'] )
        print( "Komi is "+ str(komi) )
        if self.startingBoard=='':
            print("The starting board is empty")
        else:
            print("The starting board is "+self.startingBoard)
            if self.startFromMove!='':
                print("Game starts from move number "+self.startFromMove)
        print("The player "+ordPlayerVariableAgent+" plays with a variable agent, with parameters lambda="+str(parlambda)+" and mu="+str(parmu)+", and with threshold="+str(threshold)+"%")
        print("****************************************************************************************" )
        if self.typeAIOrdPlayer[ordPlayerVariableAgent]!='SAI':
            errormessage = "ERROR!!! only AIs of type 'SAI' can play with a variable agent"
            raise Exception(errormessage)
        #start the game with the assigned parameters
        self.startGame(literalFirst,literalSecond,komi)
        if verbose==True:
            self.ToolsOrdPlayer['1'].showBoard(self.processOrd['1'])
        #make the processes move in turn
        while True:
            #pick the player
            thisOrdPlayer=self.nextOrdPlayer
            thisProcess=self.processOrd[thisOrdPlayer]
            thisColor=self.nextColor
            thisTool=self.ToolsOrdPlayer[thisOrdPlayer]
            #if winrate is higher than threshold, set mu and lambda to the parameters
            if thisOrdPlayer==ordPlayerVariableAgent:
                print('player '+thisOrdPlayer+' plays with variable agent')
                params=thisTool.extractParametersCurrentBoard(thisProcess)
                if 'winrate' in params.keys():
                    if params['winrate']>threshold:
                        thisTool.setOption(thisProcess,'lambda',parlambda)
                        thisTool.setOption(thisProcess,'mu',parmu)
                    else:
                        thisTool.setOption(thisProcess,'lambda',0)
                        thisTool.setOption(thisProcess,'mu',0)
                else:
                    print('ERROR: a variable agent can only be played by a SAI net')
                    break
            #move
            move=self.moveNext()
            if verbose==True:
                thisTool.showBoard(thisProcess)
            if self.gameStatus=='completed':
                break                  
        #print the SGF
        self.printSGFOrdProcess(thisOrdPlayer)
        #close the leelaz processes
        self.closeTwoPlayerProcesses()     
    
