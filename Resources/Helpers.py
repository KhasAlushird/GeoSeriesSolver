from sympy import (latex, simplify, sin, cos, tan, 
                   ln, exp, Abs, pi, I, E, asin, acos, atan,
                     sinh, cosh, tanh, sqrt, log, factorial)
import numpy as np
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QSize, QRect
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtCore import Qt
import re
import sys
import os
import tempfile
import importlib
# import logging


def code_generator(user_code):
    preset_code = """import sys
import math
import os
if hasattr(sys, '_MEIPASS'):
    latexify_path = os.path.join(sys._MEIPASS, 'latexify')
else:
    latexify_path = os.path.join(os.path.dirname(sys.executable), 'Lib', 'site-packages', 'latexify')
if latexify_path not in sys.path:
    sys.path.append(latexify_path)
import latexify
"""

    suffix_code = '''
def output_latex():
    return latexify.get_latex(F)
'''

    code = preset_code + user_code + suffix_code
    return code

def get_temp_code_path():
    """获取临时目录中的代码文件路径"""
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'Helpers.py')
    return file_path


def write_dynamic_code(code):
    """将代码写入临时文件"""
    file_path = get_temp_code_path()
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code)
    # logging.debug(f"动态代码已写入: {file_path}")
    return file_path


def load_dynamic_module(file_path):
    """动态加载模块"""
    temp_dir = os.path.dirname(file_path)
    if temp_dir not in sys.path:
        sys.path.append(temp_dir)
    
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    # logging.debug(f"正在加载模块: {module_name}")
    try:
        module = importlib.import_module(module_name)
        importlib.reload(module)
        return module
    except Exception as e:
        # logging.error(f"加载模块失败: {str(e)}", exc_info=True)
        raise


