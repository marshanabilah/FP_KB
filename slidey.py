import pygame, sys, random
from pygame.locals import *
from collections import deque
from copy import deepcopy
import timeit
import threading

BOARDWIDTH = 3  
BOARDHEIGHT = 3 
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK = None

#                 R    G    B
BLACK =         (  0,   0,   0)
WHITE =         (255, 255, 255)
BRIGHTBLUE =    (  0,  50, 255)
WHEAT   =       (245,  222,179)
LIGHTCORAL =    (240, 128, 128)

BGCOLOR = WHEAT
TILECOLOR = LIGHTCORAL
TEXTCOLOR = WHITE
BORDERCOLOR = WHITE
BASICFONTSIZE = 20

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = WHITE

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'



# initialize pygame and create window
pygame.init()
pygame.mixer.init() # initialize for sound
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Slidey Puzzle')
BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

FPSCLOCK = pygame.time.Clock() # For syncing the FPS
    
def draw_text(surface, text, size, x, y, color):
    '''draw text to screen'''
    font = pygame.font.Font(pygame.font.match_font('freesansbold.ttf'), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

def menu():
    '''display main menu'''    
    title = pygame.image.load(r'C:\Users\lenovo\Pictures\Slidey_Puzzle.png')
    title = pygame.transform.scale(title, (WINDOWWIDTH, 81 * 2))
    background = pygame.image.load(r'C:\Users\lenovo\Pictures\wheat.jpg') 
    background = pygame.transform.scale(background, (640,480))
    background_rect = background.get_rect()

    DISPLAYSURF.blit(background, background_rect)
    DISPLAYSURF.blit(title, (0,20))
    
    pygame.draw.rect(DISPLAYSURF, LIGHTCORAL, (130, 234, 380, 35))
    pygame.draw.rect(DISPLAYSURF, LIGHTCORAL, (170, 285, 310, 35))
    draw_text(DISPLAYSURF, "PRESS [ENTER] TO BEGIN", 35, WINDOWWIDTH/2, WINDOWHEIGHT/2, WHITE)
    draw_text(DISPLAYSURF, "PRESS [Q] TO QUIT", 35, WINDOWWIDTH/2, (WINDOWHEIGHT/2) + 50, WHITE)

    pygame.display.update()
                    
    while True:
        event = pygame.event.poll()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                break
            elif event.key == pygame.K_q:
                pygame.quit()
                sys.exit()
        elif event.type == QUIT:
            pygame.quit()
            sys.exit()   
    
class perpetualTimer():

    
    def __init__(self,t,hFunction):
        self.t=t
        self.hFunction = hFunction
        self.thread = threading.Timer(self.t,self.handle_function)
        self.state =0

    def handle_function(self):
        self.hFunction()
        self.thread = threading.Timer(self.t,self.handle_function)
        self.thread.start()

    def start(self):
        self.state =1 
        self.thread.start()

    def cancel(self):
        self.state = 0
        self.thread.cancel()

    
def drawClock():
    global clock_SURF, clock_RECT, timeElapsed
    timeElapsed = timeElapsed + 1
    clock_SURF, clock_RECT = makeText(str(timeElapsed), MESSAGECOLOR, TILECOLOR, WINDOWWIDTH - 50, WINDOWHEIGHT - 450)
    DISPLAYSURF.blit(clock_SURF, clock_RECT)
    pygame.display.update()
    #print (timeElapsed)



#Astar algorithm
def astar(board):
    startState = board
    goalState = getStartingBoard()
    closedStates = []
    openStates = []
    parent = {}
    depth = 1
    gcost = {}
    fcost = {}

    openStates.append([startState,""]) 

    #fcost = gcost + h(n), h(n)=heuristic estimate 
    gcost[str([startState, ""])] = 0
    fcost[str([startState, ""])] = 0 + manhattan(startState,goalState)

    #print fcost[str([startState, ""])]

    while len(openStates) > 0:

        smallestFCost = [sys.maxsize,-99]

        for eachState in  openStates: 
            currentFCost = fcost[str(eachState)]
            if currentFCost < smallestFCost[0]:
                smallestFCost= [currentFCost, eachState]

        index = openStates.index(smallestFCost[1])
        currentState = openStates.pop(index)

        
        if currentState[0] == goalState:
            print ("found final states")
            print ("Start State: ", startState)
            print ("Goal State: ", goalState)
            path = reconstructPath(startState, currentState, parent)
            resetAstar(board, path)
            return path

        else:
            if currentState not in closedStates:
                closedStates.append(currentState)
                neighborStates = getSuccessor(currentState[0])

                for eachState in neighborStates:
                    tentative_cost = gcost[str(currentState)] + getDistance(startState,currentState[0],parent) 

                    if eachState not in openStates or  tentative_cost < gcost[str(eachState)]:
                        
                        if str(eachState[0]) not in parent.keys():
                            parent[str(eachState[0])] = currentState
                            gcost[str(eachState)]  = tentative_cost
                            fcost[str(eachState)] = gcost[str(eachState)] + manhattan(eachState[0],goalState)
                            openStates.append(eachState)

#successors
def getSuccessor(board):
    successor = list()
    moves = [UP, DOWN, LEFT, RIGHT]
    
    #If move valid
    for eachMove in moves:
        tempBoard = deepcopy(board)
        if isValidMove(tempBoard, eachMove):
            makeMove(tempBoard, eachMove)
            successor.append([tempBoard, eachMove])
            #print tempBoard, ",", eachMove
    #print (successor)
    return successor


def reconstructPath(startState, currentState, parent):
    
    path = []
    while 1:
        path.append(currentState[1])
        currentState = parent[str(currentState[0])]
        #print (path)
        if currentState[1] == '':
            break 
    print ("Number of Steps taken to solve: ", len(path))

    return path


def getDistance(startState, currentState, parent):

    path =[]
    if str(currentState[0]) not in parent.keys():
        return 1
    else: 
        while 1:
            path.append(currentState[1])
            currentState = parent[str(currentState[0])]
            #print (path)
            if currentState[1] == '':
                break 

    return len(path)



def manhattan(currentState, goalState):

    totalDistance =0
    #print currentState
    #print goalState
    for i in range (1,BOARDWIDTH*BOARDHEIGHT+1):

  
        for x in range(BOARDWIDTH):
            for y in range (BOARDHEIGHT):
                if currentState[x][y] == i:
                    currentXY = [x,y]
                    break 
        
        for x in range(BOARDWIDTH):
            for y in range (BOARDHEIGHT):
                if goalState[x][y] == i:
                    goalXY = [x,y]
                    break
 
        dx = abs(currentXY[0] - goalXY[0])
        dy = abs(currentXY[1] - goalXY[1])
        totalDistance += (dx + dy)
        #print totalDistance

    return totalDistance


def getStartingBoard():
    counter = 1
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(counter)
            counter += BOARDWIDTH
        board.append(column)
        counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1

    board[BOARDWIDTH-1][BOARDHEIGHT-1] = BLANK
    return board


def getBlankPosition(board):
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == BLANK:
                return (x, y)


def makeMove(board, move):
    blankx, blanky = getBlankPosition(board)

    if move == UP:
        board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]


