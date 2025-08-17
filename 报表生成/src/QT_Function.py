'''
Author: 李晓乐
Date: 2025-08-05 18:25:05
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-08-17 20:10:54
FilePath: \QT\报表生成\src\QT_Function.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal, QDate
from PyQt6 import uic
from Database_Function import DatabaseManager
from pathlib import Path

# 自定义一个继承自QObject的类，用于重定向stdout
class Emitter(QObject):
    text_written = pyqtSignal(str)  # 定义一个信号，用于传递文本

    def write(self, text):
        self.text_written.emit(text) 
    def flush(self):
        pass  
    # 这两个函数是重定向时必须包含的
    
def load_stylesheet(filename):
    with open(filename, "r") as f:
        return f.read()
    
    

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()
        ui_path_main = (Path(__file__).parent.parent / "ui" / "main.ui")
        style_path=(Path(__file__).parent.parent / "ui" / "Ubuntu.qss")
        self.style = load_stylesheet(style_path)
        self.ui_main=uic.loadUi(ui_path_main,self)
        self.ui_main.setStyleSheet(self.style)
               
        self.connectload()
        
        #重定向
        self.emitter=Emitter()
        self.emitter.text_written.connect(self.update_status_bar)
        sys.stdout = self.emitter
        self.ui_main.show()
        self.database=DatabaseManager() 
    
    #建立控件间的链接
    def connectload(self):
        self.ui_main.action_2.triggered.connect(self.show_vehicle_manager)
        self.ui_main.action.triggered.connect(self.show_vehicle_distribution)
        self.ui_main.dateEdit.setDate(QDate.currentDate())
        self.ui_main.dateEdit_2.setDate(QDate.currentDate())
        self.ui_main.dateEdit_3.setDate(QDate.currentDate())
    
    #加载车辆管理窗口    
    def show_vehicle_manager(self):
        ui_path_vehicle = (Path(__file__).parent.parent / "ui" / "vehicle_manager.ui")
        self.ui_vehicle=uic.loadUi(ui_path_vehicle,self)
        self.ui_vehicle.setStyleSheet(self.style)
        self.ui_vehicle.show()
        self.ui_main.hide()
        self.ui_vehicle.comboBox.activated.connect(self.on_activated)
        self.ui_vehicle.pushButton.clicked.connect(self.vehicle)
        
    def show_vehicle_distribution(self):
        ui_path_vehicle = (Path(__file__).parent.parent / "ui" / "vehicle_distribution.ui")
        self.ui_vehicle_distribution=uic.loadUi(ui_path_vehicle,self)
        self.ui_vehicle_distribution.setStyleSheet(self.style)
        self.ui_vehicle_distribution.show()
        self.ui_main.hide()
        
    #车辆管理窗口选项激活时，界面变化
    def on_activated(self, index):
        # 根据选中的车辆类型更新界面
        vehicle_manager_action = self.ui_vehicle.comboBox.itemText(index)
        if vehicle_manager_action=="增加车辆" :
            pass
        if vehicle_manager_action=="修改车辆" :
            pass
        if vehicle_manager_action=="删除车辆" :
            pass
        if vehicle_manager_action==" " :
            pass
        
    # 提交车辆管理结果
    def vehicle(self):
        manager_action=self.ui_vehicle.comboBox.currentText()
        if manager_action=="增加车辆":
            self.database.insert_vehicle_data(vehicle_number=self.ui_vehicle.lineEdit.text(), 
                                              vehicle_type=self.ui_vehicle.comboBox_2.currentText(), 
                                              vehicle_ip=self.ui_vehicle.lineEdit_2.text(), 
                                              load_capacity=self.ui_vehicle.lineEdit_3.text())
        if manager_action=="修改车辆":
            pass
        if manager_action=="删除车辆":
            pass
        if manager_action==" ":
            pass
    # 更新状态栏显示    
    def update_status_bar(self, text):        
        self.status_bar.showMessage(text.strip())
        
    # 恢复标准输出    
    def closeEvent(self, event):
        sys.stdout = sys.__stdout__
        super().closeEvent(event)