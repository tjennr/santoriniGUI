import random
from player import DIRECTION
from command import MoveCommand, BuildCommand
import tkinter.messagebox

class TurnTemplate:
    '''A template for a turn, which can be human-made, randomly-made, or heuristically-made'''
    def __init__(self, board, player, gui):
        self._board = board
        self._player = player
        self._gui = gui

    def _move(self, row, col, old, new, worker):
        '''Calls move command'''
        move_command = MoveCommand(self._gui)
        move_command.execute(row, col, old, new, worker)

    def _build(self, row, col):
        '''Calls build command'''
        build_command = BuildCommand(self._gui)
        build_command.execute(row, col)

    def run(self):
        raise NotImplementedError("Subclasses must implement the run method.")


class HumanTurn(TurnTemplate):
    '''Takes user input to decide what worker to use and what direction to move/build to'''
    def run(self):
        self._bind_select()

    # Binds select function to each button
    def _bind_select(self):
        for row in range(5):
            for col in range(5):
                self._gui.buttons[row][col].bind("<Button-1>", lambda event, r=row, c=col: self._verify_valid_worker(r, c))

    # Verifies that selected worker is valid before allowing actual selection
    def _verify_valid_worker(self, row, col):
        cell = self._board.get_specific_cell(row, col)
        workername = cell.get_occupying_worker()

        if self._player.color == 'white' and (workername == 'Y' or workername == 'Z'):
            tkinter.messagebox.showwarning(title=None, message=("That is not your worker"))
        elif self._player.color == 'blue' and (workername == 'A' or workername == 'B'):
            tkinter.messagebox.showwarning(title=None, message=("That is not your worker"))
        elif not self._player.check_valid_worker(workername):
            tkinter.messagebox.showwarning(title=None, message=("Not a valid worker"))
        else:
            worker = self._player.select_worker(workername)
            if worker.no_moves_left(self._board):
                tkinter.messagebox.showwarning(title=None, message=("That worker cannot move"))
                return
            self._select_worker(row, col, workername)

    def _select_worker(self, row, col, worker):        
        cell = self._board.get_specific_cell(row, col)
        worker = self._player.select_worker(worker)
        
        # Remove all button functionality and bind move function to valid adjacent buttons
        self._gui._unbind_buttons()
        adjacent_positions = [
            (row-1, col-1), (row-1, col), (row-1, col+1),
            (row, col-1),                 (row, col+1),
            (row+1, col-1), (row+1, col), (row+1, col+1)
        ]
        for adj_row, adj_col in adjacent_positions:
            if self._board.in_bounds(adj_row, adj_col):
                adj_cell = self._board.get_specific_cell(adj_row, adj_col)
                if adj_cell.is_valid_move(cell):
                    self._gui.buttons[adj_row][adj_col].bind("<Button-1>", lambda event, 
                                                         r=adj_row, c=adj_col, old_r=row, old_c=col, w=worker: self._move(r, c, old_r, old_c, w))
                    self._gui.buttons[adj_row][adj_col].config(bg="#FFFFE0")


class RandomTurn(TurnTemplate):
    '''Randomly decides which worker to use, where to move, and where to build to'''
    def run(self):
        # Randomly choose worker
        worker = random.choice(self._player.get_workers())

        # Get all possible moves and corresponding build directions for that worker
        worker_moves = worker.enumerate_moves(self._board)

        # If no moves available...
        if worker_moves == {}:
            # Try to move other worker
            workers = self._player.get_workers()
            if worker == workers[0]:
                worker = workers[1]
            else:
                worker = workers[0]
            # Get other worker's possible moves
            worker_moves = worker.enumerate_moves(self._board)
            # If other worker also has no moves left, end the game
            if worker_moves == {}:
                self._gui.check_game_end(self._player, othercondition=True)
                return
            
        # Randomly choose move direction, represented by the keys in the dictionary
        move_dir = random.choice(list(worker_moves.keys()))

        # Randomly choose build direction, represented by the values of the move direction key
        build_dir = random.choice(worker_moves[move_dir])

        move_x = worker.x + DIRECTION[move_dir]['x']
        move_y = worker.y + DIRECTION[move_dir]['y']
        build_x = move_x + DIRECTION[build_dir]['x']
        build_y = move_y + DIRECTION[build_dir]['y']

        # Move and build in that given direction
        self._move(move_x, move_y, worker.x, worker.y, worker)
        self._build(build_x, build_y)


