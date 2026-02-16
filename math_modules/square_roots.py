import math

def square_root(x):
    """
    Return the square root of x.
    Raises ValueError if x is negative.
    """
    if x < 0:
        raise ValueError("Cannot take square root of a negative number.")
    return math.sqrt(x)
