Jako zapoctovy project jsem si vybral, ze udelam sachy s pomoci knihovy pygame.
Projekt jsem rozdelil do tri hlavnich souboru, na kterych jsem postupne pracoval.
Mozne zlepseni do budoucna:
1. algoritmus pro hledani dalsiho tahu je neefektivni, protoze se musi vzdy udelat a potom
  odstranit tahy
2. nejake vyhodnocovani tahu na zaklade "zkusenosti" pocitace z predchozich her
3. moznost vyberu grafickeho rozhrani
4. moznost vyberu obtiznosti pri hrani proti pocitaci

-----------------------------------------

Soubor ChessMain obstarava tyto funkce:

funkce loadImages
nacteni obrazku ze slozky images a jejich prirazeni ke stringum

funkce main
obstarava hlavni hraci smycku
volani funkci, ktere meni gamestate (makeMove, undoMove)
reagovani na kliknuti mysi nebo stisknuti klavesy
kdyz neni tah cloveka tak se spusti proce premysleni pocitace
animace pohybu figurek

funkce showSelectionScreen
zobrazeni obrazovky pro vyber jestli hraci budou pocitace nebo uzivatele

funkce drawGameState
vykresleni aktualniho stavu hry na obrazovku

funkce highlightSquares
zvyrazneni ctverecku na ktere jsme klikli a ctverecku, kam je mozne provest tah

funkce drawPieces, drawMoveLog, drawEngGameText, drawBoard
vykresleni veci v nazvu funkce

funkce animateMove
vykresleni animace figurky postupne po snimcich

---------------------------------------------

Soubor ChessEngine obstarava tyto funkce:

vytvoreni tridy gamestate, ktera uchovava vsechny dulezite informace o hre, vcetne aktualniho stavu hraciho pole

funkce makeMove
provadi tah, tak ze prislusnym zpusobem zmeni hraci plochu a updatuje vsechny informace o hre

funkce undoMove
vrati tah, a vsechny informace o hre do stavu predtim

funkce updateCastleRights
aktualizuje prava na rosadu

funkce getValidMoves
nalezeni vsech validnich tahu, vraci seznam validnich tahu

funkce inCheck
zjistuje jestli je sach nebo mat

funkce squareUnderAttack 
zjistuje jestli je policko ohrozeno

funkce getAllPossibleMoves
zjistuje vsechny mozne tahy

getPawnMoves, getRookMoves, getKnightMoves....
ziskani vsech tahu podle toho, na jakou se koukame figurku
tahy se pridaji na seznam tahu

trida Move
uchovava vsechny informace o tom, jaky pohyb chceme udelat

------------------------------------

Soubor SmartMoveFinder obstarava:

vytvoreni map toho, na ktere pozice by se jednotlive figurky chteli dostat, protoze by to pro ne bylo vyhodne
ohodnoceni jednostlivych figurek

funkce findBestMove
hledani jednoho nejlepsiho tahu za pomoci findMoveNegaMaxAlphaBeta

funkce findMoveNegaMaxAlphaBeta
hledani nejlepsiho tahu pomoci algoritmu z wikipedie https://en.wikipedia.org/wiki/Negamax

funkce scoreBoard
vyhodnoceni skore na hracim poli na zaklade pozic v mapach na zacatku a hodnotach figurek



