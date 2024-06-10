"""Driver File. Responsible for handling user input and current game state"""

import pygame as p
import Chess_Engine

# p.init()
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15 #for animations
IMAGES = {}

"""
Initialize a global dict of images and will be called exactly once
"""
def load_images():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("chess_images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    #We can access an image by using the dictionary

"""
Main driver for the code.
Handles user input and updates the graphics"""

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Chess")
    icon = p.image.load("chess_images/bp.png")
    p.display.set_icon(icon)
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gstate = Chess_Engine.GameState()
    valid_moves = gstate.get_valid_moves()
    move_made = False #flag for when a move is made
    animate = False #flag to animate
    load_images() #Done only once before while loop
    game_is_on = True
    selected_square = ()
    playerClicks = [] #Keep track of player clicks
    game_over = False

    while game_is_on:
        for e in p.event.get():
            if e.type == p.QUIT:
                game_is_on = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos() #mouse location (x, y)
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if selected_square == (row, col): #User clicked on the same square twice
                        selected_square = () #deselect
                        playerClicks = [] #Clear player clicks
                    else:
                        selected_square = (row, col)
                        playerClicks.append(selected_square) #append for both clicks
                    if len(playerClicks) == 2: #after 2nd click
                        move = Chess_Engine.Move(playerClicks[0], playerClicks[1], gstate.board)
                        print(move.get_chess_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gstate.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                selected_square = () #reset player clicks
                                playerClicks = []

                        if not move_made:
                            playerClicks = [selected_square]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #Undo a move when the letter z is pressed
                    gstate.undoMove()
                    move_made = True
                    animate = False

                if e.key == p.K_r: #reset the board when 'r' is pressed
                    gstate = Chess_Engine.GameState()
                    valid_moves = gstate.get_valid_moves()
                    selected_square = ()
                    playerClicks = []
                    move_made = False
                    animate = False
        if move_made:
            if animate:
                animate_move(gstate.movelog[-1], screen, gstate.board, clock)
            valid_moves = gstate.get_valid_moves()
            move_made = False
            animate = False

        draw_stage(screen, gstate, valid_moves, selected_square)

        if gstate.check_mate:
            game_over = True
            if gstate.whiteToMove:
                draw_text(screen, 'Checkmate..... Black wins .....')
            else:
                draw_text(screen, 'Checkmate..... White wins .....')

        elif gstate.stale_mate:
            game_over = True
            draw_text(screen, '.....Stalemate.....')

        clock.tick(MAX_FPS)
        p.display.flip()

"""Highlight square selected and moves for piece selected"""

def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ("w" if gs.whiteToMove else "b"): #sq_selected is a piece that can be moved
            #highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transparency value. 0 transparent fully, 255 opaque fully
            s.fill(p.Color('brown4'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('bisque2'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))


"""
Responsible for all the graphics within a current game state"""
def draw_stage(screen, gstate, valid_moves, sq_selected):
    draw_board(screen) #draw the squares on the board
    highlight_squares(screen, gstate, valid_moves, sq_selected)
    draw_pieces(screen, gstate.board) #draw pieces on top of the squares

""""Draws the squares on the board"""
def draw_board(screen):
    global colors
    colors = [p.Color("white"), p.Color("grey")]

    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
"""Draws the pieces on the board using the current GameState.board"""
def draw_pieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]

            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(col*SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""Animating a move"""
def animate_move(move, screen, board, clock):
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_square = 10 #frames to move one square
    frames_count = (abs(dR) + abs(dC)) * frames_per_square

    for frame in range(frames_count+1):
        r, c = (move.start_row + dR*frame/frames_count, move.start_col + dC*frame/frames_count)
        draw_board(screen)
        draw_pieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        #draw captured piece onto rectangle
        if move.place_captured != "--":
            screen.blit(IMAGES[move.place_captured], end_square)

        #draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(80)

def draw_text(screen, text):
    font = p.font.SysFont("comicsansms", 32, True, False)
    text_object = font.render(text, 0, p.Color('Gray'))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color('Black'))
    screen.blit(text_object, text_location.move(2, 2))


if __name__ == "__main__":
    main()