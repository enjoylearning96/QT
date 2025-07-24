'''
Author: 李晓乐
Date: 2025-04-24 20:25:31
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-07-22 08:59:18
FilePath: \QT\多线程ping - v3.1\src\main.py
Description: 

t (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
# main.py

from PyQt6.QtWidgets import QApplication
from QTFunction import DynamicUI 
import sys

if __name__ == "__main__":
    app =QApplication(sys.argv)
    window = DynamicUI(targetuiFile="./main_window.ui",targetparaFile="../data/para.yaml")     
    window.show()        
    sys.exit(app.exec())
    