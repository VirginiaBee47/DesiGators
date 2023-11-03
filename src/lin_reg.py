from numpy import array

import numpy as np

def linear_regression(X: list, Y: list) -> list:

    X = np.array(X)
    Y = np.array(Y)

    [m, b] = np.polyfit(X, Y, 1)

    return m, b