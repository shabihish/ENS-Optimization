import numpy as np


def roll_non_zero_rows_to_beginning(arr, axis=0):
    prev_max = np.max(arr)
    marr = np.sort(np.where(arr == 0, prev_max + 1, arr), axis=1)
    return np.where(marr == prev_max + 1, 0, marr)


def get_next_valued_slice_along_axis(arr, axis=0):
    if axis == 0:
        args = np.argmax(arr.any(axis=0), axis=0)
    else:
        args = np.argmax(arr.any(axis=axis - 1), axis=axis - 1)

    return arr[..., np.arange(arr.shape[axis - 1]), args]


def get_last_valued_slice_along_axis(arr, axis=0):
    arr = arr[..., ::-1]
    if axis == 0:
        args = np.argmax(arr.any(axis=0), axis=0)
    else:
        args = np.argmax(arr.any(axis=axis - 1), axis=axis - 1)

    return arr[..., np.arange(arr.shape[axis - 1]), args]
