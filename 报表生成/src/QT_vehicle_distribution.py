import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QListWidgetItem, QMessageBox,
                            QInputDialog, QCheckBox)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from PyQt6 import uic

class ShovelWidget(QCheckBox):
    """自定义电铲选择复选框"""
    def __init__(self, shovel_id, parent=None):
        super().__init__(f"电铲 {shovel_id}", parent)
        self.shovel_id = shovel_id

class VehicleDistribution(QMainWindow):
    def __init__(self,current_shift,shovel_options):
        super().__init__()
        # 加载 UI 文件
        ui_path = (Path(__file__).parent.parent / "ui" / "vehicle_distribution.ui")
        style_path = (Path(__file__).parent.parent / "ui" / "Ubuntu.qss")
        uic.loadUi(ui_path, self)
        with open(style_path, "r") as style_file:
            self.setStyleSheet(style_file.read())
        # 初始化变量
        self.current_shift = current_shift
        self.shovel_options = shovel_options
        self.selected_shovels = []   # 选中的电铲列表
        self.shovel_widgets = {}     # 电铲组件字典
        self.vehicles = self.load_vehicle_data()
        
        # 初始化电铲选择列表
        self.init_shovel_selection()
        
        # 连接信号
        self.setup_connections()
        
        # 初始更新显示
        self.update_display()
    
    def init_shovel_selection(self):
        """初始化电铲选择列表"""
        # 清空现有选项
        self.listWidget_shovelSelect.clear()
        
        # 添加电铲选项
        for option in self.shovel_options:
            item = QListWidgetItem(option)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget_shovelSelect.addItem(item)
    
    def setup_connections(self):
        """连接信号和槽"""
        self.pushButton_confirmShovel.clicked.connect(self.on_confirm_shovel_selection)
        self.comboBox_filter.currentTextChanged.connect(self.update_display)
        self.listWidget_vehicles.itemDoubleClicked.connect(self.edit_vehicle_status)
    
    def on_confirm_shovel_selection(self):
        """确认电铲选择"""
        selected_shovels = []
        
        # 获取选中的电铲
        for i in range(self.listWidget_shovelSelect.count()):
            item = self.listWidget_shovelSelect.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                shovel_id = item.text().replace("电铲", "")  # 提取数字
                selected_shovels.append(shovel_id)

        if not selected_shovels:
            QMessageBox.warning(self, "提示", "请至少选择一个电铲")
            return
        
        self.selected_shovels = selected_shovels
        self.create_shovel_widgets()
        self.update_display()
    
    def create_shovel_widgets(self):
        """创建选中的电铲组件"""
        # 清空现有电铲组件
        self.clear_shovel_widgets()
        
        # 创建新的电铲组件
        for shovel_id in self.selected_shovels:
            self.create_single_shovel_widget(shovel_id)
    
    def clear_shovel_widgets(self):
        """清空所有电铲组件"""
        for shovel_id in list(self.shovel_widgets.keys()):
            widget = self.shovel_widgets.pop(shovel_id)
            widget.deleteLater()
    
    def create_single_shovel_widget(self, shovel_id):
        """创建单个电铲组件"""
        from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QListWidget, QPushButton
        
        # 创建电铲组
        shovel_group = QGroupBox(f"电铲 {shovel_id}")
        layout = QVBoxLayout()
        
        # 车辆列表
        vehicle_list = QListWidget()
        vehicle_list.setFixedHeight(120)
        vehicle_list.setObjectName(f"shovel{shovel_id}_list")
        
        # 分配按钮
        assign_btn = QPushButton("↑ 分配选中车辆")
        assign_btn.clicked.connect(lambda checked, s_id=shovel_id: self.assign_vehicle(s_id))
        
        layout.addWidget(vehicle_list)
        layout.addWidget(assign_btn)
        shovel_group.setLayout(layout)
        
        # 添加到布局和字典
        self.shovelContainerLayout.addWidget(shovel_group)
        self.shovel_widgets[shovel_id] = {
            'group': shovel_group,
            'list': vehicle_list,
            'button': assign_btn
        }
    
    def load_vehicle_data(self):
        """加载车辆数据"""
        return [
            {"id": "V001", "model": "卡车A", "status": "待令", "shovel": None},
            {"id": "V002", "model": "卡车A", "status": "待令", "shovel": None},
            {"id": "V003", "model": "卡车B", "status": "待令", "shovel": None},
            {"id": "V004", "model": "卡车C", "status": "待令", "shovel": None},
            {"id": "V005", "model": "卡车C", "status": "待令", "shovel": None},
            {"id": "V006", "model": "卡车A", "status": "运行中", "shovel": "1"},
            {"id": "V007", "model": "卡车B", "status": "运行中", "shovel": "2"},
            {"id": "V008", "model": "卡车A", "status": "故障", "shovel": None},
            {"id": "V009", "model": "卡车B", "status": "维修中", "shovel": "3"}
        ]
    
    def update_display(self):
        """更新所有列表显示"""
        # 清空车辆列表
        self.listWidget_vehicles.clear()
        
        # 清空所有电铲列表
        for shovel_data in self.shovel_widgets.values():
            shovel_data['list'].clear()
        
        selected_model = self.comboBox_filter.currentText()
        
        for vehicle in self.vehicles:
            text = f"{vehicle['id']} - {vehicle['model']} - {vehicle['status']}"
            
            if vehicle['shovel'] in self.selected_shovels:
                # 已分配到当前选择的电铲
                shovel_data = self.shovel_widgets.get(vehicle['shovel'])
                if shovel_data:
                    item = QListWidgetItem(text)
                    self.set_item_color(item, vehicle['status'])
                    shovel_data['list'].addItem(item)
            elif selected_model == "所有型号" or vehicle['model'] == selected_model:
                # 未分配或分配到其他电铲的车辆
                item = QListWidgetItem(text)
                self.set_item_color(item, vehicle['status'])
                self.listWidget_vehicles.addItem(item)
    
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VehicleSystem()
    window.show()
    sys.exit(app.exec())