def isValidMove(board, move):
    blankx, blanky = getBlankPosition(board)
    return (move == UP and blanky != len(board[0]) - 1) or            (move == DOWN and blanky != 0) or            (move == LEFT and blankx != len(board) - 1) or            (move == RIGHT and blankx != 0)


def getRandomMove(board, lastMove=None):
    validMoves = [UP, DOWN, LEFT, RIGHT]

    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)

    return random.choice(validMoves)


def getLeftTopOfTile(tileX, tileY):
    left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
    top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
    return (left, top)


def getSpotClicked(board, x, y):
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = getLeftTopOfTile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)


def drawTile(tilex, tiley, number, adjx=0, adjy=0):
    left, top = getLeftTopOfTile(tilex, tiley)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, TILESIZE, TILESIZE))
    textSurf = BASICFONT.render(str(number), True, TEXTCOLOR)
    textRect = textSurf.get_rect()
    textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
    DISPLAYSURF.blit(textSurf, textRect)


def makeText(text, color, bgcolor, top, left):
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


def drawBoard(board, message):
    DISPLAYSURF.fill(BGCOLOR)
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(textSurf, textRect)

    for tilex in range(len(board)):
        for tiley in range(len(board[0])):
            if board[tilex][tiley]:
                drawTile(tilex, tiley, board[tilex][tiley])

    left, top = getLeftTopOfTile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(ASTAR_SURF, ASTAR_RECT)
    DISPLAYSURF.blit(timer_SURF, timer_RECT)
    DISPLAYSURF.blit(clock_SURF, clock_RECT)
    DISPLAYSURF.blit(move_SURF, move_RECT)
    DISPLAYSURF.blit(numMove_SURF, numMove_RECT)


