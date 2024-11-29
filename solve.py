from functions import *

if __name__ == "__main__":
    boardTemplate = cv.imread(boardTemplatePath)
    boardTemplate = getBoard(boardTemplate)
    boardTemplate = resizeBoard(boardTemplate, 1980, 1980)
    for game in range(1, nGames + 1):
        board = getNewBoard()
        turnsFile = os.path.join(trainDir, f'{game}_turns.txt')
        trainImages = [image for image in trainImagesCopy if image.startswith(str(game))]
        trainAnnotations = [file for file in trainAnnotationsCopy if file.startswith(str(game))]
        previousRoundBoard = boardTemplate
        with open(turnsFile, 'r') as f:
            turnsContent = f.readlines()
        turnsContent.append('')
        line = turnsContent[0]
        player, turns = line.split()
        turns = int(turns)
        turnNumber = len(turnsContent)
        currentMove = 1
        gameScoreFile = os.path.join(solutionDir, f'{game}_scores.txt')
        for i in range(1, turnNumber):
            score = 0
            turn = turnsContent[i]
            if turn != '':
                nextPlayer, nextTurns = turn.split()
                nextTurns = int(nextTurns)
            else:
                nextPlayer = 'final'
                nextTurns = 51
            if i != 1:
                with open(gameScoreFile, 'a') as f:
                    f.write('\n')
            identifiedPieces = []
            for img in trainImages[turns - 1 : nextTurns - 1]:
                image = cv.imread(os.path.join(trainDir, img))

                cutoutBoard = getBoard(image)
                resizedBoard = resizeBoard(cutoutBoard, 1980, 1980)
                cellsX, cellsY, cellsW, cellsH = getCells(resizedBoard)
                cellW, cellH = cellsW // nCells, cellsH // nCells

                currentBoardHSV = cv.cvtColor(resizedBoard, cv.COLOR_BGR2HSV)
                previousBoardHSV = cv.cvtColor(previousRoundBoard, cv.COLOR_BGR2HSV)

                hueDifference = cv.absdiff(currentBoardHSV[:, :, 0], previousBoardHSV[:, :, 0])
                _, hueThreshold = cv.threshold(hueDifference, 50, 60, cv.THRESH_BINARY)

                satDifference = cv.absdiff(currentBoardHSV[:, :, 1], previousBoardHSV[:, :, 1])
                _, satThreshold = cv.threshold(satDifference, 50, 55, cv.THRESH_BINARY)

                valueDifference = cv.absdiff(currentBoardHSV[:, :, 2], previousBoardHSV[:, :, 2])
                _, valueThreshold = cv.threshold(valueDifference, 50, 53, cv.THRESH_BINARY)

                combinedDiff = cv.bitwise_or(hueThreshold, satThreshold)
                combinedDiff = cv.bitwise_or(combinedDiff, valueThreshold)

                kernel = np.ones((3, 3), np.uint8)
                dilatedDifference = cv.dilate(combinedDiff, kernel)

                maxHueConentration = getMaxEnergyConcentration(hueThreshold)
                _, maxHueThresholded = cv.threshold(maxHueConentration, 220, 255, cv.THRESH_BINARY)
                maxHueThresholded = maximizeRightSideEnergy(maxHueThresholded)

                kernel = np.ones((9, 9), np.uint8)
                maxHueThresholded = cv.erode(maxHueThresholded, kernel)

                pad = 30
                maxHueThresholded[: cellsY - pad, :] = 0
                maxHueThresholded[cellsY + cellsH + pad : , :] = 0
                maxHueThresholded[:, : cellsX - pad] = 0
                maxHueThresholded[:, cellsX + cellsW + pad :] = 0
                
                maxSatConentration = getMaxEnergyConcentration(satThreshold)
                _, maxSatThresholded = cv.threshold(maxSatConentration, 240, 255, cv.THRESH_BINARY)

                maxSatThresholded[: cellsY - pad, :] = 0
                maxSatThresholded[cellsY + cellsH + pad : , :] = 0
                maxSatThresholded[:, : cellsX - pad] = 0
                maxSatThresholded[:, cellsX + cellsW + pad :] = 0

                maxValueConcentration = getMaxEnergyConcentration(valueThreshold)

                maxHSVThresholded = None
                if sum(maxHueThresholded.flatten()) < 2550000:
                    maxHSVThresholded = cv.bitwise_or(maxHueThresholded, maxSatThresholded)
                else:
                    maxHSVThresholded = maxHueThresholded
                dilatedDifference = cv.bitwise_and(dilatedDifference, maxHSVThresholded)

                contours, _ = cv.findContours(dilatedDifference,  cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

                try:
                    largest_contour = max(contours, key=cv.contourArea)
                except:
                    continue

                x, y, w, h = cv.boundingRect(largest_contour)
                if (w >= 100 or h >= 100) and (w < 100 or h < 100):
                    w = max(w, 100)
                    h = max(h, 100)
                croppedBoard = resizedBoard[y:y+h, x:x+w]

                identifiedPiece = matchPiece(croppedBoard)
                y, x = y + identifiedPiece[1][0], x + identifiedPiece[1][1]

                offset = 30
                i, j = getCellIndex(
                    cellW, cellH, x - cellsX + offset - 40, y - cellsY + offset - 20, nCells
                )

                board[i - 1][ord(j) - ord('A')] = identifiedPiece[0]
                pieces[identifiedPiece[0]] -= 1

                turnSolutionFile = os.path.join(solutionDir, f'{game}_{currentMove:02d}.txt')
                with open(turnSolutionFile, 'w') as f:
                    f.write(f'{i}{j} {identifiedPiece[0]}')

                identifiedPieces.append(identifiedPiece[0])

                score += getScore(identifiedPiece[0], (i - 1, ord(j) - ord('A')), board)

                previousRoundBoard = resizedBoard
                currentMove += 1

            
            with open(gameScoreFile, 'a') as f:
                f.write(f'{player} {turns} {int(score)}')

            player, turns = nextPlayer, nextTurns