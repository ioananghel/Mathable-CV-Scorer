import matplotlib.pyplot as plt
import cv2 as cv
from math import ceil, floor, sqrt
from configs import *

def showImage(title, image, grayscale=True):
    colorMap = None
    if grayscale == True:
        colorMap = 'gray'
    image=cv.resize(image,(0,0),fx=0.3,fy=0.3)
    plt.imshow(image, cmap=colorMap)
    plt.title(title)
    plt.axis('off')
    plt.show()

def getBoard(img):
    boardMaskLow = (100, 50, 50)
    boardMaskHigh = (140, 255, 255)

    hsvImage = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    boardMask = cv.inRange(hsvImage, boardMaskLow, boardMaskHigh)

    contours, _ = cv.findContours(boardMask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    largestContour = max(contours, key=cv.contourArea)
    x, y, w, h = cv.boundingRect(largestContour)

    cutoutBoard = img[y : y + h, x : x + w]

    return cutoutBoard

def resizeBoard(board, width, height):
    board = cv.resize(board, (width, height), interpolation=cv.INTER_LINEAR)
    return board

def getCells(img):
    cellsMaskLow = (90, 50, 190)
    cellsMaskHigh = (100, 100, 255)

    placedPiecesLow = (15,0,150)
    placedPiecesHigh = (80,60,255)

    hsvImage = cv.cvtColor(img, cv.COLOR_BGR2HSV)

    cellsMask = cv.inRange(hsvImage, cellsMaskLow, cellsMaskHigh)
    placedPiecesMask = cv.inRange(hsvImage, placedPiecesLow, placedPiecesHigh)

    cellsMask = cv.bitwise_or(cellsMask, placedPiecesMask)
    kernel = np.ones((17, 17), np.uint8)
    cellsMask = cv.dilate(cellsMask, kernel)

    contours, _ = cv.findContours(cellsMask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    largestContour = max(contours, key=cv.contourArea)

    x, y, w, h = cv.boundingRect(largestContour)

    return x, y, w, h

def matchPiece(piece):
    correlations = []
    maxLocs = []
    pieceCopy = piece.copy()
    pieceCopy = cv.cvtColor(pieceCopy, cv.COLOR_BGR2GRAY)
    for i in pieces.keys():
        templateImagePath = os.path.join(templatesDir, f'{i}.jpg')
        templateImage = cv.imread(templateImagePath)
        pad = 10
        templateImage = templateImage[pad:-pad, pad:-pad]
        templateImage = cv.cvtColor(templateImage, cv.COLOR_BGR2GRAY)
        corr = cv.matchTemplate(pieceCopy, templateImage,  cv.TM_CCOEFF_NORMED)
        _, _, _, maxLoc = cv.minMaxLoc(corr)
        corr=np.max(corr)
        correlations.append(corr)
        maxLocs.append(maxLoc)

    maxLoc = maxLocs[np.argmax(correlations)]
    topLeft = maxLoc

    return list(pieces.keys())[np.argmax(correlations)], topLeft

def getCellIndex(cellW, cellH, identifiedX, identifiedY, nCells):
    threshold = 0.6

    i = identifiedY / cellH
    j = identifiedX / cellW

    if i - (identifiedY // cellH) >= threshold:
        i = ceil(identifiedY / cellH)
    else:
        i = identifiedY // cellH
    if j - (identifiedX // cellW) >= threshold:
        j = ceil(identifiedX / cellW)
    else:
        j = identifiedX // cellW

    i += 1
    j += 1

    i = min(max(i, 1), nCells)
    j = min(max(j, 1), nCells)

    return i, chr(ord('A') + j - 1)

def getMaxEnergyConcentration(board):
    kernel = np.full((10, 10), 1/10)
    energyConcentration = cv.filter2D(board, -1, kernel)
    return energyConcentration

def maximizeRightSideEnergy(board):
    kernel = np.full((5, 5), 0.5/5)
    kernel[:, 50:] = 1.5/5
    maximizedRightSideEnergy = cv.filter2D(board, -1, kernel)
    return maximizedRightSideEnergy

def checkCombinations(position, constraint, currentBoard):
    i, j = position
    operations = []
    if constraint is not None:
        operations = [constraint]
    else:
        operations = ["+", "-", "*", "/"]

    print(f'received check for operations {operations}')
    
    possibleCombinations = []
    if i - 2 >= 0 and currentBoard[i - 2][j] != -1 and currentBoard[i - 1][j] != -1:
        possibleCombinations.append((currentBoard[i - 2][j], currentBoard[i - 1][j]))
    if j - 2 >= 0 and currentBoard[i][j - 2] != -1 and currentBoard[i][j - 1] != -1:
        possibleCombinations.append((currentBoard[i][j - 2], currentBoard[i][j - 1]))
    if i + 2 < nCells and currentBoard[i + 2][j] != -1 and currentBoard[i + 1][j] != -1:
        possibleCombinations.append((currentBoard[i + 1][j], currentBoard[i + 2][j]))
    if j + 2 < nCells and currentBoard[i][j + 2] != -1 and currentBoard[i][j + 1] != -1:
        possibleCombinations.append((currentBoard[i][j + 1], currentBoard[i][j + 2]))

    print(f'Checking combianations for {possibleCombinations}')

    satisfied = 0
    for combination in possibleCombinations:
        a, b = combination
        for operation in operations:
            result = None
            if operation == "+":
                result = a + b
            elif operation == "-":
                result = abs(a - b)
            elif operation == "/":
                try:
                    result = a / b if a > b else b / a
                except:
                    continue
            elif operation == "*":
                result = a * b

            if result == currentBoard[i][j]:
                print(f'satisfied {a} {operation} {b} == {currentBoard[i][j]}')
                satisfied += 1
                break

    return satisfied

def getScore(piece, position, currentBoard):
    i, j = position
    constraint = None
    if (i + 1, j + 1) in constraints:
        constraint = constraints[(i + 1, j + 1)]

    print(f'Checking combiations for {position, constraint}, with multiplier of {multiplier[i][j]}')

    return piece * multiplier[i][j] * checkCombinations(position, constraint, currentBoard)