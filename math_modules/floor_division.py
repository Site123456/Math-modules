def floor_divide(a, b):
    """
    Performs integer (floor) division.
    """
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a // b
