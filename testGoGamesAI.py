import os
import subprocess
import sys
import time
sys.path.append('../../tools')
from GoGameAI import GoGameAI, GoAITools

## SAI (must change according to whether nets are 9x9 or 19x19)
leelaz="/home/schroeder/SAI/run/leelaz"
leelaz="/home/schroeder/SAI/bin/sai"
# leelaz="/home/schroeder/SAI/bin/lzsai-gpu-0.16-0"
# leelaz="C:/Users/Eloisa/SAI/sai-0.17.5-gpu/sai.exe"

## KataGo
KG='/home/schroeder/SAI/bin/katago'
#KG='/home/schroeder/SAI/bin/katago_1.4.2' 


## literals
visits=str(10)
r=2
rKG = ( 2 * r/100 - 1 )
literal={}
literal['SAI']='-v '+visits+' --lambda 0 --mu 0 --nrsymm -r '+str(r)+'  -t 1 --noponder --precision single -g'
literal['LZ']='-v '+visits+' --nrsymm -r '+str(r)+'  -t 1 --noponder --precision single -g'
literal['KG']='maxVisits='+visits+',allowResignation=true,resignThreshold=-0.96,resignConsecTurns=1'

# # NETS 9x9
S1= '../../../ricerca_large/experimentSAIagainstWeakOpponentsMirror/2_sampleNetsSAI29/sample/S1/94619dea457de054503cec030269ce842c47055ba51e96db8fee841dfbaf05f9.gz'
#S1= 'C:/Users/Eloisa/SAI/Dropbox/ricerca_large/experimentSAIagainstWeakOpponentsMirror/2_sampleNetsSAI29/sample/S1/94619dea457de054503cec030269ce842c47055ba51e96db8fee841dfbaf05f9.gz'
Wg= '../../../ricerca_large/experimentSAIagainstWeakOpponentsMirror/2_sampleNetsSAI29/sample/Wg/f877b1ff100d9d741f0b87607a4c26ab17287220b3e0788a8a4359a8f2a40d06.gz'
#Wg= 'C:/Users/Eloisa/SAI/Dropbox/ricerca_large/experimentSAIagainstWeakOpponentsMirror/2_sampleNetsSAI29/sample/Wg/f877b1ff100d9d741f0b87607a4c26ab17287220b3e0788a8a4359a8f2a40d06.gz'

# # NETS 19x19 SAI
SAIa="../../../ricerca_large/sai19x19/SAI/nets/g011/b5463579a10b7ed313f2f0f0054b28d413da03fd4414778dfac9cef9cbc24aca.gz"
SAIb="../../../ricerca_large/sai19x19/SAI/nets/g009/0f33040c2b862cb80f4fc763a48eae5c02a29777de244c803e61b66feab4eef4.gz"
SAI322="../../../ricerca_large/sai19x19/SAI/nets/SAI322/2fed30ebf0c4d813f8d126e42830a800f3988943eb18295b4536d3d19f3f6717.gz"

# NETS 19x19 LZ
LZ107="../../../ricerca_large/sai19x19/LZ/nets/LZ107/b776808133ed4ee57b6819f81922e18a656f967641b8fd79a21afa033a7cf77b.gz"

# # NETS 19x19 KG
KGnet="/home/schroeder/Dropbox/ricerca_large/katago/example/g170-b30c320x2-s2271129088-d716970897.bin.gz"

literalSAI=literal['SAI']
literalKG=literal['KG']

# #(firstAI, secondAI,typeFirstAI, typeSecondAI, firstPlayer,secondPlayer,colorFirst,fileSGF,startingBoard)
# PLAY DEFAULT FROM EMPTY BOARD
gameTest= GoGameAI(leelaz,KG,'SAI','KG', SAI322,KGnet,'B','testPlayDefault.sgf','')
gameTest.playDefault(literalSAI,literalKG,7.5,verbose=True)
print('gtp result of the game',gameTest.final_score)
print('colorwinner',gameTest.winnerColor)
print('winner',gameTest.gameWinner)

# # PLAY DEFAULT FROM EMPTY BOARD only SAI
# gameTest= GoGameAI(leelaz,leelaz,'SAI','SAI', SAI322,SAI322,'B','testPlayDefault.sgf','')
# gameTest.playDefault(literalSAI,literalSAI,7.5,verbose=True)
# print('gtp result of the game',gameTest.final_score)
# print('colorwinner',gameTest.winnerColor)
# print('winner',gameTest.gameWinner)

# # PLAY WITH VARIABLE AGENT only SAI
# gameTest= GoGameAI(leelaz,leelaz,'SAI','SAI', SAI322,SAI322,'B','testPlayWithaVariableAgent.sgf','')
# gameTest.playWithVariableAgent(literalSAI,literalSAI,'1',50,0,0.5,7.5,verbose=True)
# print('gtp result of the game',gameTest.final_score)
# print('colorwinner',gameTest.winnerColor)
# print('winner',gameTest.gameWinner)

