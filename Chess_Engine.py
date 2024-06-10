"""Responsible for storing the information about the current state of a chess game.
Responsible for determining the valid moves at the current state, keeping a move log
"""
class GameState():
    def __init__(self):
        #board is an 8x8 2d array and each element has 2 characters..
        #The first character represents the color of the piece, 'b' or 'w'
        #Second character represents the type of the piece
        #"--" represents an empty space with no piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.move_functions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.whiteToMove = True
        self.movelog = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.check_mate = False
        self.stale_mate = False
        self.enpassent_possible = () #coordinates for the square where the en passent capture is possible
        self.current_castling_right = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
                                               self.current_castling_right.wqs, self.current_castling_right.bqs)]




    """
    Takes a move as a parameter and executes it. Does not work for castling and pawn promotion"""
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.movelog.append(move) #add to the move log so it can be undone later
        self.whiteToMove = not self.whiteToMove #switch turns
        #update king's location
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

        #pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        #enpassent move
        if move.is_enpassent_move:
            self.board[move.start_row][move.end_col] = "--" #capturing the pawn

        #update enpassent_possible variable
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2: #only on 2 square pawn advances
            self.enpassent_possible = ((move.start_row + move.end_row)//2, move.start_col)
        else:
            self.enpassent_possible = ()

        #castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2: #king side castling
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1] #moves the rook
                self.board[move.end_row][move.end_col + 1] = "--"
            else: #queen side castling
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = "--"

        #update castling rights : whenever it is a rook or king move
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
                                               self.current_castling_right.wqs, self.current_castling_right.bqs))

    '''
    Undo the last made move
    '''
    def undoMove(self):
        if len(self.movelog) != 0:
            move = self.movelog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.place_captured
            self.whiteToMove = not self.whiteToMove #switch turns
            # update king's location
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)

            #undo en passent
            if move.is_enpassent_move:
                self.board[move.end_row][move.end_col] = '--' #leave landing square blank
                self.board[move.start_row][move.end_col] = move.place_captured
                self.enpassent_possible = (move.end_row, move.end_col)

            #undo a 2 square pawn advance
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                self.enpassent_possible = ()

            #undo castling rights
            self.castle_rights_log.pop() #get rid of the new castle rights from the move we are undoing
            new_rights = self.castle_rights_log[-1] #set the current castle rights to the last one in the list
            self.current_castling_right = CastleRights(new_rights.wks, new_rights.bks, new_rights.wqs, new_rights.bqs)

            #undo the castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2: #kingside
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = "--"
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = "--"

    """
        Update the castle rights given the move
        """

    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False

        elif move.piece_moved == 'bK':
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False

        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.current_castling_right.wqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_right.wks = False

        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.current_castling_right.bqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_right.bks = False

    '''
    All Moves considering checks
    '''
    def get_valid_moves(self):
        temp_enpassent_possible = self.enpassent_possible
        temp_castle_rights = CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
                                          self.current_castling_right.wqs, self.current_castling_right.bqs) #copy the current castling rights
        # generate all possible moves
        moves = self.get_all_possible_moves()
        if self.whiteToMove:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
        # for each move, make the move
        for i in range(len(moves)-1, -1, -1): #when removing from a list, go through backwards
            self.make_move(moves[i])
            # generate all opponent's move
            # for each opponent's move, see if the attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i]) # if they do, it's not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck(): #in check, hence, checkmate
                self.check_mate = True
            else: #stalemate
                self.stale_mate = True
        else:
            self.check_mate = False
            self.stale_mate = False

        self.enpassent_possible = temp_enpassent_possible
        self.current_castling_right = temp_castle_rights
        return moves

    '''
    Determine if the current player is in check
    '''
    def inCheck(self):
        if self.whiteToMove:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])


    '''
    Determine if the enemy can attack the square r, c
    '''
    def square_under_attack(self, r, c):
        self.whiteToMove = not self.whiteToMove #switch to opponent's pov
        opponent_moves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove  # switch turns back
        for move in opponent_moves:
            if move.end_row == r and move.end_col == c: #square under attack
                return True
        return False

    '''
    All moves without considering checks
    '''
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)
        return moves

    '''
    Get all the pawn moves for the pawn at row, col and add these to the moves list
    '''
    def get_pawn_moves(self, r, c, moves):
        if self.whiteToMove: #White to move
            if self.board[r-1][c] == '--': #1 square pawn advance
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": #2 square pawn advance
                    moves.append(Move((r, c), (r-2, c), self.board))

            if c-1 >= 0: #captures to the left
                if self.board[r-1][c-1][0] == 'b': #black piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassent_possible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, is_enpassent_move=True))

            if c+1 <= 7: #captures to the right
                if self.board[r - 1][c + 1][0] == 'b':  # black piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r-1, c+1) == self.enpassent_possible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, is_enpassent_move=True))

        else:
            if self.board[r+1][c] == '--': #1 square pawn advance
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--": #2 square pawn advance
                    moves.append(Move((r, c), (r+2, c), self.board))

            if c-1 >= 0: #captures to the left
                if self.board[r+1][c-1][0] == 'w': #white piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassent_possible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, is_enpassent_move=True))

            if c+1 <= 7: #captures to the right
                if self.board[r+1][c + 1][0] == 'w':  # white piece to capture
                    moves.append(Move((r, c), (r+1, c + 1), self.board))
                elif (r+1, c+1) == self.enpassent_possible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, is_enpassent_move=True))


    '''
        Get all the rook moves for the rook at row, col and add these to the moves list
    '''

    def get_rook_moves(self, r, c, moves):
        if self.whiteToMove:
            # Explore the vertical top (r-1, c)
            x = r
            y = c

            while True:
                x -= 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds

                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'b':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'b':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))

            # Explore the vertical bottom (r+1, c)
            x = r
            y = c

            while True:
                x += 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds

                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'b':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'b':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))
            # Explore the horizontal right (r, c+1)
            x = r
            y = c

            while True:
                y += 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds

                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'b':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'b':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))
            # Explore the horizontal left (r, c-1)
            x = r
            y = c

            while True:
                y -= 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds

                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'b':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'b':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))
        else:
            # Black movement
            # Explore the vertical top (r-1, c)
            x = r
            y = c

            while True:
                x -= 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds

                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'w':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'w':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))

            # Explore the vertical bottom (r+1, c)
            x = r
            y = c

            while True:
                x += 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds

                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'w':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'w':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))
            # Explore the horizontal right (r, c+1)
            x = r
            y = c

            while True:
                y += 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds

                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'w':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'w':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))
            # Explore the horizontal left (r, c-1)
            x = r
            y = c

            while True:
                y -= 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds

                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'w':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'w':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))


    def get_knight_moves(self, r, c, moves):
        if self.whiteToMove:
            # Generate all possible moves
            possible_moves = [(r+1, c+2), (r+1, c-2), (r-1, c-2), (r-1, c+2),
                              (r+2, c+1), (r+2, c-1), (r-2, c+1), (r-2, c-1)]

            def in_bounds(x, y):
                r_in_bound = (x < len(self.board)) and (x >= 0)
                c_in_bound = (y < len(self.board[0])) and (y >= 0)
                return r_in_bound and c_in_bound

            for i in possible_moves:
                if in_bounds(i[0], i[1]):
                    if self.board[i[0]][i[1]] == '--' or self.board[i[0]][i[1]][0] == 'b': #Movement or capture the enemy piece
                        moves.append(Move((r, c), (i[0], i[1]), self.board))

        else:
            # Generate all possible moves
            possible_moves = [(r + 1, c + 2), (r + 1, c - 2), (r - 1, c - 2), (r - 1, c + 2),
                              (r + 2, c + 1), (r + 2, c - 1), (r - 2, c + 1), (r - 2, c - 1)]

            def in_bounds(x, y):
                r_in_bound = (x < len(self.board)) and (x >= 0)
                c_in_bound = (y < len(self.board[0])) and (y >= 0)
                return r_in_bound and c_in_bound

            for i in possible_moves:
                if in_bounds(i[0], i[1]):
                    if self.board[i[0]][i[1]] == '--' or self.board[i[0]][i[1]][0] == 'w':  # Movement or capture the enemy piece
                        moves.append(Move((r, c), (i[0], i[1]), self.board))


    def get_bishop_moves(self, r, c, moves):
        if self.whiteToMove:
            # explore the top-left route (r-1, c-1)
            x = r
            y = c

            while True:
                x -= 1
                y -= 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds


                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'b':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'b':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))


            # explore the top-right route (r-1, c+1)
            x = r
            y = c
            while True:
                x -= 1
                y += 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds


                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'b':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'b':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))
            # explore the bottom-left route (r+1, c-1)
            x = r
            y = c
            while True:
                x += 1
                y -= 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds

                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'b':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'b':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))
            # explore the bottom-right route (r+1, c+1)
            x = r
            y = c
            while True:
                x += 1
                y += 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds

                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'b':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'b':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))
        else:
            # explore the top-left route (r-1, c-1)
            x = r
            y = c

            while True:
                x -= 1
                y -= 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds

                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'w':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'w':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))

            # explore the top-right route (r-1, c+1)
            x = r
            y = c
            while True:
                x -= 1
                y += 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds

                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'w':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'w':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))
            # explore the bottom-left route (r+1, c-1)
            x = r
            y = c
            while True:
                x += 1
                y -= 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds

                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'w':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'w':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))
            # explore the bottom-right route (r+1, c+1)
            x = r
            y = c
            while True:
                x += 1
                y += 1

                # checking if you're still on the board
                x_in_bounds = (x >= 0) and (x < len(self.board))
                y_in_bounds = (y >= 0) and (y < len(self.board[0]))
                on_the_board = x_in_bounds and y_in_bounds

                if not on_the_board:
                    break

                # check if you hit another white piece and also ability to advance
                if self.board[x][y] != "--" and self.board[x][y][0] != 'w':
                    break

                # check if black piece is in the way
                elif self.board[x][y][0] == 'w':
                    moves.append(Move((r, c), (x, y), self.board))
                    break

                moves.append(Move((r, c), (x, y), self.board))

        # pass

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        ally_color = 'w' if self.whiteToMove else 'b'
        # Get all possible king movements
        possible_moves = [(r+1, c), (r+1, c+1), (r+1, c-1), (r, c-1), (r, c+1), (r-1, c), (r-1, c+1), (r-1, c-1)]

        def in_bounds(x, y):
            r_in_bound = (x < len(self.board)) and (x >= 0)
            c_in_bound = (y < len(self.board[0])) and (y >= 0)
            return r_in_bound and c_in_bound

        for i in possible_moves:
            if in_bounds(i[0], i[1]):
                if self.board[i[0]][i[1]] == '--' or self.board[i[0]][i[1]][0] != ally_color: #Movement or capture the enemy piece
                    moves.append(Move((r, c), (i[0], i[1]), self.board))



    '''
    Generate all valid castle moves for the king at (r, c) and add them to the list of moves
    '''

    def get_castle_moves(self, r , c, moves):
        if self.square_under_attack(r, c):
            return #can't castle if we are in check
        if (self.whiteToMove and self.current_castling_right.wks) or (not self.whiteToMove and self.current_castling_right.bks):
            self.get_king_side_castle_moves(r, c, moves)
        if (self.whiteToMove and self.current_castling_right.wqs) or (not self.whiteToMove and self.current_castling_right.bqs):
            self.get_queen_side_castle_moves(r, c, moves)

    def get_king_side_castle_moves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castle_move = True))

    def get_queen_side_castle_moves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, is_castle_move = True))

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}

    rows_to_ranks = {val: key for (key, val) in ranks_to_rows.items()}

    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}

    cols_to_files = {val: key for (key, val) in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassent_move = False, is_castle_move = False):
         self.start_row = start_sq[0]
         self.start_col = start_sq[1]
         self.end_row = end_sq[0]
         self.end_col = end_sq[1]
         self.piece_moved = board[self.start_row][self.start_col]
         self.place_captured = board[self.end_row][self.end_col]
         #pawn promotion
         self.is_pawn_promotion = (self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7)

         #enpassent
         self.is_enpassent_move = is_enpassent_move
         if self.is_enpassent_move:
             self.place_captured = 'wp' if self.piece_moved == 'bp' else 'bp'
         #castling
         self.is_castle_move = is_castle_move

         self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col


    '''
    Overriding the equals method
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]