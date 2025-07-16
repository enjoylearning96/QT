import sys
from PyQt6 import QtWidgets, uic

# 动态加载 UI 文件
class MyWindow(QtWidgets.QMainWindow):
    def __init__(self, ui_file):
        super().__init__()
        # 加载 UI 文件
        uic.loadUi(ui_file, self)

# 主程序入口
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # 指定 UI 文件路径
    ui_file = "薪资统计.ui"  # 替换为你的 .ui 文件路径

    # 创建窗口并显示
    window = MyWindow(ui_file)
    window.show()

    # 运行应用程序
    sys.exit(app.exec())