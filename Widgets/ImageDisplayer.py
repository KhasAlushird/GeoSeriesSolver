import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QWidget,
                QVBoxLayout, QCheckBox, QComboBox,QMessageBox,QHBoxLayout,QStackedLayout,QSlider,QLabel,QStackedWidget,QLineEdit,QPushButton)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sympy import (latex, simplify, sin, cos, tan, 
                   ln, exp, Abs, pi, I, E, asin, acos, atan,
                     sinh, cosh, tanh, sqrt, log, factorial)
import math

from Resources.PlotCanvas import PlotCanvas

class ImageDisplayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        self.plot_canvas = PlotCanvas(self)
        layout.addWidget(self.plot_canvas)

        layout1 = QVBoxLayout()
        layout2 = QVBoxLayout()
        layout3 = QVBoxLayout()
        # 添加 combobox
        self.combox_label = QLabel('选择n的范围:', self)
        self.combobox = QComboBox()
        self.combobox.addItems(['0-10', '0-50', '0-100'])
        self.combobox.textActivated[str].connect(self._set_variable_range)

        self.combox_label2 = QLabel('选择n的范围:', self)
        self.combobox2 = QComboBox()
        self.combobox2.addItems(['0-10', '0-50', '0-100'])
        self.combobox2.textActivated[str].connect(self._set_variable_range)




        # 添加 checkable 的选项
        self.checkbox = QCheckBox('添加趋势线', self)
        self.checkbox.stateChanged.connect(self._add_trend_line)
        

        self.checkbox2 = QCheckBox('显示数列值', self)
        self.checkbox2.stateChanged.connect(self._add_value_tag)
        
        self.checkbox3 = QCheckBox('对比模式', self)
        self.checkbox4 = QCheckBox('显示函数值', self)
        self.checkbox3_2 = QCheckBox('对比模式',self)
        self.checkbox3_2.setChecked(True)
        self.checkbox4_2 = QCheckBox('显示函数值',self)
        self.checkbox3.stateChanged.connect(self.change_compare_mode)
        self.checkbox3_2.stateChanged.connect(self.change_compare_mode)
        
        self.checkbox4.stateChanged.connect(self._add_value_tag)
        self.checkbox4_2.stateChanged.connect(self._add_value_tag)
        #slider 相关
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setRange(0, 10)
        self.slider.valueChanged.connect(self._slider_value_changed)
        self.slider_label = QLabel('滑动改变n的大小:',self)

        self.n_inputer = QLineEdit(self)
        self.submit_button_for_n = QPushButton('提交',self)
        self.submit_button_for_n.clicked.connect(self._submit_curr_n)
        self.submit_button_for_n_label = QLabel('输入n:',self)
        
        #layout1: 不是函数列模式下启用：
        hbox_for_layout1 = QHBoxLayout()
        hbox_for_layout1.addWidget(self.checkbox)
        hbox_for_layout1.addWidget(self.checkbox2)
        layout1.addLayout(hbox_for_layout1)
        layout1.addWidget(self.combox_label)
        layout1.addWidget(self.combobox)





        #layout2:函数列模式，并且不是对比模式下启用:
        hbox_for_layout2 = QHBoxLayout()
        hbox_for_layout2.addWidget(self.checkbox3)
        hbox_for_layout2.addWidget(self.checkbox4)
        layout2.addLayout(hbox_for_layout2)
        hbox_for_layout2_2 = QHBoxLayout()
        hbox_for_layout2_2.addWidget(self.submit_button_for_n_label)
        hbox_for_layout2_2.addWidget(self.n_inputer)
        hbox_for_layout2_2.addWidget(self.submit_button_for_n)
        layout2.addLayout(hbox_for_layout2_2)

        #layout3:函数列模式，且是对比模式：
        hbox_for_layout3 = QHBoxLayout()
        hbox_for_layout3.addWidget(self.checkbox3_2)
        hbox_for_layout3.addWidget(self.checkbox4_2)
        layout3.addLayout(hbox_for_layout3)
        hbox_for_layout3_2 = QHBoxLayout()
        hbox_for_layout3_2.addWidget(self.slider_label)
        hbox_for_layout3_2.addWidget(self.slider)
        layout3.addLayout(hbox_for_layout3_2)
        layout3.addWidget(self.combox_label2)
        layout3.addWidget(self.combobox2)
        # 创建两个 QWidget 用于 QStackedWidget
        widget1 = QWidget()
        widget1.setLayout(layout1)
        widget2 = QWidget()
        widget2.setLayout(layout2)
        widget3 = QWidget()
        widget3.setLayout(layout3)

        # 使用 QStackedWidget 替换 QStackedLayout
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(widget1)
        self.stacked_widget.addWidget(widget2)
        self.stacked_widget.addWidget(widget3)

        self.stacked_widget.setCurrentIndex(0)

        layout.addWidget(self.stacked_widget)


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

    def change_compare_mode(self,compare_mode:bool):
        if compare_mode:
            self.plot_canvas.compare_mode = True
            self.stacked_widget.setCurrentIndex(2)
            self.checkbox3_2.setChecked(True)

        else:
            self.plot_canvas.compare_mode = False
            self.stacked_widget.setCurrentIndex(1)
            self.checkbox3.setChecked(False)

    
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
        if text == '0-10':
            self.slider.setRange(0, 10)
        elif text == '0-50':
            self.slider.setRange(0, 50)
        elif text == '0-100':
            self.slider.setRange(0, 100)
        self.plot_canvas.plot()
        self.plot_canvas.plot()

    def _submit_curr_n(self):
        n=self.n_inputer.text()
        try:
            n = int(n)
        except:
            QMessageBox.warning(self,'警告','n必须为0-100内的整数')
            return
        if 0<=n<=100:
            self.plot_canvas.curr_n_for_serieFonction = n
            print('submit button execute: self.plot_canvas.plot()')
            try:
                print('curr expression:',self.plot_canvas.expression)
                print('curr_n = ',self.plot_canvas.curr_n_for_serieFonction)
            except Exception as e:
                print('occur exception,',e)
            self.plot_canvas.plot()
        else:
            QMessageBox.warning(self,'警告','n必须为0-100内的整数')

    def _slider_value_changed(self, value):
        self.plot_canvas.curr_n_for_serieFonction = value
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