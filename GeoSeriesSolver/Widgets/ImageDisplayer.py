import sys
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import (QApplication, QWidget,
                QVBoxLayout, QCheckBox, QComboBox,QMessageBox,QHBoxLayout,
                QSlider,QLabel,QStackedWidget,QLineEdit,QPushButton,QSplitter)
from PyQt6.QtCore import Qt
from sympy import (latex, simplify, sin, cos, tan, 
                   ln, exp, Abs, pi, I, E, asin, acos, atan,
                     sinh, cosh, tanh, sqrt, log, factorial)
import math

from GeoSeriesSolver.Resources.PlotCanvas import PlotCanvas
from GeoSeriesSolver.Resources.PolarPlotCanvas import PolarPlotCanvas
from GeoSeriesSolver.Resources.Helpers import function_range_getter

class ImageDisplayer(QWidget):
    def __init__(self,localization, parent=None):
        self.localization = localization
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.complex_mode = False
        layout = QVBoxLayout(self)
        self.plot_canvas = PlotCanvas(self,self.localization['plot_canvas'])
        self.polar_canvas = PolarPlotCanvas(self,self.localization['polar_canvas'])
        self.current_canvas = self.plot_canvas
        self.stacked_canvas = QStackedWidget()
        self.stacked_canvas.addWidget(self.plot_canvas)
        self.stacked_canvas.addWidget(self.polar_canvas)
        # layout.addWidget(self.stacked_canvas)

        layout1 = QVBoxLayout()
        layout2 = QVBoxLayout()
        layout3 = QVBoxLayout()
        # 添加 combobox
        self.combox_label = QLabel(self.localization['n_range_label'], self)
        self.combobox = QComboBox()
        self.combobox.addItems(['0-10', '0-50', '0-100'])
        self.combobox.textActivated[str].connect(self._set_variable_range)

        self.combox_label2 = QLabel(self.localization['n_range_label'], self)
        self.combobox2 = QComboBox()
        self.combobox2.addItems(['0-10', '0-50', '0-100'])
        self.combobox2.textActivated[str].connect(self._set_variable_range)




        # 添加 checkable 的选项
        self.checkbox = QCheckBox(self.localization['add_trend_line'], self)
        self.checkbox.stateChanged.connect(self._add_trend_line)
        

        self.checkbox2 = QCheckBox(self.localization['show_serie_val'], self)
        self.checkbox2.stateChanged.connect(self._add_value_tag)
        
        self.checkbox3 = QCheckBox(self.localization['compare_mode'], self)
        self.checkbox4 = QCheckBox(self.localization['show_func_val'], self)
        self.checkbox3_2 = QCheckBox(self.localization['compare_mode'],self)
        self.checkbox3_2.setChecked(True)
        self.clear_button = QPushButton(self.localization['clear'],self)
        self.checkbox3.stateChanged.connect(self.change_compare_mode)
        self.checkbox3_2.stateChanged.connect(self.change_compare_mode)
        
        self.checkbox4.stateChanged.connect(self._add_value_tag)
        self.clear_button.clicked.connect(self._clear_plot)
        #slider 相关
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setRange(0, 9)
        self.slider.valueChanged.connect(self._slider_value_changed)
        self.slider_label = QLabel(self.localization['slider_label'],self)

        self.n_inputer = QLineEdit(self)
        self.submit_button_for_n = QPushButton(self.localization['submit_button'],self)
        self.submit_button_for_n.clicked.connect(self._submit_curr_n)
        self.submit_button_for_n_label = QLabel(self.localization['input_n'],self)
        
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
        hbox_for_layout3.addWidget(self.clear_button)
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

        # layout.addWidget(self.stacked_widget)

        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setStyleSheet("QSplitter::handle { background-color: lightgray; }")
        splitter.addWidget(self.stacked_canvas)
        splitter.addWidget(self.stacked_widget)
        layout.addWidget(splitter)
        

    def set_expression_for_canvas(self,text_list:list):
        self.change_compare_mode(False)
        self.current_canvas.set_expression(text_list)

    def set_dom_of_def(self,range_text:str):
        range_list = function_range_getter(range_text)
        if range_list[0] == 'error':
            QMessageBox.warning(self, self.localization['msg_warning'],self.localization['msg_rangeError'])
            return
        self.plot_canvas.function_range = range_list


    def change_serie_mode(self, serie_mode:bool):
        if not self.complex_mode:
            self.checkbox.setEnabled(not serie_mode)
        self.current_canvas.serie_mode = serie_mode

    def change_advance_mode(self,advance_mode:bool):
        if advance_mode:
            self.stacked_canvas.setCurrentIndex(0)
            self.current_canvas = self.plot_canvas
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
        self.plot_canvas.clear_plot()
        if compare_mode:
            self.plot_canvas.compare_mode = True
            self.stacked_widget.setCurrentIndex(2)
            self.checkbox3_2.setChecked(True)
            self.plot_canvas.plot()

        else:
            if self.plot_canvas.serieFonction_mode:
                self.plot_canvas.compare_mode = False
                self.stacked_widget.setCurrentIndex(1)
                self.checkbox3.setChecked(False)
            else:
                self.stacked_widget.setCurrentIndex(0)

    def change_complex_mode(self,complex_mode:bool):
        self.complex_mode = complex_mode
        if complex_mode:
            self.stacked_canvas.setCurrentIndex(1)
            self.current_canvas = self.polar_canvas
            self.checkbox2.setEnabled(False)
            self.checkbox.setEnabled(False)
            # print(self.checkbox.isEnabled())
            # print('curr canvas is: polar')
        else:
            self.stacked_canvas.setCurrentIndex(0)
            self.current_canvas = self.plot_canvas
            self.checkbox2.setEnabled(True)
            self.checkbox.setEnabled(True)

    
    #这一步仅是判断趋势线是否有定义的算法，具体趋势线的绘制在plot里面
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
                    try:
                        if not isinstance(val,complex):
                            if math.isnan(val):
                                invalid_count += 1
                    except (TypeError, ValueError) as e:
                        invalid_count +=1

                    if invalid_count >= 15:
                        QMessageBox.warning(self, self.localization['msg_warning'], self.localization['msg_trendline'])
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
        self.current_canvas.range_mode = text
        # if text == '0-10':
        #     self.slider.setRange(0, 10)
        # elif text == '0-50':
        #     self.slider.setRange(0, 50)
        # elif text == '0-100':
        #     self.slider.setRange(0, 100)
        self.current_canvas.plot()

    def _submit_curr_n(self):
        n=self.n_inputer.text()
        try:
            n = int(n)
        except:
            QMessageBox.warning(self,self.localization['msg_warning'],self.localization['msg_nError'])
            return
        if 0<=n<=100:
            self.plot_canvas.curr_n_for_serieFonction = n
            # print('submit button execute: self.plot_canvas.plot()')
            # try:
            #     print('curr expression:',self.plot_canvas.expression)
            #     print('curr_n = ',self.plot_canvas.curr_n_for_serieFonction)
            # except Exception as e:
            #     print('occur exception,',e)
            self.plot_canvas.plot()
        else:
            QMessageBox.warning(self,self.localization['msg_warning'],self.localization['msg_nError'])

    def update_texts(self, localization):
        self.localization = localization
        self.checkbox.setText(localization['add_trend_line'])
        self.checkbox3.setText(localization['compare_mode'])
        self.checkbox3_2.setText(localization['compare_mode'])
        self.checkbox2.setText(localization['show_serie_val'])
        self.checkbox4.setText(self.localization['show_func_val'])
        self.combox_label.setText(self.localization['n_range_label'])
        self.combox_label2.setText(self.localization['n_range_label'])
        self.clear_button.setText(self.localization['clear'])
        self.slider_label.setText(self.localization['slider_label'])
        self.submit_button_for_n.setText(self.localization['submit_button'])
        self.submit_button_for_n_label.setText(self.localization['input_n'])

        self.plot_canvas.update_texts(self.localization['plot_canvas'])
        self.polar_canvas.update_texts(self.localization['polar_canvas'])


    def _slider_value_changed(self, value):
        # self.plot_canvas.curr_n_for_serieFonction = value
        # self.plot_canvas.plot()
        self.plot_canvas.draw_vertical_line(value)
        # print('slider value changed',value)

    def _clear_plot(self):
        self.plot_canvas.clear_vertical_lines()
        # print('clear_plot execute')

# def main():
#     app = QApplication(sys.argv)
#     main_window = QWidget()
#     main_window.setWindowTitle('Main Application')
#     main_window.setGeometry(100, 100, 800, 600)

#     layout = QVBoxLayout(main_window)
#     image_displayer = ImageDisplayer(main_window)
#     layout.addWidget(image_displayer)

#     main_window.show()
#     sys.exit(app.exec())

# if __name__ == '__main__':
#     main()