import os
import numpy as np
import cv2 as cv

rootDir = os.getcwd()
trainDir = os.path.join(rootDir, 'antrenare')
templatesDir = os.path.join(rootDir, 'imagini_auxiliare/templates/')
trainImages = os.listdir(trainDir)
trainImages = sorted([image for image in trainImages if '.jpg' in image])
trainImagesCopy = trainImages.copy()
trainAnnotations = os.listdir(trainDir)
trainAnnotations = sorted([file for file in trainAnnotations if '.txt' in file])
trainAnnotationsCopy = trainAnnotations.copy()
boardTemplatePath = os.path.join(templatesDir, '01.jpg')
solutionDir = os.path.join(rootDir, 'evaluare', 'fisiere_solutie', '463_Anghel_Ioan-Tudor-Alexandru')

nGames = 4

nCells = 14
origBoard = np.full((nCells, nCells), -1)
origBoard[6][6] = 1
origBoard[6][7] = 2
origBoard[7][6] = 3
origBoard[7][7] = 4
def getNewBoard():
    return origBoard.copy()
multiplier = np.ones((nCells, nCells))
rows = [i for i in range(14)]
cols = [chr(ord('A') + i) for i in range(14)]

for i in range(5):
    multiplier[i][i] = 2
    multiplier[i + 9][i + 9] = 2
    multiplier[nCells - i - 1][i] = 2
    multiplier[i][nCells - i - 1] = 2

multiplier[0][0] = 3
multiplier[0][6] = 3
multiplier[0][7] = 3
multiplier[0][13] = 3
multiplier[6][0] = 3
multiplier[6][13] = 3
multiplier[7][0] = 3
multiplier[7][13] = 3
multiplier[13][0] = 3
multiplier[13][6] = 3
multiplier[13][7] = 3
multiplier[13][13] = 3

constraints = {
    (2, 5): "/",
    (2, 10): "/",
    (3, 6): "-",
    (3, 9): "-",
    (4, 7): "+",
    (4, 8): "*",
    (5, 2): "/",
    (5, 7): "*",
    (5, 8): "+",
    (5, 13): "/",
    (6, 3): "-",
    (6, 12): "-",
    (7, 4): "*",
    (7, 5): "+",
    (7, 10): "*",
    (7, 11): "+",
    (8, 4): "+",
    (8, 5): "*",
    (8, 10): "+",
    (8, 11): "*",
    (9, 3): "-",
    (9, 12): "-",
    (10, 2): "/",
    (10, 7): "+",
    (10, 8): "*",
    (10, 13): "/",
    (11, 7): "*",
    (11, 8): "+",
    (12, 6): "-",
    (12, 9): "-",
    (13, 5): "/",
    (13, 10): "/"    
}
 
pieces = {
    0: 1, 
    
    1: 7, 2: 7, 3: 7, 4: 7, 5: 7, 6: 7, 7: 7, 8: 7, 9: 7, 10: 7, 
    
    11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 19: 1,
    
    20: 1, 21: 1, 24: 1, 25: 1, 27: 1, 28: 1,
    
    30: 1, 32: 1, 35: 1, 36: 1,
    
    40: 1, 42: 1, 45: 1, 48: 1, 49: 1,
    
    50: 1, 54: 1, 56: 1,
    
    60: 1, 63: 1, 64: 1,
    
    70: 1, 72: 1,
    
    80: 1, 81: 1,
    
    90: 1
}
