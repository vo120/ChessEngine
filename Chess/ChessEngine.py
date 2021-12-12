"""
This class is where all the information about the current state of a chess game is stored. It will also be where the
valid moves at the current state are determined. It will also track the moves and make a log of it.
"""

# Main piece of information about the board is stored here
class GameBoard():
    def __init__(self):
        # board is an 8x8 2D list, where each element of the list has 2 characters.
        # The first character represents the color of the piece, 'b' or 'w'
        # The second character represents the type of the piece, 'K', 'Q', 'R', 'B', 'N', or 'P'
        # Standard Chess Notation (2 letter string representing the pieces): bR = black Rook, bN = black Knight,
        # bQ = black Queen, bB = black Bishop, bP = black Pawn, wP = white Pawn, wR = white Rook, wN = white Knight,
        # wB = white Bishop, wK = white King
        self.board = [  # A list of lists where each list represents a row on a chessboard (starts at top left of board)
            # Note: in this notation (not standard Chess Notation), this is row 0
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # The string "--" represents blank space on the board
            ["--", "--", "--", "--", "--", "--", "--", "--"],  # with no piece
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {"P": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                              "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}

        self.whiteToMove = True
        self.logOfMoves = []

        # keeps track of kings to make valid move calculations and simplify castling (rows, colns)
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)

        # keeps track of checkmate and stalemate
        self.checkMate = False
        self.staleMate = False

        self.isInCheck = False
        self.pins = []
        self.checks = []

        # for En Passant Move
        self.enPassantPossible = ()  # square where en passant capture can happen
        self.enPassantLogs = [self.enPassantPossible]

        # for castling move
        self.currentCastlingRights = CastleRights(True, True, True, True)
        # self.castleRightsLog =  [self.currentCastlingRights] # this will pose a problem as we are not copying the
        # self.currentCastlingRights object we are just storing another reference to it.
        self.castleRightsLog = [
            CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,  # correct way
                         self.currentCastlingRights.bks, self.currentCastlingRights.bqs)]

    '''
    Takes a move as a parameter and executes it. This will not work for castling, pawn promotion, and en-passant. 
    '''

    def makeChessMove(self, move):  # allows player to make move
        self.board[move.startRow][move.startCol] = "--"  # when piece is moved, space on board is empty
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.logOfMoves.append(move)  # log the move so we can undo it later; display history of game
        # self.whiteToMove = not self.whiteToMove  # swap players to switch turns
        # update the king's location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        if move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # for Pawn Promotion
        if move.isPawnPromotion:
            # if (self.whiteToMove) or (not self.whiteToMove):
            #promotedPiece = input("Enter your choice to Promote : Q, R, B or N : ")
            # else:
            promotedPiece = "Q"
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece

        # En-Passant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'  # capturing the piece(pawn)

        # Update enPassantPossible Variable
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:  # only for 2 square pawn advance
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enPassantPossible = ()

        # Updating En Passant Logs
        self.enPassantLogs.append(self.enPassantPossible)

        # castle Move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # king side castling
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1] # moves the rook to its new square
                self.board[move.endRow][move.endCol + 1] = '--'  # erases old rook
            else:  # queen side castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'
            '''
            Another way to do castling:
          if move.endCol < move.startCol:  # for castling at queen side
                self.board[move.endRow][0] = "--"
                self.board[move.endRow][move.endCol + 1] = move.pieceMoved[0] + "R"
            else:  # for castling at king side
                self.board[move.endRow][7] = "--"
                self.board[move.endRow][move.endCol - 1] = move.pieceMoved[0] + "R" 
                '''

        # Update Castling Rights
        self.updateCastlingRights(move)
        newCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.wqs,
                                       self.currentCastlingRights.bks, self.currentCastlingRights.bqs)
        self.castleRightsLog.append(newCastleRights)

        self.whiteToMove = not self.whiteToMove  # swap the turns of the players

    '''
    Undo the last move made. 
    '''

    def undoMove(self):
        if len(self.logOfMoves) == 0:
            print('No move done at this time. Can\'t UNDO at the start of the game.')
            return
        if len(self.logOfMoves) != 0:  # make sure there is a move to undo
            move = self.logOfMoves.pop()  # pop removes the move but also returns it so you have a reference to it
            self.board[move.startRow][move.startCol] = move.pieceMoved  # reverse piece that was moved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove  # switch turns back between players
            # update the king's position on the board after undoing the move if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.endRow, move.endCol)

            # undo En Passant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'  # removes the pawn that was captured
                self.board[move.startRow][move.endCol] = move.pieceCaptured  # returns the piece that was captured

            self.enPassantLogs.pop()
            self.enPassantPossible = self.enPassantLogs[-1]

            # undo castling rights:
            self.castleRightsLog.pop()  # get rid of last updated castling right in makeChessMove method
            newCastleRights = self.castleRightsLog[-1]
            '''Redundant but another way to do it:
            self.currentCastlingRights.wks = self.castleRightsLog[-1].wks  # update current castling right
            self.currentCastlingRights.wqs = self.castleRightsLog[-1].wqs  # update current castling right
            self.currentCastlingRights.bks = self.castleRightsLog[-1].bks  # update current castling right
            self.currentCastlingRights.bqs = self.castleRightsLog[-1].bqs  # update current castling right'''
            self.currentCastlingRights = CastleRights(newCastleRights.wks, newCastleRights.bks, newCastleRights.wqs, newCastleRights.bqs)

            # undo castling move:
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # for king side castling
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else:  # for queen side castling
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"

            # resets checkmate and stalemate to false
            self.checkMate = False
            self.staleMate = False

    '''
    Updates the castling right that is given to a move (when it is a rook or king move). 
    '''

    def updateCastlingRights(self, move):
        # if king or rook is moved
        if move.pieceMoved == "wK":
            self.currentCastlingRights.wqs = False
            self.currentCastlingRights.wks = False

        elif move.pieceMoved == "bK":
            self.currentCastlingRights.bqs = False
            self.currentCastlingRights.bks = False

        elif move.pieceMoved == "wR":
            if move.startRow == 7 and move.startCol == 0:  # left white rook [7,0] (row, coln)
                self.currentCastlingRights.wqs = False
            elif move.startRow == 7 and move.startCol == 7:  # right white rook [7, 7]
                self.currentCastlingRights.wks = False

        elif move.pieceMoved == "bR":
            if move.startRow == 0 and move.startCol == 0:  # left black rook [0,0] (row,coln)
                self.currentCastlingRights.bqs = False
            elif move.startRow == 0 and move.startCol == 7:  # right black rook [0,7]
                self.currentCastlingRights.bks = False

        # if the rook is captured
        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        if move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False

    '''
    All moves the user can make considering checks.
    '''

    def getValidMoves(self):
        # tempEnPassant = self.enPassantPossible
        tempCastlingRights = self.currentCastlingRights
        moves = []
        self.isInCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]

        if self.isInCheck:
            if len(self.checks) == 1:  # only does 1 check (block check or move king)
                # 1. generate all possible moves
                moves = self.getAllPossibleMoves()
                # to block check -> move piece in-between King and enemy piece Attacking
                check = self.checks[0]  # check information
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]  # enemy piece causing the check
                validSquares = []  # sq. to which we can bring our piece to block the check
                # if knight then it needs to be captured or move the king
                if pieceChecking[1] == "N":
                    validSquares.append((checkRow, checkCol))
                # other pieces can be blocked
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)  # check[2] & check[3] are check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:  # once you reach attacking piece stop.
                            break
                # 2. for each move, make the move; eliminates any move that doesn't block king or capture the piece
                for i in range(len(moves) - 1, -1, -1):  # when removing from a list, go backwards through the list to avoid bugs
                    if moves[i].pieceMoved[1] != "K":  # this move doesn't move the king, it must be a piece capture or block
                        # print((moves[i].endRow, moves[i].endCol))
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])  # move does not block or capture piece
            else:  # double checks because it must move the king
                self.getKingMoves(kingRow, kingCol, moves)

        else:  # not in check so all moves can work
            moves = self.getAllPossibleMoves()

            # 3. generate all opponent's moves
            # 4. for each opponent's move, see if they attack you king
            # self.whiteToMove = not self.whiteToMove  # switch terms  before calling isInCheck because makeChessMoves swtiched the turns
            # if self.isInCheck():
            # moves.remove(moves[i])  # 5. if they do attack your king, it's not a valid move
            # self.whiteToMove = not self.whiteToMove
            # self.undoMove()
        if len(moves) == 0:  # either checkmate or stalemate
            if self.isInCheck:
                self.checkMate = True
                if self.whiteToMove:
                    print("Black Wins!")
                else:
                    print("White Wins!")
            else:
                self.staleMate = True
                print("DRAW! (Stalemate)", end=', ')
                if self.whiteToMove:
                    print("White does not have any moves")
                else:
                    print("Black does not have any moves")
        else:
            self.staleMate = False
            self.checkMate = False
        self.currentCastlingRights = tempCastlingRights

        # get Updated Castling Moves for black king and white king locations
        self.getCastlingMoves(kingRow, kingCol, moves)

        # self.enPassantPossible = tempEnPassant

        return moves

    ''' 
    This method returns if a player is pinned or a king is in check
    '''

    def checkForPinsAndChecks(self):
        pins = []  # sq. where allied pinned piece is and the direction of pin
        checks = []  # sq. where enemy is attacking the king
        isInCheck = False
        # basic info
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # checks outward from king for pins and checks and keeps track of them
        #               Up      Left     Down    Right     U L      U R      D L     D R
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for j in range(len(directions)):  # stands for direction => [0,3] -> orthogonal || [4,7] -> diagonal
            d = directions[j]
            possiblePins = ()  # reset possible pins
            for i in range(1, 8):  # stands for number of squares away
                endRow = startRow + (d[0] * i)
                endCol = startCol + (d[1] * i)
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':  # when we call this function from getKingMoves we temp. move king -> this generates a phantom king and actual king is protecting it so we don't want that.
                        if possiblePins == ():  # 1st piece that too ally -> might be a pin
                            possiblePins = (endRow, endCol, d[0], d[1])
                        else:  # 2nd ally piece so no pins or checks in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        pieceType = endPiece[1]
                        # Five different possibilities here:
                        # 1) orthogonally away from King, piece is a Rook
                        # 2) Diagonally away from King, piece -> Bishop
                        # 3) 1 sq. diagonally away King, piece -> Pawn
                        # 4) Any Direction away, piece -> Queen
                        # 5) 1 sq. any direction, piece  -> King
                        if (0 <= j <= 3 and pieceType == "R") or \
                                (4 <= j <= 7 and pieceType == "B") or \
                                (i == 1 and pieceType == "P") and (
                                (enemyColor == "w" and 6 <= j <= 7) or
                                (enemyColor == "b" and 4 <= j <= 5)) or \
                                (pieceType == "Q") or \
                                (i == 1 and pieceType == "K"):
                            if possiblePins == ():  # no piece blocking, so check
                                isInCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # there exists possibility of pin
                                pins.append(possiblePins)
                                break
                        else:  # enemy piece not applying check
                            break
                else:  # OFF BOARD
                    break
        # possible checks from knight moves:
        knightMoves = [(-1, -2), (-2, -1), (1, -2), (2, -1), (1, 2), (2, 1), (-1, 2), (-2, 1)]
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":  # enemy knight attacking king
                    isInCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))
        return isInCheck, pins, checks

    '''
    This method will show if current player is in check or not. 
    '''

    def isInCheck(self):
        if self.whiteToMove:  # for white's turn to move
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:  # for black's turn to move
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    '''
    This method will determine if the enemy can attack the square rows, colns
    '''

    def squareUnderAttack(self, rows, colns):
        '''This is the less optimized way. Generates opponenets move and then sees if under attack. Max 16 opponents piece, 8 moves per piece
        (128 moves).
        self.whiteToMove = not self.whiteToMove  # switch to opponent's turn/point of view
        opponentsMove = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turns back
        for move in opponentsMove:
            if move.endRow == rows and move.endCol == colns:  # square is under attack
                return True
        return False
        '''
        # This is the more optimized way. This way takes into account the square you want to move away from and calculates the threat
        # Max 64 opponents piece, 8 moves per piece = 64 moves total
        allyColor = 'w' if self.whiteToMove else 'b'
        enemyColor = 'b' if self.whiteToMove else 'w'
        directions = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        underAttack = False
        for j in range(len(directions)):  # stands for direction => [0,3] -> orthogoal || [4,7] -> diagonal
            d = directions[j]
            for i in range(1, 8):  # stands for number of sq. away
                endRow = rows + (d[0] * i)
                endCol = colns + (d[1] * i)
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor:
                        break
                    elif endPiece[0] == enemyColor:
                        pieceType = endPiece[1]
                        # Five different possibilities here:
                        # 1) orthogonally away from king and piece is a Rook
                        # 2) Diagonally away from King and piece is a Bishop
                        # 3) 1 sq. diagonally away from King and piece is a Pawn
                        # 4) Any Direction away and piece is a Queen
                        # 5) 1 sq. any direction and piece is a King
                        if (0 <= j <= 3 and pieceType == 'R') or \
                                (4 <= j <= 7 and pieceType == 'B') or \
                                (i == 1 and pieceType == 'P') and (
                                (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5)) or \
                                (pieceType == 'Q') or \
                                (i == 1 and pieceType == 'K'):

                            return True
                        else:  # enemy piece not applying check
                            break
                else:  # OFF BOARD
                    break
        if underAttack:
            return True
        # CHECK FOR KNIGHT CHECKS:
        knightMoves = [(-1, -2), (-2, -1), (1, -2), (2, -1), (1, 2), (2, 1), (-1, 2), (-2, 1)]
        for m in knightMoves:
            endRow = rows + m[0]
            endCol = colns + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':  # enemy knight attacking king
                    return True
        return False

    '''
    All moves without taking checks into consideration. This is for moves within both pieces in question. 
    '''

    def getAllPossibleMoves(self):
        moves = []
        for rows in range(len(self.board)):  # rows in the length of board (8)/number of rows
            for colns in range(len(self.board[rows])):  # length of current row that we're looking at
                turn = self.board[rows][colns][0]  # accessing a given square on board & its character 'w'(white) or 'b'(black)
                piece = self.board[rows][colns][1]
                if not (self.whiteToMove ^ (turn == "w")):
                    # if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    if piece != "-":
                        self.moveFunctions[piece](rows, colns, moves)  # call appropriate get piece move function
                    # piece = self.board[rows][colns][1]  # takes a look at the piece so see what kind it is
                    # self.moveFunctions[piece](rows, colns, moves)  # calls the appropriate move function based on piece type
                    '''
                    you can also do this in place of self.moveFunctions[piece] for all pieces:
                    if piece == 'P':
                        self.getPawnMoves(rows, colns, moves)  # getting the pawn the moves at this row & coln & add it to the list of moves
                    elif piece == 'R':
                        self.getRookMoves(rows, colns, moves)
                    '''
        return moves

    '''
    Method to get all the pawn moves for the pawn located in row, colns, and add these moves to the list.
    '''

    def getPawnMoves(self, rows, colns, moves):
        piecePinned = False
        pinDirection = ()
        # print((self.pins))
        for i in range(len(self.pins) - 1, -1, -1):
            if (self.pins[i][0] == rows and self.pins[i][1] == colns):
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
            # white pawn moves
        if self.whiteToMove:
            # checking if square above is empty
            if self.board[rows - 1][colns] == "--":
                # if it is we append that as a valid move
                moves.append(Move((rows, colns), (rows - 1, colns), self.board))
                # checks if the piece hasn't been moved so it can do a double move
                if rows == 6 and self.board[rows - 2][colns] == "--":
                    moves.append(Move((rows, colns), (rows - 2, colns), self.board))
            # captures to the left
            if colns - 1 >= 0:
                if self.board[rows - 1][colns - 1][0] == "b":
                    moves.append(Move((rows, colns), (rows - 1, colns - 1), self.board))
                elif (rows - 1, colns - 1) == self.enPassantPossible:
                    moves.append(Move((rows, colns), (rows - 1, colns - 1), self.board, isEnpassantMove=True))
            # captures to the right
            if colns + 1 <= 7:
                if self.board[rows - 1][colns + 1][0] == "b":
                    moves.append(Move((rows, colns), (rows - 1, colns + 1), self.board))
                elif (rows - 1, colns + 1) == self.enPassantPossible:
                    moves.append(Move((rows, colns), (rows - 1, colns + 1), self.board, isEnpassantMove=True))

        # black pawn moves
        elif not self.whiteToMove:
            if self.board[rows + 1][colns] == "--":
                # checking if square below is empty
                moves.append(Move((rows, colns), (rows + 1, colns), self.board))
                # checks if the piece hasn't been moved so it can do a double move
                if rows == 1 and self.board[rows + 2][colns] == "--":
                    moves.append(Move((rows, colns), (rows + 2, colns), self.board))
            # captures to the left
            if colns - 1 >= 0:
                if self.board[rows + 1][colns - 1][0] == "w":
                    moves.append(Move((rows, colns), (rows + 1, colns - 1), self.board))
                elif (rows + 1, colns - 1) == self.enPassantPossible:
                    moves.append(Move((rows, colns), (rows + 1, colns - 1), self.board, isEnpassantMove=True))
            # captures to the right
            if colns + 1 <= 7:
                if self.board[rows + 1][colns + 1][0] == "w":
                    moves.append(Move((rows, colns), (rows + 1, colns + 1), self.board))
                elif (rows + 1, colns + 1) == self.enPassantPossible:
                    moves.append(Move((rows, colns), (rows + 1, colns + 1), self.board, isEnpassantMove=True))
        ''' Another way to implement it:
        if self.whiteToMove and self.board[rows][colns][0] == 'w':  # white pawns moves
            if self.board[rows - 1][colns] == "--":  # it's [rows-1] because we're going up the board. White pawns are decreasing up the board; 1 square pawn advance
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((rows, colns), (rows - 1, colns), self.board))
                    if rows == 6 and self.board[rows - 2][colns] == "--":  # 2 square pawn advance
                        moves.append(Move((rows, colns), (rows - 2, colns), self.board))
            if colns - 1 >= 0:  # make sure that capture to left side of board (no -1)
                if self.board[rows - 1][colns - 1][0] == 'b':  # enemy piece to capture (white captures black)
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(Move((rows, colns), (rows - 1, colns - 1), self.board))  # captures piece located: forward & to the left
                    elif (rows + 1, colns + 1) == self.enPassantPossible:
                        moves.append(Move((rows, colns), (rows - 1, colns - 1), self.board, isEnpassantMove=True))
            if colns + 1 <= 7:  # less than length of board (7); captures to the right side of board
                if self.board[rows - 1][colns + 1][0] == 'b':
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((rows, colns), (rows - 1, colns + 1), self.board))
                    elif (rows - 1, colns + 1) == self.enPassantPossible:
                        moves.append(Move((rows, colns), (rows - 1, colns + 1), self.board, isEnpassantMove=True))
        if not self.whiteToMove and self.board[rows][colns][0] == 'b':  # black pawn moves
            if self.board[rows + 1][colns] == "--":  # 1 square move
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((rows, colns), (rows + 1, colns), self.board))
                    if rows == 1 and self.board[rows + 2][colns] == "--":  # 2 square moves
                        moves.append(Move((rows, colns), (rows + 2, colns), self.board))
            # capturing
            if colns - 1 >= 0:  # capture to the left
                if not piecePinned or pinDirection == (1, -1):
                    if self.board[rows + 1][colns - 1][0] == 'w':
                        moves.append(Move((rows, colns), (rows + 1, colns - 1), self.board))
                    elif (rows + 1, colns - 1) == self.enPassantPossible:
                        moves.append(Move((rows, colns), (rows + 1, colns - 1), self.board, isEnpassantMove=True))
            if colns + 1 <= 7:  # capture to right
                if not piecePinned or pinDirection == (1, 1):
                    if self.board[rows + 1][colns + 1][0] == 'w':
                        moves.append(Move((rows, colns), (rows + 1, colns + 1), self.board))
                    elif (rows + 1, colns + 1) == self.enPassantPossible:
                        moves.append(Move((rows, colns), (rows + 1, colns + 1), self.board, isEnpassantMove=True))'''
        # todo: add pawn promotions later

    '''
    Method to get all the rook moves for the rook located at row, colns, and add these moves to the list.
    '''

    def getRookMoves(self, rows, colns, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if (self.pins[i][0] == rows and self.pins[i][1] == colns):
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[rows][colns][1] != "Q":  # added because we use the same function for queen
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemy_color = "b" if self.whiteToMove else "w"
        ''' 
        you can also say: 
        if self.whiteToMove:
            enemy_color = 'b'
        else: 
            enemy_color = 'w'
        '''
        for d in directions:
            for i in range(1, 8):  # it's really 1-7 but 8 isn't included
                endRow = rows + d[0] * i
                endCol = colns + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # empty space valid
                            moves.append(Move((rows, colns), (endRow, endCol), self.board))
                        elif endPiece[0] == enemy_color:  # enemy piece valid
                            moves.append(Move((rows, colns), (endRow, endCol), self.board))
                            break  # can't jump the enemy piece
                        else:  # friendly piece invalid (can't capture it)
                            break
                else:  # square off the board (can't capture)
                    break

    '''
    Method to get all the knight moves for the knight located at row, colns, and add these moves to the list.
    '''

    def getKnightMoves(self, rows, colns, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if (self.pins[i][0] == rows and self.pins[i][1] == colns):
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))  # knight moves in L shape
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = rows + m[0]
            endCol = colns + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:  # not an ally piece (empty or enemy piece)
                        moves.append(Move((rows, colns), (endRow, endCol), self.board))

    '''
    Method to get all the bishop moves for the bishop located at row, colns, and add these moves to the list.
    '''

    def getBishopMoves(self, rows, colns, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if (self.pins[i][0] == rows and self.pins[i][1] == colns):
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # 4 diagonals
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):  # bishop can move max of 7 squares
                endRow = rows + d[0] * i
                endCol = colns + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # check to make sure it's on the board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":  # empty space valid
                            moves.append(Move((rows, colns), (endRow, endCol), self.board))
                        elif endPiece[0] == enemy_color:  # enemy piece valid
                            moves.append(Move((rows, colns), (endRow, endCol), self.board))
                            break  # can't jump the enemy piece
                        else:  # friendly piece invalid (can't capture it)
                            break
                else:  # square off the board (can't capture)
                    break

    '''
    Method to get all the queen moves for the queen located at row, colns, and add these moves to the list.
    '''

    def getQueenMoves(self, rows, colns, moves):  # great example of abstraction since Queen can move any where on board
        self.getRookMoves(rows, colns, moves)
        self.getBishopMoves(rows, colns, moves)

    '''
    Method to get all the king moves for the king located at row, colns, and add these moves to the list.
    '''

    def getKingMoves(self, rows, colns, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = rows + kingMoves[i][0]
            endCol = colns + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # not an ally piece (empty or enemy piece)
                    # temporarily move the king to the new location
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    if allyColor == "b":
                        self.blackKingLocation = (endRow, endCol)
                    # check for if in check(also checks for pins)
                    isInCheck, pins, checks = self.checkForPinsAndChecks()
                    # if not check then valid move
                    if not isInCheck:
                        moves.append(Move((rows, colns), (endRow, endCol), self.board))
                    # place king back in original location
                    if allyColor == "w":
                        self.whiteKingLocation = (rows, colns)
                    if allyColor == "b":
                        self.blackKingLocation = (rows, colns)

    '''
    Generate all valid castle moves for the king at (rows, colns) and add them to the list of moves
    '''

    def getCastlingMoves(self, rows, colns, moves):  # could add allyColor as a parameter
        if self.squareUnderAttack(rows, colns):
            return  # you can't castle while in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or \
                (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(rows, colns, moves)

        if (self.whiteToMove and self.currentCastlingRights.wqs) or \
                (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(rows, colns, moves)

    def getKingSideCastleMoves(self, rows, colns, moves):
        if self.board[rows][colns + 1] == "--" and self.board[rows][colns + 2] == "--":
            if not self.squareUnderAttack(rows, colns + 1) and not self.squareUnderAttack(rows, colns + 2):
                moves.append(Move((rows, colns), (rows, colns + 2), self.board, isCastleMove=True))

    def getQueenSideCastleMoves(self, rows, colns, moves):
        if self.board[rows][colns - 1] == "--" and self.board[rows][colns - 2] == "--" and self.board[rows][colns - 3] == "--":
            if not self.squareUnderAttack(rows, colns - 1) and not self.squareUnderAttack(rows, colns - 2):
                moves.append(Move((rows, colns), (rows, colns - 2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

    '''
	Overloading the __str__ function to print the updating Castling Rights Properly
	'''
    def __str__(self):
        ''' Another way of doing it:
        if str.Move.isCastleMove:
            return "0-0" if self.Move.endCol == 6 else "0-0-0"
        endSquare = self.Move.getRankFile(self.Move.endRow, self.Move.endCol)
        if self.Move.pieceMoved[1] == "p":
            if self.Move.pieceCaptured:
                return self.Move.colsToFiles[self.Move.startCol] + "x" + endSquare
            else:
                return endSquare + "Q" if self.Move.isPawnPromotion else endSquare

        moveString = self.Move.pieceMoved[1]
        if self.Move.pieceCaptured:
            moveString += "x"
            return moveString + endSquare'''
        return ("Updating Castling Rights(wk, wq, bk, bq) : " + str(self.wks) + " " + str(self.wqs) + " " + str(self.bks) + " " + str(self.bqs))

class Move():
    # maps keys to the their values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1,
                   "8": 0}  # takes the ranks(rows in chess notation) and matches it up based on rows of the matrix
    rowsToRanks = {v: k for k, v in
                   ranksToRows.items()}  # reversing a ranksToRows dictionary using for look up (switching key:values in ranksToRows)
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}  # reversed coln

    def __init__(self, startSquare, endSquare, board, isEnpassantMove=False, isCastleMove=False):  # a move in chess has start & end square, board allows to store
        # info about the move & validate it)
        self.startRow = startSquare[0]  # 1st tuple for starting square
        self.startCol = startSquare[1]  # 2nd tuple for starting square
        self.endRow = endSquare[0]  # 1st tuple for ending square
        self.endCol = endSquare[1]  # 2nd tuple for ending square
        self.pieceMoved = board[self.startRow][self.startCol]  # keeping track of info, hasn't moved yet.
        self.pieceCaptured = board[self.endRow][self.endCol]  # user wanted to move from this (see lines 32 & 33) startRow/Col to endRow/Col
        # pawn-promotion
        self.isPawnPromotion = (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7)
        # en-passant
        # self.isEnpassantMove = False
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"

        # CastleMove
        self.isCastleMove = isCastleMove

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol  # gives a unique move ID between 0 - 7777 Ex. if move is 0002 -> move from row 0, coln 0 to row 0, coln 2

    '''
    Overriding the equals method
    '''

    def __eq__(self, other):  # comparing the object to another object(other)
        if isinstance(other, Move):  # making sure other is part of the Move class
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):  # returns rankFileNotation (not real chess notation (file[a-h] then rank[1-8]) for the move
        '''
        Another way to do it:
        if self.isPawnPromotion:
            # another way to do it but you would have to break the loop
            # promotedPiece = input("Enter your choice to Promote : Q, R, B or N : ")
            promotedPiece = 'Q'
            return self.getRankFile(self.endRow, self.endCol) + promotedPiece
        if self.isCastleMove:
            if self.endCol == 1:
                return "0-0-0"
            else:
                return "0-0"
        if self.isEnpassantMove:
            return self.getRankFile(self.startRow, self.startCol)[0] + "x" + self.getRankFile(self.startRow, self.startCol) + "e.p."
        if self.pieceCaptured != "--":
            if self.pieceMoved[1] == "p":
                return self.getRankFile(self.startRow, self.startCol)[0] + "x" + self.getRankFile(self.startRow, self.startCol)
            else:
                return self.pieceMoved[1] + "x" + self.getRankFile(self.endRow, self.endCol)
        else:
            if self.pieceMoved[1] == "P":
                return self.getRankFile(self.endRow, self.endCol)
            else:
                return self.pieceMoved[1] + self.getRankFile(self.endRow, self.endCol) '''
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, rows, colns):  # helper method for getChessNotation; takes rank & file for 1 square
        return self.colsToFiles[colns] + self.rowsToRanks[rows]
