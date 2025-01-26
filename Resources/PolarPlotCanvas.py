import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QMessageBox
import os
import importlib
from Resources.Helpers import serie_calculer, serieFonction_calculer, Grandiant_color
from sympy import (latex, simplify, sin, cos, tan, 
                   ln, exp, Abs, pi, I, E, asin, acos, atan,
                   sinh, cosh, tanh, sqrt, log, factorial)

class PolarPlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure()
        self.ax = fig.add_subplot(111, projection='polar')
        super().__init__(fig)
        self.setParent(parent)
        self.show_value = False
        self.serie_mode = False
        self.advanced_mode = False
        self.serieFonction_mode = False
        self.compare_mode = False
        self.have_error = False
        self.have_warned_for_nan = False
        self.have_warned_for_showValue = 0
        self.range_mode = '0-10'
        self.expression = 'n + 2*I'
        self.latex_expression = r'$n + 2I$'
        self.curr_n_for_serieFonction = 1

        self.annotations = []
        self.mpl_connect('button_press_event', self.on_click)
        self.plot()

    def clear_plot(self):
        self.ax.clear()
        self.draw()

    def set_expression(self, text_list: list):
        self.have_warned_for_nan = False
        self.expression = text_list[1]
        self.latex_expression = '$'
        self.latex_expression += text_list[0]
        self.latex_expression += '$'
        self.plot()

    
    def plot(self):
        self.ax.clear()
        title = self.latex_expression
        if (not self.compare_mode) and self.serieFonction_mode:
            title += f'  n={self.curr_n_for_serieFonction}'
        self.ax.set_title(title)
        self._complex_scatter()
        self.draw()

    def _complex_scatter(self):
        self.have_warned_for_showValue +=1
        if self.have_warned_for_showValue ==2:
            QMessageBox.information(self, "提示", "可以点击蓝点获取数列值")
        if self.range_mode == '0-10':     
            n_points = np.arange(0, 11)
        elif self.range_mode == '0-50':
            n_points = np.arange(0, 51)
        else:
            n_points = np.arange(0,101)
        r = np.zeros_like(n_points, dtype=float)
        theta = np.zeros_like(n_points, dtype=float)
        colors = []
        for i, n in enumerate(n_points):
            try:
                val = eval(self.expression, {"n": n, "I": I, "np": np, "sin": sin, "cos": cos, "tan": tan, "ln": ln, "exp": exp, "Abs": Abs, "pi": pi, "E": E, "asin": asin, "acos": acos, "atan": atan, "sinh": sinh, "cosh": cosh, "tanh": tanh, "sqrt": sqrt, "log": log, "factorial": factorial})
                val = complex(val)
                r[i] = abs(val)
                theta[i] = np.angle(val)
                colors.append(Grandiant_color(self.range_mode,n))
            except Exception as e:
                r[i] = np.nan
                theta[i] = np.nan
                colors.append((0,0,0))
        self.scatter = self.ax.scatter(theta, r, marker='o',c=colors, label='Complex Series')
        
        # 过滤掉 NaN 和 Inf 值
        r_filtered = r[np.isfinite(r)]
        if len(r_filtered) > 0:
            self.ax.set_ylim(0, np.nanmax(r_filtered) * 1.1)  # 设置径向范围
        
        self.ax.legend()
        self.thetas = theta
        self.rs = r

    def on_click(self, event):
        if event.inaxes == self.ax:
            cont, ind = self.scatter.contains(event)
            if cont:
                data_index = ind["ind"][0]
                n = data_index
                r_val = self.rs[data_index]
                theta_val = self.thetas[data_index]
                
                # 检查是否已有标签
                existing_annotation = None
                for annotation in self.annotations:
                    if annotation.xy == (theta_val, r_val):
                        existing_annotation = annotation
                        break
                
                if existing_annotation:
                    # 移除已有标签
                    existing_annotation.remove()
                    self.annotations.remove(existing_annotation)
                else:
                    # 添加新标签
                    annotation = self.ax.annotate(f'n={n}, r={r_val:.2f}, θ={theta_val:.2f}', (theta_val, r_val), textcoords="offset points", xytext=(10, 10), ha='center', color='red', fontweight='bold')
                    self.annotations.append(annotation)
                
                self.draw()

