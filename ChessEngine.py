class GameState(): # trida ktera reprezentuje aktualni stav hry
    def __init__(self): # konstruktor tridy
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
        self.whiteToMove = True # zacina bily
        self.moveLog = [] # seznam pro uchovavani tahu
        self.moveFunctions = { # kadza funkce pro nalezeni vsech moznych tahu je reprezentovana pismenem podle figurky
            'p': self.getPawnMoves,
            'R': self.getRookMoves,
            'N': self.getKnightMoves,
            'B': self.getBishopMoves,
            'Q': self.getQueenMoves,
            'K': self.getKingMoves
        }
        self.whiteKingLocation = (7, 4) # lokaci krale pouzivame pozdeji pro sach mat
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () # souradnice, kde je enpassant mozny
        self.enpassantPossibleLog = [self.enpassantPossible] # log kdy je enpassant mozny, abychom pri oddelavani tahu mohli vratit hodnotu zpet
        self.currentCastlingRight = CastleRights(True, True, True, True) # jestli je rosada mozna
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, 
                                             self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, 
                                             self.currentCastlingRight.bqs)] # log kdy je rosada mozna abychom mohli vracet tahy
    

    def makeMove(self, move): # funkce pro provedeni tahu
        self.board[move.startRow][move.startCol] = "--" # odstrani figurku ze startovniho policka
        self.board[move.endRow][move.endCol] = move.pieceMoved # polozi figurku na konecne policko
        self.moveLog.append(move) # zaznamena se tah
        self.whiteToMove = not self.whiteToMove # prepne se hrac
        if move.pieceMoved == 'wK': # kdyz se pohne kral tak se zmeni jeho lokace
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isPawnPromotion: # kdyz pesec dojde na konec tak se zmeni na kralovnu
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        if move.isEnpassantMove: # kdyz se stane enpassant tak policko mezi startovnim a konecnym bude prazdny
            self.board[move.startRow][move.endCol] = '--'

        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: # kdyz se pohne pesec o dva dopredu tak se upravi pravidlo pro enpassant
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()


        if move.isCastleMove: # kdyz se stane rosada
            if move.endCol - move.startCol == 2: # rosada z kralovy strany
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #pohne vezi
                self.board[move.endRow][move.endCol+1] = '--' #smaz starou vez
            else: # rosada ze strany kralovny
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol-2] = '--'

        self.enpassantPossibleLog.append(self.enpassantPossible) # ulozi se informace jestli je enpassant mozny

        self.updateCastleRights(move) # aktualizuje se moznost rosady
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, 
                                            self.currentCastlingRight.bks,
                                            self.currentCastlingRight.wqs, 
                                            self.currentCastlingRight.bqs))


    def undoMove(self): # odstraneni tahu
        if len(self.moveLog) != 0: # kdyz log tahu neni prazdny
            move = self.moveLog.pop() # vymazani posledniho tahu
            self.board[move.startRow][move.startCol] = move.pieceMoved # vraceni figurky kterou jsme hybali
            self.board[move.endRow][move.endCol] = move.pieceCaptured # vraceni zabrane figurky
            self.whiteToMove = not self.whiteToMove # prepnuti hrace
            if move.pieceMoved == 'wK': # kdyz se pohlo kralem tak se nastavi hodnota jeho lokace zpet na startovni
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            
            if move.isEnpassantMove: # kdys se stal enpassant tah tak se vrati
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured

            self.enpassantPossibleLog.pop()# posledni moznost enpassant se odstrani
            self.enpassantPossible = self.enpassantPossibleLog[-1]

            self.castleRightsLog.pop() # posledni moznost rosady se odstrani
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks,
                                                     newRights.bks,
                                                     newRights.wqs,
                                                     newRights.bqs)
            
            if move.isCastleMove: # kdyz se stala rosada tak se to vrati zpet
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = '--'

            self.checkMate = False
            self.staleMate = False

    def updateCastleRights(self, move): # funkce ktera aktualizuje prava na rosadu
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

        # kdyz umre vez tak se zase aktualizuji prava na rosadu
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False


    def getValidMoves(self): # funkce pro nalezeni vsech validnich tahu
        tempEnpassantPossible = self.enpassantPossible # temporay enpassant, protoze s nim pracujeme ve funkci
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, 
                                        self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, 
                                        self.currentCastlingRight.bqs)

        moves = self.getAllPossibleMoves() # nalezeni vsech moznych tahu
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves) # nalezeni tahu rosada
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        #filtrace neplatnych tahu
        for i in range(len(moves)-1, -1, -1): # smycka prochazi vsechny prvky od konce aby nevznikaly problemy s indexovanim
            self.makeMove(moves[i]) # tah se provede
            self.whiteToMove = not self.whiteToMove # zmeni se kdo je na rade
            if self.inCheck(): # zkontroluje se jestli je hrac v sachu
                moves.remove(moves[i]) # odstrsni se tah v sachu
            self.whiteToMove = not self.whiteToMove # prepne se hrac
            self.undoMove() # vrati se stav zpet pomoci undo move
        
        if len(moves) == 0: # kdyz nezbyly zadne tahy
            if self.inCheck(): # kdyz je v sachu tak je mat
                self.checkMate = True
            else:
                self.staleMate = True # jinak je pat remiza
        else:
            self.checkMate = False
            self.staleMate = False

        self.enpassantPossible = tempEnpassantPossible # vraceni zpet stavu enpassant
        self.currentCastlingRight = tempCastleRights

        return moves # vrati seznamo validnich tahu


    def inCheck(self): # zjistuje jestli je sach
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])


    def squareUnderAttack(self, r, c): # zjistuje jestli je policko ohrozeno
        self.whiteToMove = not self.whiteToMove # prepne se hrac
        oppMoves = self.getAllPossibleMoves() # zjisti se vsechny mozne tahy protivnika
        self.whiteToMove = not self.whiteToMove # prepne se hrac zpet
        for move in oppMoves: # pro vsechny tahy v oponentovych tazich
            if move.endRow == r and move.endCol == c: # kdyz se shoduji konecna radek a sloupec
                return True
        return False
        

    def getAllPossibleMoves(self): # zjistuje vsechny mozne tahy
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0] # zjisteni kdo ma tah
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove): # kdyz ma tah bily nebo cerny
                    piece = self.board[r][c][1] # nastaveni jakou mame figurku
                    self.moveFunctions[piece](r, c, moves) # zjistuje tahy podle seznamu move functions pro kazdou figurku
        return moves
    

    def getPawnMoves(self, r, c, moves): # ziska tahy pescu
        if self.whiteToMove: # kdyz hraje bily tak se divame za spoda a radky odecitame
            if self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1,c), self.board))# do seznamu tahu se prida tah
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r,c), (r-2,c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r,c), (r-1,c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r-1,c-1), self.board, isEnpassantMove=True))

            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r,c), (r-1,c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r-1,c+1), self.board, isEnpassantMove=True))


        else:# kdyz hraje cerny tak se divame seshora a radky pricitame
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board)) # do seznamu tahu se prida tah
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
                
            if c - 1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r+1,c-1), self.board, isEnpassantMove=True))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r+1, c+1), self.board, isEnpassantMove=True))


    def getRookMoves(self, r, c, moves): # ziskani tahu veze
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) # mozne smery pohybu, ktere potom budeme nasobit
        enemyColor = "b" if self.whiteToMove else "w" # kdyz hraje bily tak se barva nepritele nastavi na cernou
        for d in directions: # projede vsechny smery
            for i in range(1, 8): # projede to 8x
                endRow = r + d[0] * i # koncovy radek = radek + smer * 1-8
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # kontrola jestli cilove pozice je na sachovnici
                    endPiece = self.board[endRow][endCol] # zjistuje co je na cilovem policku
                    if endPiece == "--": # kdyz je prazdne
                        moves.append(Move((r,c), (endRow, endCol), self.board)) # ulozi se tah
                    elif endPiece[0] == enemyColor: # kdyz je tam nepritel
                        moves.append(Move((r, c), (endRow, endCol), self.board)) # ulozi se tah
                        break
                    else:
                        break
                else:
                    break
            

    def getKnightMoves(self, r, c, moves): # ziskani tahu kone
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)) # vsechny pohyby ktere muze udelat kun
        allyColor = "w" if self.whiteToMove else "b" # kdyz hraje bily tak se barva spojence da na bilou
        for m in knightMoves: # pro kazdy pohyb co muze udelat kun
            endRow = r + m[0] 
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8: # jestli je na hraci plose
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # kdyz na cilovem policku neni spojenec
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    def getBishopMoves(self, r, c, moves): # ziska vsechny tahy strelce
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1)) # tahle funkce je hodne podobna vezi akorat diagonalne
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break


    def getKingMoves(self, r, c, moves): # tahy krale, skoro stejna jako pro kone
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))



    def getCastleMoves(self, r, c, moves): # tahy rosady
        if self.squareUnderAttack(r, c): # kdyz bude policko kterym chceme pohnout ohrozeno
            return
        # kdyz bude mozne udelat rosadu tak se zikaji vsechny tahy rosady
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves) 
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)


    def getKingsideCastleMoves(self, r, c, moves): # rosada z kralovy strany
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--': # kdyz jsou policka mezi kralem a vezi prazdna
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2): # kdyz nejsou policka ohrozena
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))
    
    
    def getQueensideCastleMoves(self, r, c, moves):# rosada z kralovniny strany
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':# kdyz jsou policka mezi kralem a vezi prazdna
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2): # kdyz nejsou policka ohrozena
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))


    def getQueenMoves(self, r, c, moves): # tahy kralovny kombinuji tahy veze a strelce
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)



class CastleRights(): # trida pro praci s pravem na rosadu
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move(): # trida pohyb, ktera uchovava vsechny informace o objektu pohybu
    ranksToRows = { #ranks jsou radky odspoda, rows jsou radky odshora
        "1": 7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0
    }
    rowsToRanks = {
        v: k for k, v in ranksToRows.items()
    }
    filesToCols = { # prevadi sloupce podle pismenek na cisla
        "a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7
    }
    colsToFiles = {
        v: k for k, v in filesToCols.items()
    }

    #konstruktor se vsemi dulezitymi informacemi
    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        
        #rozhodne jestli jsme pescem dojeli nakonec a muze se vymenit za kralovnu
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)

        self.isEnpassantMove = isEnpassantMove # pokud je tah enpassant
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp' # nastavi piece captured protoze jsme presocili

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol # identifikace tahu
        self.isCastleMove = isCastleMove

    def __eq__(self, other): # porovnava dva tahy na zaklade jejich id
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    
    def getChessNotation(self): # vraci sachovou notaci tahu
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c): # prevadi zadany radek a sloupec na sachovou notaci
        return self.colsToFiles[c] + self.rowsToRanks[r]