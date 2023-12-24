import columns_mechanics
import pygame
import random

_INITIAL_WIDTH = 600
_INITIAL_HEIGHT = 600
_BACKGROUND_COLOR = pygame.Color(57, 62, 65)
_BOARD_COLOR = pygame.Color(84,73,75)
_S_COLOR = pygame.Color(241, 247, 237)
_W_COLOR = pygame.Color(145, 199, 177)
_T_COLOR = pygame.Color(179, 57, 81)
_X_COLOR = pygame.Color(227, 208, 129)
_Y_COLOR = pygame.Color(238, 150, 75)
_Z_COLOR = pygame.Color(100, 255, 169)

class ColumnsGame:
    def __init__(self):
        self._game = columns_mechanics.ColumnsGame(13,6)
        self._game.create_board('EMPTY')
        self._state = self._game.get_board()

        self._running = True

        self._jewel_center_x = None
        self._jewel_center_y = None
        self._board_width = None
        self._board_height = None

        self._game_over = False

        self._clock = pygame.time.Clock()

    def run(self) -> None:
        pygame.init()
        self._resize_surface((_INITIAL_WIDTH,_INITIAL_HEIGHT))

        tick = 0
        frame = 0

        while self._running:
            
            new_tick = pygame.time.get_ticks()
            if new_tick != tick:
                tick = new_tick
                frame += 1

            #faller will fall every at 1 fps while the game is at 10 fps
            if frame % 10 == 0:
                self._idle_move()
            self._handle_event()
            self._redraw()

            while self._game_over == True:
                self._print_text()
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._running = False
                        return
            
        pygame.quit()
    
    def _redraw(self) -> None:
        '''Displays the new frame for the game with the board and its contents'''
        surface = pygame.display.get_surface()

        surface.fill(_BACKGROUND_COLOR)
        self._draw_rect()
        self._draw_jewels()
        
        pygame.display.flip()
        self._clock.tick(10)
    
    def _print_text(self) -> None:
        '''Displays the Game Over text when the user loses'''
        surface = pygame.display.get_surface()
        width, height = surface.get_size()

        font = pygame.font.SysFont('Arial', 30)
        surface.fill(pygame.Color(255,255,255))
        img = font.render('GAME OVER', True, (0,0,0))
        
        text_w = img.get_width()
        text_h = img.get_height()

        surface.blit(img,(width/2 - text_w/2, height/2 - text_h/2))
    
    def _make_faller(self) -> None:
        '''Randomly selects colors to create a faller'''
        color_options = ('S','W','T','X','Y','Z')
        column = list(range(6))
        for i in column:
            if self._state[3][i] != ' ':
                column.remove(i)
        column_num = random.choice(column)+1
        self._game.create_faller(f'F {column_num} {color_options[random.randrange(6)]} {color_options[random.randrange(6)]} {color_options[random.randrange(6)]}')

    def _resize_surface(self, size: tuple[int, int]) -> None:
        '''Makes the window resizable for the user'''
        pygame.display.set_mode(size, pygame.RESIZABLE)

    def _draw_rect(self) -> None:
        '''Displays the rectangle acting as the board of the game based on the ratio of the width and height
        Makes sure the entire board fits on the screen no matter the window size'''
        surface = pygame.display.get_surface()
        width, height = surface.get_size()
        if width/height > 6/13:
            tl_x = 0.5*width-(self.rect_width(height)/2)
            pygame.draw.rect(surface,_BOARD_COLOR,(tl_x,0, self.rect_width(height),height))
            self._board_height = height
            self._board_width = self.rect_width(height)
            
        else:
            tl_y = 0.5*height - (self.rect_height(width)/2)
            pygame.draw.rect(surface, _BOARD_COLOR, (0, tl_y, width, self.rect_height(width)))
            self._board_width = width
            self._board_height = self.rect_height(width)

    def rect_height(self, width: float) -> float:
        '''
        Returns the proportional height of the board's rectangle based on the width of the window
        Only called if ratio (width/height) is less than or equal to 6/13
        '''
        height = width/6
        height *= 13
        return height
        
    def rect_width(self, height: float) -> float:
        '''Returns the proportional width of the board's rectangle based on the height of the window
        Only called if ratio (width/height) is greater than 6/13'''
        width = height/13
        width *= 6
        return width

    def _handle_event(self) -> None:
        '''Reads whether the user exited out of the window, pressed the right/left arrow, or clicked space
        Will exit the game, move the faller right/left, or rotate the jewels respectively'''
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self._game.rotate_faller()
                    elif event.key == pygame.K_RIGHT:
                        self._game.move_faller_right()
                    elif event.key == pygame.K_LEFT:
                        self._game.move_faller_left()
        except columns_mechanics.GameOverError:
            self._game_over = True
                
    def _idle_move(self) -> None:
        '''If there is no user input, the move would be an idle move and will make the faller fall (whichever one comes first)'''
        self._game.faller_down()
        if self._game.get_faller_status() == 'frozen' or self._game.get_faller_status() == None:
            self._game_over = self._game.check_for_game_over()
            if self._game_over == False:
                self._make_faller()
            else:
                return
        
    def _color(self, color: str) -> pygame.Color:
        '''Depending on the letter on the board, it corresponds to the color that the jewel should
        be when drawn in the pygame window'''
        if color == 'S':
            return _S_COLOR
        if color == 'W':
            return _W_COLOR
        if color == 'T':
            return _T_COLOR
        if color == 'X':
            return _X_COLOR
        if color == 'Y':
            return _Y_COLOR
        if color == 'Z':
            return _Z_COLOR

    def _draw_jewel(self, coords: tuple[int,int], color: str) -> None:
        '''
        Depending on the coordinate of the jewel on the board, draws the jewel exactly in the center of
        that spot on the pygame window
        Also prints if the faller becomes frozen
        '''
        
        surface = pygame.display.get_surface()

        y_coord = coords[0]-2
        x_coord = coords[1]+1

        pixels_per_box = self._board_height/13

        self._center_y = pixels_per_box*y_coord - pixels_per_box/2
        self._center_x = (surface.get_size()[0]/2 - self._board_width/2) + (pixels_per_box*x_coord - pixels_per_box/2)
        pygame.draw.circle(surface, self._color(color), (self._center_x,self._center_y), self._board_width/6/2)

    def _draw_faller(self, coords: tuple[int,int], color: str) -> None:
        '''If the coordinate on the board is that of a faller jewel, the jewel will be
        printed differently with another circle in the middle'''

        surface = pygame.display.get_surface()

        y_coord = coords[0]-2
        x_coord = coords[1]+1

        pixels_per_box = self._board_height/13

        self._center_y = pixels_per_box*y_coord - pixels_per_box/2
        self._center_x = (surface.get_size()[0]/2 - self._board_width/2) + (pixels_per_box*x_coord - pixels_per_box/2)
        pygame.draw.circle(surface, self._color(color), (self._center_x,self._center_y), self._board_width/6/2)
        pygame.draw.circle(surface, _BOARD_COLOR, (self._center_x,self._center_y), self._board_width/6/4)

    def _draw_landed_faller(self, coords:tuple[int,int], color:str) -> None:
        '''If the coordinate on the board is that of a faller jewel and the state of the faller jewel
        was landed, the jewel will be printed differently with a smaller circle in the middle than the usual faller jewel'''

        surface = pygame.display.get_surface()

        y_coord = coords[0]-2
        x_coord = coords[1]+1

        pixels_per_box = self._board_height/13

        self._center_y = pixels_per_box*y_coord - pixels_per_box/2
        self._center_x = (surface.get_size()[0]/2 - self._board_width/2) + (pixels_per_box*x_coord - pixels_per_box/2)
        pygame.draw.circle(surface, self._color(color), (self._center_x,self._center_y), self._board_width/6/2)
        pygame.draw.circle(surface, _BOARD_COLOR, (self._center_x,self._center_y), self._board_width/6/8)


    def _draw_jewels(self) -> None:
        '''Decides whether to draw a faller jewel or a normal jewel on the board'''
        for row in range(3, len(self._state)):
            curr_row = self._state[row]
            for val in range(len(curr_row)):
                #if the value matches the coordinates of any of the faller jewels
                if (row == self._game.get_bot_coords()[0] and val == self._game.get_bot_coords()[1] and self._game.get_faller_status() != 'frozen' and self._game.get_faller_status() != None)\
                or (row == self._game.get_mid_coords()[0] and val == self._game.get_mid_coords()[1] and self._game.get_faller_status() != 'frozen' and self._game.get_faller_status() != None)\
                or (row == self._game.get_top_coords()[0] and val == self._game.get_top_coords()[1] and self._game.get_faller_status() != 'frozen' and self._game.get_faller_status() != None):
                    if self._game.get_faller_status() == 'landed':
                        self._draw_landed_faller((row, val), curr_row[val])
                    else:
                        self._draw_faller((row,val), curr_row[val])

                #if the value is not a faller jewel
                elif self._game.get_faller_status() == 'frozen' or self._game.get_faller_status() == None:
                    if curr_row[val] != ' ':
                        self._draw_jewel((row, val), curr_row[val])
                    self._game_over = self._game.check_for_game_over()
                
                #catches any other circumstance of a jewel
                else:
                    if self._state[row][val] != ' ':
                        self._draw_jewel((row, val), curr_row[val])

if __name__ == '__main__':
    ColumnsGame().run()


