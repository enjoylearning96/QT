from QT_Function import  UI
from PyQt6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = UI()
    sys.exit(app.exec())