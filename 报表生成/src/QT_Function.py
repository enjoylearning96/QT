'''
Author: 李晓乐
Date: 2025-08-05 18:25:05
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-08-09 21:02:14
FilePath: \QT\报表生成\src\QT_Function.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QStatusBar, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6 import uic
from DatabaseFunction import DatabaseManager

# 自定义一个继承自QObject的类，用于重定向stdout
class Emitter(QObject):
    text_written = pyqtSignal(str)  # 定义一个信号，用于传递文本

    def write(self, text):
        self.text_written.emit(text) 
    def flush(self):
        pass  
    # 这两个函数是重定向时必须包含的

class UI(QMainWindow):
    def __init__(self,targetuiFile,targetparaFile):
        super(UI, self).__init__()
        self.ui_main=uic.loadUi("../ui/main.ui",self)
        self.database=DatabaseManager()
        self.connectload()
        self.ui_vehicle=uic.loadUi("../ui/vehicle_manager.ui",self)
        
        #重定向
        self.emitter=Emitter()
        self.emitter.text_written.connect(self.update_status_bar)
        sys.stdout = self.emitter
    
    #简历控件间的链接
    def connectload(self)
        pass
    
    # 更新状态栏显示    
    def update_status_bar(self, text):        
        self.status_bar.showMessage(text.strip())
        
    # 恢复标准输出    
    def closeEvent(self, event):
        sys.stdout = sys.__stdout__
        super().closeEvent(event)