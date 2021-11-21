# ToolsForSAIAndFriends
This repository contains mainly Python tools to be used to run experiments on [SAI](https://github.com/sai-dev/sai), [Leela Zero](https://github.com/leela-zero/leela-zero), and [KataGo](https://github.com/lightvector/KataGo). Earlier versions of these tools have been used to conduct the experiments described in [this](https://arxiv.org/abs/1905.10863) paper. 

# GoGameAI

This contains the class **GoGameAI** which manages games between any pair of nets among SAI, Leela Zero and KataGo. The auxiliaty class **GoGameTools** is also implemented. 

The module comes with a script **toolGoAITools** containing examples of usage.

# toolsKataGoAnalysisEngine

This module contains some tools that facilitate using the [JSON-based analysis engine](https://github.com/lightvector/KataGo/blob/master/docs/Analysis_Engine.md) of KataGo: 

* three functions that export an sgf file to 
  * a Python list of lists, e.g. [["W","P5"],["B","P6"]]
  * a Python list of strings, e.g. ['["W","P5"]','["B","P6"]']
  * a string, e.g. '["W","P5"],["B","P6"]'
* a class **interfaceKataGoAnalysisEngine** that allows opening a session of the engine; then 3 methods allow requesting queries   
  * launchQueryAndReturn(), a low-level method that requires indicating a JSON query
  * analyse_listOfLists(), that requires indicating
    * a Python list of lists, e.g. [["W","P5"],["B","P6"]],
    * a turn to be analysed, 
    * the rules, 
    * the komi, and 
    * the point of view 
  * analyse_sgf(), that requires indicating
    * a sgf file, 
    * a turn to be analysed, 
    * the rules, 
    * the komi, and 
    * the point of view 

All methods return a Python dictionary with the same format as the JSON output of the engine.
 
 The module comes with a script **test_toolsKataGoAnalysisEngine.py** containing examples of usage.
