from errors import InvalidMoveError, GameOverError, InvalidParametersError
import random

class Faller:
    def __init__(self, column, colors):
        self.column = column
        self.row = -3
        self.colors = colors
        self.colors.reverse()
        self.state = 'Moving'

    def rotate(self) -> None:
        '''Rotates faller, each jewel drops down, bottom one goes to top'''
        if self:
            temp_var = self.colors[0]
            for l in range(len(self.colors) - 1):
                self.colors[l] = self.colors[l + 1]
            self.colors[len(self.colors) - 1] = temp_var

    def can_move_faller(self, board, direction) -> bool:
        '''checks if can move faller to the left or to the right'''
        new_column = self.column + (-1 if direction == 'left' else 1)
      
        if new_column < 1 or new_column > len(board.board[0]):  
            return False

        for i in range(len(self.colors)):
            row = self.row - i
            if 0 <= row < len(board.board):  
                if board.board[row][new_column - 1] != ' ': 
                    return False

        return True

    def move_faller(self, board, direction):
        '''moves faller to the left or right by changing faller column'''
        self.column += -1 if direction == 'left' else 1


class Board:
    def __init__(self, rows, columns):
        self.rows = rows + 3  # Add 3 buffer rows above the board
        self.columns = columns
        self.board = []
        self.faller = None
        self.status = False
        self.remaining_colors = []
        self.stored_faller_column = 0

    def get_board_state(self) -> list:
        '''Return the current board state'''
        return self.board

    def get_faller_state(self) -> Faller:
        '''Return the current faller state'''
        return self.faller

    def get_game_over_status(self) -> bool:
        '''returns the game over status for checking if game is over'''
        return self.status


    def clear_matches(self, matches: set) -> None:
        """Clear the flashing effect of the matched cells."""
        for r, c in matches:
            if '*' in self.board[r][c]:
                self.board[r][c] = self.board[r][c].strip('*')


    def check_matches(self) -> set:
        '''checks for matches in every direction, returns set of coordinates of the matches'''
        matches = set()

        # Check horizontal matches
        for r in range(self.rows):  # Include buffer rows
            for c in range(self.columns - 2):
                if self.board[r][c] != ' ' and self.board[r][c] == self.board[r][c + 1] == self.board[r][c + 2]:
                    matches.update({(r, c), (r, c + 1), (r, c + 2)})

        # Check vertical matches
        for c in range(self.columns):
            for r in range(self.rows - 2):  # Include buffer rows
                if self.board[r][c] != ' ' and self.board[r][c] == self.board[r + 1][c] == self.board[r + 2][c]:
                    matches.update({(r, c), (r + 1, c), (r + 2, c)})

        # Check diagonal matches (top-left to bottom-right)
        for r in range(self.rows - 2):  # Include buffer rows
            for c in range(self.columns - 2):
                if self.board[r][c] != ' ' and self.board[r][c] == self.board[r + 1][c + 1] == self.board[r + 2][c + 2]:
                    matches.update({(r, c), (r + 1, c + 1), (r + 2, c + 2)})

        # Check diagonal matches (top-right to bottom-left)
        for r in range(self.rows - 2):  # Include buffer rows
            for c in range(2, self.columns):
                if self.board[r][c] != ' ' and self.board[r][c] == self.board[r + 1][c - 1] == self.board[r + 2][c - 2]:
                    matches.update({(r, c), (r + 1, c - 1), (r + 2, c - 2)})

        return matches



    def add_remaining_colors(self) -> None:
        '''adds remaining colors to board when match happens partly off the board'''
        if self.remaining_colors:
            temp_row = 0
            for r in range(self.rows):
                if self.board[r][self.stored_faller_column - 1] != ' ':
                    temp_row = r - 1
                    break

                
            for c in range(len(self.remaining_colors)):
                self.board[temp_row - c][self.stored_faller_column - 1] = self.remaining_colors[c]

        self.remaining_colors = list()


    def settle_board(self) -> None:
        '''settles board by dropping down each jewel if there is empty space'''
        for c in range(self.columns):
            # Collect all non-space elements in the column, including from the buffer rows
            column_elements = [self.board[r][c] for r in range(self.rows) if self.board[r][c] != ' ']
            
            for r in range(self.rows):
                if r < self.rows - len(column_elements):
                    self.board[r][c] = ' '
                else:
                    self.board[r][c] = column_elements[r - (self.rows - len(column_elements))]
            
    
    def add_row(self, row: str) -> None:
        '''adds row to the board, used when creating board with contents'''
        self.board.append(list(row))
            

    def create_faller(self, column, colors) -> None:
        '''creates faller, sets it to the board's initialized faller object'''
        if column < 1 or column > self.columns:
            raise InvalidParametersError(f"Column {column} is out of bounds.")
        if len(colors) != 3:
            raise InvalidParametersError("A faller must have exactly three colors.")
        
        if self.faller is None:
            # Check if the top of the visible board (row 3) is blocked (game over condition)
            if self.board[3][column - 1] != ' ':
                self.status = True
                return

            # Create the faller
            self.faller = Faller(column, colors[:])
            
            # Place the faller at the first visible row (row 3)
            self.faller.row = 2

            # Immediately check if the faller can "land"
            next_row = self.faller.row + 1
            if next_row < self.rows and self.board[next_row][self.faller.column - 1] != ' ':
                self.faller.state = 'Landed'
        else:
            raise InvalidMoveError("A faller is already active.")


    def create_random_faller(self, grid_cols, jewel_types):
        """Create a random faller in a random column."""
        column = random.randint(1, grid_cols)
        colors = random.choices(jewel_types, k=3)
        self.create_faller(column, colors)
        
    def update_faller(self, command: str) -> None:
        '''Updates faller based on inputted direction, L, R, D, or C'''
        if self.status:
            raise GameOverError("Cannot update faller; the game is over.")
        
        if self.faller:
            if self.faller.state == 'Moving':
                if command == 'C':
                    next_row = self.faller.row + 1
                    if next_row + 1 < self.rows and self.board[next_row][self.faller.column - 1] == ' ':
                        return
                    else:
                        self.faller.state = 'Landed'
                        return
                if command == 'D':
                    next_row = self.faller.row + 1
                    if next_row < self.rows and self.board[next_row][self.faller.column - 1] == ' ':
                        if next_row + 1 < self.rows and self.board[next_row + 1][self.faller.column - 1] == ' ':
                            self.faller.row = next_row
                            self.faller.state = 'Moving'
                            return
                        self.faller.row = next_row
                        self.faller.state = 'Landed'
                        return
                    else:
                        self.faller.state = 'Landed'
                        return
                elif command == 'R':
                    next_row = self.faller.row + 1
                    if self.faller.can_move_faller(self, 'right'):
                        if next_row < self.rows and self.board[next_row][self.faller.column] == ' ':
                            self.faller.state = 'Moving'
                        else:
                            self.faller.state = 'Landed'
                        self.faller.move_faller(self, 'right')
                    return 

                elif command == 'L':
                    next_row = self.faller.row + 1
                    if self.faller.can_move_faller(self, 'left'):
                        if next_row < self.rows and self.board[next_row][self.faller.column - 2] == ' ':
                            self.faller.state = 'Moving'
                        else:
                            self.faller.state = 'Landed'
                            
                        self.faller.move_faller(self, 'left')
                    return
            
            elif self.faller.state == 'Landed':
                if '*' in self.board[self.faller.row - 1][self.faller.column - 1]:
                    return
                if command == 'D':
                    next_row = self.faller.row + 1
                    if next_row < self.rows and self.board[next_row][self.faller.column - 1] == ' ':
                        self.faller.state = 'Moving'
                        return
                    else:
                        self.freeze_faller()
                        return
                
                        
                elif command == 'R':
                    next_row = self.faller.row + 1
                    if self.faller.can_move_faller(self, 'right'):
                        if next_row < self.rows and self.board[next_row][self.faller.column] == ' ':
                            self.faller.state = 'Moving'
                        else:
                            self.faller.state = 'Landed'
                        self.faller.move_faller(self, 'right')
                    return 

                elif command == 'L':
                    next_row = self.faller.row + 1
                    if self.faller.can_move_faller(self, 'left'):
                        if next_row < self.rows and self.board[next_row][self.faller.column - 2] == ' ':
                            self.faller.state = 'Moving'
                        else:
                            self.faller.state = 'Landed'
                            
                        self.faller.move_faller(self, 'left')
                    return
        
        #else:
            #raise InvalidMoveError("No active faller to update.")
    def freeze_faller(self) -> None:
        """Freezes the current faller into the board."""
        if self.faller:
            for i in range(3):
                row = self.faller.row - i
                if row >= 0:
                    self.board[row][self.faller.column - 1] = self.faller.colors[i]
                else:
                    self.remaining_colors.append(self.faller.colors[i])

            # Check buffer rows for game over
            self.check_buffer_rows()

            self.faller = None




    def remove_marked_cells(self) -> None:
        '''remove the cells marked with * (matches)'''
        for r in range(self.rows):  # Include buffer rows
            for c in range(self.columns):
                if '*' in self.board[r][c]:
                    self.board[r][c] = ' '


    
    def create_empty_board(self) -> None:
        '''creates empty board if user specifies empty'''
        for r in range(self.rows):
            temp_list = list()
            for c in range(self.columns):
                temp_list.append(' ')
            self.board.append(temp_list)

    def set_matches(self, matches: set) -> None:
        '''Clear the matched cells by setting them to empty spaces'''
        for r, c in matches:
            if '*' in self.board[r][c]:
                return
            else: 
                self.board[r][c] = f'*{self.board[r][c]}*'

    def check_buffer_rows(self) -> None:
        """Check the buffer rows (top 3 rows) for non-empty cells to set game over."""
        for r in range(3):  # Buffer rows are the first 3 rows
            if any(cell != ' ' for cell in self.board[r]):
                self.status = True
                raise GameOverError("Game over: Buffer rows are occupied.")

