from cell import Cell

class Board:
    '''Represents the Santorini board, a 5x5 grid of cells'''
    def __init__(self):
        self._cells = [[Cell(x, y) for y in range(5)] for x in range(5)]
    
    def get_specific_cell(self, x, y):
        '''Returns the cell at the specified x, y coordinate'''
        return self._cells[x][y]
    
    def set_worker_at_cell(self, worker_name, x, y):
        '''Sets a given worker name at the cells of the given x, y coordinate'''
        cell = self.get_specific_cell(x, y)
        cell.occupy(worker_name)
    
    def in_bounds(self, x, y):
        '''Returns True if the given x, y coordinates are in bound with the board'''
        return 5 > x >= 0 and 5 > y >= 0
    
    def win_condition_satisfied(self):
        '''Returns True if there is a worker on a cell of height 3'''
        for row in self._cells:
            for cell in row:
                if cell.get_height() == 3 and cell.is_occupied():
                    return True
        return False
    
    def __str__(self):
        string = ""
        for row in self._cells:
            string += "+--+--+--+--+--+\n"
            row_string = ""
            for cell in row:
                if cell.is_occupied():
                    row_string += f"|{cell.get_height()}{cell.get_occupying_worker()}"
                else:
                    row_string += f"|{cell.get_height()} "
            string += row_string + "|\n"
        string += "+--+--+--+--+--+"
        return string