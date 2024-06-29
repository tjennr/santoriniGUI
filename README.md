# santoriniGUI

A GUI representation of the Santorini 2-player board game. \
Implemented in Python and tkinter following OOP structure with various design patterns.

## Game Rules
Each player has 2 workers:
* Player White has workers A and B
* Player Blue has workers Z and Y
  
The goal is to build a building of height 3 and then move a worker on top of it. \
In each turn, players will choose a worker first to move then build in an adjacent cell. Workers can move to any adjacent cell so long as the cell height is not > 1 taller than the worker's current cell. Valid cells to move/build to will be highlighted in yellow.

## How to Run
arg 1 = player White type; human, random, heuristic \
arg 2 = player Blue type; human, random, heuristic \
arg 3 = enable undo/redo feature; on, off \
arg 4 = enable score display; on, off

python main.py [player white type] [player blue type] [undo/redo on/off] [score display on/off]

## Design Patterns
Implements various OOP design patterns including the observer, template, memento, and command patterns.
* Observer: observes game end state
* Template: template for different player types' behaviors
* Memento: allows for undo/redo feature
* Command: allows Player objects to call move and build
