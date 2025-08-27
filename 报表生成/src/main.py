'''
Author: 李晓乐
Date: 2025-07-25 22:06:11
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-08-27 22:31:47
FilePath: \QT\报表生成\src\main.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
from QT_Function import  UI
from PyQt6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = UI()
    sys.exit(app.exec())