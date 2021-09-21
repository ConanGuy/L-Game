import math
import os
import pygame
import numpy as np
from operator import add, sub
from consts import *
from copy import deepcopy

class LPiece:

    def __init__(self, square=[0,0], angle=0, mirror=False):
        self.mainSquare = square
        self.angle = angle
        self.mirror = mirror
        
    def get_squares(self):
        c = -1 if self.mirror else 1
        squares = [
            list(map(add, self.mainSquare.copy(), [0,0])),
            list(map(add, self.mainSquare.copy(), [c,0])),
            list(map(add, self.mainSquare.copy(), [0,1])),
            list(map(add, self.mainSquare.copy(), [0,2]))
        ]

        return self.rotate_all_points(squares)

    def rotate_all_points(self, squares):
        newSquares = []
        for s in squares:
            newSquares.append(self.rotate_point(s))
        return newSquares

    def rotate_point(self, p):
        s = math.sin(math.radians(self.angle))
        c = math.cos(math.radians(self.angle))

        toOrigin = list(map(sub, p, self.mainSquare))

        newx = int(toOrigin[0] * c + toOrigin[1] * s)
        newy = int(-toOrigin[0] * s + toOrigin[1] * c)

        return list(map(add, [newx,newy], self.mainSquare))

    def collide(self, other):
        return any(p in other.get_squares() for p in self.get_squares())

    def move(self, c):
        lc = self.copy()
        change = True  
        lc.mainSquare = list(map(add, lc.mainSquare, c))
        for s in lc.get_squares():
            x, y = tuple(s)
            
            if not (0 <= x < GRID_COLS and 0 <= y < GRID_ROWS):
                change = False
                break

        if change:
            self.mainSquare = lc.mainSquare

    def copy(self):
        return LPiece(self.mainSquare.copy(), self.angle, self.mirror)

    def __str__(self):
        return str(self.get_squares())

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        return self.mainSquare == other.mainSquare and self.angle == other.angle and self.mirror == other.mirror

class LGame:

    def __init__(self, coins= None, players=None, current=0):
        self.coins = [
            [0,GRID_ROWS-1],
            [GRID_COLS-1,0]
        ] if coins == None else coins

        self.players = [LPiece([1,0], 0, False),LPiece([2,GRID_ROWS-1], 180, False)] if players == None else players
        self.currentPlayer = current
        self.phase = 0

    def __str__(self):
        s = ''
        for x in range(3,-1,-1):
            for y in range(0,4):
                if [y,x] in self.coins:
                    s += 'C'
                elif [y,x] in self.players[0].get_squares():
                    s += '1'
                elif [y,x] in self.players[1].get_squares():
                    s += '2'
                else:
                    s += '*'
            s += '\n'
        return s

    def copy(self):
        return LGame(self.coins.copy(), deepcopy(self.players.copy()), self.currentPlayer)

    def is_valid(self):
        for p in self.players:
            squares = p.get_squares()
            if any(c in squares for c in self.coins):
                return False

            for s in squares:
                x, y = tuple(s)
                if not (0 <= x < GRID_COLS and 0 <= y < GRID_ROWS):
                    return False

        return not self.players[0].collide(self.players[1])

    def is_end(self):
        for mirror in [True, False]:
            for angle in [0,90,180,270]:

                for i in range(GRID_COLS):
                    for j in range(GRID_ROWS):
                        lc = self.copy()
                        p = LPiece([i,j], angle, mirror)
                        if p != self.players[self.currentPlayer]:
                            lc.players[self.currentPlayer] = p
                            if lc.is_valid():
                                return False

        return True   

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        ret = True
        if self.coins[0] == other.coins[0]:
            if self.coins[1] != other.coins[1]:
                return False
        elif self.coins[0] == other.coins[1]:
            if self.coins[1] != other.coins[0]:
                return False
        else:
            return False

        return self.players[0] == other.players[0] and self.players[1] == other.players[1]
