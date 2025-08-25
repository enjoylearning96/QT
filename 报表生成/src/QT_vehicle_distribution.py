import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QListWidgetItem, QMessageBox,
                            QInputDialog, QCheckBox,QListWidget)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from PyQt6 import uic
from pathlib import Path
import time


class ShovelWidget(QCheckBox):
    """自定义电铲选择复选框"""
    def __init__(self, shovel_id, parent=None):
        super().__init__(f"电铲 {shovel_id}", parent)
        self.shovel_id = shovel_id

class VehicleDistribution(QMainWindow):
    def __init__(self,database):
        super().__init__()
        # 加载 UI 文件
        ui_path = (Path(__file__).parent.parent / "ui" / "vehicle_distribution.ui")
        style_path = (Path(__file__).parent.parent / "ui" / "Ubuntu.qss")
        self.ui=uic.loadUi(ui_path, self)
        with open(style_path, "r") as style_file:
            self.setStyleSheet(style_file.read())
        # 初始化变量
        self.database = database
        self.shovel_options = []
        self.shovel_optionss = self.database.get_vehicle_data(vehicle_type="电铲")
        for option in self.shovel_optionss:
            self.shovel_options.append(option["vehicle_number"])
        self.selected_shovels = []   # 选中的电铲列表
        self.shovel_widgets = {}     # 电铲组件字典
        
        # 初始化电铲选择列表
        self.init_shovel_selection()
        
        # 初始化车辆列表
        self.init_vehicle_list()

        # 连接信号
        self.setup_connections()
               
        self.ui.show()
    
    # 初始化电铲选择列表
    def init_shovel_selection(self):
        """初始化电铲选择列表"""
        # 清空现有选项
        self.listWidget_shovelSelect.clear()
        
        # 添加电铲选项
        for option in self.shovel_options:
            item = QListWidgetItem(option)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget_shovelSelect.addItem(item)
        
    # 初始化车辆列表
    def init_vehicle_list(self):
        
        for vehicle_data in self.database.get_vehicle_data(vehicle_type="矿卡-930E"):
            item = QListWidgetItem(f"{vehicle_data['vehicle_number']}")
            item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget_930E.addItem(item)
        for vehicle_data in self.database.get_vehicle_data(vehicle_type="矿卡-830E"):
            item = QListWidgetItem(f"{vehicle_data['vehicle_number']}")
            item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget_830E.addItem(item)
        for vehicle_data in self.database.get_vehicle_data(vehicle_type="矿卡-NTE330"):
            item = QListWidgetItem(f"{vehicle_data['vehicle_number']}")
            item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget_NTE330.addItem(item)
        for vehicle_data in self.database.get_vehicle_data(vehicle_type="矿卡-NTE360"):
            item = QListWidgetItem(f"{vehicle_data['vehicle_number']}")
            item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget_NTE360.addItem(item)
        for vehicle_data in self.database.get_vehicle_data(vehicle_type="矿卡-33900"):
            item = QListWidgetItem(f"{vehicle_data['vehicle_number']}")
            item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget_33900.addItem(item)

    def setup_connections(self):
        """连接信号和槽"""
        self.pushButton_confirmShovel.clicked.connect(self.on_confirm_shovel_selection)
        self.pushButton_2.clicked.connect(self.update_display_add)
        self.pushButton_3.clicked.connect(self.update_display_remove)
        self.pushButton.clicked.connect(self.record_save)
        for i in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(i)  # 获取标签页            
            # 在标签页中查找所有的 ListWidget
            for list_widget in tab.findChildren(QListWidget):
                list_widget.itemDoubleClicked.connect(self.edit_vehicle_status)

    #确认电铲选择
    def on_confirm_shovel_selection(self):
        selected_shovels = []
        
        # 获取选中的电铲
        for i in range(self.listWidget_shovelSelect.count()):
            item = self.listWidget_shovelSelect.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                shovel_id = item.text()
                selected_shovels.append(shovel_id)

        if not selected_shovels:
            QMessageBox.warning(self, "提示", "请至少选择一个电铲")
            return
        
        self.selected_shovels = selected_shovels
        self.create_shovel_widgets()
    
    #修改标签页为选中的电铲
    def create_shovel_widgets(self):
        
        num=len(self.selected_shovels)-2
        if num>0:
            for i in range(num):                
                self.tabWidget_shovelSelect.addTab(self.listWidget(), "")
        for i in range(len(self.selected_shovels)):
            self.tabWidget_shovelSelect.setTabText(i, f"电铲 {self.selected_shovels[i]}")
    
    #分配时对电铲的车辆进行更新
    def update_display_add(self):
        """更新所有列表显示"""
        #获取当前所选择的电铲
        selected_model = self.tabWidget_shovelSelect.currentWidget()
        #获取当前所选择的车辆
        current_tab = self.tabWidget.currentWidget()
        if current_tab:
            #多个时使用findChildren
            list_widget = current_tab.findChild(QListWidget)
            if list_widget:
                selected_vehicles = []
                for i in range(list_widget.count()):
                    item = list_widget.item(i)
                    if item.checkState() == Qt.CheckState.Checked:
                        selected_vehicles.append(item.text())
                        item.setText(f"{item.text()} - {self.tabWidget_shovelSelect.tabText(self.tabWidget_shovelSelect.currentIndex())}")
                        self.toggle_item_state(item)
                        
                # for item in list_widget.selectedItems():
                #     selected_vehicles.append(item.text())
                #     item.setText(f"{item.text()} - {self.tabWidget_shovelSelect.tabText(self.tabWidget_shovelSelect.currentIndex())}")
                #     self.toggle_item_state(item)
                #     time.sleep(0.1)  # 添加延时
        selected_model.findChild(QListWidget).addItems(selected_vehicles)
        

    def update_display_remove(self):
        pass
    
    def set_item_color(self, item, status):
        """根据状态设置颜色"""
        colors = {
            "待令": QColor(200, 200, 200),
            "运行中": QColor(144, 238, 144),
            "故障": QColor(255, 99, 71),
            "维修中": QColor(255, 165, 0)
        }
        item.setBackground(colors.get(status, QColor(255, 255, 255)))
    
    def assign_vehicle(self, shovel_id):
        """分配车辆到电铲"""
        selected_items = self.listWidget_vehicles.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "提示", "请先选择一辆车")
            return
        
        selected_text = selected_items[0].text()
        vehicle_id = selected_text.split(" - ")[0]
        
        # 找到对应的车辆数据
        for vehicle in self.vehicles:
            if vehicle['id'] == vehicle_id:
                if vehicle['shovel']:
                    QMessageBox.warning(self, "提示", "该车辆已分配给其他电铲")
                    return
                
                vehicle['shovel'] = shovel_id
                vehicle['status'] = "运行中"
                break
        
        self.update_display()
        QMessageBox.information(self, "成功", f"已分配车辆 {vehicle_id} 到电铲 {shovel_id}")
    
    def edit_vehicle_status(self, item):
        """设置车辆状态"""
        text = item.text()
        vehicle_id = text.split(" - ")[0]
        
        for vehicle in self.vehicles:
            if vehicle['id'] == vehicle_id:
                status, ok = QInputDialog.getItem(
                    self, "设置状态", "选择车辆状态:",
                    ["待令", "运行中", "故障", "维修中"], 0, False
                )
                
                if ok and status:
                    old_shovel = vehicle['shovel']
                    vehicle['status'] = status
                    
                    if status == "故障":
                        vehicle['shovel'] = None
                        if old_shovel:
                            QMessageBox.information(self, "提示", 
                                                  f"车辆 {vehicle_id} 设置为故障状态，已解除电铲分配")
                    
                    self.update_display()
                break
    
    # 切换单个项目的可选状态
    def toggle_item_state(self, item):
        
        if item.flags() & Qt.ItemFlag.ItemIsEnabled:
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            print(f"已禁用: {item.text()}")
        else:
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled)
            print(f"已启用: {item.text()}")        
    def record_save(self):
        pass