'''
Storing all the information about the current state of chess game.
Determining valid moves at current state.
It will keep move log.
'''

class GameState():
    def __init__(self):
        '''
        Board is an 8x8 2d list, each element in list has 2 characters.
        The first character represtents the color of the piece: 'b' or 'w'.
        The second character represtents the type of the piece: 'R', 'N', 'B', 'Q', 'K' or 'p'.
        "--" represents an empty space with no piece.
        '''
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
        self.move_functions = {"p": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves,
                               "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}
        self.white_to_move = True
        self.move_log = []
        self.whiteKing_loc = (7,4)
        self.blackKing_loc = (0,4)
        self.in_check = False
        self.pins = []
        self.checks = []

    def make_move(self, move):
        # make the start sq empty
        self.board[move.start_row][move.start_col] = '--'
        # moving the piece
        self.board[move.end_row][move.end_col]  = move.piece_moved
        
        self.move_log.append(move)
        
        self.white_to_move = not self.white_to_move 

    def get_possible_moves(self):
        """
        All moves without considering checks.
        """
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == "w" and self.white_to_move) or (turn == "b" and not self.white_to_move):
                    piece = self.board[row][col][1]
                    self.move_functions[piece](row, col, moves)  # calls appropriate move function based on piece type
        return moves

    def undo_move(self):
        if len(self.move_log) != 0: #make sure the move log is not 0
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move  = not self.white_to_move #switch turn

    def get_valid_moves(self):
        moves = []
        self.in_check, self.pins, self.checks = self.find_pinsAndChecks()
        if self.white_to_move:
            king_row = self.whiteKing_loc[0]
            king_col = self.whiteKing_loc[1]
        else:
            king_row = self.blackKing_loc[0]
            king_col = self.blackKing_loc[1]
        if self.in_check:
            if len(self.checks) == 1: # Only one piece is checking -> block or move the king
                moves = self.get_possible_moves()
                #block
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_sq = []
                if piece_checking[1] == 'N':
                    valid_sq = [check_row][check_col]
                else:
                    for i in range(1,8): 
                        a = (king_row + check[2]*i, king_col + check[3]*i) 
                        valid_sq.append(a)
                        if a[0] == check_row and a[1] == check_col:
                            break
                for i in range(len(moves)-1, -1, -1):
                    if moves[i].piece_moved[1] != 'K':
                        if not (moves[i].end_row, moves[i].end_col) in valid_sq:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(king_row, king_col, moves)
        else:
            moves = self.get_possible_moves()
        return moves

    def find_pinsAndChecks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.whiteKing_loc[0]
            start_col = self.whiteKing_loc[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.blackKing_loc[0]
            start_col = self.blackKing_loc[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemy_type == "R") or \
                            (4 <= j <= 7 and enemy_type == "B") or \
                            (i == 1 and enemy_type == "p" and 
                            ((enemy_color == "w" and 6 <= j <= 7) or \
                            (enemy_color == "b" and 4 <= j <= 5))) or \
                            (enemy_type == "Q") or \
                            (i == 1 and enemy_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":  # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pins, checks

    '''Get pawn moves'''
    def get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_to_move:
            if self.board[r-1][c] == '--': #pawn advance
                if not piece_pinned or pin_direction == (-1,0) or pin_direction == (1,0):
                    moves.append(Move((r,c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == '--':
                        moves.append(Move((r,c), (r-2, c), self.board))
            if c-1 >= 0: #capture to the left
                if not piece_pinned or pin_direction in ((-1,-1), (1,1), (1,-1), (-1,1)):                
                    if self.board[r-1][c-1][0] == 'b': #enemy piece to capture
                        moves.append(Move((r,c), (r-1, c-1), self.board))
            if c+1 <= 7: #capture to the right
                if self.board[r-1][c+1][0] == 'b':
                    if not piece_pinned or pin_direction in ((-1,-1), (1,1), (1,-1), (-1,1)): 
                        moves.append(Move((r,c), (r-1, c+1), self.board))

        else:
            if self.board[r+1][c] == '--': #pawn advance
                if not piece_pinned or pin_direction == (1,0): 
                    moves.append(Move((r,c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == '--':
                        moves.append(Move((r,c), (r+2, c), self.board))
            if c-1 >= 0: #capture to the left
                if not piece_pinned or pin_direction in ((-1,-1), (1,1), (1,-1), (-1,1)): 
                    if self.board[r+1][c-1][0] == 'w': #enemy piece to capture
                        moves.append(Move((r,c), (r+1, c-1), self.board))
            if c+1 <= 7: #capture to the right
                if not piece_pinned or pin_direction in ((-1,-1), (1,1), (1,-1), (-1,1)): 
                    if self.board[r+1][c+1][0] == 'w': 
                        moves.append(Move((r,c), (r+1, c+1), self.board))            

    '''Get rook moves'''
    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1,0), (0,-1), (1,0), (0,1))
        enemy_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0]*i
                end_col = c + d[1]*i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':
                        moves.append(Move((r,c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r,c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    '''Get bishop moves'''
    def get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))  # diagonals: up/left up/right down/right down/left
        enemy_color = "b" if self.white_to_move else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = r + direction[0] * i
                end_col = c + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:  # check if the move is on board
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":  # empty space is valid
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # capture enemy piece
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:  # friendly piece
                        break
                else:  # off board
                    break

    '''Get knight moves'''
    def get_knight_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        knight_moves = ((-2,1), (2,1), (-2,-1), (2,-1), (1,2), (-1,-2), (1,-2), (-1,2))
        ally_color = 'w' if self.white_to_move else 'b'
        for d in knight_moves:
            end_row = r + d[0]
            end_col = c + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(Move((r,c), (end_row, end_col), self.board))
    
    '''Get king moves'''
    def get_king_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        king_moves = ((-1,0),  (0,1), (1,0), (0,-1), (1,1), (-1,1), (-1,-1), (1,-1))
        allY_color = 'w' if self.white_to_move else 'b'
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != allY_color:
                    moves.append(Move((r,c), (end_row, end_col), self.board))

    '''Get queen moves'''
    def get_queen_moves(self, r, c, moves):
        self.get_bishop_moves(r, c, moves)
        self.get_rook_moves(r, c, moves)
        
class Move():
    #maps key to values
    #key: value 
    ranks_to_rows = {'1':7, '2':6, '3':5, '4':4, 
                    '5':3, '6':2, '7':1, '8':0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {'a':0, 'b': 1, 'c':2, 'd':3, 
                    'e': 4,'f':5, 'g': 6, 'h':7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.moveID = self.start_row*1000 + self.start_col*100 + self.end_row*10 + self.end_col
        print(self.moveID)

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + "-" + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]





















