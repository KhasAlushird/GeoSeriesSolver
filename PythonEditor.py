import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit,
                             QPushButton,QWidget,QVBoxLayout,QMessageBox,QLabel,QPlainTextEdit)
from PyQt6.QtGui import QFont, QKeyEvent, QTextCharFormat, QColor, QSyntaxHighlighter,QTextFormat
from PyQt6.QtCore import Qt,QRect
from pygments import lex
from pygments.lexers.python import PythonLexer
from pygments.token import Token
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal
from _temp_code import output_latex
import os
import re
import ast
from Helpers import LineNumberArea



class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.lexer = PythonLexer()
        self.highlighting_rules = self.init_highlighting_rules()

    def init_highlighting_rules(self):
        rules = []
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(42, 102, 173))  # 深蓝色
        rules.append((Token.Keyword, keyword_format))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(136, 215, 252))  # 浅蓝色
        rules.append((Token.String, string_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(136, 215, 252))  # 浅蓝色
        rules.append((Token.Comment, comment_format))

        # Operators
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor(255, 255, 255))  # 白色
        rules.append((Token.Operator, operator_format))

        # Functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(217, 214, 159))  # 浅橙色
        rules.append((Token.Name.Function, function_format))

        # Classes
        class_format = QTextCharFormat()
        class_format.setForeground(QColor(136, 215, 252))  # 浅蓝色
        rules.append((Token.Name.Class, class_format))

        # Variables
        variable_format = QTextCharFormat()
        variable_format.setForeground(QColor(136, 215, 252))  # 浅蓝色
        rules.append((Token.Name.Variable, variable_format))

        return rules

    def highlightBlock(self, text):
        for token, content in lex(text, self.lexer):
            for rule_token, format in self.highlighting_rules:
                if token in rule_token:
                    start = text.find(content)
                    length = len(content)
                    self.setFormat(start, length, format)

        # Highlight parentheses
        self._highlight_parentheses(text)

    def _highlight_parentheses(self, text):
        stack = []
        for i, char in enumerate(text):
            if char == '(':
                stack.append(i)
            elif char == ')':
                if stack:
                    start = stack.pop()
                    if not stack:
                        # 最外层括号
                        format = QTextCharFormat()
                        format.setForeground(QColor(222, 135, 29))  # 最外层括号颜色
                        self.setFormat(start, 1, format)
                        self.setFormat(i, 1, format)
                    else:
                        # 内层括号
                        format = QTextCharFormat()
                        format.setForeground(QColor(139, 87, 196))  # 内层括号颜色
                        self.setFormat(start, 1, format)
                        self.setFormat(i, 1, format)

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: rgb(31, 31, 31); color: rgb(136, 215, 252);")
        self.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.highlighter = PythonHighlighter(self.document())
        self.setPlaceholderText()
        self.textChanged.connect(self.check_syntax)

        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.line_number_area.update_line_number_area_width)
        self.updateRequest.connect(self.line_number_area.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.line_number_area.update_line_number_area_width()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area.line_number_area_width(), cr.height()))

    def highlight_current_line(self):
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor(44, 44, 44)
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def setPlaceholderText(self):
        # 设置预设的文字
        preset_text = """import latexify
import math

def F(n):
    if n == 0:
        return math.cos(n)
    else:
        return F(n-1) + 1

def output_latex():
    return latexify.get_latex(F)
"""
        self.setPlainText(preset_text)
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Tab.value:
            self.insertPlainText("    ")  # 插入四个空格进行缩进
        else:
            super().keyPressEvent(event)


    def check_syntax(self):
        code = self.toPlainText()
        try:
            ast.parse(code)
            self.parent().syntax_label.setText("语法正确")
            self.parent().syntax_label.setStyleSheet("color: green;")
        except SyntaxError as e:
            self.parent().syntax_label.setText(f"存在语法错误: {e}")
            self.parent().syntax_label.setStyleSheet("color: red;")

class PythonEditor(QWidget):
    code_text = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.editor = CodeEditor()
        layout = QVBoxLayout(self)
        layout.addWidget(self.editor)   
        self.submit_button = QPushButton('提交', self)
        self.submit_button.clicked.connect(self._submit)
        self.syntax_label = QLabel("语法检查")
        self.syntax_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.syntax_label)
        layout.addWidget(self.submit_button)

    def _submit(self):
        code = self.editor.toPlainText()
        if not re.search(r'def\s+F\s*\(', code):
            QMessageBox.warning(self, "警告", "'F'函数缺失")
            return
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, "_temp_code.py")
        with open(file_path, 'w') as file:
            file.write(code)

        self.code_text.emit(output_latex())
        print(output_latex())
    


        
    



def main():
    app = QApplication(sys.argv)
    main_window = QWidget()
    main_window.setWindowTitle('Main Application')
    main_window.setGeometry(100, 100, 800, 600)

    layout = QVBoxLayout(main_window)
    image_displayer = PythonEditor()
    layout.addWidget(image_displayer)

    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()