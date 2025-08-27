'''
Author: 李晓乐
Date: 2025-08-23 11:41:24
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-08-27 22:54:40
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
        style_path = (Path(__file__).parent.parent / "ui" / "Ubuntu.qss")
        self.ui_vehicle=uic.loadUi(ui_path_vehicle,self)
        with open(style_path, "r") as style_file:
            self.setStyleSheet(style_file.read())
        self.ui_vehicle.comboBox_3.hide()
        self.ui_vehicle.show()
        self.ui_vehicle.comboBox.currentTextChanged.connect(self.on_combo_text_changed)
        self.ui_vehicle.pushButton.clicked.connect(self.vehicle)

    
    #车辆管理窗口选项激活时，界面变化
    def on_combo_text_changed(self, text):
        # 根据选中的车辆类型更新界面
        vehicle_manager_action = text
        if vehicle_manager_action=="增加车辆" :
            self.ui_vehicle.comboBox_3.hide()
            self.ui_vehicle.lineEdit.show()
        else:
            self.ui_vehicle.lineEdit.hide()
            self.type_changed(self.ui_vehicle.comboBox_2.currentText())
            self.ui_vehicle.comboBox_3.show()
            self.ui_vehicle.comboBox_2.currentTextChanged.connect(self.type_changed)
            
    # 根据车辆类型刷新车辆列表
    def type_changed(self, text):
        vehicles = self.database.get_vehicle_data(vehicle_type=text)
        self.ui_vehicle.comboBox_3.clear()
        self.ui_vehicle.comboBox_3.addItems([str(v['vehicle_number']) for v in vehicles])
        self.vehicle_number_changed(self.ui_vehicle.comboBox_3.currentText())
        self.ui_vehicle.comboBox_3.currentTextChanged.connect(self.vehicle_number_changed)
    
    def vehicle_number_changed(self, text):
        vehicle_data=self.database.get_vehicle_data(vehicle_number=text)
        if vehicle_data:
            self.ui_vehicle.lineEdit_2.setText(vehicle_data[0]['vehicle_ip'])
            self.ui_vehicle.lineEdit_3.setText(str(vehicle_data[0]['load_capacity']))

    # 提交车辆管理结果
    def vehicle(self):
        manager_action=self.ui_vehicle.comboBox.currentText()
        if manager_action=="增加车辆":
            self.vehicle_add()
        if manager_action=="修改车辆":
            self.vehicle_update()
        if manager_action=="删除车辆":
            self.vehicle_delete()
        
    # 新增车辆，先检测车辆编号是否存在，ip是否有效
    def vehicle_add(self):
        vehicle_exists=self.database.get_vehicle_data(vehicle_number=self.ui_vehicle.lineEdit.text(), 
                                                                    vehicle_type=self.ui_vehicle.comboBox_2.currentText())
        if not vehicle_exists:
            self.database.insert_vehicle_data(vehicle_number=self.ui_vehicle.lineEdit.text(), 
                                              vehicle_type=self.ui_vehicle.comboBox_2.currentText(), 
                                              vehicle_ip=self.ui_vehicle.lineEdit_2.text(), 
                                              load_capacity=self.ui_vehicle.lineEdit_3.text())
        else :
            QMessageBox.warning(self, "警告", "车辆已存在，无法添加！")
            
    # 修改车辆
    def vehicle_update(self):
        self.database.update_vehicle_data(vehicle_number=self.ui_vehicle.comboBox_3.currentText(), 
                                        vehicle_type=self.ui_vehicle.comboBox_2.currentText(), 
                                        vehicle_ip=self.ui_vehicle.lineEdit_2.text(), 
                                        load_capacity=self.ui_vehicle.lineEdit_3.text())
    # 删除车辆
    def vehicle_delete(self):
        self.database.delete_vehicle_data(vehicle_number=self.ui_vehicle.comboBox_3.currentText())