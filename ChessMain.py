'''
Main driver file.
Handling user input.
Displaying current GameStatus object.
'''

import pygame as p
import ChessEngine
import sys

WIDTH = HEIGHT = 512
DIMENSION = 8

SQ_SIZE = HEIGHT // DIMENSION

MAX_FPS = 15
    
IMAGES = {}


def load_images():
    pieces = ['wp', 'bp', 'wR', 'bR', 'wN', 'bN', 'wB', 'bB', 'wK', 'bK', 'wQ', 'bQ']

    for piece in pieces:
        image_path = r'C:\Users\TranCongThinh\Desktop\New folder\image\{}.png'.format(piece)
        IMAGES[piece] = p.transform.scale(p.image.load(image_path), (SQ_SIZE, SQ_SIZE))
        
        
def main():
    '''
    The main driver for our code.
    This will handle user input and updating the graphics.
    '''
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False #flag variable for when a move is made
    
    load_images() #do this only once before while loop
    
    running = True
    sq_selected = () #no square is selected initially, this will keep track of the last click of the user (tuple(row,col))
    player_clicks = [] #this will keep track of player clicks (two tuples)

    while running:
        for e in p.event.get():  
            if e.type == p.QUIT:
                running = False
                p.quit()
                sys.exit()
            #mouse handler            
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #(x, y) location of the mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sq_selected == (row, col): #user clicked the same square twice
                    sq_selected = () #deselect
                    player_clicks = [] #clear clicks
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected) #append for both 1st and 2nd click
                if len(player_clicks) == 2: #after 2nd click                                                                    
                    move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                    print(move.get_chess_notation)
                    if move in valid_moves:
                        print(move.get_chess_notation()) 
                        gs.make_move(move)
                        move_made = True
                        sq_selected = () #reset user clicks
                        player_clicks = []
                    else:
                        player_clicks = [sq_selected]
            #key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undo_move()
                    move_made = True
                    
        if move_made:
            valid_moves = gs.get_valid_moves()
            move_made = False
                    
        draw_game_state(screen, gs, valid_moves, sq_selected) 
        clock.tick(MAX_FPS)
        p.display.flip()

def high_light(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'): #sq_selected is the sq that can be moved
            h = p.Surface((SQ_SIZE, SQ_SIZE)) #highlight the selected sq
            h.set_alpha(100) #transperancy
            h.fill(p.Color('blue'))
            screen.blit(h, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves
            h.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(h, (SQ_SIZE*move.end_col, SQ_SIZE*move.end_row))


def draw_game_state(screen, gs, valid_moves, sq_selected):
    '''
    Responsible for all the graphics within current game state.
    '''
    draw_board(screen) #draw squares on the board
    high_light(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board) #draw pieces on top of those squares      

def draw_board(screen):
    '''
    Draw the squares on the board.
    The top left square is always light.
    '''
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row+column) % 2)]
            p.draw.rect(screen, color, p.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
    

def draw_pieces(screen, board):
    '''
    Draw the pieces on the board using the current game_state.board
    '''
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))
         
                
if __name__ == "__main__":
    main()