import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QStackedWidget, QPushButton, QToolBar,
                                QSplitter,QComboBox, QSizePolicy,QLabel)
from PyQt6.QtCore import Qt

from Widgets.ExpressionInputer import ExpressionInputer
from Widgets.ImageDisplayer import ImageDisplayer
from Widgets.LatexRender import LatexRender
from Widgets.PythonEditor import PythonEditor
import os
import yaml


def load_translations(language):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    loc_file_path = os.path.join(current_dir, 'Locolizations', f'{language}.yaml')
    with open(loc_file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)
    
class MainWindow(QMainWindow):
    def __init__(self,locoalization):
        super().__init__()
        self.locoalization = locoalization
        self.initUI()

    def initUI(self):
        # 工具栏
        self.toolbar = QToolBar(self.locoalization['main_window']['toolbar'])
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        # 基本组件
        self.expression_inputer = ExpressionInputer()
        self.python_editor = PythonEditor()
        self.image_displayer = ImageDisplayer()
        self.latex_render = LatexRender()

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.expression_inputer)
        self.stacked_widget.addWidget(self.python_editor)

        # 附加组件
        self.toggle_button = QPushButton(self.locoalization['main_window']['advanced_mode'], self)
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self._toggle_mode)
        self.toolbar.addWidget(self.toggle_button)
        
        self.language_combobox_label = QLabel(self.locoalization['main_window']['language_label'], self)
        self.toolbar.addWidget(self.language_combobox_label)

        self.language_combobox = QComboBox(self)
        self.language_combobox.addItems(['中文','English','Français'])
        self.language_combobox.currentIndexChanged.connect(self._change_language)
        self.toolbar.addWidget(self.language_combobox)

        # 信号连接槽函数
        self.expression_inputer.expression_changed_signal_displayer.connect(self.image_displayer.set_expression_for_canvas)
        self.expression_inputer.expression_changed_signal_render.connect(self.latex_render.render)
        self.expression_inputer.expression_changed_signal_render_error.connect(self.latex_render.error_render)
        self.expression_inputer.trendline_checkbox_signal.connect(self.image_displayer.change_serie_mode)
        self.expression_inputer.serieFonction_mode_signal.connect(self.image_displayer.change_serieFonction_mode)
        self.expression_inputer.complex_mode_signal.connect(self.image_displayer.change_complex_mode)

        self.python_editor.code_text.connect(self.latex_render.render)
        self.python_editor.advanced_mode_signal.connect(self.image_displayer.plot_canvas.plot)

        # 布局
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
        self.setWindowTitle(self.locoalization['main_window']['title'])
        self.setGeometry(100, 100, 800, 600)

    def _toggle_mode(self):
        if self.toggle_button.isChecked():
            self.stacked_widget.setCurrentWidget(self.python_editor)
            self.image_displayer.change_advance_mode(True)
            self.toggle_button.setText(self.locoalization['main_window']['normal_mode'])
        else:
            self.stacked_widget.setCurrentWidget(self.expression_inputer)
            self.image_displayer.change_advance_mode(False)
            self.toggle_button.setText(self.locoalization['main_window']['advanced_mode'])
    
    

    
    def _change_language(self,index:int):
        '''
        0-> 中文  1->英语 2->法语
        '''
        if index == 0:
            language = 'zh'
        elif index == 1:
            language = 'en'
        else:
            language = 'fr'
        self.locoalization = load_translations(language)
        self._update_texts()

    def _update_texts(self):
        self.toolbar.setWindowTitle(self.locoalization['main_window']['toolbar'])
        self.toggle_button.setText(self.locoalization['main_window']['advanced_mode'] if not self.toggle_button.isChecked() else self.locoalization['main_window']['normal_mode'])
        self.setWindowTitle(self.locoalization['main_window']['title'])

def main():
    app = QApplication(sys.argv)
    language = 'zh'
    locoalization = load_translations(language)
    main_window = MainWindow(locoalization)
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()