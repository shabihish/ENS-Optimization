import numpy as np


def roll_non_zero_rows_to_beginning(arr, axis=0):
    marr = np.sort(np.where(arr == 0, arr.max() + 1, arr), axis=1)
    return np.where(marr == marr.max(), 0, marr)
