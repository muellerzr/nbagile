from fastai.vision.all import *
import numpy as np

class Arithmetic():
    """A class that can perform basic arithmetic on ops"""
    _o = 2
    _b = 5
    _c = 3
    class A():
        def __init__(self, o:int):
            """
            Parameters
            ----------
            o : int
              An integer
            """
            self.o = o
        
    def __init__(self, a:int, b:(int, float)):
        """
        Parameters
        ----------
        a : int
          The first number to use
        b : (int, float)
          The second number to use
        """
        self.a = a
        self.b = b
    
    @delegates()
    def add(self):
        """Adds self.a and self.b
    
        Returns
        -------
        (int, float)
          Sum of a and b
        """
        return (self.a + self.b)
    
def foo(a:int, b:int):
    """Adds

    Parameters
    ----------
    a : int
      First
    b : int
      Second

    Returns
    -------
    (int, float)
      Sum of a and b
    """
    return (a + b)

def baz(a:int, b:int):
    """Subtracts

    Parameters
    ----------
    a : int
      First
    b : int
      Second

    Returns
    -------
    (int, float)
      Difference of a and b
    """
    return (a - b)

myConst = 22

def bar(a:int, b:int):
    """Multiplies

    Parameters
    ----------
    a : int
      First
    b : int
      Second

    Returns
    -------
    (int, float)
      Product of a and b
    """
    return (a * b)