def slideAnimation(board, direction, message, animationSpeed):
    
    blankx, blanky = getBlankPosition(board)
    if direction == UP:
        movex = blankx
        movey = blanky + 1
    elif direction == DOWN:
        movex = blankx
        movey = blanky - 1
    elif direction == LEFT:
        movex = blankx + 1
        movey = blanky
    elif direction == RIGHT:
        movex = blankx - 1
        movey = blanky

    drawBoard(board, message)
    baseSurf = DISPLAYSURF.copy()
    
    moveLeft, moveTop = getLeftTopOfTile(movex, movey)
    pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

    for i in range(0, TILESIZE, animationSpeed):
        checkForQuit()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == UP:
            drawTile(movex, movey, board[movex][movey], 0, -i)
        if direction == DOWN:
            drawTile(movex, movey, board[movex][movey], 0, i)
        if direction == LEFT:
            drawTile(movex, movey, board[movex][movey], -i, 0)
        if direction == RIGHT:
            drawTile(movex, movey, board[movex][movey], i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def generateNewPuzzle(numSlides):
    sequence = []
    board = getStartingBoard()
    drawBoard(board, '')
    pygame.display.update()
    pygame.time.wait(500) # pause 500 milliseconds for effect
    lastMove = None
    for i in range(numSlides):
        move = getRandomMove(board, lastMove)
        slideAnimation(board, move, 'Generating new puzzle...', animationSpeed=int(TILESIZE / 3))
        makeMove(board, move)
        sequence.append(move)
        lastMove = move
    return (board, sequence)


def resetAnimation(board, allMoves):
    revAllMoves = allMoves[:] # gets a copy of the list
    revAllMoves.reverse()

    for move in revAllMoves:
        if move == UP:
            oppositeMove = DOWN
        elif move == DOWN:
            oppositeMove = UP
        elif move == RIGHT:
            oppositeMove = LEFT
        elif move == LEFT:
            oppositeMove = RIGHT
        slideAnimation(board, oppositeMove, '', animationSpeed=int(TILESIZE / 2))
        makeMove(board, oppositeMove) 
        
def resetAstar(board, allMoves):
    # make all of the moves in allMoves in reverse.
    revAllMoves = allMoves[:] # gets a copy of the list
    revAllMoves.reverse()

    for move in revAllMoves:
        slideAnimation(board, move, '', animationSpeed=int(TILESIZE / 2))
        makeMove(board, move)
                        

def main(): 
    '''main loop'''
    global FPSCLOCK, DISPLAYSURF, BASICFONT, RESET_SURF, RESET_RECT, NEW_SURF, NEW_RECT
    global ASTAR_SURF, ASTAR_RECT
    global timer_SURF, timer_RECT
    global clock_SURF, clock_RECT
    global move_SURF, move_RECT, numMove_SURF, numMove_RECT
    global timeElapsed 

    background = pygame.image.load(r'C:\Users\lenovo\Pictures\wheat.jpg') 
    background = pygame.transform.scale(background, (640,480))
    background_rect = background.get_rect() 
    
    running = True
    show_menu = True        
    while running: # main game loop
        
        if show_menu:
            menu()
            pygame.time.delay(1500)
            RESET_SURF, RESET_RECT = makeText('Reset',    TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 90)
            NEW_SURF,   NEW_RECT   = makeText('New Game', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 60)
            ASTAR_SURF, ASTAR_RECT = makeText('A* Solver',    TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 30)
            timer_SURF, timer_RECT = makeText('Timer:',    TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 450)
            clock_SURF, clock_RECT = makeText('0',    TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 50, WINDOWHEIGHT - 450)
            move_SURF, move_RECT = makeText('Moves:',    TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 120, WINDOWHEIGHT - 420)
            numMove_SURF, numMove_RECT = makeText('0',    TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 50, WINDOWHEIGHT - 420)


            mainBoard, solutionSeq = generateNewPuzzle(80)
            SOLVEDBOARD = getStartingBoard() 
            allMoves = [] 
            
            moves = 0
            timeElapsed = 1
            t = perpetualTimer(1, drawClock)
            t.start()

        show_menu = False
        FPSCLOCK.tick(FPS) # number of FPS per loop
        pygame.display.flip()
             
        slideTo = None # the direction, if any, a tile should slide
        msg = 'Click tile or press arrow keys to slide.' 
        if mainBoard == SOLVEDBOARD:
            msg = 'Solved!'
            t.cancel()

        drawBoard(mainBoard, msg)

        checkForQuit()
        for event in pygame.event.get(): 
            if event.type == MOUSEBUTTONUP:
                spotx, spoty = getSpotClicked(mainBoard, event.pos[0], event.pos[1])

                if (spotx, spoty) == (None, None):
                    if RESET_RECT.collidepoint(event.pos):
                        resetAnimation(mainBoard, allMoves)
                        clock_SURF, clock_RECT = makeText('0',    TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 50, WINDOWHEIGHT - 450)
                        timeElapsed=0
                        if t.state == 0: 
                            t = perpetualTimer(1, drawClock)
                            t.start()
                        moves = 0
                        allMoves = []
                    elif NEW_RECT.collidepoint(event.pos):
                        mainBoard, solutionSeq = generateNewPuzzle(80)
                        clock_SURF, clock_RECT = makeText('0',    TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 50, WINDOWHEIGHT - 450)
                        numMove_SURF, numMove_RECT = makeText('0',    TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 50, WINDOWHEIGHT - 420)
                        moves =0
                        timeElapsed =0
                        if t.state == 0: 
                            t = perpetualTimer(1, drawClock)
                            t.start()
                        allMoves = []
                    #Astar button
                    elif ASTAR_RECT.collidepoint(event.pos):
                        #resetAnimation(mainBoard, solutionSeq + allMoves) # clicked on Solve button
                        moves = len(astar(mainBoard))
                        numMove_SURF, numMove_RECT = makeText(str(moves),    TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 50, WINDOWHEIGHT - 420)
                        allMoves = []
                else:
                    blankx, blanky = getBlankPosition(mainBoard)
                    if spotx == blankx + 1 and spoty == blanky:
                        slideTo = LEFT
                    elif spotx == blankx - 1 and spoty == blanky:
                        slideTo = RIGHT
                    elif spotx == blankx and spoty == blanky + 1:
                        slideTo = UP
                    elif spotx == blankx and spoty == blanky - 1:
                        slideTo = DOWN

            elif event.type == KEYUP:
                if event.key in (K_LEFT, K_a) and isValidMove(mainBoard, LEFT):
                    slideTo = LEFT
                    moves = moves+1
                elif event.key in (K_RIGHT, K_d) and isValidMove(mainBoard, RIGHT):
                    slideTo = RIGHT
                    moves = moves+1
                elif event.key in (K_UP, K_w) and isValidMove(mainBoard, UP):
                    slideTo = UP
                    moves = moves+1
                elif event.key in (K_DOWN, K_s) and isValidMove(mainBoard, DOWN):
                    slideTo = DOWN
                    moves = moves+1

        if slideTo:
            slideAnimation(mainBoard, slideTo, 'Click tile or press arrow keys to slide.', 8) 
            makeMove(mainBoard, slideTo)
            allMoves.append(slideTo) # record the slide

        numMove_SURF, numMove_RECT = makeText(str(moves),    TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 50, WINDOWHEIGHT - 420)

        pygame.display.update()
        FPSCLOCK.tick(FPS)
        
        pygame.display.flip()
        

        
def terminate():
    pygame.quit()
    sys.exit()

def checkForQuit():
    for event in pygame.event.get(QUIT): 
        terminate() 
    for event in pygame.event.get(KEYUP): 
        if event.key == K_ESCAPE:
            terminate() 
        pygame.event.post(event) 

        

if __name__ == "__main__":
    main()
