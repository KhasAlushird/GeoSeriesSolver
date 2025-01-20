import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QWidget,
                QVBoxLayout, QCheckBox, QComboBox,QMessageBox)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sympy import (latex, simplify, sin, cos, tan, 
                   ln, exp, Abs, pi, I, E, asin, acos, atan,
                     sinh, cosh, tanh, sqrt, log, factorial)
import math
from Helpers import serie_calculer
class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig, self.ax = plt.subplots()
        super().__init__(fig)
        self.setParent(parent)
        self.show_line = False
        self.show_value = False
        self.serie_mode = False
        self.have_warned_for_nan = False
        self.range_mode = '0-10'
        self.expression = 'n**2'
        self.plot()

    def set_expression(self, expression):
        self.have_warned_for_nan = False
        self.expression = expression
        self.plot()

    def plot(self):
        self.ax.clear()
        if self.serie_mode:
            self.expression = self.expression.replace('n','k')
            self.ax.set_title(r'$S_n = \sum_{k=0}^{n}  '  + f'{latex(simplify(self.expression))}$')
            self.ax.set_ylabel(r'$S_n$', fontsize=14, rotation=0)
        else:
            self.ax.set_title(r'$U_n = '  + f'{latex(simplify(self.expression))}$')
            self.ax.set_ylabel(r'$U_n$', fontsize=14, rotation=0)
        self.ax.set_xlabel('n')
        self._point_scatter(self.range_mode)
        self.draw()

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

        # 添加 checkable 的选项
        self.checkbox = QCheckBox('添加趋势线', self)
        self.checkbox.stateChanged.connect(self._add_trend_line)
        layout.addWidget(self.checkbox)

        self.checkbox2 = QCheckBox('显示数列值',self)
        self.checkbox2.stateChanged.connect(self._add_value_tag)
        layout.addWidget(self.checkbox2)


        # 添加 combobox
        self.combobox = QComboBox(self)
        self.combobox.addItems(['0-10', '0-50', '0-100'])
        self.combobox.textActivated[str].connect(self._set_variable_range)
        layout.addWidget(self.combobox)

    def change_serie_mode(self, if_enable):
        self.checkbox.setEnabled(if_enable)
        self.plot_canvas.serie_mode = not if_enable

    
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