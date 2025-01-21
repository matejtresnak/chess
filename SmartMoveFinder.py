import random

pieceScore = {"K": 0, # hodnota jednotlivych figurek
              "Q": 10,
              "R": 5,
              "B": 3,
              "N": 3,
              "p": 1}

#tady jsem vytvoril mapy, abych zaridil, aby se jednotlive figurky posouvali na vyhodnejsi policka radsi nez jinam
knightScores = [[1, 1, 1, 1, 1, 1, 1, 1], # pro kone je vyhodne byt uprostred
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishopScores = [[4, 3, 2, 1, 1, 2, 3, 4], # pro strelce je vyhodne byt na diagonalach
                [3, 4, 3, 2, 2, 3, 4, 3],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [2, 3, 4, 3, 3, 4, 3, 2],
                [3, 4, 3, 2, 2, 3, 4, 3],
                [4, 3, 2, 1, 1, 2, 3, 4]]

queenScores = [[1, 1, 1, 3, 1, 1, 1, 1], # pro kralovnu je vyhodne byt v pozici na sach
               [1, 2, 3, 3, 3, 1, 1, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 2, 3, 3, 3, 2, 2, 1],
               [1, 4, 3, 3, 3, 4, 2, 1],
               [1, 2, 3, 3, 3, 1, 1, 1],
               [1, 1, 1, 3, 1, 1, 1, 1]]

rookScores = [[4, 3, 4, 4, 4, 4, 3, 4], # pro vez je vyhodne byt tak aby orozovala opacnou stranu
              [4, 4, 4, 4, 4, 4, 4, 4,],
              [1, 1, 2, 3, 3, 2, 1, 1,],
              [1, 2, 3, 4, 4, 3, 2, 1,],
              [1, 2, 3, 4, 4, 3, 2, 1,],
              [1, 1, 2, 3, 3, 2, 1, 1,],
              [4, 4, 4, 4, 4, 4, 4, 4,],
              [4, 3, 4, 4, 4, 4, 3, 4]]

whitePawnScores = [[8, 8, 8, 8, 8, 8, 8, 8], # pro bile pesce je vyhodne jit nahoru
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [0, 0, 0, 0, 0, 0, 0, 0]]

blackPawnScores = [[0, 0, 0, 0, 0, 0, 0, 0], # pro cerne pesce je vyhodne jit dolu
                   [1, 1, 1, 0, 0, 1, 1, 1],
                   [1, 1, 2, 3, 3, 2, 1, 1],
                   [1, 2, 3, 4, 4, 3, 2, 1],
                   [2, 3, 3, 5, 5, 3, 3, 2],
                   [5, 6, 6, 7, 7, 6, 6, 5],
                   [8, 8, 8, 8, 8, 8, 8, 8],
                   [8, 8, 8, 8, 8, 8, 8, 8]]

piecePositionScores = {"N": knightScores, # k pismenkum figurek prirazuju mapy
                       "Q": queenScores,
                       "B": bishopScores,
                       "R": rookScores,
                       "bp": blackPawnScores,
                       "wp": whitePawnScores}


CHECKMATE = 1000 # hodnota sach matu
STALEMATE = 0 # hodnota remizy
DEPTH = 2 # kolik tahu dopredu promysli pocitac

def findRandomMove(validMoves): # vybere nahodny tah
    return validMoves[random.randint(0, len(validMoves)-1)]

"""
def findBestMove(gs, validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gs.makeMove(playerMove)
        opponentsMoves = gs.getValidMoves()
        
        if gs.staleMate:
            opponentMaxScore = STALEMATE
        elif gs.checkMate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentsMove in opponentsMoves:
                gs.makeMove(opponentsMove)
                gs.getValidMoves()
                if gs.checkMate:
                    score = CHECKMATE
                elif gs.staleMate:
                    score = STALEMATE
                else:
                    score = -turnMultiplier * scoreMaterial(gs.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gs.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gs.undoMove()
        
    return bestPlayerMove
"""

def findBestMove(gs, validMoves, returnQueue): # vybere nejlepsi tah podle findMoveNegaMaxAlphaBeta 
    global nextMove, counter
    nextMove = None
    counter = 0 # kolik tahu musel projet
    #findMoveMinMax(gs, validMoves, DEPTH, gs.whiteToMove)
    findMoveNegaMaxAlphaBeta(gs, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1) # rozeberu ve funkci
    print(counter)
    returnQueue.put(nextMove) # do returnqueue se vlozi dalsi tah

def findMoveMinMax(gs, validMoves, depth, whiteToMove):
    global nextMove
    if depth == 0:
        return scoreMaterial(gs.board)
    
    if whiteToMove:
        maxScore = -CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return maxScore
    
    else:
        minScore = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMoveMinMax(gs, nextMoves, depth - 1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gs.undoMove()
        return minScore

def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove, counter
    counter += 1
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)

        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs, nextMoves, depth-1, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
    return maxScore

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier): # alpha beta jsou orezavaci hodnoty pro pruning, turn multiplier je jestli skore minimalizujeme nebo maximalizujeme
    global nextMove, counter # nextmove uchovava nejlepsi tah na nejvyssi urovni stromu
    counter += 1

    # BILY CHCE SKORE MAXIMALIZOVAT A CERNY MINIMALIZOVAT

    if depth == 0: # zakladni pripad kdyz je hloubka stromu 0 tak se sachovnice vyhodnoti
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE # zajistuje ze prvni tah bude vzdy lepsi
    for move in validMoves: # projede vsechny validni tahy
        gs.makeMove(move) # aktualizuje sachovnici na zaklade aktualniho tahu
        nextMoves = gs.getValidMoves() # najde vsechnu dalsi tahy pro aktualni tah
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)# rekurzivni volani, negativni skore znamena ze maximalizace jednoho hrace je minimalizace druheho
        if score > maxScore: # pokud zjistene skore je vetsi nez maximalni skore
            maxScore = score # maximalni skore se nastavi jako skore
            if depth == DEPTH: # kdyz jsme projeli posledni uroven stromu, kterou resime
                nextMove = move # nastavi se dalsi tah na tah
                print(move, score)
        gs.undoMove() # tah ktery jsme udelali zase odstranime
        if maxScore > alpha: #pruning - kdyz maximalni skore je vetsi nez alpha
            alpha = maxScore # nastavi se alpha na maximalni skore
        if alpha >= beta: # kdyz je alpha vetsi nebo rovna bta tak se ukonci cyklus
            break
    return maxScore

def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.staleMate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                #score it positionally
                piecePositionScore = 0
                if square[1] != "K":
                    if square[1] == "p":
                        piecePositionScore = piecePositionScores[square][row][col]
                    else:
                        piecePositionScore = piecePositionScores[square[1]][row][col]

                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore * .1
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore * .1
    return score


# vyhodnoceni sachovnice pouze na zaklade hodnot figurek na sachovnici
def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score

