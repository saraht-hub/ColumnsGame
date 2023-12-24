import sys

class InvalidMoveError(Exception):
    '''Raised when user tries to make a faller in an invalid column'''
    pass

class GameOverError(Exception):
    '''Raised when the user tries to make a faller in a column that doesn't exist'''
    pass

class ColumnsGame():
    def __init__(self, r: int, c: int):
        self._r = r
        self._c = c

        self._begin_board = []
        self._board = []
        
        self._top_jewel = None
        self._mid_jewel = None
        self._bot_jewel = None

        self._faller_x = None
        self._top_y = None
        self._mid_y = None
        self._bot_y = None

        self._faller_col = None
        self._faller_type = None

    def get_bot_coords(self) -> tuple:
        return (self._bot_y,self._faller_x)
    
    def get_board(self) -> list[list[str]]:
        return self._board
    
    def get_mid_coords(self) -> tuple:
        return (self._mid_y,self._faller_x)
    
    def get_top_coords(self) -> tuple:
        return (self._top_y,self._faller_x)

    def create_board(self, command: str) -> list[list[str]]:
        '''Given the command to either make an empty or pre determined board, either returns an empty 
        list of list of ' ', or returns a list of lists of strings based on the pattern of the values given'''

        if self._c >= 3 and self._r >= 4:
            if command == 'EMPTY':
                for i in range(self._r+3):
                    curr_row = []
                    for j in range(self._c):
                        curr_row.append(' ')
                    self._board.append(curr_row)
            elif command == 'CONTENTS':
                self._board = self._begin_board
            self.gravity()
            self.matching()
            return self._board
        else:
            raise ValueError
        
    def content_board(self, board: list[list[str]]) -> list[list[str]]:
        '''Turns the patterns of strings given to the function into a list of list of strings with either
        the jewel color or a space'''
        top_jewel_line = [[' ']*self._c]
        mid_jewel_line = [[' ']*self._c]
        bot_jewel_line = [[' ']*self._c]
        self._begin_board = []
        self._begin_board.extend(top_jewel_line+mid_jewel_line+bot_jewel_line)
        for row in board:
            curr_row = []
            for i in range(len(row)):
                curr_row += row[i]
            self._begin_board.append(curr_row)
        return self._begin_board
        
    
    def faller_down(self) -> list[list[str]]:
        '''
        Checks if there is a value under the jewel, and if there is, the jewel moves down
        Goes from the bottom row to the top to make sure any jewels falling affects the jewel above it
        Changes the faller type to either landed or frozen depending on whether a jewel was already under it or not
        If the jewel isn't a faller, will automatically go all the way down
        '''
        for row in range(len(self._board)-1,-1,-1):
            for col in range(self._c):
                jewel = self._board[row][col]
                if row == self._bot_y and col == self._faller_x:
                    #if there is something under the faller
                    if self._bot_y == len(self._board)-1:
                        if self._faller_type == 'landed':
                            self._faller_type = 'frozen'
                        elif self._faller_type == 'frozen':
                            self._reset_faller()
                        else:
                            self._faller_type = 'landed'
                    elif self._board[self._bot_y+1][col] != ' ':
                        if self._faller_type == 'landed':
                            self._faller_type = 'frozen'
                        elif self._faller_type == 'frozen':
                            self._reset_faller()
                        else:
                            self._faller_type = 'landed'
                    #if space under is empty
                    else:
                        self._board[row+1][col] = jewel
                        self._board[row][col] = self._mid_jewel
                        self._board[row-1][col] = self._top_jewel
                        self._board[row-2][col] = ' '
                        self._bot_y, self._mid_y, self._top_y = self._bot_y+1, self._mid_y+1,self._top_y+1
                        if self._bot_y == len(self._board)-1:
                            self._faller_type = 'landed'
                        elif self._board[self._bot_y+1][col] != ' ':
                            self._faller_type = 'landed'
        return self._board
    
    def gravity(self) -> list[list[str]]:
        '''All the non-faller jewels will automatically go as far down as they can before landing on another jewel'''
        if self._faller_type == None or self._faller_type == 'frozen':
            while True:
                no_empty_under = True
                for row in range(len(self._board)-2,-1,-1):
                    for col in range(self._c):
                        curr_val = self._board[row][col]
                        if curr_val != ' ':
                            if self._board[row+1][col] == ' ':
                                self._board[row+1][col] = curr_val
                                self._board[row][col] = ' '
                                no_empty_under = False
                if no_empty_under == True:
                    return self._board
    
    def create_faller(self, command: str) -> list[list[str]]:
        '''Creates a faller on the top 3 rows of the board and assigns the location of each faller to an x and y value
        Assigns the faller type as falling automatically'''
        if self.check_for_game_over() == False:
            if self._faller_type == None or self._faller_type == 'frozen':
                self._faller_type = 'falling'
                command = command.split(' ')
                faller_col = int(command[1])-1
                
                if faller_col < self._c:
                    self._faller_x = faller_col
                    self._bot_y = 2
                    self._mid_y = 1
                    self._top_y = 0

                    #bookmark the jewels
                    self._bot_jewel = command[4]
                    self._mid_jewel = command[3]
                    self._top_jewel = command[2]

                    #add jewels to proper column location
                    self._board[self._bot_y][self._faller_x] = self._bot_jewel
                    self._board[self._mid_y][self._faller_x] = self._mid_jewel
                    self._board[self._top_y][self._faller_x] = self._top_jewel

                    self.faller_down()
                    return self._board
                else:
                    raise InvalidMoveError
        else:
            raise GameOverError
    
    def move_faller_right(self) -> list[list[str]]:
        '''
        If there are no jewels to the right of the bottom jewel, then the faller will move right
        If moving the faller right lands it right on top of a jewel, faller becomes landed status
        '''
        if self.check_for_game_over() == False:
            if self._faller_type != 'frozen' and self._faller_type != None:
                if self.can_move('right') == True:
                    #fills previous pos with empty space;
                    self._board[self._bot_y][self._faller_x] = ' '
                    self._board[self._mid_y][self._faller_x] = ' '
                    self._board[self._top_y][self._faller_x] = ' '

                    #moves all jewels in faller to the right
                    self._faller_x += 1
                    self._board[self._top_y][self._faller_x] = self._top_jewel
                    self._board[self._mid_y][self._faller_x] = self._mid_jewel
                    self._board[self._bot_y][self._faller_x] = self._bot_jewel

                    if self._bot_y == self._r + 2:
                        self._faller_type = 'landed'
                    elif self._board[self._bot_y+1][self._faller_x] != ' ':
                        self._faller_type = 'landed'
            return self._board
        else:
            raise GameOverError
        
    
    def move_faller_left(self) -> list[list[str]]:
        '''
        If there are no jewels to the left of the bottom jewel, the faller will move left
        If moving the faller left lands it on top of a jewel, faller becomes landed status
        '''
        if self.check_for_game_over() == False:
            if self._faller_type != 'frozen' and self._faller_type != None:
                    if self.can_move('left') == True:
                        #fills previous pos with empty space;
                        self._board[self._bot_y][self._faller_x] = ' '
                        self._board[self._mid_y][self._faller_x] = ' '
                        self._board[self._top_y][self._faller_x] = ' '

                        #moves all jewels in faller to the right
                        self._faller_x -= 1
                        self._board[self._top_y][self._faller_x] = self._top_jewel
                        self._board[self._mid_y][self._faller_x] = self._mid_jewel
                        self._board[self._bot_y][self._faller_x] = self._bot_jewel
                    if self._bot_y == self._r + 2:
                        self._faller_type = 'landed'
                    elif self._board[self._bot_y+1][self._faller_x] != ' ':
                        self._faller_type = 'landed'
            return self._board
        else:
            raise GameOverError
    def can_move(self, direction: str) -> bool:
        '''Checks if there are any jewels next to the bottom faller jewel'''
        if direction == 'right':
            if self._faller_x+1 < self._c:
                if self._board[self._bot_y][self._faller_x+1] != ' ':
                    return False
                else:
                    return True
        if direction == 'left':
            if self._faller_x-1 >= 0:
                if self._board[self._bot_y][self._faller_x-1] != ' ':
                    return False
                else:
                    return True
    
    def get_faller_status(self) -> str:
        '''Returns whether the faller is falling, landed, or frozen'''
        return self._faller_type
    
    def rotate_faller(self) -> list[list[str]]:
        '''
        Moves the top and middle faller jewel to the middle and bottom faller jewel spot respectively
        Moves the bottom faller jewel to the top faller jewel position
        '''
        if self.check_for_game_over() == False:
            if self._faller_type != 'frozen' and self._faller_type != None:
                bot, mid, top = self._bot_jewel, self._mid_jewel, self._top_jewel
                self._board[self._bot_y][self._faller_x] = mid
                self._board[self._mid_y][self._faller_x] = top
                self._board[self._top_y][self._faller_x] = bot

                self._bot_jewel = mid
                self._mid_jewel = top
                self._top_jewel = bot 
                
            return self._board
        else:
            raise GameOverError
    
    def no_matches(self) -> bool:
        '''Checks if there are no more matches to be made
        Will always be used after matching functions'''
        if self._faller_type == 'frozen' or self._faller_type == None:
            board = self._board
            self.matching()
            self.pop()
            if self._board == board:
                return True
            else:
                return False

    def matching(self) -> list[list[str]]:
        '''
        If three or more jewels match either vertically, horizontally, or diagonally, it will mark the coordinates of the jewel
        '''
        self._matched_coords = []

        if self._faller_type == 'frozen' or self._faller_type == None:
            for row in range(3,len(self._board)):
                for col in range(self._c):
                    if self._board[row][col] != ' ':
                        #if 3+ match horizontally -> save coordinates
                        if col+2 < self._c:
                            if self._board[row][col] == self._board[row][col+1] == self._board[row][col+2]:
                                self._matched_coords.append((row,col))
                                self._matched_coords.append((row,col+1))
                                self._matched_coords.append((row,col+2))
                        #if 3+ match vertically -> save coordinates
                        if row+2 < self._r+3:
                            if self._board[row][col] == self._board[row+1][col] == self._board[row+2][col]:
                                self._matched_coords.append((row,col))
                                self._matched_coords.append((row+1,col))
                                self._matched_coords.append((row+2,col))
                        # if 3+ match diagonally downwards -> save coordinaes
                        if row+2 < self._r+3 and col+2 < self._c:
                            if self._board[row][col] == self._board[row+1][col+1] == self._board[row+2][col+2]:
                                self._matched_coords.append((row,col))
                                self._matched_coords.append((row+1,col+1))
                                self._matched_coords.append((row+2,col+2))
                        # if 3+ match diagonally upwards -> save coordinates
                        if row-2 > 2 and col+2 < self._c:
                            if self._board[row][col] == self._board[row-1][col+1] == self._board[row-2][col+2]:
                                self._matched_coords.append((row,col))
                                self._matched_coords.append((row-1,col+1))
                                self._matched_coords.append((row-2,col+2))
        
        # self.pop()        
        return self._board

    def get_matched(self) -> list[tuple]:
        return self._matched_coords
    
    def pop(self) -> None:
        '''Removes the jewels in the coordinaets that were marked in the matching function and replaces with a space'''
        if self._faller_type == None:
            for location in self._matched_coords:
                self._board[location[0]][location[1]] = ' '
            self._reset_faller
            self.gravity()
    
    def check_for_game_over(self) -> bool:
        '''Checks if any faller jewels are outside of the user's board (anything past row index 2)
        Returns False if the game isn't over, True if the game is over'''
        has_jewel = False
        # if self._faller_type == 'frozen' or self._faller_type == None:
        if self.no_matches() == True:
            for row in range(3):
                for col in range(len(self._board[row])):
                    if self._board[row][col] != ' ':
                        has_jewel = True
        return has_jewel
            
    def _reset_faller(self) -> None:
        '''Does not assign anything to the faller variables until another faller is made'''
        self._faller_x = None
        self._top_y = None
        self._mid_jewel = None
        self._faller_type = None
