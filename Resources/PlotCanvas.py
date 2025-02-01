import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.collections import PathCollection
from PyQt6.QtWidgets import QMessageBox
import os
import importlib
from Resources.Helpers import serie_calculer,serieFonction_calculer,Grandiant_color
from Resources._temp_code import F

from sympy import (latex, simplify, sin, cos, tan, 
                   ln, exp, Abs, pi, I, E, asin, acos, atan,
                     sinh, cosh, tanh, sqrt, log, factorial)



class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None,localization = None):
        fig, self.ax = plt.subplots()
        self.localization = localization
        super().__init__(fig)
        self.setParent(parent)
        self.show_line = False
        self.show_value = False
        self.serie_mode = False
        self.advanced_mode = False
        self.serieFonction_mode = False
        self.compare_mode = False
        self.have_error = False
        self.have_warned_for_nan = False
        self.range_mode = '0-10'
        self.expression = 'n**2'
        self.latex_expression = r'$n^2$'
        self.curr_n_for_serieFonction = 1
        # self.curr_x_for_vertical = 1
        self.ten_x_points = []
        self.ten_y_points = [[],[],[],[],[],[],[],[],[],[]]
        self.function_range = [0,False,10,False]
        self.plot()

    def clear_plot(self):
        self.ax.clear()
        self.draw()

    def set_expression(self, text_list:list):
        self.have_warned_for_nan = False
        self.expression = text_list[1]
        self.latex_expression = '$'
        self.latex_expression += text_list[0]
        self.latex_expression+='$'
        self.plot()

    def _F_reloader(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        resources_dir = os.path.join(current_dir, '..', 'Resources')
        if resources_dir not in sys.path:
            sys.path.append(resources_dir)
        
        import _temp_code
        importlib.reload(_temp_code)
        F = _temp_code.F
        return F
    
    def plot(self):
        # if not self.compare_mode:
        #     self.ax.clear()
        self.ax.clear()
        if self.advanced_mode:
            self.ax.set_title('F(n)')
            self.ax.set_ylabel('F(n)', fontsize=14, rotation=0)
            self.ax.set_xlabel('n')
        else:
            title = self.latex_expression
            if (not self.compare_mode) and self.serieFonction_mode:
                title+= f'  n={self.curr_n_for_serieFonction}'
            self.ax.set_title(title)
            if self.serie_mode:
                self.ax.set_ylabel(r'$S_n$', fontsize=14, rotation=0)
                if not self.serieFonction_mode:
                    self.ax.set_xlabel('n')
                else:
                    self.ax.set_xlabel('x')
            else:
                if not self.serieFonction_mode:
                    self.ax.set_ylabel(r'$U_n$', fontsize=14, rotation=0)
                    self.ax.set_xlabel('n')
                else:
                    self.ax.set_ylabel(r'$f_n$', fontsize=14, rotation=0)
                    self.ax.set_xlabel('x')

        if self.serieFonction_mode:
            self._fonction_scatter()
        else:
            self._point_scatter(self.range_mode)
        self.draw()


    def _fonction_scatter(self):
        # print('execute serie fonction calculer')
        left_val, left_open, right_val, right_open = self.function_range
        x_points = np.linspace(left_val, right_val, 400)

        if left_open:
            x_points = x_points[x_points > left_val]
        if right_open:
            x_points = x_points[x_points < right_val]

       
        
        # right_val  = self.function_range[0]
        # left_val = self.function_range[2]
        step = (right_val - left_val) / 10
        self.ax.set_xticks(np.arange(left_val, right_val + step, step))

        if self.compare_mode:
            indices = np.linspace(0, len(x_points) - 1, 10).astype(int)
            self.ten_x_points = [x_points[i] for i in indices]
            self.ten_y_points = [[],[],[],[],[],[],[],[],[],[]]
            for n in range(1, int(self.range_mode.split('-')[1]) + 1):
                result = serieFonction_calculer(self.expression, n, self.serie_mode, x_points)
                if result[0]:
                    QMessageBox.warning(self, self.localization['msg_warning'], self.localization['msg_undef'])
                    return
                
                x_points = result[1]
                y_points = result[2]
                ten_y_points = result[3]
                for i in range(10):
                    self.ten_y_points[i].append(ten_y_points[i])
                r_g_b_tuple = Grandiant_color(self.range_mode, n)
                self.ax.plot(x_points, y_points, color=r_g_b_tuple)
                

            self.draw_vertical_line(0)


        else:
            result = serieFonction_calculer(self.expression,self.curr_n_for_serieFonction,self.serie_mode,x_points)
            if result[0]:
                QMessageBox.warning(self, self.localization['msg_warning'], self.localization['msg_undef'])
        
            x_points = result[1]
            y_points = result[2]
            self.ax.plot(x_points, y_points, color='blue')
            if self.function_range[1]:
                self.ax.scatter([x_points[0]], [y_points[0]], edgecolor='b', facecolor='none', s=26)
            if self.function_range[3]:
                self.ax.scatter([x_points[-1]], [y_points[-1]], edgecolor='b', facecolor='none', s=26)
     
        if self.show_value:
            step = 50
            #注：enumerate(zip(x_points, y_points))每个元素形如 i,(x,y)
            for i,(x1, y) in enumerate(zip(x_points, y_points)):
                # print(i,x1,y)
                if i % step ==0:
                    if np.isfinite(float(y)):  # 仅为有效点添加标签
                        self.ax.annotate(f'({x1:.1f}, {y:.1f})', (x1, y), textcoords="offset points", xytext=(0, 10), ha='center')

    def draw_vertical_line(self,curr_index_x:int):
        # print('curr index is',curr_index_x)
        if self.range_mode == '0-10':
            s_size = 30
        elif self.range_mode == '0-50':
            s_size = 18
        else:
            s_size = 11
        # print('curr y is ',self.ten_y_points[curr_index_x])
        for y_val in self.ten_y_points[curr_index_x]:
            self.ax.scatter([self.ten_x_points[curr_index_x]], [y_val], color='green', s=s_size,alpha=0.7)
        self.ax.axvline(x=self.ten_x_points[curr_index_x], color='green', linestyle='-',alpha=0.5)

        self.draw()

    def clear_vertical_lines(self):
        for line in self.ax.get_lines():
            if line.get_linestyle() == '-' and line.get_color() == (0.0, 1.0, 0.0, 0.5):
                line.remove()
        for collection in self.ax.collections:
            if isinstance(collection,PathCollection):
                collection.remove()
        self.draw()

    def update_texts(self,localization):
        self.localization = localization

    def _point_scatter(self, range_mode):
        if range_mode == '0-10':
            self.ax.set_xticks(np.arange(0, 11, 1))
            x_points = np.arange(0, 11, 1)
            x = np.linspace(0, 10, 400)
            point_size = 50
        elif range_mode == '0-50':
            self.ax.set_xticks(np.arange(0, 51, 5))
            x_points = np.arange(0, 51, 1)
            x = np.linspace(0, 50, 400)
            point_size = 30
        else:
            self.ax.set_xticks(np.arange(0, 101, 10))
            x_points = np.arange(0, 101, 1)
            x = np.linspace(0, 100, 400)
            point_size = 10

        y_points = []
        for n in x_points:
            #进阶模式算法
            if self.advanced_mode:
                F = self._F_reloader()
                
                try:
                    y_points.append(F(n))
                except:
                    msg1 = self.localization['msg_point']
                    msg2 = self.localization['msg_undef_point']
                    QMessageBox.warning(self, self.localization['msg_warning'], f'{msg1} {n} {msg2}')
                    return

            else:
                #普通模式算法
                if not self.serie_mode:
                    #普通模式下，非级数模式算法
                    val = eval(self.expression, {"n": n, 'k':n,"np": np, "sin": sin, "cos": cos, "tan": tan, "ln": ln, "exp": exp, "Abs": Abs, "pi": pi, "I": I, "E": E, "asin": asin, "acos": acos, "atan": atan, "sinh": sinh, "cosh": cosh, "tanh": tanh, "sqrt": sqrt, "log": log, "factorial": factorial})
                    self.have_error = True
                    try:
                        if not isinstance(val, complex):
                            if np.isfinite(float(val)):
                                y_points.append(val)
                                self.have_error = False
                            else:
                                y_points.append(np.nan)
                        else:
                            y_points.append(np.nan)
                    except (TypeError, ValueError) as e:
                        y_points.append(np.nan)

                else:
                    #普通模式下，级数模式算法
                    result = serie_calculer(self.expression,range_mode)
                    y_points.append(result[n+1])
                    self.have_error = result[0]


        self.ax.scatter(x_points, y_points, color='red', s=point_size)
        
        if self.show_value:
            step = 1
            if self.range_mode == '0-50':
                step = 5
            elif self.range_mode == '0-100':
                step = 10
            for i, (x1, y) in enumerate(zip(x_points, y_points)):
                if not np.isnan(float(y)):  # 仅为有效点添加标签
                    #y 是要格式化的数值。：代表格式化字符串，.2f是格式
                    if i % step ==0:
                        self.ax.annotate(f'{y:.2f}', (x1, y), textcoords="offset points", xytext=(0, 10), ha='center')
                   

        ###请勿调整show value 和 show line 之间的前后关系！！！
        if self.show_line:
            y = []
            for n in x:
                val = eval(self.expression, {"n": n, 'k':n,"np": np, "sin": sin, "cos": cos, "tan": tan, "ln": ln, "exp": exp, "Abs": Abs, "pi": pi, "I": I, "E": E, "asin": asin, "acos": acos, "atan": atan, "sinh": sinh, "cosh": cosh, "tanh": tanh, "sqrt": sqrt, "log": log, "factorial": factorial})
                try:
                    val = float(val)
                    y.append(val)
                except (TypeError, ValueError) as e:
                    y.append(np.nan)

            self.ax.plot(x,y,color = 'blue')

                
        if self.have_error and not self.have_warned_for_nan:
            QMessageBox.warning(self, self.localization['msg_warning'] , self.localization['msg_undef'])
            self.have_warned_for_nan = True


        

