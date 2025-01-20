import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from ExpressionInputer import ExpressionInputer
from ImageDisplayer import ImageDisplayer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        layout = QHBoxLayout(central_widget)  # 使用 QHBoxLayout 进行左右布局

        self.expression_inputer = ExpressionInputer()
        self.image_displayer = ImageDisplayer()

        # 连接 ExpressionInputer 的信号到 ImageDisplayer 的方法
        self.expression_inputer.expression_changed_signal.connect(self.image_displayer.plot_canvas.set_expression)
        self.expression_inputer.trendline_checkbox_signal.connect(self.image_displayer.change_serie_mode)

        layout.addWidget(self.expression_inputer)
        layout.addWidget(self.image_displayer)

        self.setCentralWidget(central_widget)
        self.setWindowTitle('GeoSerieSolver')
        self.setGeometry(100, 100, 800, 600)

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()