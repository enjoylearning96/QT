import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QListWidgetItem, QMessageBox,
                            QInputDialog, QCheckBox,QListWidget,QTabWidget,QWidget)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt, QDate, QTime
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
        
        # 初始化时间相关控件
        self.init_time_controls()

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
        
        for vehicle_data in self.database.get_vehicle_data(vehicle_type="矿卡-930E",vehicle_available=1):
            item = QListWidgetItem(f"{vehicle_data['vehicle_number']}")
            item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget_930E.addItem(item)
        for vehicle_data in self.database.get_vehicle_data(vehicle_type="矿卡-830E",vehicle_available=1):
            item = QListWidgetItem(f"{vehicle_data['vehicle_number']}")
            item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget_830E.addItem(item)
        for vehicle_data in self.database.get_vehicle_data(vehicle_type="矿卡-NTE330",vehicle_available=1):
            item = QListWidgetItem(f"{vehicle_data['vehicle_number']}")
            item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget_NTE330.addItem(item)
        for vehicle_data in self.database.get_vehicle_data(vehicle_type="矿卡-NTE360",vehicle_available=1):
            item = QListWidgetItem(f"{vehicle_data['vehicle_number']}")
            item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget_NTE360.addItem(item)
        for vehicle_data in self.database.get_vehicle_data(vehicle_type="矿卡-33900",vehicle_available=1):
            item = QListWidgetItem(f"{vehicle_data['vehicle_number']}")
            item.setCheckState(Qt.CheckState.Unchecked)
            self.listWidget_33900.addItem(item)

    def init_time_controls(self):
        """初始化时间相关控件"""
        self.dateEdit.setDate(QDate.currentDate())
        current_time = QTime.currentTime()
        if current_time < QTime(8, 30):
            self.comboBox.setCurrentIndex(2)
        elif current_time < QTime(16, 30):
            self.comboBox.setCurrentIndex(0)
        else:
            self.comboBox.setCurrentIndex(1)

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
        for shovel_id in self.selected_shovels:
            self.database.insert_shift_record(self, date = QDate.currentDate().toString("yyyy-MM-dd"),
                                              shift = self.comboBox.currentText(),, 
                                              shovel_id = shovel_id,
                                              vehicle_count = 0,
                                              production = 0)
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
        tabs=self.tabWidget.findChildren(QWidget)
        selected_vehicles = []
        for tab in tabs:
            #多个时使用findChildren
            list_widget = tab.findChild(QListWidget)
            if list_widget:                
                for i in range(list_widget.count()):
                    item = list_widget.item(i)
                    if item is not None and item.checkState() == Qt.CheckState.Checked:
                        selected_vehicles.append(f"{self.tabWidget.tabText(self.tabWidget.currentIndex())} - {item.text()}")
                        item.setText(f"{item.text()} - {self.tabWidget_shovelSelect.tabText(self.tabWidget_shovelSelect.currentIndex())}")
                        item.setCheckState(Qt.CheckState.Unchecked)
                        self.toggle_item_state(item)
        for item_data in selected_vehicles:
            item = QListWidgetItem(item_data)
            item.setCheckState(Qt.CheckState.Unchecked)
            selected_model.findChild(QListWidget).addItem(item)
            
            

    def update_display_remove(self):
        tabs=self.tabWidget_shovelSelect.findChildren(QWidget)
        selected_vehicles = []
        for tab in tabs:
            list_widget = tab.findChild(QListWidget)
            if list_widget:                
                # 从后往前遍历，避免索引变化
                for i in range(list_widget.count() - 1, -1, -1):
                    item = list_widget.item(i)
                    if item is not None and item.checkState() == Qt.CheckState.Checked:
                        selected_vehicles.append(item.text())
                        list_widget.takeItem(list_widget.row(item))
        for vehicle in selected_vehicles:
            vehicle_type = vehicle.split(" - ")[0]
            vehicle_number = vehicle.split(" - ")[1]
            for i in range(self.tabWidget.count()):
                tab = self.tabWidget.widget(i)
                if self.tabWidget.tabText(i) == vehicle_type:
                    list_widget = tab.findChild(QListWidget)
                    if list_widget:
                        for i in range(list_widget.count()):
                            item = list_widget.item(i)
                            if item.text().split(" - ")[0] == vehicle_number:
                                item.setText(f"{vehicle_number}")
                                self.toggle_item_state(item)

    # def set_item_color(self, item, status):
    #     """根据状态设置颜色"""
    #     colors = {
    #         "待令": QColor(200, 200, 200),
    #         "运行中": QColor(144, 238, 144),
    #         "故障": QColor(255, 99, 71),
    #         "维修中": QColor(255, 165, 0)
    #     }
    #     item.setBackground(colors.get(status, QColor(255, 255, 255)))
    
    def edit_vehicle_status(self, item):
        """设置车辆状态"""
        text = item.text()

        status_exist = 0
        try: 
            vehicle_number = text.split(" - ")[0]
            try:
                shovel_id = text.split(" - ")[1].split(" : ")[0]
                # 状态已存在
                status_exist = 1
            except:
                shovel_id = text.split(" - ")[1]
        except:
            vehicle_number = text
            shovel_id=None
        
        vehicle_status, ok = QInputDialog.getItem(
            self, "车辆状态", "选择车辆状态:",
            ["正常", "故障"], 0, False
        )
        if ok and vehicle_status == "故障":                   
            fault_type, ok = QInputDialog.getItem(
            self, "故障记录", "选择故障类型:",
            ["原车故障", "无人故障", "线控故障"], 0, False
            )
            if ok and fault_type:
                fault_description, ok = QInputDialog.getText(
                    self, "故障描述", "请输入故障描述:"
                )
                if ok and fault_description:
                    fault_duration,ok = QInputDialog.getDouble(
                        self, "故障时长", "请输入故障时长(小时):", 
                        value=0.0, min=0.0, max=8, decimals=2
                    )
                    
                    if ok:
                        # 若电铲存在，则工作时长等于班次工作时长减去故障时长
                        if shovel_id:
                            shift_operating_hours = 8.0
                            operating_hours = shift_operating_hours - fault_duration
                        else:
                            operating_hours = 0
                            
                        self.database.insert_vehicle_record(vehicle_number=vehicle_number, 
                                                                        date=QDate.currentDate().toString("yyyy-MM-dd"), 
                                                                        shovel_id=shovel_id, 
                                                                        vehicle_status=vehicle_status,
                                                                        vehicle_fault_type=fault_type, 
                                                                        vehicle_fault_description=fault_description,
                                                                        vehicle_fault_duration=fault_duration, 
                                                                        vehicle_operating_hours=0, 
                                                                        vehicle_production=0, 
                                                                        shift=self.comboBox.currentText())
                        if status_exist == 0:
                            item.setText(f"{item.text()} : {vehicle_status}")
        elif ok and vehicle_status == "正常":
            self.database.delete_vehicle_record(vehicle_number=vehicle_number, date=QDate.currentDate().toString("yyyy-MM-dd"), shift=self.comboBox.currentText())
            if status_exist == 1:
                # 如果状态已存在，去掉状态部分
                item.setText(f"{item.text().split(' : ')[0]}")

    # 切换单个项目的可选状态
    def toggle_item_state(self, item):
        
        # 判断当前 item 是否可勾选（即是否有 ItemIsUserCheckable 标志）
        if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
            # 设置为不可被勾选，但可被双击
            flags = item.flags()
            flags &= ~Qt.ItemFlag.ItemIsUserCheckable  # 取消可勾选
            item.setFlags(flags)
            print(f"已禁用: {item.text()}")
        else:
            # 设置为可被勾选
            flags = item.flags()
            flags |= Qt.ItemFlag.ItemIsUserCheckable  # 增加可勾选
            item.setFlags(flags)
            print(f"已启用: {item.text()}")
            
    #保存无故障车辆记录到数据库
    def record_save(self):
        tabs=self.tabWidget.findChildren(QWidget)
        for tab in tabs:
            #多个时使用findChildren
            list_widget = tab.findChild(QListWidget)
            if list_widget:                
                for i in range(list_widget.count()):
                    item = list_widget.item(i)
                    text = item.text()
                    try: 
                        vehicle_number = text.split(" - ")[0]
                        try:
                            shovel_id = text.split(" - ")[1].split(" : ")[0]
                            vehicle_status=text.split(" - ")[1].split(" : ")[1]
                            pass
                            # 若故障，则无需重复插入
                        except:
                            shovel_id = text.split(" - ")[1]
                            vehicle_status="运行"
                    except: 
                        vehicle_number = text
                        shovel_id=None
                        vehicle_status="待令"
                    self.database.insert_vehicle_record(vehicle_number=vehicle_number, 
                                                        date=QDate.currentDate().toString("yyyy-MM-dd"), 
                                                        shovel_id=shovel_id, 
                                                        vehicle_status=vehicle_status,
                                                        vehicle_operating_hours=0, 
                                                        vehicle_production=0, 
                                                        shift=self.comboBox.currentText())