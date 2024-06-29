from decimal import setcontext, BasicContext
import tkinter as tk
import tkinter.messagebox
from memento import Originator, CareTaker
from game import GameState
from tkmacosx import Button
from turn import HumanTurn, RandomTurn, HeuristicTurn
from observer import Subject, EndGameObserver

setcontext(BasicContext)

class SantoriniGUI(Subject):
    '''Game Manager as a GUI'''

    def __init__(self, playerWhite_type='human', playerBlue_type='human', memento=True, score_display=False):
        super().__init__()
        self._game = GameState(playerWhite_type, playerBlue_type, memento, score_display)
        self._game_observer = EndGameObserver()
        self.attach(self._game_observer)
        self._memento = memento
        if memento:
            self._originator = Originator(self)
            self._caretaker = CareTaker(self._originator)
        self._score_display = score_display
        self._player = self._alternate_player()
        self._game.set_curr_player(self._player)
        self.buttons = []

        self._window = tk.Tk()
        self._window.title("Santorini")

        # Display turn info
        self._info_frame = tk.Frame(self._window)
        self._info_frame.grid(row=0, column=3, columnspan=3)
        self._display_turn_info()

        # Display board
        self._board_frame = tk.Frame(self._window)
        self._board_frame.grid(row=2, column=1, columnspan=8, sticky="ew")
        self._display_board()

        # Display next/undo/redo if enabled
        if self._memento:
            self._memento_frame = tk.Frame(self._window)
            self._memento_frame.grid(row=0, column=1, columnspan=2)
            self._display_memento()
        else:
            self._player_turn()

        # Display score if enabled
        self._score_frame = tk.Frame(self._window)
        self._score_frame.grid(row=0, column=6, columnspan=5)
        self._display_score()

        self._window.mainloop()

    # Update state to the next round and display on window
    def _next_round(self):
        self._increment_turn_count()
        self._player = self._alternate_player()
        self._game.set_curr_player(self._player)
        self._display_board()
        self._display_turn_info()
        self._display_score()
        if self._memento:
            self._display_memento()
        else:
            self._player_turn()
        self.check_game_end(self._player)

    # Call appropriate turn template based on the player's type
    def _player_turn(self):
        if self._player.type == 'human':
            HumanTurn(self._game.get_board(), self._player, self).run()
        elif self._player.type == 'random':
            RandomTurn(self._game.get_board(), self._player, self).run()
        elif self._player.type == 'heuristic':
            HeuristicTurn(self._game.get_board(), self._player, self).run()

    # Change players
    def _alternate_player(self):
        if self._game.get_turncount() % 2 == 1:
            return self._game.get_white()
        else:
            return self._game.get_blue()
        
    # Display board
    def _display_board(self):
        self.buttons.clear()
        for row in range(5):
            row_buttons = []
            for col in range(5):
                cell = self._game.get_board().get_specific_cell(row, col)
                text = ''
                height = cell.get_height()
                if cell.is_occupied():
                    text += f"{cell.get_occupying_worker()}"
                while height > 0:
                    text += '\n[ ]'
                    height -= 1
                button = Button(self._board_frame, text=text, width=100, height=100)
                button.grid(row=row, column=col)
                row_buttons.append(button)
            self.buttons.append(row_buttons)
        
    def check_game_end(self, player, othercondition=False):
        '''Prompt user to play again and either restarts or exits game'''
        if self._game.get_board().win_condition_satisfied() or player.workers_cant_move() or othercondition:
            if player.color == 'white':
                winner = 'blue'
            else:
                winner = 'white'
            self.notify("end", winner)
            if self._game_observer.restart():
                # Reset game state
                self._game = GameState(self._game.get_white().type, self._game.get_blue().type, self._memento, self._score_display)
                self._game_observer = EndGameObserver()
                self.attach(self._game_observer)
                self._player = self._alternate_player()
                self._game.set_curr_player(self._player)
                # Update GUI
                self._display_board()
                self._display_turn_info()
                self._display_score()
                if self._memento:
                    self._display_memento()
                else:
                    self._player_turn()
            else:
                self._window.destroy()
                exit(0)
    
    def move(self, row, col, old_row, old_col, worker):
        '''Move specified worker to a new cell'''
        # Remove worker from old cell
        old_cell = self._game.get_board().get_specific_cell(old_row, old_col)
        old_cell.remove()
        
        # Move worker to new cell
        new_cell = self._game.get_board().get_specific_cell(row, col)
        new_cell.occupy(worker.name)
        worker.update_pos(row, col)
        self._display_board()

        # Remove all button functionality and bind build function to valid adjacent buttons
        self._unbind_buttons()
        adjacent_positions = [
            (row-1, col-1), (row-1, col), (row-1, col+1),
            (row, col-1),                 (row, col+1),
            (row+1, col-1), (row+1, col), (row+1, col+1)
        ]
        for adj_row, adj_col in adjacent_positions:
            if self._game.get_board().in_bounds(adj_row, adj_col):
                adj_cell = self._game.get_board().get_specific_cell(adj_row, adj_col)
                if adj_cell.is_valid_build():
                    self.buttons[adj_row][adj_col].bind("<Button-1>", lambda event, r=adj_row, c=adj_col: self.build(r, c))
                    self.buttons[adj_row][adj_col].config(bg="#FFFFE0")

    def build(self, row, col):
        '''Build in the specified cell'''
        cell = self._game.get_board().get_specific_cell(row, col)
        if cell.is_valid_build():
            cell.build()
            self._next_round()

    # Display undo/redo/undo buttons
    def _display_memento(self):
        def _undo():
            if self._caretaker.history_isempty():
                self._messagebox("No past rounds to undo. Please select a different option")
            else:
                # Save the current state in case user wants to redo
                self._originator.change_state(self._game)
                self._caretaker.do_redo()
                # Restore the undo game state
                self._game = self._caretaker.undo()
                self._player = self._game.get_curr_player()
                # Update window display to restored game state
                self._display_board()
                self._display_turn_info()
                self._display_score()
                self._require_memento_selection()
        
        def _redo():
            if self._caretaker.undone_isempty():
                self._messagebox("No past rounds to redo. Please select a different option")
            else:
                # Save the current state in case user wants to undo again
                self._originator.change_state(self._game)
                self._caretaker.do()
                # Restore the redo game state
                self._game = self._caretaker.redo()
                self._player = self._game.get_curr_player()
                # Update window display to restored game state
                self._display_board()
                self._display_turn_info()
                self._display_score()
                self._require_memento_selection()
            
        def _next():
            # Save the current state
            self._originator.change_state(self._game)
            self._caretaker.do()
            self._caretaker.clear_undone()
            _destory_memento()
            self._player_turn()

        def _destory_memento():
            for widget in self._memento_frame.winfo_children():
                widget.destroy()

        self._require_memento_selection()
        tk.Button(self._memento_frame, text="Undo",
                command=_undo).grid(row=1, column=1)
        tk.Button(self._memento_frame,
                text="Redo",
                command=_redo).grid(row=1, column=2)
        tk.Button(self._memento_frame,
                text="Next",
                command=_next).grid(row=1, column=4)

    # Alerts player to select undo/redo/next before they can make a move
    def _require_memento_selection(self):
        for row in range(5):
                for col in range(5):
                    self.buttons[row][col].bind("<Button-1>", lambda event: self._messagebox("Please select undo/redo/next"))
    
    # Replaces any previous button functionality and prevents player from selecting these buttons
    def _unbind_buttons(self):
        for row in range(5):
            for col in range(5):
                self.buttons[row][col].bind("<Button-1>", lambda event: self._messagebox("You cannot select this space"))

    def _messagebox(self, message):
        tkinter.messagebox.showwarning(title=None, message=message)

    def _display_turn_info(self):
        info = f"Turn: {self._game.get_turncount()}, {self._player.color} ({self._player.workers})"
        info_label = tk.Label(self._info_frame, text=str(info))
        info_label.grid(row=0, column=0, padx=5, pady=5)

    def _display_score(self):
        if self._score_display:
            data_white = self.get_curr_move_data(self._game.get_white())
            score_white = f'white score: {data_white[0]}, {data_white[1]}, {data_white[2]}'
            score_white_label = tk.Label(self._score_frame, text=str(score_white))
            score_white_label.grid(row=0, column=0, padx=2, pady=2)

            data_blue = self.get_curr_move_data(self._game.get_blue())
            score_blue = f'blue score: {data_blue[0]}, {data_blue[1]}, {data_blue[2]}'
            score_blue_label = tk.Label(self._score_frame, text=str(score_blue))
            score_blue_label.grid(row=1, column=0, padx=2, pady=2)
        
    def _increment_turn_count(self):
        self._game.increment_turn_count()
    
    def _calculate_curr_height_score(self, player):
        '''Calculates current height score usign workers' current position'''
        workers = player.get_workers()
        cell1 = self._game.get_board().get_specific_cell(workers[0].x, workers[0].y)
        cell2 = self._game.get_board().get_specific_cell(workers[1].x, workers[1].y)

        return cell1.get_height() + cell2.get_height()
    
    def _calculate_curr_center_score(self, player):
        '''Calculates current center score using workers' current position'''
        workers = player.get_workers()

        return workers[0].get_ring_level(workers[0].x, workers[0].y) \
        + workers[1].get_ring_level(workers[1].x, workers[1].y)
    
    def _calculate_curr_distance(self, worker1, worker2):
        return max(abs(worker2.y - worker1.y), abs(worker2.x - worker1.x))

    def _calculate_curr_distance_score(self, player):
        '''Calculates current distance score using all workers' positions'''
        players = self.get_both_players()
        
        white_workers = players[0].get_workers()
        worker_A = white_workers[0]
        worker_B = white_workers[1]

        blue_workers = players[1].get_workers()
        worker_Y = blue_workers[0]
        worker_Z = blue_workers[1]

        distance_AZ = self._calculate_curr_distance(worker_A, worker_Z)
        distance_BY = self._calculate_curr_distance(worker_B, worker_Y)

        distance_AY = self._calculate_curr_distance(worker_A, worker_Y)
        distance_BZ = self._calculate_curr_distance(worker_B, worker_Z)
        if player.color == 'white':
            return 8 - (min(distance_BY, distance_AY) + min(distance_BZ, distance_AZ))
        elif player.color == 'blue':
            return 8 - (min(distance_AZ, distance_AY) + min(distance_BY, distance_BZ))
        
    def get_curr_move_data(self, player):
        '''Creates a tuple containing current height, center, distance score'''
        height_score = self._calculate_curr_height_score(player)
        center_score = self._calculate_curr_center_score(player)
        distance_score = self._calculate_curr_distance_score(player)
        return [height_score, center_score, distance_score]
    
    def get_scoredisplay(self):
        '''Returns True if score display is enabled'''
        return self._score_display
    
    def get_both_players(self):
        '''Returns both players'''
        return self._game.get_players()