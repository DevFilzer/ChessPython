"""
Responsible for storing all the information about the current state of a chess game. Also resposible for determinig all valid moves at the current state
"""

import pygame as p
import ChessEngine

# Global Variables
WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 24 # for animation later on
IMAGES = {}

"""
Initialize a global dictionary of images. This will be called once in main
"""
def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" +  piece + ".png"), (SQ_SIZE, SQ_SIZE))
        # Allow us to acess an image by calling IMAGES[piece]

"""
Main function of our code, this will handle user input and update the graphics
"""
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("White"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when  a move is made

    loadImages() #Only doing this once, before the while loop
    running = True
    sqSelected = () # No squares selected initially, keep tracks of the last click of the user
    playerClicks = [] # keep track of player clicks (2 tuples: [(6,4), (4, 4)])
    while running:
        for  e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse Handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() # (x, y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col): # the user clicked on the same square twice
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected) # append both 1st and 2nd clicks
                if len(playerClicks) == 2: 
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True
                    sqSelected = ()
                    playerClicks = []
            # Keys Handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
        
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()

"""
Responsible for  all the graphics within a current game state
"""
def drawGameState(screen, gs):
    drawBoard(screen) # draw squares on the board
    # TODO: add in piece highlighting or move suggestion (later)
    drawPieces(screen, gs.board) #draw pieces on top of those squares
"""
Draw the squares on the board. The top left square is always light
"""
def  drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main()