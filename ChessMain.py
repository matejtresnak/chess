import pygame as p
import ChessEngine
import SmartMoveFinder
from multiprocessing import Process, Queue # pouzival jsem na threadovani, abych mohl hybat okne i kdyz premysli pocitac

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 300
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

#funkce pro nacteni obrazku figurek
def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"] #seznam s nazvy figurek
    for piece in pieces:
        #vytvoreni slovniku klic: nazev figurky, data jsou obrazky figurek
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    playerOne, playerTwo = showSelectionScreen() #vybrani jestli player one a two budou clovek (true) nebo pocitac (false)

    p.init() # inicializace pygame 
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT)) #inicializace okna
    clock = p.time.Clock() #inicializace hodin, abychom meli animace
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont('consolas', 13, False, False)
    gs = ChessEngine.GameState() # inicializace objektu gs z modulu ChessEngine
    validMoves = gs.getValidMoves() 
    moveMade = False # promenna abychom vedeli, kdy byl proveden tah
    animate = False # promenna pro to, abychom vedeli kdy delat animaci

    loadImages()
    running = True
    sqSelected = () # promenna vytvory prazdny tuple, ktery bude slouzit k identifikaci vybraneho policka
    playerClicks = [] # seznam zaznam kliknuti co hrac udela
    gameOver = False 
    #playerOne = True #if a human is playing white, then this will be true. if ai is playing white, then this will be false
    #playerTwo = False
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo) # boolean jestli je tah hrace nebo pocitace
        for e in p.event.get():
            if e.type == p.QUIT: # kdyz uzivatel zavre okno tak se zastavi smycka
                running = False
            elif e.type == p.MOUSEBUTTONDOWN: # kdyz uzivatel klikne
                if not gameOver:
                    location = p.mouse.get_pos() #zjisteni polohy kliknuti mysi, vrati tuple s pixelama
                    #prevedeni polohy kliknuti na sloupce a radky sachovnice
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col) or col > 7: # pokud uzivatel klikne na stejne misto nebo mimo sachovnici
                        sqSelected = ()
                        playerClicks = []
                    else: #kdyz uzivatel klikne na policko tak se pozice ulozi do dvou promennych
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    if len(playerClicks)==2 and humanTurn: #kdyz uzivatel kliknul dvakrat a je na rade
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board) # vytvori objekt move z enginu
                        print(move.getChessNotation()) # do konzole se vypise tah
                        for i in range(len(validMoves)): # projde vsechnu validni tahy
                            if move == validMoves[i]: # pokud je tah uzivatele ve validnich tahach
                                gs.makeMove(validMoves[i]) # provede se tah
                                #stal se tah, udelame animaci
                                moveMade = True
                                animate = True
                                #reset promennych
                                sqSelected = ()
                                playerClicks = []
                        # kdyz se nestal tah tak se akorat do player clicks prida vybrane policko
                        if not moveMade:
                            playerClicks = [sqSelected]
            
            # kdyz uzivatel stiskne klavesu
            elif e.type == p.KEYDOWN:
                # klavesa Z slouzi k vraceni tahu
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False

                    if AIThinking: #pokud zrovna premysli AI tak se to premysleni zrusi
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                # klavesa R slouzi k resetu hry
                if e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

                    if AIThinking: #pokud zrovna premysli AI tak se to premysleni zrusi
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
        
        if not gameOver and not humanTurn and not moveUndone: # kdyz neni tah cloveka
            if not AIThinking: #kdyz nepremusli AI tak se premysleni spusti
                AIThinking = True
                print("thinking...")
                returnQueue = Queue() # queue se pouziva pro predavani dat mezi thready
                # vytvori a odstartuje se proces hledani tahu AI
                moveFinderProcess = Process(target=SmartMoveFinder.findBestMove, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive(): # kdyz skonci proces hledani tahu AI
                print("done thinking")
                AIMove = returnQueue.get() # ziskani tahu AI z queue z procesu premysleni
                if AIMove is None: # kdyz nenajde zadny nejlepsi tah tak se udela nahodny tah
                    AIMove = SmartMoveFinder.findRandomMove(validMoves)
                gs.makeMove(AIMove) # provede se AI tah
                moveMade = True
                animate = True
                AIThinking = False

        if moveMade:
            if animate: # kdyz se stal tah a ma se animovat
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            # reset vseho
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False
        
        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont) # zobrazi se aktualni game state

        # kdyz je je sachmat nebo remiza
        if gs.checkMate or gs.staleMate:
            gameOver = True
            if gs.staleMate:
                text = 'Stalemate'
            else:
                if gs.whiteToMove:
                    text = 'Black wins by checkmate'
                else:
                    text = 'White wins by checkmate'
            drawEndGameText(screen, text)

        clock.tick(MAX_FPS) # zajistuje ze aktualizace nebude smycka rychla
        p.display.flip() # zmeny provedene v hernim okne se zobrazi


