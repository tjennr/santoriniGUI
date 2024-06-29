from abc import ABC, abstractmethod

class Command(ABC):
    '''Abstract command interface'''
    def __init__(self, gui):
        self._gui = gui

    @abstractmethod
    def execute(self):
        pass

class MoveCommand(Command):
    '''Concrete command for move'''
    def execute(self, row, col, old, new, worker):
        self._gui.move(row, col, old, new, worker)

class BuildCommand(Command):
    '''Concrete command for build'''
    def execute(self, row, col):
        self._gui.build(row, col)