# # PLAY WITH VARIABLE AGENT
# gameTest= GoGameAI(leelaz,KG,'SAI','KG', SAI322,KGnet,'B','testPlayWithaVariableAgent.sgf','')
# gameTest.playWithVariableAgent(literalSAI,literalKG,'1',50,0,0.5,7.5)
# print('gtp result of the game',gameTest.final_score)
# print('colorwinner',gameTest.winnerColor)
# print('winner',gameTest.gameWinner)





# # PLAY DEFAULT FROM STARTING BOARD
# literal=literalSAI+ ' --logfile temp_logLZ.txt '
# gameTest= GoGameAI(leelaz,KG,'SAI','KG', SAI322,KGnet,'B','testPlayDefault.sgf','LZ107_SAI138_B-1.sgf',startFromMove='150')
# gameTest.playDefault(literal,literalKG,7.5,verbose=True)
# print('gtp result of the game',gameTest.final_score)
# print('colorwinner',gameTest.winnerColor)
# print('winner',gameTest.gameWinner)


# # PRINT SGF (for testing purposes)
# gameTest= GoGameAI(leelaz,KG,'SAI','KG', SAIa,KGnet,'B','testSGF_KG.sgf','')
# gameTest.startGame(literalSAI,literalKG,6.5)
# #gameTest.printSGF(gameTest.processOrd['2'],'KG')
# gameTest.printSGFOrdProcess('2')
# gameTest.closeTwoPlayerProcesses()



# # FEW ROUNDS (for testing purposes)
# #gameTest= GoGameAI(leelaz,KG,'SAI','KG', SAIa,KGnet,'B','testSGF_KG.sgf','')
# gameTest= GoGameAI(leelaz,KG,'LZ','KG', LZ107,KGnet,'B','testSGF_KG.sgf','/home/schroeder/Dropbox/ricerca_large/experiments_sai19x19_SGFs/2_baseline_games//LZ107_SAI138/LZ107_SAI138_B-1.sgf',startFromMove='150')
# literal=literalSAI+ ' --logfile temp_logLZ.txt '
# gameTest.startGame(literal ,literalKG,7.5)
# ToolsOrdPlayer=gameTest.ToolsOrdPlayer
# ToolsOrdPlayer['1'].showBoard(gameTest.processOrd['1'])
# ct=0
# #while gameTest.gameStatus=='ongoing':
# while ct<8:
#     ct=ct+1
#     ordmove=str(ct)
#     # gameTest.showBoard(gameTest.processOrd[gameTest.nextOrdPlayer],gameTest.typeAIOrdPlayer[gameTest.nextOrdPlayer])
#     ToolsOrdPlayer[gameTest.nextOrdPlayer].showBoard(gameTest.processOrd[gameTest.nextOrdPlayer])
#     print('player',gameTest.nextOrdPlayer,'is thinking on this board...')
#     gameTest.moveNext()
#     #gameTest.showBoard(gameTest.nextOrdPlayer,gameTest.typeAIOrdPlayer[gameTest.nextOrdPlayer])
# gameTest.closeTwoPlayerProcesses()

# # FEW ROUNDS, NO MOVENEXT (for testing purposes)
# gameTest= GoGameAI(KG,leelaz,'KG','LZ',KGnet,LZ107,'B','testSGF_KG.sgf','/home/schroeder/Dropbox/ricerca_large/experiments_sai19x19_SGFs/2_baseline_games//LZ107_SAI138/LZ107_SAI138_B-1.sgf',startFromMove='150')
# literal=literalSAI+ ' --logfile temp_logLZ.txt '
# gameTest.startGame(literalKG,literal,7.5)
# ToolsOrdPlayer=gameTest.ToolsOrdPlayer
# ToolsOrdPlayer['1'].showBoard(gameTest.processOrd['1'])
# ct=0
# #while gameTest.gameStatus=='ongoing':
# while ct<8:
#     ct=ct+1
#     ordmove=str(ct)
#     ToolsOrdPlayer[gameTest.nextOrdPlayer].showBoard(gameTest.processOrd[gameTest.nextOrdPlayer])
#     print('player',gameTest.nextOrdPlayer,'is thinking on this board...')
#     thisOrdPlayer=gameTest.nextOrdPlayer
#     thisProcess=gameTest.processOrd[thisOrdPlayer]
#     thisColor=gameTest.nextColor
#     thisTypeAI=gameTest.typeAIOrdPlayer[thisOrdPlayer]
#     print('player:',thisOrdPlayer)
#     move=gameTest.ToolsOrdPlayer[thisOrdPlayer].generateMove(thisProcess,thisColor,debugging=True)
#     if move=="resign":
#         gameTest.gameStatus='completed'
#     if move=="pass" and gameTest.lastMoveIsPass==1:
#         gameTest.gameStatus='completed'
#     if move=="pass":
#         gameTest.lastMoveIsPass=1
#     else:
#         gameTest.lastMoveIsPass=0
#     #inform the other player of the move
#     otherOrd=gameTest.otherOrdPlayer[thisOrdPlayer]
#     gameTest.ToolsOrdPlayer[otherOrd].incorporateMove(gameTest.processOrd[otherOrd],move,thisColor)
#     #if the move terminated the game, set and return attributes referring to winner and result; otherwise, prepare the next move: switch nextOrdPlayer and nextColor
#     if gameTest.gameStatus=='completed':
#         gameTest.colorWhichHasResigned=thisColor if move=="resign" else 'counting points'
#         thisProcess.stdin.write("final_score\n")
#         thisProcess.stdin.flush()
#         while True:
#             outputFinalScore=thisProcess.stdout.readline()[:-1]
#             print('reading score...',outputFinalScore)
#             if len(outputFinalScore)>2:
#                 break
#         # print('final_score from leelaz',outputFinalScore)
#         gameTest.final_score=outputFinalScore if gameTest.colorWhichHasResigned=='counting points' else '= '+gameTest.otherColor[gameTest.colorWhichHasResigned]+'+R'
#         gameTest.returnAllResults()
#     else:
#         gameTest.nextOrdPlayer=gameTest.otherOrdPlayer[thisOrdPlayer]
#         gameTest.nextColor=gameTest.otherColor[thisColor]   
# gameTest.closeTwoPlayerProcesses()


