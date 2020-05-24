# ToolsForSAIAndFriends
This repository contains mainly Python tools to be used to run experiments on [SAI](https://github.com/sai-dev/sai), [Leela Zero](https://github.com/leela-zero/leela-zero), and [KataGo](https://github.com/lightvector/KataGo). Earlier versions of these tools have been used to conduct the experiments described in [this](https://arxiv.org/abs/1905.10863) paper. 

# GoGameAI

This contains the class GoGameAI which manages games between any pair of nets among SAI, Leela Zero and KataGo

# toolsKataGoAnalysisEngine

This module contains some tools that facilitate using the [JSON-based analysis engine](https://github.com/lightvector/KataGo/blob/master/docs/Analysis_Engine.md) of KataGo: 
* three functions that export an sgf file to 
  * a Python list of lists 
  * a Python list of strings
  * a string
* a class **interfaceKataGoAnalysisEngine** that allows opening a session of the engine; a method then allows requesting queries indicating   * a sgf file, 
  * a turn to be analysed, 
  * the rules, 
  * the komi, and 
  * the point of view; 
 the method returns a Python dictionary with the same format as the JSON output of the engine.
 
 The module comes with a script **interfaceKataGoAnalysisEngine** containing an example of use.
