from board import Board
from player import PlayerWhite, PlayerBlue

class GameState:
    '''Stores a state of a game including the board, players, turn count, and score display'''
    def __init__(self, playerWhite_type, playerBlue_type, memento, score_display):
        self._board = Board()
        self._playerWhite = PlayerWhite(self._board, playerWhite_type)
        self._playerBlue = PlayerBlue(self._board, playerBlue_type)
        self._turn_count = 1
        self._memento = memento
        self._score_display = score_display

    def get_board(self):
        '''Returns the board'''
        return self._board
    
    def get_white(self):
        '''Returns player White'''
        return self._playerWhite
    
    def get_blue(self):
        '''Returns player Blue'''
        return self._playerBlue

    def get_players(self):
        '''Returns both players'''
        return [self._playerWhite, self._playerBlue]
    
    def get_turncount(self):
        '''Returns turn count'''
        return self._turn_count
    
    def get_memento(self):
        '''Returns memento'''
        return self._memento

    def get_scoredisplay(self):
        '''Returns True if the game is displaying the score'''
        return self._score_display
    
    def increment_turn_count(self):
        '''Increments the game's turn count'''
        self._turn_count += 1

    def set_curr_player(self, player):
        self._curr_player = player

    def get_curr_player(self):
        return self._curr_player