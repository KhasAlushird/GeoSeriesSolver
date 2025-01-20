import sys
from PyQt6.QtWidgets import QLabel, QLineEdit,QHBoxLayout, QApplication, QWidget, QCheckBox, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWebEngineWidgets import QWebEngineView
from sympy import latex,simplify
from PyQt6.QtCore import Qt
from Helpers import latex_render

class ExpressionInputer(QWidget):
    expression_changed_signal = pyqtSignal(str)  # 定义一个信号，传递字符串类型的解析式
    trendline_checkbox_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.trendline_checkbox_enabled = True
        layout = QVBoxLayout(self)
        self.expression_shower = QWebEngineView(self)
        layout.addWidget(self.expression_shower)
        self.inputer = QLineEdit(self)
        self.inputer.textChanged[str].connect(self._label_shower)
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

        self.checkbox2 = QCheckBox('更多表达式',self)
        self.checkbox2.stateChanged.connect(self._change_buttons)
        checkboxes.addWidget(self.checkbox2)
        layout.addLayout(checkboxes)

        self.submit = QPushButton('提交', self)
        self.submit.clicked.connect(self._submit)
        layout.addWidget(self.submit)

    def _serie_mode(self, state):
        if state == Qt.CheckState.Checked.value:
            self.trendline_checkbox_enabled = False
        else:
            self.trendline_checkbox_enabled = True
        self._label_shower(self.inputer.text())
        # todo: 实现级
        pass


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
        

    def _label_shower(self, text: str):
    # 使用 sympy 将 Python 表达式转换为 LaTeX 表达式
        try:
            if not self.trendline_checkbox_enabled:
                prefix = r'S_n = \sum_{k=0}^{n} '
                text = text.replace('n','k')
            else:
                text = text.replace('k','n')
                prefix = r'U_n = '
            latex_expression = latex(simplify(text))
            html_content = latex_render(prefix,latex_expression)
            self.expression_shower.setHtml(html_content)
        except Exception as e:
            self.expression_shower.setHtml(f"<p>Error: {e}</p>")

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
        if self.trendline_checkbox_enabled:
            self.trendline_checkbox_signal.emit(True)
        else:
            self.trendline_checkbox_signal.emit(False)
        text = self.inputer.text()
        text = text.replace('k', 'n') 
        self.expression_changed_signal.emit(text)

def main():
    app = QApplication(sys.argv)
    ex = ExpressionInputer()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()