class HeuristicTurn(TurnTemplate):
    '''Calculates move score based on certain critera and moves worker that has the highest move score'''
    def run(self):
        # Get list containing the best move data
        best_move_data = self.get_best_move_data()

        # Assign corresponding data points in list to variables
        worker = best_move_data[0]
        move_dir = best_move_data[1]
        build_dir = best_move_data[2]
        height_score = best_move_data[3]
        center_score = best_move_data[4]
        distance_score = best_move_data[5]

        move_x = worker.x + DIRECTION[move_dir]['x']
        move_y = worker.y + DIRECTION[move_dir]['y']
        build_x = move_x + DIRECTION[build_dir]['x']
        build_y = move_y + DIRECTION[build_dir]['y']

        # Move player in best direction, build in best direction
        self._move(move_x, move_y, worker.x, worker.y, worker)
        self._build(build_x, build_y)

    def get_best_move_data(self):
        '''Iterates through every possible move and corresponding build direction and finds
        which combination would yield the highest move score. Returns a list containing the best
        worker to move, move direction, build direction, and height/center/distance scores'''

        # Get current player's workers
        workers = self._player.get_workers()

        # Initialize lists to keep track of best scores
        move_scores = []
        move_list = []
        best_moves_list = []

        # For each worker get all possible moves and corresponding build directions
        for worker in workers:
            worker_moves = worker.enumerate_moves(self._board)
            # For each possible move direction and for each possible build direction tied to the move direction..
            for move_dir in worker_moves.keys():
                for build_dir in worker_moves[move_dir]:
                    # Calculate where the new x/y coords would be and get that cell
                    move_x = worker.x + DIRECTION[move_dir]['x']
                    move_y = worker.y + DIRECTION[move_dir]['y']
                    build_x = move_x + DIRECTION[build_dir]['x']
                    build_y = move_y + DIRECTION[build_dir]['y']
                    move_to_cell = self._board.get_specific_cell(move_x, move_y)

                    # If the cell being moved to has a height of 3, don't perform any calculations,
                    # just return moving to that cell as the best direction, as it results in an instant win
                    if move_to_cell.get_height == 3:
                        return [worker, move_dir, build_dir, -1, -1, -1]

                    # Calculate scores
                    height_score = self._calculate_height_score(worker, move_x, move_y)
                    center_score = self._calculate_center_score(worker, move_x, move_y)
                    distance_score = self._calculate_distance_score(worker, move_x, move_y)
                    move_score = self._calculate_move_score(height_score, center_score, distance_score)

                    # Append all possible move scores to list of move scores
                    move_scores.append(move_score)

                    # Append all possible move/build directions for each worker to list
                    move_list.append((worker, move_score, move_dir, build_dir, height_score, center_score, distance_score))
        
        # Now that list is populated, find the max move score
        best_move_score = max(move_scores)

        # Go through each tuple in move_list, and only add tuples that posses the max move score to best_moves_list
        for entry in move_list:
            if entry[1] == best_move_score:
                best_moves_list.append(entry)

        # If there are multiple moves that yield max move score, randomly choose between one of them
        if len(best_moves_list) > 1:
            entry = random.choice(best_moves_list)
            best_worker = entry[0]
            best_move_dir = entry[2]
            best_build_dir = entry[3]
            height_score = entry[4]
            center_score = entry[5]
            distance_score = entry[6]
        elif len(best_moves_list) == 1:
            best_worker = best_moves_list[0][0]
            best_move_dir = best_moves_list[0][2]
            best_build_dir = best_moves_list[0][3]
            height_score = best_moves_list[0][4]
            center_score = best_moves_list[0][5]
            distance_score = best_moves_list[0][6]

        return [best_worker, best_move_dir, best_build_dir, height_score, center_score, distance_score]

    # Calculates height score after given worker is moved
    def _calculate_height_score(self, worker, move_x, move_y):
        workers = self._player.get_workers()

        if worker == workers[0]:
            other_worker = workers[1]
        else:
            other_worker = workers[0]

        # Get cell that worker would move to
        cell1 = self._board.get_specific_cell(move_x, move_y)

        # Get cell that other worker currently stands on
        cell2 = self._board.get_specific_cell(other_worker.x, other_worker.y)
        
        return cell1.get_height() + cell2.get_height()

    # Calculates center score after given worker is moved
    def _calculate_center_score(self, worker, move_x, move_y):
        workers = self._player.get_workers()

        if worker == workers[0]:
            other_worker = workers[1]
        else:
            other_worker = workers[0]

        return worker.get_ring_level(move_x, move_y) + other_worker.get_ring_level(other_worker.x, other_worker.y)

    # Calculates distance based on two workers' positions
    def _calculate_distance(self, worker1, worker2):
        return max(abs(worker2[1] - worker1[1]), abs(worker2[0] - worker1[0]))

    # Calculates distance score after given worker is moved
    def _calculate_distance_score(self, worker, move_x, move_y):
        players = self._gui.get_both_players()
        
        # Get workers associated with white player
        white_workers = players[0].get_workers()
        worker_A = white_workers[0]
        worker_B = white_workers[1]

        # Get workers associated with blue player
        blue_workers = players[1].get_workers()
        worker_Y = blue_workers[0]
        worker_Z = blue_workers[1]

        # Calculate distance based on if current worker being moved is A, B, Y, or Z
        if worker.name == worker_A.name:
            distance_AZ = self._calculate_distance((move_x, move_y), (worker_Z.x, worker_Z.y))
            distance_BY = self._calculate_distance((worker_B.x, worker_B.y), (worker_Y.x, worker_Y.y))

            distance_AY = self._calculate_distance((move_x, move_y), (worker_Y.x, worker_Y.y))
            distance_BZ = self._calculate_distance((worker_B.x, worker_B.y), (worker_Z.x, worker_Z.y))

            return 8 - (min(distance_BY, distance_AY) + min(distance_BZ, distance_AZ))
        elif worker.name == worker_B.name:
            distance_AZ = self._calculate_distance((worker_A.x, worker_A.y), (worker_Z.x, worker_Z.y))
            distance_BY = self._calculate_distance((move_x, move_y), (worker_Y.x, worker_Y.y))

            distance_AY = self._calculate_distance((worker_A.x, worker_A.y), (worker_Y.x, worker_Y.y))
            distance_BZ = self._calculate_distance((move_x, move_y), (worker_Z.x, worker_Z.y))

            return 8 - (min(distance_BY, distance_AY) + min(distance_BZ, distance_AZ))
        elif worker.name == worker_Y.name:
            distance_AZ = self._calculate_distance((worker_A.x, worker_A.y), (worker_Z.x, worker_Z.y))
            distance_BY = self._calculate_distance((worker_B.x, worker_B.y), (move_x, move_y))

            distance_AY = self._calculate_distance((worker_A.x, worker_A.y), (move_x, move_y))
            distance_BZ = self._calculate_distance((worker_B.x, worker_B.y), (worker_Z.x, worker_Z.y))

            return 8 - (min(distance_AZ, distance_AY) + min(distance_BY, distance_BZ))
        elif worker.name == worker_Z.name:
            distance_AZ = self._calculate_distance((worker_A.x, worker_A.y), (move_x, move_y))
            distance_BY = self._calculate_distance((worker_B.x, worker_B.y), (worker_Y.x, worker_Y.y))

            distance_AY = self._calculate_distance((worker_A.x, worker_A.y), (worker_Y.x, worker_Y.y))
            distance_BZ = self._calculate_distance((worker_B.x, worker_B.y), (move_x, move_y))

            return 8 - (min(distance_AZ, distance_AY) + min(distance_BY, distance_BZ))
    
    # Calculates move score using given height, center, and distance score
    def _calculate_move_score(self, height_score, center_score, distance_score):
        c1, c2, c3 = 3, 2, 1
        return c1 * height_score \
            + c2 * center_score \
            + c3 * distance_score