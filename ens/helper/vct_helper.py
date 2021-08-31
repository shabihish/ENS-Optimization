import numpy as np


def roll_non_zero_rows_to_beginning(arr, axis=0):
    prev_max = np.max(arr)
    marr = np.sort(np.where(arr == 0, prev_max + 1, arr), axis=1)
    return np.where(marr == prev_max + 1, 0, marr)