def showSelectionScreen(): # funkce pro zobrazeni okna s vyberem hracu
    # tohle je docela jednoducha pochopitelna funkce takze to nemam moc okomentovany
    p.init()
    screen = p.display.set_mode((400, 300))
    p.display.set_caption("Player Selection")
    font = p.font.SysFont('consolas', 24)
    clock = p.time.Clock()

    # Výchozí nastavení
    playerOneHuman = True
    playerTwoHuman = True

    # Barvy
    white = (255, 255, 255)
    black = (0, 0, 0)
    buttonColor = (200, 200, 200)
    highlightColor = (170, 170, 170)
    selectedColor = (100, 200, 100)

    # Tlačítka
    buttons = {
        "Player One: Human": p.Rect(50, 50, 300, 50),
        "Player One: Computer": p.Rect(50, 120, 300, 50),
        "Player Two: Human": p.Rect(50, 190, 300, 50),
        "Player Two: Computer": p.Rect(50, 260, 300, 50),
    }

    running = True
    while running:
        screen.fill(white)
        title = font.render("Select Players", True, black)
        screen.blit(title, (120, 10))

        for text, rect in buttons.items():
            # Změna barvy na základě aktuálního výběru
            if (text == "Player One: Human" and playerOneHuman) or \
               (text == "Player One: Computer" and not playerOneHuman) or \
               (text == "Player Two: Human" and playerTwoHuman) or \
               (text == "Player Two: Computer" and not playerTwoHuman):
                color = selectedColor
            else:
                color = highlightColor if rect.collidepoint(p.mouse.get_pos()) else buttonColor

            p.draw.rect(screen, color, rect)
            label = font.render(text, True, black)
            screen.blit(label, (rect.x + 10, rect.y + 10))

        for event in p.event.get():
            if event.type == p.QUIT:
                p.quit()
                exit()

            elif event.type == p.MOUSEBUTTONDOWN:
                if buttons["Player One: Human"].collidepoint(event.pos):
                    playerOneHuman = True
                elif buttons["Player One: Computer"].collidepoint(event.pos):
                    playerOneHuman = False
                elif buttons["Player Two: Human"].collidepoint(event.pos):
                    playerTwoHuman = True
                elif buttons["Player Two: Computer"].collidepoint(event.pos):
                    playerTwoHuman = False

            elif event.type == p.KEYDOWN and event.key == p.K_RETURN:
                running = False

        p.display.flip()
        clock.tick(MAX_FPS)

    return playerOneHuman, playerTwoHuman


def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont): # funkce pro vykresleni aktualniho stavu hry
    drawBoard(screen) # nakresleni policek
    highlightSquares(screen, gs, validMoves, sqSelected) # zvyrazneni vybraneho policka a validnich tahu
    drawPieces(screen, gs.board) # nakresleni figurek
    drawMoveLog(screen, gs, moveLogFont) # nakresleni move logu

def drawBoard(screen): # nakresleni policek
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def highlightSquares(screen, gs, validMoves, sqSelected): # zvyrazneni vybraneho policka a validnich tahu
    if sqSelected != (): # kdyz vybrany tah neni prazdny
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #pokud sqSelected je figurka kterou muzeme hybat
            # zvyrazneni vybraneho policka
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))

            # zvyrazneni validnich policek
            s.fill(p.Color('yellow'))
            for move in validMoves: # projede vsechny tahy ve validnich tahach
                if move.startRow == r and move.startCol == c: # pokud startovni radek a sloupec se shoduje s vybranym polickem
                    screen.blit(s, (SQ_SIZE*move.endCol, SQ_SIZE*move.endRow))

def drawPieces(screen, board): # nakresleni figurek
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c] # urceni jaka figurka se zobrazi, board je z gamestatu z enginu
            if piece != "--": # pokud figurka neni prazdne policko tak se nakresli
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE,r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawMoveLog(screen, gs, font): # nakresleni move logu
    moveLogRect = p.Rect(BOARD_WIDTH, 0, MOVE_LOG_PANEL_WIDTH, MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("black"), moveLogRect)
    moveLog = gs.moveLog # nacteni move logu z gamestatu
    moveTexts = [] # seznam tahu
    for i in range(0, len(moveLog), 2): # prochazi log tahu po dovou (bily a cerny)
        moveString = str(i//2 + 1) + ". " + moveLog[i].getChessNotation() + " " # vytvori se retezec pro aktualni tah
        if i+1 < len(moveLog): # pokud existuje druhy tah v paru
            moveString += moveLog[i+1].getChessNotation() + " " # prida se druhy tah do retezce
        moveTexts.append(moveString) # retezec se prida do seznamu

    movesPerRow = 3
    padding = 5
    textY = padding
    for i in range(0, len(moveTexts), movesPerRow): # prochazi seznam tahu a vykresluje je po radcich
        text = ""
        for j in range(movesPerRow):
            if i + j < len(moveTexts):
                text += moveTexts[i+j] #kazdy tah se prida na radek
        textObject = font.render(text, True, p.Color('white')) # vytvoreni objektu pro pismo
        textLocation = moveLogRect.move(padding, textY)# Určíme pozici textu v panelu logu
        screen.blit(textObject, textLocation)# Vykreslíme text na obrazovku
        textY += textObject.get_height() # Posuneme Y pozici pro další řádek textu

def animateMove(move, screen, board, clock): #animace tahu
    global colors
    dR = move.endRow - move.startRow #rozdil v mezi konecnym a startovnim radkem
    dC = move.endCol - move.startCol # rozdil mezi konecnym a startovnim sloupcem
    framesPerSquare = 10 # za kolik snimku prejede figurka 1 policko 
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare # kolik snimku bude potreba na animaci
    for frame in range(frameCount+1): # pujde tolikrak kolik je potreba snimku na animaci
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount) # radek a sloupec se postupne meni podle toho v jake fazi animaci jsme
        drawBoard(screen)
        drawPieces(screen, board)

        #vymazani figurky ze startovni pozice
        color = colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        #vykresleni zabirane figurky
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol*SQ_SIZE, enPassantRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        #vykresleni pohybujici se figurky
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def drawEndGameText(screen, text):# vykresleni textu na konci hry
    font = p.font.SysFont('consolas', 32, True, False)
    textObject = font.render(text, 0, p.Color('Red'))
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2, BOARD_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)


if __name__ == "__main__":
    main()

