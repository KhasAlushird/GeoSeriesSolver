import latexify
import math

def F(n):
    if n == 0:
        return math.cos(n)
    else:
        return F(n-1) + 2

def output_latex():
    return latexify.get_latex(F)
