from queue import PriorityQueue
from copy import deepcopy
from enum import Enum
import time

dx, dy = [1, -1, 0, 0], [0, 0, 1, -1]

DDD=None

class Data:
    def __init__(self, h, puzzle, stk):
        self.h = h
        self.puzzle = puzzle
        self.stk = stk

    def __lt__(self, other):
        if self.h != other.h:
            return self.h > other.h
        else:
            return len(self.stk) < len(other.stk)

class Dir(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
class Dir2(Enum):
    UP = 1
    DOWN = 0
    LEFT = 3
    RIGHT = 2


class Board:
    def __init__(self, puzzle, target):
        self.puzzle = puzzle
        self.target = target


    def setPuzzle(self, puzzle):
        self.puzzle = puzzle

    def setTarget(self, target):
        self.target = target

    def huristic(self, curPuzzle):
        target = self.target
        X, Y = self.getSize()
        i = j = 0
        flag = False

        for i in range(X):  # 타겟의 인덱스 찾기
            for j in range(Y):
                if target == curPuzzle[i][j]:
                    flag = True
                    break
            if flag:
                break

        cnt = 0
        for n in range(X):  #빈 주차공간과 타겟과의 맨하탄 거리
            for m in range(Y):
                if curPuzzle[n][m] == -1:
                    cnt += abs(i - n) + abs(j - m)

        return (X + Y - i - j - 2) + cnt*0.1   # 맨하탄 거리*1.5 + cnt

    def huristic2(self, curPuzzle):
        target = self.target
        X, Y = self.getSize()
        i = j = 0
        flag = False

        for i in range(X):  # 타겟의 인덱스 찾기
            for j in range(Y):
                if target == curPuzzle[i][j]:
                    flag = True
                    break
            if flag:
                break

        return (X + Y - i - j - 2)

    def directOutCar(self):
        X, Y = self.getSize()
        curPuzzle = self.puzzle
        visit = []
        pq = PriorityQueue()

        pq.put((self.huristic2(curPuzzle), curPuzzle, []))
        visit.append(curPuzzle)
        res = False

        while not res and not pq.empty():
            h, curPuzzle, stk = pq.get()
            x = y = 0

            for x in range(X):
                flag = False
                for y in range(Y):
                    if curPuzzle[x][y] == self.target:
                        flag = True
                        break
                if flag:
                    break


            for i in range(4):
                nx = x + dx[i]
                ny = y + dy[i]

                if 0 <= nx < X and 0 <= ny < Y and curPuzzle[nx][ny] == -1:
                    temp = deepcopy(curPuzzle)
                    temp[nx][ny] = self.target
                    temp[x][y] = -1

                    if temp not in visit:
                        stack = deepcopy(stk)
                        stack.append([x, y, i])
                        pq.put((self.huristic2(temp), temp, stack))
                        visit.append(temp)

            if curPuzzle[X - 1][Y - 1] == self.target:
                res = True

        if not res:
            print("There's no empty parking slot")
            return None
        else:
            return stk



    def algorithm(self):
        pq = PriorityQueue()
        X, Y = self.getSize()
        visit = []
        dirOut = self.directOutCar()
        if dirOut:
            return (True, dirOut)
        # pq.put(Data(self.huristic(self.puzzle), self.puzzle, []))
        pq.put((self.huristic(self.puzzle), self.puzzle, []))
        visit.append(self.puzzle)
        res = False
        while not res and not pq.empty():
            # print(res)
            ##########################
            # data = pq.get()
            # h = data.h
            # curPuzzle = data.puzzle
            # stk = data.stk
            # ##########################
            h, curPuzzle, stk = pq.get()
            ##########################
            # print(h)
            # for c in range(5):
            #     print("%d\t%d\t%d"%(curPuzzle[c][0], curPuzzle[c][1], curPuzzle[c][2]))
            #print(stk)

            emptyIdx = []
            # self.mPrint(h, curPuzzle)
            for x in range(X):
                for y in range(Y):
                    if curPuzzle[x][y] == -1:
                        emptyIdx.append((x, y))

            for x, y in emptyIdx:

                for i in range(4):
                    nx = x + dx[i]
                    ny = y + dy[i]

                    if (0 <= nx < X) and (0 <= ny < Y) and curPuzzle[nx][ny] != -1:
                        temp = deepcopy(curPuzzle)
                        t = temp[x][y]
                        temp[x][y] = temp[nx][ny]
                        temp[nx][ny] = t

                        if temp not in visit:
                            stack = deepcopy(stk)
                            stack.append([nx, ny, i])
                            pq.put((self.huristic(temp), temp, stack))
                            # pq.put(Data(self.huristic(temp), temp, stack))
                            visit.append(temp)

            if curPuzzle[X - 1][Y - 1] == self.target:
                res = True
        if not res:
            print("There's no empty parking slot")
        else:
            return (False, stk)

    def getSize(self):
        X = len(self.puzzle)
        Y = len(self.puzzle[0])
        return X, Y

    def mPrint(self, h, curPuzzle):
        print(h)
        for i in curPuzzle:
            print(i)


if __name__ == "__main__":

    puzzle = []
    cnt = 2
    for i in range(5):
        puzzle.append([])
        for j in range(10):
            puzzle[i].append(cnt)
            cnt+=1

    #puzzle[0][0]=1
    #puzzle[4][9] = -1

    #DDD=0.1
    puzzle = [[-1,-1,-1],[1,-1,-1],[4,5,6],[8,-1,-1]]
    #puzzle = [[2,3,1],[4,5,6],[7,8,9],[10,11,12],[13,14,-1]]
    #puzzle = [[1,2,3],[4,5,6],[7,8,9],[10,11,12],[13,14,-1]]
    #print(puzzle)
    #print("start")

    board = Board(puzzle, 1)
    #print(board.getSize())
    # print(board.huristic(puzzle))
    start = time.time()
    flag ,stk = board.algorithm()
    end = time.time()
    #print(DDD, ":", len(stk))

    for i in stk:
        print(i[0]+1, i[1]+1, '->', i[0]+1-dx[i[2]], i[1]+1-dy[i[2]]) # x,y -> dx, dy
        #print(i[0]+1, i[1]+1, Dir(i[2]))
    print("time : ", end - start)
