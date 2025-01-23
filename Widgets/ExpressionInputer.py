import sys
from PyQt6.QtWidgets import QLabel, QLineEdit,QHBoxLayout, QApplication, QWidget, QCheckBox, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from sympy import latex,simplify
from PyQt6.QtCore import Qt
import re

class ExpressionInputer(QWidget):
    expression_changed_signal_displayer = pyqtSignal(list)  # 发送给ImageDisplayer,格式为[latex_expression,sympy_expression]
    expression_changed_signal_render = pyqtSignal(str)
    expression_changed_signal_render_error = pyqtSignal(str)
    trendline_checkbox_signal = pyqtSignal(bool)
    serieFonction_mode_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.initUI()
        self.serie_mode = False
        self.serieFonction_mode = False

    def initUI(self):
        layout = QVBoxLayout(self)
        self.inputer = QLineEdit(self)
        self.inputer.textChanged[str].connect(self._send_to_render)
        layout.addWidget(self.inputer)


        self.buttons = self._buttons_generator()
        for i in range(3):
            buttons_layout_temp = QHBoxLayout()
            for j in range(3):
                buttons_layout_temp.addWidget(self.buttons[i * 3 + j])
            layout.addLayout(buttons_layout_temp)
            
        checkboxes = QHBoxLayout()
        self.checkbox = QCheckBox('级数模式', self)
        self.checkbox.stateChanged.connect(self._serie_mode)
        checkboxes.addWidget(self.checkbox)

        self.checkbox3 = QCheckBox('函数列模式',self)
        self.checkbox3.stateChanged.connect(self._serieFonction_mode)
        checkboxes.addWidget(self.checkbox3)

        self.checkbox2 = QCheckBox('更多表达式',self)
        self.checkbox2.stateChanged.connect(self._change_buttons)
        checkboxes.addWidget(self.checkbox2)
        layout.addLayout(checkboxes)

        self.submit = QPushButton('提交', self)
        self.submit.clicked.connect(self._submit)
        layout.addWidget(self.submit)

    def _serie_mode(self, state):
        if state == Qt.CheckState.Checked.value:
            self.serie_mode = True
        else:
            self.serie_mode = False
        self._send_to_render(self.inputer.text())
        
        self.trendline_checkbox_signal.emit(not self.serie_mode)


    def _serieFonction_mode(self,state):
        self.inputer.clear()
        if state == Qt.CheckState.Checked.value:
            self.serieFonction_mode = True
        else:
            self.serieFonction_mode = False

        self._send_to_render(self.inputer.text())

        self.serieFonction_mode_signal.emit(self.serieFonction_mode)


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
            ('e', 'e'),
            ('i', 'I')]
        
        else:
            expressions= [('arcsin', 'asin('),
            ('arccos', 'acos('),
            ('arctan', 'atan('),
            ('sinh', 'sinh('),
            ('cosh', 'cosh('),
            ('tanh', 'tanh('),
            ('√', 'sqrt()'),
            ('log10', 'log(n,10)'),
            ('!', 'factorial(')
            ]
        for i in range(9):
            self.buttons[i].disconnect()
            self.buttons[i].setText(expressions[i][0])
            self.buttons[i].clicked.connect(lambda _, expr=expressions[i][1]: self._insert_expression(expr))
        

    def _send_to_render(self, text: str):
        try:
            text = self._latex_expression_generator(text)[0]
            self.expression_changed_signal_render.emit(text)
        except Exception as e:
            self.expression_changed_signal_render_error.emit(str(e))


    #输出按钮列表
    def _buttons_generator(self)->list:
        buttons = []
        expressions = [('sin', 'sin()'),
            ('cos', 'cos('),
            ('tan', 'tan('),
            ('ln', 'ln('),
            ('exp', 'exp('),
            ('| |', 'Abs('),
            ('π', 'pi'),
            ('e', 'e'),
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
        if not self.serie_mode:
            self.trendline_checkbox_signal.emit(True)
        else:
            self.trendline_checkbox_signal.emit(False)
        text = self.inputer.text()
        text_LIST = self._latex_expression_generator(text)
        print(text_LIST)
        self.expression_changed_signal_displayer.emit(text_LIST)

def main():
    app = QApplication(sys.argv)
    ex = ExpressionInputer()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()


