import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic import loadUi
from QTfunction import QTFunctions

class MainWindow(QMainWindow):  # 你的主窗口类
    def __init__(self):
        self.self.qt_functions = QTFunctions()
        app = QApplication(sys.argv)
        window = QMainWindow()

        try:
            # 动态加载UI文件
            loadUi("window_main.ui", window)  #  确保window_main.ui在同一目录下

            # 应用样式表
            with open("Ubuntu.qss", "r") as f:
                style = f.read()
            window.setStyleSheet(style)

            window.show()
            sys.exit(app.exec())
        except FileNotFoundError:
            print("Error: UI file or stylesheet not found.")
        except Exception as e:
            print(f"An error occurred: {e}")

    

if __name__ == "__main__":
    main()