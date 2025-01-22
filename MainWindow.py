# import sys
# import os
# from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget,
#                               QHBoxLayout,QVBoxLayout,QStackedWidget,QPushButton,QToolBar)

# from Widgets.ExpressionInputer import ExpressionInputer
# from Widgets.ImageDisplayer import ImageDisplayer
# from Widgets.LatexRender import LatexRender
# from Widgets.PythonEditor import PythonEditor
# from PyQt6.QtCore import Qt
# from PyQt6.QtWidgets import QSizePolicy

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.initUI()

#     def initUI(self):
#         #工具栏
#         toolbar = QToolBar('工具栏')
#         self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

#         #基本组件
#         self.expression_inputer = ExpressionInputer()
#         self.python_editor = PythonEditor()
#         self.image_displayer = ImageDisplayer()
#         self.latex_render = LatexRender()

#         self.stacked_widget = QStackedWidget()
#         self.stacked_widget.addWidget(self.expression_inputer)
#         self.stacked_widget.addWidget(self.python_editor)

#         #附加组件
#         self.toggle_button = QPushButton('进阶模式', self)
#         self.toggle_button.setCheckable(True)
#         self.toggle_button.clicked.connect(self._toggle_mode)

#          # 信号连接槽函数
#         self.expression_inputer.expression_changed_signal_displayer.connect(self.image_displayer.plot_canvas.set_expression)
#         self.expression_inputer.expression_changed_signal_render.connect(self.latex_render.render)
#         self.expression_inputer.expression_changed_signal_render_error.connect(self.latex_render.error_render)
#         self.expression_inputer.trendline_checkbox_signal.connect(self.image_displayer.change_serie_mode)
        
        
#         #布局
#         toolbar.addWidget(self.toggle_button)
#         central_widget = QWidget()
#         layout = QHBoxLayout(central_widget)  # 使用 QHBoxLayout 进行左右布局

#         layout_left = QVBoxLayout()
#         layout_left.addWidget(self.latex_render)
#         layout_left.addWidget(self.expression_inputer)
#         # self.latex_render.setSizePolicy(QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding))
#         # self.expression_inputer.setSizePolicy(QSizePolicy(QSizePolicy.Policy.MinimumExpanding ,QSizePolicy.Policy.MinimumExpanding))
#         # layout_left.addWidget(self.stacked_widget)

#         layout.addLayout(layout_left)
#         layout.addWidget(self.image_displayer)
        
#         self.setCentralWidget(central_widget)


#         #其余初始化选项
#         self.setWindowTitle('GeoSeriesSolver')
#         self.setGeometry(100, 100, 800, 600)

#     def _toggle_mode(self):
#         if self.toggle_button.isChecked():
#             self.stacked_widget.setCurrentWidget(self.python_editor)
#             self.toggle_button.setText("普通模式")
#         else:
#             self.stacked_widget.setCurrentWidget(self.expression_inputer)
#             self.toggle_button.setText("进阶模式")

# def main():
#     app = QApplication(sys.argv)
#     main_window = MainWindow()
#     main_window.show()
#     sys.exit(app.exec())

# if __name__ == '__main__':
#     main()


import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QToolBar, QSplitter, QSizePolicy)
from PyQt6.QtCore import Qt

from Widgets.ExpressionInputer import ExpressionInputer
from Widgets.ImageDisplayer import ImageDisplayer
from Widgets.LatexRender import LatexRender
from Widgets.PythonEditor import PythonEditor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 工具栏
        toolbar = QToolBar('工具栏')
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        # 基本组件
        self.expression_inputer = ExpressionInputer()
        self.python_editor = PythonEditor()
        self.image_displayer = ImageDisplayer()
        self.latex_render = LatexRender()

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.expression_inputer)
        self.stacked_widget.addWidget(self.python_editor)

        # 附加组件
        self.toggle_button = QPushButton('进阶模式', self)
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self._toggle_mode)

        # 信号连接槽函数
        self.expression_inputer.expression_changed_signal_displayer.connect(self.image_displayer.plot_canvas.set_expression)
        self.expression_inputer.expression_changed_signal_render.connect(self.latex_render.render)
        self.expression_inputer.expression_changed_signal_render_error.connect(self.latex_render.error_render)
        self.expression_inputer.trendline_checkbox_signal.connect(self.image_displayer.change_serie_mode)

        self.python_editor.code_text.connect(self.latex_render.render)
        self.python_editor.advanced_mode_signal.connect(self.image_displayer.plot_canvas.plot)

        # 布局
        toolbar.addWidget(self.toggle_button)
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)  # 使用 QHBoxLayout 进行左右布局

        layout_left = QVBoxLayout()
        layout_left.addWidget(self.latex_render)
        layout_left.addWidget(self.stacked_widget)
        self.latex_render.setSizePolicy(QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding))
        self.stacked_widget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding))

        left_widget = QWidget()
        left_widget.setLayout(layout_left)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(self.image_displayer)

        layout.addWidget(splitter)
        self.setCentralWidget(central_widget)

        # 其余初始化选项
        self.setWindowTitle('GeoSeriesSolver')
        self.setGeometry(100, 100, 800, 600)

    def _toggle_mode(self):
        if self.toggle_button.isChecked():
            self.stacked_widget.setCurrentWidget(self.python_editor)
            self.image_displayer.change_advance_mode(True)
            self.toggle_button.setText("普通模式")
        else:
            self.stacked_widget.setCurrentWidget(self.expression_inputer)
            self.image_displayer.change_advance_mode(False)
            self.toggle_button.setText("进阶模式")

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()