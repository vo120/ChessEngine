"""
This is the main driver file responsible for handling user input and displaying the current GameState object.
"""
import sys
import pygame as pg
from Chess import ChessEngine # This is so there is access to the board/game state
# pg.init() you can initilize game up here as well but if you do, delete line font init below and pg init in the main
pg.font.init()

#testing out another way to import: from Chess.ChessEngine import Game_Board

WIDTH = HEIGHT = 512 # 400 IS ANOTHER OPTION (HIGHER -> HIGHER RESOLUTION)
DIMENSION = 8  # The dimensions of a chess board are 8x8
SQUARE_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  # For animations later on
MOVE_LOG_PANEL_WIDTH = 512 # 250 leaves a huge white space at the right
MOVE_LOG_PANEL_HEIGHT = HEIGHT
MOVE_LOG = True
MOVE_LOG_FONT = pg.font.SysFont('Arial', 16, False, False, None)
IMAGES = {}  # Dictionary of imagesForChessPieces of the chess pieces

''' 
Initializing a global dictionary of imagesForChessPieces. This will be called exactly once in the main so it does not load multiple 
imagesForChessPieces. 
'''

def load_images():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bP', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load("imagesForChessPieces/" + piece + ".png"),
                                           (SQUARE_SIZE, SQUARE_SIZE))
    # Note: An image can also be accessed by saying 'IMAGES['wP']' etc.


'''
This the main driver for the code which will take care of the user input and updating the graphics.
'''


def main():
    pg.init()  # Initializing pygame
    screen = pg.display.set_mode((WIDTH + MOVE_LOG_PANEL_HEIGHT, HEIGHT))  # Screen variable
    clock = pg.time.Clock()  # creating the clock to keep track of time
    screen.fill(pg.Color("white"))  # filling screen with white background color
    game_state = ChessEngine.GameBoard()  # creating a game_state object calling the constructor GameState()
    validMoves = game_state.getValidMoves()  # able to see list of moves user made and see if its in list of valid moves engine generated & then can only make those moves
    moveMade = False  # flag variable for when a move is made (then make a new set of validmoves, else don't regenerate validmoves function)
    load_images()  # only doing this once before the while loop
    running = True
    animate = False	 # flag variable to note when we should animate the piece movement
    squareSelected = () # keeps track of the last click of the user (tuple: row and coln); no square selected initially
    playerClicks = [] # keeps track of the player clicks (2 tuples: [(6,4), (4,4)]) <- moving white pawn from one location to next
    playerOne = True  # if Human is playing white -> this will be true
    playerTwo = True  # if Human is playing black -> this will be true
    gameOver = False  # True in case of Checkmate and Stalemate

    while running:
            humanTurn = (game_state.whiteToMove and playerOne) or (not game_state.whiteToMove and playerTwo)
            for a in pg.event.get():
                if a.type == pg.QUIT:  # so the game exits when the user quits it
                    running = False
                    pg.quit()
                    sys.exit()
                # mouse handler
                elif a.type == pg.MOUSEBUTTONDOWN:
                    if not gameOver:
                        location = pg.mouse.get_pos() # (x, y) location of the mouse
                        coln = location[0]//SQUARE_SIZE # column where the mouse is located in the board
                        row = location[1]//SQUARE_SIZE # row where mouse is located in the board; double divides b/c needs to be integers
                        if(coln >= 8): 	# click out of board (on move log panel) -> do nothing
                            continue
                        if squareSelected == (row, coln) or coln >= 8: # the user clicked the same square twice (undo action)/ already selected a square
                            squareSelected = () # deselect the square then
                            playerClicks = [] # clear player clicks and restart it
                        else: # selecting a different square than previously selected
                            squareSelected = (row, coln)
                            playerClicks.append(squareSelected) #appending the clicks to player click list (1st click, 2nd click) see note playerclicks
                            # note: append for both 1st & second click
                            if len(playerClicks) == 2 and humanTurn: # len of player clicks after 2nd click
                                move = ChessEngine.Move(playerClicks[0], playerClicks[1], game_state.board)
                                #to check: print(move.getChessNotation())
                                for i in range(len(validMoves)):
                                    if move == validMoves[i]:
                                        game_state.makeChessMove(validMoves[i]) #makes moves
                                        moveMade = True
                                        animate = True
                                        squareSelected = ()  # reset user clicks
                                        playerClicks = []  # reset player clicks
                                if not moveMade:  # invalid move or if a user did a 2nd click on another piece
                                    playerClicks = [squareSelected]  # instead or resetting clicks, this resets the click to current square selection
                #key handler
                elif a.type == pg.KEYDOWN:  # this event fires everytime a user pushes a key; it records that key
                    if a.key == pg.K_z:  # undo when 'z' is pressed
                        game_state.undoMove()
                        animate = False
                        gameOver = False
                        moveMade = True # another option "validMoves = game_state.getValidMoves()"
                    if a.key == pg.K_r:  # reset the game if 'r' is pressed
                        game_state = ChessEngine.GameBoard()
                        sqSelected = ()
                        playerClicks = []
                        moveMade = False
                        animate = False
                        gameOver = False
                        validMoves = game_state.getValidMoves()
            if moveMade: # generates new set of valid moves and sets flag back to false
                    if len(game_state.logOfMoves) > 0 and animate:
                        animate = False
                        moveMade = False
                        animateMove(game_state.logOfMoves[-1], screen, game_state.board, clock)
                    validMoves = game_state.getValidMoves()
                    #moveMade = False
            drawStateOfGame(screen, game_state, squareSelected, validMoves)

            #Print Checkmate
            if game_state.checkMate:
                gameOver = True
                if game_state.whiteToMove:
                    drawEndGameText(screen, "Black Won by Checkmate!");
                else:
                    drawEndGameText(screen, "White Won by Checkmate!");

            #Print Stalemate
            elif game_state.staleMate:
                gameOver = True
                drawEndGameText(screen, "Draw due to Stalemate!")

            clock.tick(MAX_FPS)
            pg.display.flip()
