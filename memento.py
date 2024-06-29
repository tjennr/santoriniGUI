import copy

class Memento:
    '''Stores the santorini game state'''
    # State is the board data
    def __init__(self, state):
        self._state = state

    def get_state(self):
        '''Returns game state'''
        return self._state


class Originator:
    '''Stores a state which can be changed.
    Also saves states inside mementos and restores states from mementos'''
    def __init__(self, state):
        self._state = copy.deepcopy(state)

    def change_state(self, state):
        '''Changes the current state of the originator'''
        self._state = copy.deepcopy(state)

    def save(self):
        '''Creates an instance of a memento that stores self's state and returns the memento'''
        return Memento(self._state)

    def restore(self, memento):
        '''Restores its state from a given memento'''
        self._state = memento.get_state()

    def get_state(self):
        '''Returns state'''
        return self._state


class CareTaker:
    '''Works with mementos via the originator'''
    def __init__(self, originator):
        self._originator = originator
        self._history = []
        self._undone = []

    def do(self):
        '''Creates a memento from the originator's current state and
        appends it to the history list'''
        memento = self._originator.save()
        self._history.append(memento)

    def do_redo(self):
        '''Creates a memento from the originator's current state and
        appends it to the undone list'''
        memento = self._originator.save()
        self._undone.append(memento)

    def undo(self):
        '''Returns the last memento in history and restores it in originator's state'''
        memento = self._history.pop()
        try:
            self._originator.restore(memento)
            return memento.get_state()
        except Exception:
            self.undo()

    def redo(self):
        '''Returns the last memento in history and restores it in originator's state'''
        memento = self._undone.pop()
        try:
            self._originator.restore(memento)
            return memento.get_state()
        except Exception:
            self.redo()

    def history_isempty(self):
        '''Returns True if history list is empty'''
        if not len(self._history):
            return True
        return False
        
    def undone_isempty(self):
        '''Returns True if undone list is empty'''
        if not len(self._undone):
            return True
        return False

    def clear_undone(self):
        '''Clears the list of undone. Do this when player chooses "next"'''
        self._undone = []