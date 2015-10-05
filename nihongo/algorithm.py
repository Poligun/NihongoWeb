from collections import defaultdict
import random

def getLcs(string1, string2):
    f, p = {}, {}
    #Initialize
    for i in range(len(string1) + 1):
        f[(i, 0)], p[(i, 0)] = 0, -1
    for j in range(len(string2) + 1):
        f[(0, j)], p[(0, j)] = 0, -1
    #dp
    maxF = [0, (0, 0)]
    for i in range(1, len(string1) + 1):
        for j in range(1, len(string2) + 1):
            if string1[i - 1] == string2[j - 1]:
                f[(i, j)] = f[(i - 1, j - 1)] + 1
                p[(i, j)] = 0
            elif f[(i - 1, j)] >= f[(i, j - 1)]:
                f[(i, j)] = f[(i - 1, j)]
                p[(i, j)] = 1
            else:
                f[(i, j)] = f[(i, j - 1)]
                p[(i, j)] = 2
            if f[(i, j)] > maxF[0]:
                maxF = [f[(i, j)], (i, j)]
    #back tracing
    lcs = ''
    i = maxF[1]
    while p[i] != -1:
        if p[i] == 0:
            lcs += string1[i[0] - 1]
            i = (i[0] - 1, i[1] - 1)
        elif p[i] == 1:
            i = (i[0] - 1, i[1])
        else:
            i = (i[0], i[1] - 1)
    return lcs[::-1]

def weightedSample(candidates, weightFunc, number):
    weightedList = [[c, weightFunc(c)] for c in candidates]
    result = []
    random.seed()
    for _ in range(number):
        choice = random.random() * sum(element[1] for element in weightedList)
        weightSum = 0
        for i in range(len(weightedList)):
            candidate, weight = weightedList[i]
            weightSum += weight
            if choice < weightSum:
                result.append(candidate)
                del weightedList[i]
                break
    return result

def weightedChoice(candidates, weightFunc):
    return weightedSample(candidates, weightFunc, 1)[0]

def multiplyArrays(*arrays):
    if len(arrays) == 0:
        return []
    result = [[e] for e in arrays[0]]
    for i in range(1, len(arrays)):
        newResult = []
        for listElement in result:
            for element in arrays[i]:
                newResult.append(listElement + [element])
        result = newResult
    return result

if __name__ == '__main__':
    print(getLcs('global', 'printing'))
