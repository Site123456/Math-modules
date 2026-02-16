def mod(a, b):
    """
    Return a modulo b.
    Raises ZeroDivisionError if b is zero.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot modulo by zero.")
    return a % b
