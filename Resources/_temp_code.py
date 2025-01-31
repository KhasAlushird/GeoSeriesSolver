import latexify
import math

def F(n):
    if n == 0 or n==1:
        return 1
    else:
        return F(n-1) + F(n-2)

def output_latex():
    return latexify.get_latex(F)
