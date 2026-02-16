def factorial(n):
    """
    Returns the factorial of a non-negative integer.
    Supports integer inputs only.
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError("Factorial is only defined for non-negative integers.")
    
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
