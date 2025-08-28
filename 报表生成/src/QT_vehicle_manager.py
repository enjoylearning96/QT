import sys
import re
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QDialog, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6 import uic
from pathlib import Path

ui_path_vehicle = (Path(__file__).parent.parent / "ui" / "vehicle_manager.ui")
ui_path_ok = (Path(__file__).parent.parent / "ui" / "vehicle_manager_ok.ui")
style_path = (Path(__file__).parent.parent / "ui" / "Ubuntu.qss")
    

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui_ok=uic.loadUi(ui_path_ok,self)

class VehicleManager(QMainWindow):
    def __init__(self,database):
        super().__init__()
        self.database = database
        self.ui_vehicle = uic.loadUi(ui_path_vehicle,self)
        self.ui_ok = EditDialog()
        with open(style_path, "r") as style_file:
            self.setStyleSheet(style_file.read())
        self.auto_add_secondary_nodes()
        self.treeWidget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.ui_vehicle.pushButton_add.clicked.connect(lambda: self.vehicle_action(self.treeWidget.currentItem(), action="add"))
        self.ui_vehicle.pushButton_remove.clicked.connect(lambda: self.vehicle_action(self.treeWidget.currentItem(), action="remove"))
        self.ui_vehicle.show()

    def auto_add_secondary_nodes(self):
        # 遍历所有一级节点
        for i in range(self.treeWidget.topLevelItemCount()):
            parent_item = self.treeWidget.topLevelItem(i)
            parent_text = parent_item.text(0)
            vehicle_datas = self.database.get_vehicle_data(vehicle_type=parent_text)
            # 为该一级节点添加对应的二级节点
            for vehicle_data in vehicle_datas:
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(1, str(vehicle_data["vehicle_number"]))
                child_item.setText(2, str(vehicle_data["vehicle_ip"]))
                child_item.setText(3, str(vehicle_data["load_capacity"]))
                child_item.setText(4, str(vehicle_data["available"]))
    def on_item_double_clicked(self, item, column):
        """双击二级节点进行编辑"""
        # 只处理二级节点（有父节点的节点）
        if item.parent() is not None:
            self.edit_secondary_node(item)
    
    def edit_secondary_node(self, item):
        """编辑二级节点内容"""
        self.ui_ok.lineEdit.setText(item.text(1))
        self.ui_ok.lineEdit.setEnabled(False)
        self.ui_ok.lineEdit_2.setText(item.text(2))
        self.ui_ok.lineEdit_3.setText(item.text(3))
        if item.text(4):
            self.ui_ok.checkBox.setChecked(True)
        else:
            self.ui_ok.checkBox.setChecked(False)
        self.ui_ok.buttonBox.accepted.disconnect()
        self.ui_ok.buttonBox.accepted.connect(lambda: self.vehicle_action(item,action="edit"))
        self.ui_ok.buttonBox.rejected.connect(self.ui_ok.close)
        self.ui_ok.show()

    def vehicle_action(self, item, action):
        """处理车辆操作"""
        if action == "edit":
            self.vehicle_update(item)
        elif action == "add":
            self.vehicle_add(item)
        elif action == "remove":
            self.vehicle_remove(item)

    def vehicle_update(self,item):
        """更新车辆信息"""
        if item and item.parent() is not None:
            item.setText(1, self.ui_ok.lineEdit.text())
            item.setText(2, self.ui_ok.lineEdit_2.text())
            item.setText(3, self.ui_ok.lineEdit_3.text())
            item.setText(4, "1" if self.ui_ok.checkBox.isChecked() else "0")
            if self.validate_ip_address(item.text(2)):
                if self.validate_load_weight(weight=item.text(3)):
                        self.database.update_vehicle_data(vehicle_number=item.text(1), 
                                                        vehicle_ip=item.text(2), 
                                                        vehicle_load_capacity=item.text(3), 
                                                        vehicle_available=item.text(4))

    def vehicle_remove(self,item):
        """删除车辆信息"""
        if item and item.parent() is not None:
            item.parent().removeChild(item)
            self.database.delete_vehicle_data(vehicle_number=item.text(1))

    def vehicle_add(self,item):
        """添加车辆信息"""
        self.ui_ok.lineEdit.setEnabled(True)
        self.ui_ok.buttonBox.accepted.disconnect()
        self.ui_ok.buttonBox.accepted.connect(lambda: self.vehicle_add_confirm(item))
        self.ui_ok.buttonBox.rejected.connect(self.ui_ok.close)
        self.ui_ok.show()
        
    def vehicle_add_confirm(self,item):
        """确认添加车辆信息"""  
              
        new_item = QTreeWidgetItem(item.parent())
        new_item.setText(1, self.ui_ok.lineEdit.text())
        new_item.setText(2, self.ui_ok.lineEdit_2.text())
        new_item.setText(3, self.ui_ok.lineEdit_3.text())
        new_item.setText(4, "1" if self.ui_ok.checkBox.isChecked() else "0")
        if item and item.parent() is not None:
            item.parent().addChild(new_item)
            vehicle_type = item.parent().text(0)
        if item is not None and item.parent() is None:
            item.addChild(new_item)
            vehicle_type = item.text(0)
            vehicle_exists=self.database.get_vehicle_data(vehicle_number=new_item.text(1), 
                                                                    vehicle_type=vehicle_type)
            if self.validate_ip_address(new_item.text(2)):
                if self.validate_load_weight(weight=new_item.text(3)):
                    if new_item.text(1)!="":
                        if not vehicle_exists:
                            self.database.insert_vehicle_data(vehicle_number=new_item.text(1), 
                                                            vehicle_type=vehicle_type,
                                                            vehicle_ip=new_item.text(2), 
                                                            vehicle_load_capacity=new_item.text(3), 
                                                            vehicle_available=new_item.text(4))
                        else :
                            QMessageBox.warning(self.ui_vehicle, "警告", "车辆已存在，无法添加！")
                    else:
                        QMessageBox.warning(self.ui_vehicle, "警告", "车辆编号不能为空！")
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