from fractions import Fraction

def make_fraction(numerator, denominator=1):
    """
    Return a Fraction object from numerator and denominator.
    Raises ZeroDivisionError if denominator is zero.
    """
    return Fraction(numerator, denominator)

def add_fractions(f1, f2):
    """
    Return the sum of two Fraction objects.
    """
    return f1 + f2

def subtract_fractions(f1, f2):
    """
    Return the difference of two Fraction objects.
    """
    return f1 - f2

def multiply_fractions(f1, f2):
    """
    Return the product of two Fraction objects.
    """
    return f1 * f2

def divide_fractions(f1, f2):
    """
    Return the quotient of two Fraction objects.
    Raises ZeroDivisionError if f2 is zero.
    """
    if f2 == 0:
        raise ZeroDivisionError("Cannot divide by zero fraction.")
    return f1 / f2
