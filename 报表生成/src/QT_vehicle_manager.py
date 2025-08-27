'''
Author: 李晓乐
Date: 2025-08-23 11:41:24
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-08-27 23:43:15
FilePath: \QT\报表生成\src\QT_vehicle_manager.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import sys
import re
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
            self.ui_vehicle.lineEdit_2.setText("")
            self.ui_vehicle.lineEdit_3.setText("")
        else:
            self.ui_vehicle.lineEdit.hide()
            self.type_changed(self.ui_vehicle.comboBox_2.currentText())
            self.ui_vehicle.comboBox_3.show()
            self.ui_vehicle.comboBox_2.currentTextChanged.connect(self.type_changed)
            
    # 根据车辆类型刷新车辆列表
    def type_changed(self, text):
        if self.ui_vehicle.comboBox.currentText()=="增加车辆":
            pass
        else:
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
        if self.validate_ip_address(self.ui_vehicle.lineEdit_2.text()):
            if self.validate_load_weight(weight=self.ui_vehicle.lineEdit_3.text()):
                if self.ui_vehicle.lineEdit.text()!="":
                    if not vehicle_exists:
                        self.database.insert_vehicle_data(vehicle_number=self.ui_vehicle.lineEdit.text(), 
                                                        vehicle_type=self.ui_vehicle.comboBox_2.currentText(), 
                                                        vehicle_ip=self.ui_vehicle.lineEdit_2.text(), 
                                                        load_capacity=self.ui_vehicle.lineEdit_3.text())
                    else :
                        QMessageBox.warning(self.ui_vehicle, "警告", "车辆已存在，无法添加！")
                else:
                    QMessageBox.warning(self.ui_vehicle, "警告", "车辆编号不能为空！")

    # 修改车辆
    def vehicle_update(self):
        self.database.update_vehicle_data(vehicle_number=self.ui_vehicle.comboBox_3.currentText(), 
                                        vehicle_type=self.ui_vehicle.comboBox_2.currentText(), 
                                        vehicle_ip=self.ui_vehicle.lineEdit_2.text(), 
                                        load_capacity=self.ui_vehicle.lineEdit_3.text())
    # 删除车辆
    def vehicle_delete(self):
        self.database.delete_vehicle_data(vehicle_number=self.ui_vehicle.comboBox_3.currentText())
    
    def validate_ip_address(self,ip):
        """检测IP地址是否符合规范"""
        # IP地址正则表达式
        ip_pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
        
        match = re.match(ip_pattern, ip)
        if not match:
            QMessageBox.warning(self.ui_vehicle, "警告", "IP地址格式不正确")
            return False
        
        # 检查每个数字段是否在0-255范围内
        for segment in match.groups():
            if not 0 <= int(segment) <= 255:
                QMessageBox.warning(self.ui_vehicle, "警告", "IP超出范围(0-255)")
                return False
        
        return True

    def validate_load_weight(self, weight, min_weight=0, max_weight=200):
        """检测载重量是否为数字且在合理范围内"""
        try:
            # 尝试转换为浮点数
            weight_value = float(weight)
            
            # 检查范围
            if not min_weight <= weight_value <= max_weight:
                QMessageBox.warning(self.ui_vehicle, "警告", "载重量超出范围(0-200)")
                return False
            else:
                return True
            
        except (ValueError, TypeError):
            QMessageBox.warning(self.ui_vehicle, "警告", "载重量必须是数字")
            return False