def resource_path(relative_path):
    """ 动态获取资源路径 """
    if hasattr(sys, '_MEIPASS'):
        # 打包后的路径：_MEIPASS/_internal/
        base_path = sys._MEIPASS
    else:
        # 开发环境的路径：项目根目录
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def latex_render(latex_expression):

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
            <p>$$ {latex_expression} $$</p>
            </body>
            </html>
            """
    
    
    return html_content

def serie_calculer(expression,range_mode)->list:
    '''
    返回列表的第一个值为bool,反映是否有无定义的点,其余为S(n)的值
    '''
    if range_mode == '0-10':
        end = 11
    elif range_mode == '0-50':
        end = 51
    else:
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

def function_range_getter(fonction_range:str)->list:
    '''
    返回形式[左数值,是否开区间,右数值,是否开区间]
    '''
    try:
        # 解析 fonction_range
        left, right = fonction_range.split(',')
        left = left.strip()
        right = right.strip()

        # 处理左边界
        if left[0] == '(':
            left_open = True
            left_value = left[1:]
        elif left[0] == '[':
            left_open = False
            left_value = left[1:]
        else:
            raise ValueError("Invalid range format")

        # 处理右边界
        if right[-1] == ')':
            right_open = True
            right_value = right[:-1]
        elif right[-1] == ']':
            right_open = False
            right_value = right[:-1]
        else:
            raise ValueError("Invalid range format")
        
        # 将边界值转换为数值
        left_value = eval(left_value.replace('E', 'np.e').replace('pi', 'np.pi'))
        right_value = eval(right_value.replace('E', 'np.e').replace('pi', 'np.pi'))

        if left_value>right_value:
            raise ValueError("Invalid range format")

        result = [left_value, left_open, right_value, right_open]
        return result

    except Exception as e:
        return['error']


def serieFonction_calculer(expression,n,serie_mode:bool,x_points:list)->list:
    '''
    返回形式：[if invalid n ,x_points,y_points,[ten_y_points]]
    '''
    error_count = 0
    error_flag_final = False


    x_points_num = len(x_points)

    y_points = []
    ten_y_points = []
    
    if not serie_mode:
        for x in x_points:
            try:
                val = eval(expression, {"n": n, "k":n,'x':x,"np": np, "sin": sin, "cos": cos, "tan": tan, "ln": ln, "exp": exp, "Abs": Abs, "pi": pi, "I": I, "E": E, "asin": asin, "acos": acos, "atan": atan, "sinh": sinh, "cosh": cosh, "tanh": tanh, "sqrt": sqrt, "log": log, "factorial": factorial})
            except ZeroDivisionError as e:
                error_count += 1
                val = np.nan
            y_points.append(val)


    else:
        n_points = np.arange(0, n+1)
        y_points_curr= []
        for n in n_points:
            y_points_curr = []
            error_flag = False
            error_count = 0
            for x in x_points:
                if error_flag:
                    break
                
                val = eval(expression, {"n":n,"k": n, 'x':x,"np": np, "sin": sin, "cos": cos, "tan": tan, "ln": ln, "exp": exp, "Abs": Abs, "pi": pi, "I": I, "E": E, "asin": asin, "acos": acos, "atan": atan, "sinh": sinh, "cosh": cosh, "tanh": tanh, "sqrt": sqrt, "log": log, "factorial": factorial})                   
                if not np.isfinite(float(val)):
                    error_count += 1
                    val = 0
                y_points_curr.append(val)
                if error_count >=15:
                    error_flag = True
                    error_flag_final = True
            if n==0:
                if not error_flag:
                    y_points = y_points_curr
                else:
                    y_points = [y*0 for y in range(0,x_points_num+1)]
            else:
                if not error_flag:
                    y_points = [y + y_curr for y,y_curr in zip(y_points,y_points_curr)]

    
    if error_count >= 200:
        error_flag_final = True

    indices = np.linspace(0, len(x_points) - 1, 10).astype(int)

    ten_y_points = [y_points[i] for i in indices]

    if error_flag_final:
        return [True, x_points, y_points,ten_y_points]  
    else:   
        return [False, x_points, y_points,ten_y_points]


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.line_number_area_paint_event(event)

    def line_number_area_width(self):
        digits = len(str(self.code_editor.blockCount()))
        space = 3 + self.code_editor.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self):
        self.code_editor.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.scroll(0, dy)
        else:
            self.update(0, rect.y(), self.width(), rect.height())

        if rect.contains(self.code_editor.viewport().rect()):
            self.update_line_number_area_width()

    def line_number_area_paint_event(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(31, 31, 31))

        block = self.code_editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.code_editor.blockBoundingGeometry(block).translated(self.code_editor.contentOffset()).top())
        bottom = top + int(self.code_editor.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(136, 215, 252))
                painter.drawText(0, top, self.width(), self.code_editor.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.code_editor.blockBoundingRect(block).height())
            block_number += 1



def Grandiant_color(range_mode:str,curr_n:int)->tuple:

    if range_mode == '0-10':
        steps = 10
    elif range_mode == '0-50':
        steps = 50
    else:
        steps = 100

    r = 0
    g = int(255 * (1 - curr_n / steps))
    b = 255

    r/=255
    g/=255
    b/=255
    return (r,g,b)


def has_illegal_variables(expression:str,serie_Fonction_mode:bool):
    # 定义合法变量和函数名
    legal_variables = {'n', 'k', 'I', 'E', 'pi'}
    if serie_Fonction_mode:
        legal_variables.add('x')
    legal_functions = {'sin', 'cos', 'tan', 'sqrt', 'log', 'exp', 'atan', 'asin','acos','sinh', 'cosh', 'tanh', 'factorial', 'Abs'}
    
    # 使用正则表达式提取所有变量
   # 匹配所有的字母，忽略空格和符号
    tokens = re.findall(r'[a-zA-Z]+', expression)

    for token in tokens:
        # 如果是函数名，跳过
        if token in legal_functions:
            continue
        # 如果是单独的变量，检查是否在合法变量列表中
        if token not in legal_variables:
            return True  # 发现非法变量，返回True
    
    return False  # 没有发现非法变量，返回False
















