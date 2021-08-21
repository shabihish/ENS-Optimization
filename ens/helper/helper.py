import os
import platform

# consts
WINDOWS = 'windows'

# clc, ... definition
clearc = lambda: os.system('cls') if platform.platform().lower() == WINDOWS else os.system('clear')

get_dist = lambda l1, l2: ((l1[0] - l2[0]) ** 2 + (l1[1] - l2[1]) ** 2) ** 0.5


def is_member(A, B):
    iloc = []
    idx = []

    for i in range(len(A)):
        x = 0
        y = -1
        for j in range(len(B)):
            if A[i] == B[j]:
                x=1
                y=j
                break
        iloc.append(x)
        idx.append(y)
    return iloc, idx
