import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QStackedWidget, QPushButton, QToolBar,
                                QSplitter,QComboBox, QSizePolicy,QLabel)
from PyQt6.QtCore import Qt

from GeoSeriesSolver.Widgets.ExpressionInputer import ExpressionInputer
from GeoSeriesSolver.Widgets.ImageDisplayer import ImageDisplayer
from GeoSeriesSolver.Widgets.LatexRender import LatexRender
from GeoSeriesSolver.Widgets.PythonEditor import PythonEditor
from GeoSeriesSolver.Resources.Helpers import resource_path
import os
import yaml
import logging




# logging.basicConfig(
#     filename='app.log',  # 日志文件名
#     level=logging.DEBUG,# 记录错误级别以上的日志
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     encoding='utf-8'
# )


# def log_sys_info():
#     """记录 sys.path 和 os.getcwd()"""
#     logging.debug("当前工作目录 (os.getcwd()): %s", os.getcwd())
#     logging.debug("模块搜索路径 (sys.path):")
#     for path in sys.path:
#         logging.debug("  %s", path)


def load_translations(language):
    """ 加载本地化文件 """
    # 动态获取资源路径
    loc_file_path = resource_path(os.path.join('Localizations', f'{language}.yaml'))
    
    # 检查文件是否存在
    if not os.path.exists(loc_file_path):
        raise FileNotFoundError(f"Localization file not found: {loc_file_path}")
    
    # 加载并返回 YAML 文件内容
    with open(loc_file_path, 'r', encoding='utf-8') as file:
        return yaml.safe_load(file)
    
class MainWindow(QMainWindow):
    def __init__(self,localization):
        # log_sys_info()
        super().__init__()
        self.localization = localization
        self.initUI()

    def initUI(self):
        # 工具栏
        self.toolbar = QToolBar(self.localization['main_window']['toolbar'])
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        # 基本组件
        self.expression_inputer = ExpressionInputer(self.localization['expression_inputer'])
        self.python_editor = PythonEditor(self.localization['python_editor'])
        self.image_displayer = ImageDisplayer(self.localization['image_displayer'])
        self.latex_render = LatexRender()

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.expression_inputer)
        self.stacked_widget.addWidget(self.python_editor)

        # 附加组件
        self.toggle_button = QPushButton(self.localization['main_window']['advanced_mode'], self)
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self._toggle_mode)
        self.toolbar.addWidget(self.toggle_button)
        
        self.language_combobox_label = QLabel(self.localization['main_window']['language_label'], self)
        self.toolbar.addWidget(self.language_combobox_label)

        self.language_combobox = QComboBox(self)
        self.language_combobox.addItems(['中文','English','Français'])
        self.language_combobox.currentIndexChanged.connect(self._change_language)
        self.toolbar.addWidget(self.language_combobox)

        # 信号连接槽函数
        self.expression_inputer.expression_changed_signal_displayer.connect(self.image_displayer.set_expression_for_canvas)
        self.expression_inputer.expression_changed_signal_render.connect(self.latex_render.render)
        self.expression_inputer.expression_changed_signal_render_error.connect(self.latex_render.error_render)
        self.expression_inputer.serie_mode_signal.connect(self.image_displayer.change_serie_mode)
        self.expression_inputer.serieFonction_mode_signal.connect(self.image_displayer.change_serieFonction_mode)
        self.expression_inputer.complex_mode_signal.connect(self.image_displayer.change_complex_mode)
        self.expression_inputer.dom_of_def_signal.connect(self.image_displayer.set_dom_of_def)

        self.python_editor.code_text.connect(self.latex_render.render)
        self.python_editor.advanced_mode_signal.connect(self.image_displayer.plot_canvas.plot)
        self.python_editor.F_signal.connect(self.image_displayer.plot_canvas.set_F)

        # 布局
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)  # 使用 QHBoxLayout 进行左右布局

        layout_left = QVBoxLayout()
        # layout_left.addWidget(self.latex_render)
        # layout_left.addWidget(self.stacked_widget)
        self.latex_render.setSizePolicy(QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding))
        self.stacked_widget.setSizePolicy(QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding))
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_splitter.setStyleSheet("QSplitter::handle { background-color: lightgray; }")
        left_splitter.addWidget(self.latex_render)
        left_splitter.addWidget(self.stacked_widget)
        left_splitter.setSizes([245, 100]) 

        layout_left.addWidget(left_splitter)

        left_widget = QWidget()
        left_widget.setLayout(layout_left)
    

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(self.image_displayer)
        # splitter.setHandleWidth(10)  # 设置手柄宽度
        splitter.setStyleSheet("QSplitter::handle { background-color: gray; }")  # 设置手柄样式

        layout.addWidget(splitter)
        self.setCentralWidget(central_widget)

        # 其余初始化选项
        self.setWindowTitle(self.localization['main_window']['title'])
        self.setGeometry(100, 100, 800, 600)

    def _toggle_mode(self):
        if self.toggle_button.isChecked():
            self.stacked_widget.setCurrentWidget(self.python_editor)
            self.image_displayer.change_advance_mode(True)
            self.toggle_button.setText(self.localization['main_window']['normal_mode'])
        else:
            self.stacked_widget.setCurrentWidget(self.expression_inputer)
            self.image_displayer.change_advance_mode(False)
            self.toggle_button.setText(self.localization['main_window']['advanced_mode'])
    
    

    
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
        self.localization = load_translations(language)
        self._update_texts()

    def _update_texts(self):
        self.toolbar.setWindowTitle(self.localization['main_window']['toolbar'])
        self.toggle_button.setText(self.localization['main_window']['advanced_mode'] if not self.toggle_button.isChecked() else self.localization['main_window']['normal_mode'])
        self.setWindowTitle(self.localization['main_window']['title'])

        #子组件的本地化
        self.expression_inputer.update_texts(self.localization['expression_inputer'])
        self.image_displayer.update_texts(self.localization['image_displayer'])
        self.python_editor.update_texts(self.localization['python_editor'])

def main():
    try:
        app = QApplication(sys.argv)
        language = 'zh'
        localization = load_translations(language)
        main_window = MainWindow(localization)
        main_window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error("程序崩溃！错误信息：", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()