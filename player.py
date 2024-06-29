DIRECTION = {
    'n': {'y': 0, 'x': -1},
    'ne': {'y': 1, 'x': -1},
    'e': {'y': 1, 'x': 0},
    'se': {'y': 1, 'x': 1},
    's': {'y': 0, 'x': 1},
    'sw': {'y': -1, 'x': 1},
    'w': {'y': -1, 'x': 0},
    'nw': {'y': -1, 'x': -1},
}

class Player:
    '''A player with 2 workers, a specified player type, and a reference to the board and game manager'''
    def __init__(self, board, player_type):
        self.workers = f'{self._worker1.name}{self._worker2.name}'
        self.type = player_type
        self._board = board
        # self._manager = manager
        self._board.set_worker_at_cell(self._worker1.name, self._worker1.x, self._worker1.y)
        self._board.set_worker_at_cell(self._worker2.name, self._worker2.x, self._worker2.y)

    def select_worker(self, name):
        '''Returns the player's worker given a worker name'''
        if self._worker1.name == name:
            return self._worker1
        elif self._worker2.name == name:
            return self._worker2

    def check_valid_worker(self, worker):
        '''Returns True if the given worker is this player's worker'''
        if worker == self._worker1.name or worker == self._worker2.name:
            return True
        else:
            return False
    
    def workers_cant_move(self):
        '''Returns True if both of this player's workers cannot move'''
        return self._worker1.no_moves_left(self._board) and self._worker2.no_moves_left(self._board)
    
    def get_workers(self):
        '''Returns both workers'''
        return [self._worker1, self._worker2]
    
    # def move(self, worker, direction):
    #     '''Calls move command'''
    #     move_command = MoveCommand(self._manager, worker, direction)
    #     move_command.execute()

    # def build(self, worker, direction):
    #     '''Calls build command'''
    #     build_command = BuildCommand(self._manager, worker, direction)
    #     build_command.execute()


class PlayerWhite(Player):
    def __init__(self, board, player_type):
        self.color = 'white'
        self._worker1 = Worker('A', 3, 1)
        self._worker2 = Worker('B', 1, 3)
        super().__init__(board, player_type)


class PlayerBlue(Player):
    def __init__(self, board, player_type):
        self.color = 'blue'
        self._worker1 = Worker('Y', 1, 1)
        self._worker2 = Worker('Z', 3, 3)
        super().__init__(board, player_type)
    
class Worker:
    '''A worker with an x, y coordinate that corresponds with the worker's position on the game board'''
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def update_pos(self, x, y):
        '''Updates position of worker with the given x, y coordinates'''
        self.x = x
        self.y = y

    def no_moves_left(self, board):
        '''Returns True if worker is not able to move'''
        curr_cell = board.get_specific_cell(self.x, self.y)
        for dir in DIRECTION:
            new_x = self.x + DIRECTION[dir]['x']
            new_y = self.y + DIRECTION[dir]['y']
            if board.in_bounds(new_x, new_y):
                new_cell = board.get_specific_cell(new_x, new_y)
                if new_cell.is_valid_move(curr_cell):
                    return False
        return True
    
    def enumerate_moves(self, board):
        '''Returns dict of available moves and builds'''
        available_move_and_builds = {}
        curr_cell = board.get_specific_cell(self.x, self.y)
        # Iterate through every move direction 
        for move_dir in DIRECTION:
            move_x = self.x + DIRECTION[move_dir]['x']
            move_y = self.y + DIRECTION[move_dir]['y']
            if board.in_bounds(move_x, move_y):
                # Get new coordinates once move is performed
                new_cell = board.get_specific_cell(move_x, move_y)
                if new_cell.is_valid_move(curr_cell):
                    available_builds = []
                    # Iterate through every build direction after move has been performed
                    for build_dir in DIRECTION:
                        new_build_x = move_x + DIRECTION[build_dir]['x']
                        new_build_y = move_y + DIRECTION[build_dir]['y']
                        if board.in_bounds(new_build_x, new_build_y):
                            new_build_cell = board.get_specific_cell(new_build_x, new_build_y)
                            if new_build_cell.is_valid_build(self.x, self.y):
                                # Append all possible builds to a list
                                available_builds.append(build_dir)
                        # Append all possible builds to the move direction key
                        available_move_and_builds[move_dir] = available_builds
        return available_move_and_builds
    
    def get_ring_level(self, x_pos, y_pos):
        '''Returns the ring level'''
        # center
        if x_pos == 2 and y_pos == 2:
            return 2
        # top row of 2nd inner ring
        elif x_pos == 1 and 1 <= y_pos <= 3:
            return 1
        # middle row of 2nd inner ring
        elif x_pos == 2 and (y_pos == 1 or y_pos == 3):
            return 1
        # bottom row of 2nd inner ring
        elif x_pos == 3 and 1 <= y_pos <= 3:
            return 1
        # top row of outer most ring
        elif x_pos == 0 and 0 <= y_pos <= 4:
            return 0
        # second row of outer most ring
        elif x_pos== 1 and (y_pos == 0 or y_pos == 4):
            return 0
        # third row of outer most ring
        elif x_pos == 2 and (y_pos == 0 or y_pos == 4):
            return 0
        # fourth row of outer most ring
        elif x_pos == 3 and (y_pos == 0 or y_pos == 4):
            return 0
        # bottom row of outer most ring
        elif x_pos == 4 and 0 <= y_pos <= 4:
            return 0