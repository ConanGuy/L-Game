from consts import *
from lgame import *
import math
import pygame

class MyWindow:

    def __init__(self, title='L-Game'):
    
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(title)

        self.game = LGame()
        self.gc = self.game.copy() 

        self.holdClick = False
        self.selectedCoin = None 
        self.resetCoin = None 

        self.run()
        
    #######################
    ##
    ## MAIN LOOP
    ##
    #######################

    def run(self):
        
        moves = {pygame.K_RIGHT: [1,0], pygame.K_LEFT: [-1,0], pygame.K_UP: [0,1], pygame.K_DOWN: [0,-1]}

        clock = pygame.time.Clock()
        ended = 0
        while ended == 0:
            
            clock.tick(TPS)



            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit(0)

                if event.type == pygame.KEYDOWN:
                    if event.key in moves:
                        if self.game.phase == 0:
                            self.gc.players[self.game.currentPlayer].move(moves[event.key])

                        elif self.selectedCoin:
                            x,y = tuple(map(add,self.selectedCoin,moves[event.key]))

                            if 0 <= x < GRID_COLS and 0 <= y < GRID_ROWS :
                                self.selectedCoin = [x,y]
                        
                    if event.key == pygame.K_PAGEDOWN:
                        if self.game.phase == 0:
                            self.gc.players[self.game.currentPlayer].angle += 90
                            self.gc.players[self.game.currentPlayer].angle %= 360
                    if event.key == pygame.K_PAGEUP:
                        if self.game.phase == 0:
                            self.gc.players[self.game.currentPlayer].angle -= 90
                            self.gc.players[self.game.currentPlayer].angle %= 360
                    if event.key == pygame.K_COMMA:
                        if self.game.phase == 0:
                            self.gc.players[self.game.currentPlayer].mirror = not self.gc.players[self.game.currentPlayer].mirror 
                    if event.key == pygame.K_RETURN:
                        if self.gc.is_valid():
                            
                            change = True

                            if self.game.phase == 0 and self.game.players == self.gc.players:
                                change = False

                            if self.game.phase == 1:
                                gc = self.gc.copy()
                                if self.selectedCoin:   
                                   gc.coins[self.resetCoin] = self.selectedCoin.copy()
                                if not gc.is_valid():
                                    change = False


                            if change:
                                self.game.phase = (self.game.phase+1)%2
                                if self.game.phase == 0:
                                    self.game.currentPlayer = (self.game.currentPlayer+1)%2
                                self.game.players = deepcopy(self.gc.players)
                                self.game.coins = deepcopy(self.gc.coins)
                                if self.selectedCoin:
                                    self.game.coins[self.resetCoin] = self.selectedCoin.copy()
                                self.gc = self.game.copy()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.click()

            self.draw()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit(0)

    #######################
    ##
    ## DRAW FCTS
    ##
    #######################

    def draw_square(self, c, color):
        x,y = tuple(c)

        px = int(GRID_X + x * (CASE_SIZE + CASE_BORDER)) 
        py = int(GRID_Y + (GRID_ROWS-1-y) * (CASE_SIZE + CASE_BORDER))

        pygame.draw.rect(self.win, color, (px,py,CASE_SIZE+CASE_BORDER+1,CASE_SIZE+CASE_BORDER+1))
        pygame.draw.rect(self.win, (0,0,0), (px,py,CASE_SIZE+CASE_BORDER+1,CASE_SIZE+CASE_BORDER+1), CASE_BORDER)

    ##########

    def draw_game(self):
        for x in range(3,-1,-1):
            for y in range(0,4):
               
                px = int(GRID_X + x * (CASE_SIZE + CASE_BORDER)) + CASE_BORDER
                py = int(GRID_Y + (GRID_ROWS-1-y) * (CASE_SIZE + CASE_BORDER)) + CASE_BORDER

                if [x,y] in self.game.coins:
                    px += int(CASE_SIZE / 2)
                    py += int(CASE_SIZE / 2)
                    pygame.draw.circle(self.win, (150,150,150), (px,py), int(3*CASE_SIZE/7))
                elif [x,y] in self.game.players[0].get_squares():
                    color = (255, 166, 166) 
                    self.draw_square([x,y], color)
                elif [x,y] in self.game.players[1].get_squares():
                    color = (147, 147, 255) 
                    self.draw_square([x,y], color)

        if self.game.phase == 0:
            for s in self.gc.players[self.gc.currentPlayer].get_squares():
                color = [(255,0,0),(0,0,255)]
                self.draw_square(s, color[self.gc.currentPlayer])
        elif self.selectedCoin:
            x,y = tuple(self.selectedCoin)

            px = int(GRID_X + x * (CASE_SIZE + CASE_BORDER)) + CASE_BORDER
            py = int(GRID_Y + (GRID_ROWS-1-y) * (CASE_SIZE + CASE_BORDER)) + CASE_BORDER

            px += int(CASE_SIZE / 2)
            py += int(CASE_SIZE / 2)
            pygame.draw.circle(self.win, (50,50,50), (px,py), int(3*CASE_SIZE/7))

    ##########

    def draw_grid(self):
        for i in range(GRID_COLS+1):
            pb = (GRID_X, GRID_Y+i*(CASE_SIZE+CASE_BORDER))
            pe = (GRID_X+GRID_WIDTH-CASE_BORDER-1, GRID_Y+i*(CASE_SIZE+CASE_BORDER))
            pygame.draw.line(self.win, (0,0,0), pb, pe, CASE_BORDER)

            pb = (GRID_X+i*(CASE_SIZE+CASE_BORDER), GRID_Y)
            pe = (GRID_X+i*(CASE_SIZE+CASE_BORDER), GRID_Y+GRID_HEIGHT-CASE_BORDER-1)
            pygame.draw.line(self.win, (0,0,0), pb, pe, CASE_BORDER)
           
    ##########
    
    def draw(self):
        self.win.fill((235, 235, 235))
                
        self.draw_game()
        self.draw_grid()

        pygame.display.update()

    #######################

    def click(self):
        if self.game.phase == 1:
            mx, my = pygame.mouse.get_pos()

            gx = (mx - GRID_X + int(CASE_BORDER/2)) // (CASE_SIZE+CASE_BORDER)
            gy = GRID_ROWS - 1 - (my - GRID_Y + int(CASE_BORDER/2)) // (CASE_SIZE+CASE_BORDER)

            coin = False
            for i,c in enumerate(self.gc.coins):
                if [gx,gy] == c:
                    self.selectedCoin = c.copy()
                    self.resetCoin = i
                    coin = True
            
            if not coin:
                self.selectedCoin = None
                self.resetCoin = None
                    

if __name__ == "__main__":
    pygame.init()
    MyWindow()