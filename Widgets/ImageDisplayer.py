import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QWidget,
                QVBoxLayout, QCheckBox, QComboBox,QMessageBox,QHBoxLayout,QStackedLayout,QSlider,QLabel,QStackedWidget)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sympy import (latex, simplify, sin, cos, tan, 
                   ln, exp, Abs, pi, I, E, asin, acos, atan,
                     sinh, cosh, tanh, sqrt, log, factorial)
import math
import os
import importlib

from Resources.Helpers import serie_calculer,serieFonction_calculer
from Resources._temp_code import F

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig, self.ax = plt.subplots()
        super().__init__(fig)
        self.setParent(parent)
        self.show_line = False
        self.show_value = False
        self.serie_mode = False
        self.advanced_mode = False
        self.serieFonction_mode = False
        self.have_warned_for_nan = False
        self.range_mode = '0-10'
        self.expression = 'n**2'
        self.latex_expression = r'$n^2$'
        self.curr_n_for_serieFonction = 1
        self.plot()

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
        self.ax.clear()
        if self.advanced_mode:
            self.ax.set_title('F(n)')
            self.ax.set_ylabel('F(n)', fontsize=14, rotation=0)
            self.ax.set_xlabel('n')
        else:
            self.ax.set_title(self.latex_expression)
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
        if not self.serieFonction_mode:
            self._point_scatter(self.range_mode)
        else:
            self._fonction_scatter()
        self.draw()

    def _fonction_scatter(self):
        result = serieFonction_calculer(self.expression,self.curr_n_for_serieFonction,self.serie_mode)
        if result[0]:
            QMessageBox.warning(self, "警告", "存在无定义的点")
        
        x_points = result[1]
        y_points = result[2]
        self.ax.set_xticks(np.arange(0, 101, 10))
        self.ax.plot(x_points, y_points, color='blue')
        if self.show_value:
            step = 10
            if not np.isnan(float(y)):  # 仅为有效点添加标签
                for i, (x1, y) in enumerate(zip(x_points, y_points)):
                    if i % step ==0:
                        self.ax.annotate(f'{y:.2f}', (x1, y), textcoords="offset points", xytext=(0, 10), ha='center')







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
            if self.advanced_mode:
                F = self._F_reloader()
                
                try:
                    y_points.append(F(n))
                except:
                    QMessageBox.warning(self, "警告", f"点{n}无定义")
                    return

            else:
                if not self.serie_mode:
                    try:
                        y_points.append(eval(self.expression, {"n": n, 'k':n,"np": np, "sin": sin, "cos": cos, "tan": tan, "ln": ln, "exp": exp, "Abs": Abs, "pi": pi, "I": I, "E": E, "asin": asin, "acos": acos, "atan": atan, "sinh": sinh, "cosh": cosh, "tanh": tanh, "sqrt": sqrt, "log": log, "factorial": factorial}))
                    except (ZeroDivisionError, ValueError, RuntimeWarning, FloatingPointError):
                        y_points.append(np.nan)  # 使用 NaN 表示错误
                else:
                    result = serie_calculer(self.expression,range_mode)
                    y_points.append(result[n+1])

        self.ax.scatter(x_points, y_points, color='red', s=point_size)
        if self.serie_mode and not self.have_warned_for_nan:
            if result[0]:
                QMessageBox.warning(self, "警告", "存在无定义的点")
                self.have_warned_for_nan = True

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
                try:
                   y.append(eval(self.expression, {"n": n, 'k':n,"np": np, "sin": sin, "cos": cos, "tan": tan, "ln": ln, "exp": exp, "Abs": Abs, "pi": pi, "I": I, "E": E, "asin": asin, "acos": acos, "atan": atan, "sinh": sinh, "cosh": cosh, "tanh": tanh, "sqrt": sqrt, "log": log, "factorial": factorial}))
                except (ZeroDivisionError, ValueError, RuntimeWarning, FloatingPointError):
                    y.append(np.nan)  # 使用 NaN 表示错误
            self.ax.plot(x, y, color='blue')
class ImageDisplayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.plot_canvas = PlotCanvas(self)
        layout.addWidget(self.plot_canvas)

        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()

        # 添加 checkable 的选项
        self.checkbox = QCheckBox('添加趋势线', self)
        self.checkbox.stateChanged.connect(self._add_trend_line)
        layout1.addWidget(self.checkbox)

        self.checkbox2 = QCheckBox('显示数列值', self)
        self.checkbox2.stateChanged.connect(self._add_value_tag)
        layout1.addWidget(self.checkbox2)

        self.checkbox3 = QCheckBox('对比模式', self)
        self.checkbox4 = QCheckBox('显示函数值', self)
        self.checkbox4.stateChanged.connect(self._add_value_tag)
        self.slider = QSlider(Qt.Orientation.Horizontal)
        layout2.addWidget(self.checkbox3)
        layout2.addWidget(self.checkbox4)
        layout2.addWidget(self.slider)

        # 创建两个 QWidget 用于 QStackedWidget
        widget1 = QWidget()
        widget1.setLayout(layout1)
        widget2 = QWidget()
        widget2.setLayout(layout2)

        # 使用 QStackedWidget 替换 QStackedLayout
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(widget1)
        self.stacked_widget.addWidget(widget2)

        layout.addWidget(self.stacked_widget)

        # 添加 combobox
        self.label = QLabel('选择n的范围:', self)
        self.combobox = QComboBox(self)
        self.combobox.addItems(['0-10', '0-50', '0-100'])
        self.combobox.textActivated[str].connect(self._set_variable_range)
        layout.addWidget(self.label)
        layout.addWidget(self.combobox)

    def change_serie_mode(self, if_enable):
        self.checkbox.setEnabled(if_enable)
        self.plot_canvas.serie_mode = not if_enable

    def change_advance_mode(self,advance_mode:bool):
        self.checkbox.setEnabled(not advance_mode)
        self.plot_canvas.advanced_mode = advance_mode


    def change_serieFonction_mode(self,serieFonction_mode:bool):
        if serieFonction_mode:
            self.plot_canvas.serieFonction_mode = True
            self.stacked_widget.setCurrentIndex(1)

        else:
            self.plot_canvas.serieFonction_mode = False
            self.stacked_widget.setCurrentIndex(0)

    
    def _add_trend_line(self, state):
        if state == Qt.CheckState.Checked.value:
            if self.plot_canvas.range_mode == '0-10':
                x = np.linspace(0, 10, 400)
            elif self.plot_canvas.range_mode == '0-50':
                x = np.linspace(0, 50, 400)
            else: 
                x = np.linspace(0, 100, 400)
            invalid_count = 0
            for n in x:
                    val = eval(self.plot_canvas.expression, {"n": n, "np": np, "sin": sin, "cos": cos, "tan": tan, "ln": ln, "exp": exp, "Abs": Abs, "pi": pi, "I": I, "E": E, "asin": asin, "acos": acos, "atan": atan, "sinh": sinh, "cosh": cosh, "tanh": tanh, "sqrt": sqrt, "log": log, "factorial": factorial})
                    if math.isnan(val):
                        invalid_count += 1
                        if invalid_count >= 15:
                            QMessageBox.warning(self, "警告", "趋势线无定义")
                            self.checkbox.setChecked(False)
                            self.plot_canvas.show_line = False
                            return
            self.plot_canvas.show_line = True
        else:
            self.plot_canvas.show_line = False

        self.plot_canvas.plot()

    def _add_value_tag(self, state):
        self.plot_canvas.show_value = (state == Qt.CheckState.Checked.value)
        self.plot_canvas.plot()

    def _set_variable_range(self, text):
        self.plot_canvas.range_mode = text
        self.plot_canvas.plot()

def main():
    app = QApplication(sys.argv)
    main_window = QWidget()
    main_window.setWindowTitle('Main Application')
    main_window.setGeometry(100, 100, 800, 600)

    layout = QVBoxLayout(main_window)
    image_displayer = ImageDisplayer(main_window)
    layout.addWidget(image_displayer)

    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()