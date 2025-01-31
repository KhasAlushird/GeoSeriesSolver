import sys
from PyQt6.QtWidgets import (QLabel, QLineEdit,QHBoxLayout, QApplication, QWidget, QCheckBox, 
                             QVBoxLayout, QMessageBox,QPushButton,QStackedWidget)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from sympy import latex,simplify
from PyQt6.QtCore import Qt
import re
from Resources.Helpers import has_illegal_variables
from PyQt6.QtWidgets import QSpacerItem, QSizePolicy

class ExpressionInputer(QWidget):
    expression_changed_signal_displayer = pyqtSignal(list)  # 发送给ImageDisplayer,格式为[latex_expression,sympy_expression]
    expression_changed_signal_render = pyqtSignal(str)
    expression_changed_signal_render_error = pyqtSignal(str)
    serie_mode_signal = pyqtSignal(bool)
    serieFonction_mode_signal = pyqtSignal(bool)
    dom_of_def_signal = pyqtSignal(str)
    complex_mode_signal = pyqtSignal(bool)

    def __init__(self,localization):
        super().__init__()
        self.localization = localization
        self.initUI()
        self.serie_mode = False
        self.serieFonction_mode = False
        self.expression_error = False

    def initUI(self):
        layout = QVBoxLayout(self)
        self.normal_inputer = QLineEdit(self)
        self.normal_inputer.textChanged[str].connect(self._send_to_render)
        self.function_inputer = QLineEdit(self)
        self.function_inputer.setMinimumHeight(30) 
        self.function_inputer.textChanged[str].connect(self._send_to_render)
        self.inputer = self.normal_inputer

        self.range_inputer_label = QLabel(self.localization['range_inputer'],self)
        self.range_inputer = QLineEdit(self)
        self.range_inputer.setMinimumHeight(30) 
        self.range_inputer.setPlaceholderText("(-E,pi]")

         # 将函数模式的 inputer 和 range_inputer 放在一个水平布局中
        self.function_layout = QHBoxLayout()
        self.function_layout.setContentsMargins(0, 0, 0, 0)  # 设置布局的边距
        self.function_layout.setSpacing(0)
        self.function_layout.addWidget(self.function_inputer,stretch=3)
        self.function_layout.addWidget(self.range_inputer_label)
        self.function_layout.addWidget(self.range_inputer,stretch=1)


        # 创建一个 QWidget 来包含函数模式的布局
        self.function_widget = QWidget()
        self.function_widget.setLayout(self.function_layout)

        self.stacked_inputer = QStackedWidget(self)
        self.stacked_inputer.addWidget(self.normal_inputer)
        self.stacked_inputer.addWidget(self.function_widget)
        self.stacked_inputer.setFixedHeight(30)
        layout.addWidget(self.stacked_inputer)


        self.buttons = self._buttons_generator()
        for i in range(3):
            buttons_layout_temp = QHBoxLayout()
            for j in range(3):
                buttons_layout_temp.addWidget(self.buttons[i * 3 + j])
            layout.addLayout(buttons_layout_temp)
            
        checkboxes = QHBoxLayout()
        self.checkbox = QCheckBox(self.localization['serie_mode'], self)
        self.checkbox.stateChanged.connect(self._serie_mode)
        checkboxes.addWidget(self.checkbox)

        self.checkbox3 = QCheckBox(self.localization['serieFonction_mode'],self)
        self.checkbox3.stateChanged.connect(self._serieFonction_mode)
        checkboxes.addWidget(self.checkbox3)

        self.checkbox2 = QCheckBox(self.localization['more_expression'],self)
        self.checkbox2.stateChanged.connect(self._change_buttons)
        checkboxes.addWidget(self.checkbox2)
        layout.addLayout(checkboxes)

        self.submit = QPushButton(self.localization['submit_button'], self)
        self.submit.clicked.connect(self._submit)
        layout.addWidget(self.submit)

    def _serie_mode(self, state):
        if state == Qt.CheckState.Checked.value:
            self.serie_mode = True
        else:
            self.serie_mode = False
        self._send_to_render(self.inputer.text())
        
        self.serie_mode_signal.emit(self.serie_mode)


    def _serieFonction_mode(self,state):
        # self.inputer.clear()
        # print('_serieFonction_mode excuted')
        # print('curr mode is',self.serieFonction_mode)
        text = self.inputer.text()
        if 'I' in text:
            QMessageBox.warning(self, self.localization['msg_warning'], self.localization['msg_complexError'])
            self.checkbox3.setChecked(False)
            return
        if state == Qt.CheckState.Checked.value:
            self.serieFonction_mode = True
            self.stacked_inputer.setCurrentIndex(1)
            self.inputer = self.function_inputer
        else:
            self.serieFonction_mode = False
            self.stacked_inputer.setCurrentIndex(0)
            self.inputer = self.normal_inputer

        self._send_to_render(self.inputer.text())



    def _latex_expression_generator(self,raw_expression)->list:
        '''
        返回[latex_expression,sympy_expression]
        '''
        sympy_expression = simplify(raw_expression)
        sympy_expression = str(sympy_expression)
        if self.serieFonction_mode and self.serie_mode:
            sympy_expression = latex_expression = re.sub(r'\bn\b', 'k', sympy_expression)

        latex_expression = latex(simplify(raw_expression))
        if self.serie_mode:
            latex_expression = re.sub(r'\bn\b', 'k', latex_expression)
            prefix = r'S_n = \sum_{k=0}^{n} '
            
        else:
            latex_expression = re.sub(r'\bk\b', 'n', latex_expression)
            if not self.serieFonction_mode:
                prefix = r'U_n = '
            else: 
                prefix = r'f_n = '

        return [prefix + latex_expression,sympy_expression]



    def _change_buttons(self,state):
        if state != Qt.CheckState.Checked.value:
            expressions = [('sin', 'sin('),
            ('cos', 'cos('),
            ('tan', 'tan('),
            ('ln', 'ln('),
            ('exp', 'exp('),
            ('| |', 'Abs('),
            ('π', 'pi'),
            ('e', 'E'),
            ('i', 'I')]
        
        else:
            expressions= [('arcsin', 'asin('),
            ('arccos', 'acos('),
            ('arctan', 'atan('),
            ('sinh', 'sinh('),
            ('cosh', 'cosh('),
            ('tanh', 'tanh('),
            ('√', 'sqrt()'),
            ('lg', 'log(n,10)'),
            ('!', 'factorial(')
            ]
        for i in range(9):
            self.buttons[i].disconnect()
            self.buttons[i].setText(expressions[i][0])
            self.buttons[i].clicked.connect(lambda _, expr=expressions[i][1]: self._insert_expression(expr))
        

    def _send_to_render(self, text: str):
        # print(text)
        try:
            self.expression_error = has_illegal_variables(text,self.serieFonction_mode)
            # print(self.expression_error)
            text = self._latex_expression_generator(text)[0]
            self.expression_changed_signal_render.emit(text)
        except Exception as e:
            self.expression_error = True
            self.expression_changed_signal_render_error.emit(str(e))


    #输出按钮列表
    def _buttons_generator(self)->list:
        buttons = []
        expressions = [('sin', 'sin('),
            ('cos', 'cos('),
            ('tan', 'tan('),
            ('ln', 'ln('),
            ('exp', 'exp('),
            ('| |', 'Abs('),
            ('π', 'pi'),
            ('e', 'E'),
            ('i', 'I')]
        for label,expression in expressions:
            button = QPushButton(label,self)
            button.clicked.connect(lambda _, expr=expression: self._insert_expression(expr))
            buttons.append(button)
        return buttons

    
    def _insert_expression(self, expression: str):
        current_text = self.inputer.text()
        new_text = current_text + expression
        self.inputer.setText(new_text)

    def _submit(self):
        text = self.inputer.text()
        if self.expression_error or (not text):
            QMessageBox.warning(self, self.localization['msg_warning'], self.localization['msg_expressionError'])
            return
        text_LIST = self._latex_expression_generator(text)
        # print(text_LIST)
        if 'I' in text:
            self.complex_mode_signal.emit(True)
            # print('complex mod on')
        else:
            self.complex_mode_signal.emit(False)
            # print('complex mode off')
        
        if  self.serie_mode:
            self.serie_mode_signal.emit(True)
        else:
            self.serie_mode_signal.emit(False)

        if self.serieFonction_mode:
            self.serieFonction_mode_signal.emit(self.serieFonction_mode)
            self.dom_of_def_signal.emit(self.range_inputer.text())

        self.expression_changed_signal_displayer.emit(text_LIST)

    def update_texts(self, localization):
        self.localization = localization
        self.checkbox.setText(self.localization['serie_mode'])
        self.checkbox3.setText(self.localization['serieFonction_mode'])
        self.checkbox2.setText(self.localization['more_expression'])
        self.submit.setText(self.localization['submit_button'])
        self.range_inputer_label.setText(self.localization['range_inputer'])


def main():
    app = QApplication(sys.argv)
    ex = ExpressionInputer()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()


