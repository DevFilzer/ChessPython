"""
This is our main driver file. Responsible for handling user input and displaying current GameState
"""
class GameState():
    def __init__(self):
        # board is an 8x8 2d list, each element of the list has 2 characters.
        # The first char determines if black or white, the seconf determines the type of piece (rook, knight, bishop, king, queen, pawn)
        # "--" represents an empty space
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
        self.moveFunctions = {"p" : self.getPawnMoves, "R" : self.getRookMoves, "N" : self.getKnightMoves,
                              "B" : self.getBishopMoves, "Q" : self.getQueenMoves, "K" : self.getKingMoves}
        
        self.whiteToMove = True
        self.moveLog = []
        
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        
        self.inCheck = False
        self.pins = []
        self.checks = []

    """
    Takes a move as a parameter and executes it. Don't work for special moves
    """
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #log the move, so we can undo it or see the history of the game
        self.whiteToMove = not self.whiteToMove #swap turns
        # tracks the location of both kings
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)


    """
    All moves cosidering checks
    """
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()

        if self.whiteToMove:
            kingRow, kingCol = self.whiteKingLocation
        else:
            kingRow, kingCol = self.blackKingLocation

        if self.inCheck:
            if len(self.checks) == 1:
                # Single check: pieces can block or capture
                moves = self.getAllPossibleMoves()
                checkRow, checkCol, checkDirRow, checkDirCol = self.checks[0]
                pieceChecking = self.board[checkRow][checkCol][1]

                validSquares = []
                if pieceChecking == "N":
                    # knights must be captured
                    validSquares = [(checkRow, checkCol)]
                else:
                    # squares between king and checker (including checker)
                    for i in range(1, 8):
                        square = (kingRow + checkDirRow * i, kingCol + checkDirCol * i)
                        validSquares.append(square)
                        if square == (checkRow, checkCol):
                            break

                # filter out illegal moves
                for i in range(len(moves) - 1, -1, -1):
                    move = moves[i]
                    if move.pieceMoved[1] != "K":
                        if (move.endRow, move.endCol) not in validSquares:
                            moves.remove(move)

            else:
                # Double check: only king moves are valid
                moves = []
                self.getKingMoves(kingRow, kingCol, moves)
                return moves
        else:
            # Not in check: all moves are valid
            moves = self.getAllPossibleMoves()

        return moves



    """
    All moves without considering checks
    """
    def getAllPossibleMoves(self):
        moves = [] 
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves) # calls the appropriate move function
        return moves

    """
    Get all the pawn moves for the pawn located at row, col and add these moves to the list
    """
    def getPawnMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        for pin in self.pins:
            if pin[0] == r and pin[1] == c:
                piecePinned = True
                pinDirection = (pin[2], pin[3])
                break

        if self.whiteToMove: # white pawns move
            if self.board[r-1][c] == "--": # 1 square pawn advance
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--": # 2 squares pawn advance
                        moves.append(Move((r, c), (r-2, c), self.board))
            #Captures
            if c-1 >= 0: #captures to the left
                if self.board[r-1][c-1][0] == "b": #check if its the enemy's piece
                    if not piecePinned or pinDirection == (-1, -1): 
                        moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7: #captures to the right
                if self.board[r-1][c+1][0] == "b":
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c), (r-1, c+1), self.board))

        else: #black turns
            if self.board[r+1][c] == "--": # 1 square pawn advance
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--": # 2 squares pawn advance
                        moves.append(Move((r, c), (r+2, c), self.board))
            # Captures
            if c-1 >= 0: #captures to the left
                if self.board[r+1][c-1][0] == "w": #check if its the enemy's piece
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7: #captures to the right
                if self.board[r+1][c+1][0] == "w":
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(Move((r, c), (r+1, c+1), self.board))

        # TODO: add pawn promotions

    """
    Get all the rook moves located ar row, col and add these to the list
    """
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for pin in self.pins:
            if pin[0] == r and pin[1] == c:
                piecePinned = True
                pinDirection = (pin[2], pin[3])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #up, left, down, right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #check wheter its on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: #same-color piece invalid
                            break
                else: # off board
                    break

    """
    Get all the knight moves located ar row, col and add these to the list
    """
    def getKnightMoves(self, r, c, moves):
        for pin in self.pins:
            if pin[0] == r and pin[1] == c:
                return
            
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)) 
        allyColor = "w" if self.whiteToMove else "b" #inverting the order seems to help with performance
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    """
    Get all the bishop moves located ar row, col and add these to the list
    """
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()

        for pin in self.pins:
            if pin[0] == r and pin[1] == c:
                piecePinned = True
                pinDirection = (pin[2], pin[3])
                break

        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # 4 Diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #check wheter its on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: #same-color piece invalid
                            break
                else: # off board
                    break
    
    """
    Get all the queen moves located ar row, col and add these to the list
    """
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)









    """
    Get all the king moves located ar row, col and add these to the list
    """
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    # place king on end square and look for checks
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # places king back on original location
                    if allyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        inCheck = False

        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow, startCol = self.whiteKingLocation
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow, startCol = self.blackKingLocation

        # Directions: vertical, horizontal, diagonal
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1),
                    (-1, -1), (-1, 1), (1, -1), (1, 1))

        for d in directions:
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (d in ((-1, 0), (1, 0), (0, -1), (0, 1)) and type == "R") or \
                        (d in ((-1, -1), (-1, 1), (1, -1), (1, 1)) and type == "B") or \
                        (type == "Q") or \
                        (type == "K" and i == 1):
                            if possiblePin == ():
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                            else:
                                pins.append(possiblePin)
                            break
                        else:
                            break
                else:
                    break
        # Knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                    (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knightMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, m[0], m[1]))

        # Pawn checks (explicitly handled instead of relying on direction index)
        if enemyColor == "b":
            # black pawns attack downwards
            if startRow + 1 <= 7:
                if startCol - 1 >= 0 and self.board[startRow + 1][startCol - 1] == "bp":
                    inCheck = True
                    checks.append((startRow + 1, startCol - 1, 1, -1))
                if startCol + 1 <= 7 and self.board[startRow + 1][startCol + 1] == "bp":
                    inCheck = True
                    checks.append((startRow + 1, startCol + 1, 1, 1))
        else:
            # white pawns attack upwards
            if startRow - 1 >= 0:
                if startCol - 1 >= 0 and self.board[startRow - 1][startCol - 1] == "wp":
                    inCheck = True
                    checks.append((startRow - 1, startCol - 1, -1, -1))
                if startCol + 1 <= 7 and self.board[startRow - 1][startCol + 1] == "wp":
                    inCheck = True
                    checks.append((startRow - 1, startCol + 1, -1, 1))

        return inCheck, pins, checks

            
    


class Move():
    # maps the keys to the values
    ranksToRows = {"1" : 7, "2" : 6, "3" : 5, "4" : 4,
                   "5" : 3, "6" : 2, "7" : 1, "8" : 0}
    rowsToRanks = {v : k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b" : 1, "c" : 2, "d" : 3,
                   "e" : 4, "f" : 5, "g" : 6, "h" : 7}
    colsToFiles = {v : k for k, v in filesToCols.items()}

    """
    Override the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]