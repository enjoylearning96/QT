'''
Author: 李晓乐
Date: 2025-08-23 11:41:24
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-08-23 13:04:41
FilePath: \QT\报表生成\src\QT_vehicle_manager.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QListWidgetItem, QMessageBox,
                            QInputDialog, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6 import uic
from pathlib import Path

class VehicleManager(QMainWindow):
    def __init__(self,database):
        super().__init__()
        # 加载 UI 文件
        self.database=database
        ui_path_vehicle = (Path(__file__).parent.parent / "ui" / "vehicle_manager.ui")
        self.ui_vehicle=uic.loadUi(ui_path_vehicle,self)
        self.ui_vehicle.setStyleSheet(self.style)
        self.ui_vehicle.show()
        self.ui_vehicle.comboBox.activated.connect(self.on_activated)
        self.ui_vehicle.pushButton.clicked.connect(self.vehicle)

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