# pg.display.quit()
#pg.quit()

'''
This method holds all of the graphics within the current state of a game. 
'''


def drawStateOfGame(screen, game_state, squareSelected, validMoves):
    drawBoard(screen)  # draws the squares on the board
    highlightSquares(screen, game_state, squareSelected, validMoves)
    if len(game_state.logOfMoves) > 0:
        highlightLastMove(screen, game_state.logOfMoves[-1])
    drawPieces(screen, game_state.board)  # draws the pieces on top of the squares
    drawMoveLog(screen, game_state)

'''  
This method draws the squares on the board. The top left square is always light (true from black and white's perspective). 
'''


def drawBoard(screen):
    colors = [pg.Color("white"), pg.Color("gray")]
    for rows in range(DIMENSION):
        for colns in range(DIMENSION):  # colns for column
                color = colors[((rows+colns) % 2)]  # tells you if the row in the column sum is even or odd & picks the colors based on that
                pg.draw.rect(screen, color, pg.Rect(colns*SQUARE_SIZE, rows*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

'''
For highlighting the correct square of selected piece and the squares it can move to
'''
def highlightSquares(screen, game_state, squareSelected, validMoves):
    if squareSelected != ():
        rows, colns = squareSelected
        enemyColor = 'b' if game_state.whiteToMove else 'w'
        allyColor = 'w' if game_state.whiteToMove else 'b'
        if game_state.board[rows][colns][0] == allyColor:
            #Highlighting the selected Square
            s = pg.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(100)		# transparency value -> 0 : 100% transparent | 255 : 100% Opaque
            s.fill(pg.Color('blue'))
            screen.blit(s, (colns*SQUARE_SIZE, rows*SQUARE_SIZE))

            #Highlighting the valid move squares
            s.fill(pg.Color('yellow'))
            for move in validMoves:
                if move.startRow == rows and move.startCol == colns:
                    endRow = move.endRow
                    endCol = move.endCol
                    if game_state.board[endRow][endCol] == '--' or game_state.board[endRow][endCol][0] == enemyColor:
                        screen.blit(s, (endCol * SQUARE_SIZE, endRow * SQUARE_SIZE))

'''
This method will highlight the last move
'''
def highlightLastMove(screen, move):
    startRow = move.startRow
    startCol = move.startCol
    endRow = move.endRow
    endCol = move.endCol
    s = pg.Surface((SQUARE_SIZE, SQUARE_SIZE))
    s.set_alpha(100)
    s.fill(pg.Color("pink"))
    screen.blit(s, (startCol * SQUARE_SIZE, startRow * SQUARE_SIZE))
    screen.blit(s, (endCol * SQUARE_SIZE, endRow * SQUARE_SIZE))

'''
This method draws the pieces on the board using the current gamestate's board variable (game_state.board).
'''
def drawPieces(screen, board):
    for rows in range(DIMENSION):
        for colns in range(DIMENSION):  # colns for column
            piece = board[rows][colns]
            if piece != "--":  # not an empty square/space
                screen.blit(IMAGES[piece], pg.Rect(colns*SQUARE_SIZE, rows*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

'''
This method will draw the Move Log
'''
def drawMoveLog(screen, game_state):
    font = MOVE_LOG_FONT
    moveLogRect = pg.Rect(WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    pg.draw.rect(screen, pg.Color('black'), moveLogRect)
    logOfMoves = []
    for i in range(0, len(game_state.logOfMoves), 2):
        moveString = str(i//2 + 1) + ".  " + str(game_state.logOfMoves[i].getChessNotation())
        if i < len(game_state.logOfMoves) - 1:  # make sure black made a move
            moveString += "  " + game_state.logOfMoves[i+1].getChessNotation()
        logOfMoves.append(moveString)

    horizontalPadding = 5
    verticalPadding = 5
    lineSpacing = 10  # can also do 2 or 5
    for i in range(len(logOfMoves)):
        textObject = font.render(logOfMoves[i], True, pg.Color('white'))
        if(verticalPadding + textObject.get_height() >= (MOVE_LOG_PANEL_HEIGHT - 1)):
            # if i > 1:
            verticalPadding = 5
            horizontalPadding += 100
        textLocation = moveLogRect.move(horizontalPadding, verticalPadding)
        verticalPadding += textObject.get_height() + lineSpacing

        screen.blit(textObject, textLocation)
'''
Animates the movement of piece
'''
def animateMove(move, screen, board, clock):
    global colors
    colors = [pg.Color(235, 235, 208), pg.Color(119, 148, 85)]
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 3		# frames to move 1 square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        rows, colns = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase piece from endRow, endCol
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = pg.Rect(move.endCol * SQUARE_SIZE, move.endRow * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pg.draw.rect(screen, color, endSquare)
        #draw captured piece back
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                endSquare = pg.Rect(move.endCol * SQUARE_SIZE, move.startRow * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], pg.Rect(colns*SQUARE_SIZE, rows*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        pg.display.flip()
        clock.tick(60)

'''
This method will write text in the middle of the screen!
'''
def drawEndGameText(screen, text):
    #  Font Name  Size Bold  Italics
    font = pg.font.SysFont('Helvitica', 32, True, False)
    textObject = font.render(text, 0, pg.Color('White'))
    textLocation = pg.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, pg.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))
    textObject = font.render(text, 0, pg.Color('Blue'))
    screen.blit(textObject, textLocation.move(4, 4))

if __name__ == "__main__": #Fixed bug that wasn't displaying the board by removing the space in " __main__" to "__main__"
    main()