# # PLAY AND GET FEEDBACK (for testing purposes)
# gameTest= GoGameAI(leelaz,KG,'SAI','KG', SAIa,KGnet,'B','testPlayDefault.sgf','')
# gameTest.startGame(literalSAI,literalKG,6.5)
# ct=0
# while gameTest.gameStatus=='ongoing':
#         ct=ct+1
#         ordmove=str(ct)
#         if gameTest.typeAIOrdPlayer[gameTest.nextOrdPlayer]=='SAI':
#             params=gameTest.extractParametersCurrentBoard(gameTest.processOrd[gameTest.nextOrdPlayer])
#             print('parameters at move '+ordmove+' according the SAI net playing ('+gameTest.colorOrdPlayer[gameTest.nextOrdPlayer]+')',params)
#         gameTest.moveNext()
# #gameTest.printSGF(gameTest.processOrd[gameTest.nextOrdPlayer],gameTest.typeAIOrdPlayer[gameTest.nextOrdPlayer])
# gameTest.printSGF(gameTest.processOrd['2'],gameTest.typeAIOrdPlayer['2'])
# gameTest.closeTwoPlayerProcesses()
# print('the final score is',gameTest.final_score)


# /home/schroeder/SAI/bin/katago gtp -model /home/schroeder/Dropbox/ricerca_large/katago/example/g170-b30c320x2-s2271129088-d716970897.bin.gz -config default_gtp.cfg -override-config maxVisits=10,allowResignation=true,resignThreshold=-0.96,resignConsecTurns=1
# loadsgf /home/schroeder/Dropbox/ricerca_large/experiments_sai19x19_SGFs/2_baseline_games//LZ107_SAI138/LZ107_SAI138_B-1.sgf 150
# play B B19
# genmove W

# #test GoAITools
# toolTest= GoAITools(KG,'KG', KGnet)
# process=toolTest.AIProcess(literalKG,currentBoard='',startFromMove='')
# toolTest.showBoard(process)
# move=toolTest.generateMove(process,'B',debugging=True)
# toolTest.closeAIProcess(process)


# # ONE MOVE (for testing purposes) # BUG
# gameTest= GoGameAI(KG,leelaz,'KG','LZ',KGnet,LZ107,'B','testSGF_KG.sgf','',startFromMove='')
# gameTest.startGame(literalKG,literalSAI,7.5)
# ToolsOrdPlayer=gameTest.ToolsOrdPlayer
# toolTest=ToolsOrdPlayer['1']
# process=gameTest.processOrd['1']
# toolTest.showBoard(process)
# print('player 1 is thinking on this board...')
# print('player: 1')
# move=toolTest.generateMove(process,'B',debugging=True)
# gameTest.closeTwoPlayerProcesses()

# # ONE MOVE (for testing purposes) # WORKS
# gameTest= GoGameAI(KG,leelaz,'KG','LZ',KGnet,LZ107,'B','testSGF_KG.sgf','',startFromMove='')
# #gameTest.startGame(literalKG,literalSAI,7.5)
# ToolsOrdPlayer=gameTest.ToolsOrdPlayer
# toolTest=ToolsOrdPlayer['1']
# gameTest.AIOrdProcess('1',literalKG)
# process=gameTest.processOrd['1']
# toolTest.setKomi(process,7.5)
# toolTest.showBoard(process)
# print('player 1 is thinking on this board...')
# print('player: 1')
# move=toolTest.generateMove(process,'B',debugging=True)
# toolTest.closeAIProcess(process)
