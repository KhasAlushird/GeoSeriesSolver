from sympy import (latex, simplify, sin, cos, tan, 
                   ln, exp, Abs, pi, I, E, asin, acos, atan,
                     sinh, cosh, tanh, sqrt, log, factorial)
import numpy as np
def latex_render(prefix,latex_expression):
    # mathjax_path = 'mathjax/MathJax.js'
    # mathjax_path = os.path.join(os.path.dirname(__file__), 'mathjax', 'MathJax.js')
    # print(mathjax_path)

    html_content = f"""
            <html>
            <head>
            <style>
                body {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }}
            </style>
            <script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML"></script>
            <script type="text/javascript">
                MathJax.Hub.Config({{
                    tex2jax: {{
                        inlineMath: [['$','$'], ['\\(','\\)']]
                    }}
                }});
                MathJax.Hub.Queue(["Typeset", MathJax.Hub, function() {{
                    var height = document.body.scrollHeight;
                }}]);
            </script>
            </head>
            <body>
            <p>$$ {prefix}{latex_expression} $$</p>
            </body>
            </html>
            """
    
    
    return html_content

def serie_calculer(expression,range_mode)->list:
    '''
    返回列表的第一个值为bool,反映是否有无定义的点,其余为S(n)的值
    '''
    if range_mode == '0-10':
        n = np.arange(0, 11, 1)
        end = 11
    elif range_mode == '0-50':
        n = np.arange(0, 51, 1)
        end = 51
    else:
        n = np.arange(0, 101, 1)
        end = 101
    result = [False]
    for i in range(end):
        try:
            val = eval(expression, {"n": i, 'k':i,"np": np, "sin": sin, "cos": cos, "tan": tan, "ln": ln, "exp": exp, "Abs": Abs, "pi": pi, "I": I, "E": E, "asin": asin, "acos": acos, "atan": atan, "sinh": sinh, "cosh": cosh, "tanh": tanh, "sqrt": sqrt, "log": log, "factorial": factorial})
        except Exception as e:
            result[0] = True
            val = 0
        if i !=0:
            last_val = result[-1]
            val += last_val
        result.append(val)
    return result


# print(serie_calculer('n','0-10'))

# latex_render('1','2')

            # <script type="text/javascript" src="file:///{mathjax_path}?config=TeX-MML-AM_CHTML"></script>

# html_content = f"""
#             <html>
#             <head>
#             <style>
#                 body {{
#                     display: flex;
#                     justify-content: center;
#                     align-items: center;
#                     height: 100vh;
#                     margin: 0;
#                 }}
#             </style>
#             <script type="text/javascript" src="{mathjax_path}?config=TeX-MML-AM_CHTML"></script>
#             <script type="text/javascript">
#                 MathJax.Hub.Config({{
#                     tex2jax: {{
#                         inlineMath: [['$','$'], ['\\(','\\)']]
#                     }}
#                 }});
#                 MathJax.Hub.Queue(["Typeset", MathJax.Hub, function() {{
#                     var height = document.body.scrollHeight;
#                 }}]);
#             </script>
#             </head>
#             <body>
#             <p>$$ {prefix} {latex_expression} $$</p>
#             </body>
#             </html>
#             """