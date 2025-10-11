import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDialog, QListWidgetItem, QMessageBox,QTreeWidget,QTreeWidgetItem,
                            QInputDialog, QCheckBox,QListWidget,QTabWidget,QVBoxLayout,QWidget, QMessageBox)
from PyQt6.QtGui import QColor,QDoubleValidator
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6 import uic
from pathlib import Path
import time

class CustomDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui=uic.loadUi(Path(__file__).parent.parent / "ui" / "error_report.ui", self)

class VehicleDistribution(QMainWindow):
    def __init__(self,database):
        super().__init__()
        # 加载 UI 文件
        ui_path = (Path(__file__).parent.parent / "ui" / "vehicle_distribution_v2.ui")
        style_path = (Path(__file__).parent.parent / "ui" / "Ubuntu.qss")
        self.ui=uic.loadUi(ui_path, self)
        with open(style_path, "r") as style_file:
            self.setStyleSheet(style_file.read())
        # 初始化变量
        self.database = database
        
        
        
        # 初始化电铲选择列表
        self.init_shovel_selection()

        
        # 初始化停车地点列表
        self.init_parking_locations()
        
        # 车辆列表字典
        self.vehicle_tree_widgets = {
            "矿卡-930E": self.treeWidget_930E,
            "矿卡-830E": self.treeWidget_830E,
            "矿卡-NTE330": self.treeWidget_NTE330,
            "矿卡-NTE360": self.treeWidget_NTE360,
            "矿卡-33900": self.treeWidget_33900
        }
        
        # 初始化时间相关控件
        self.init_time_controls()
        
        # 更新数据
        self.update_all()
        self.save_all_to_database()

        # 连接信号
        self.setup_connections()
        self.show()
    
    # 初始化电铲选择列表
    def init_shovel_selection(self):
        # 电铲列表字典
        self.shovel_list_widgets = {}
        
        self.tabWidget_shovelSelect.clear()
        shovel_optionss = self.database.get_vehicle_data(vehicle_type="电铲",vehicle_available=1)
        for option in shovel_optionss:
            
            # 添加标签页tab
            tab = QWidget()
            self.tabWidget_shovelSelect.addTab(tab, option['vehicle_number'])
            
            # 创建垂直布局并设置为标签页的布局
            layout = QVBoxLayout(tab)
            layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
            
            # 创建列表控件，命名与标签页文本保持一致
            list_widget = QListWidget()
            list_widget.setObjectName(f"listWidget_{option['vehicle_number']}")
            list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
            self.shovel_list_widgets[option['vehicle_number']] = list_widget
            # 将列表控件添加到布局中
            layout.addWidget(list_widget)

    # 初始化停车地点列表
    def init_parking_locations(self):
        self.parking_list_widgets = {}
        self.tabWidget_parkingSelect.clear()
        parking_locations = self.database.get_vehicle_data(vehicle_type="停车区域",vehicle_available=1)
        for location in parking_locations:
            # 添加标签页tab
            tab = QWidget()
            self.tabWidget_parkingSelect.addTab(tab, location['vehicle_number'])
            
            # 创建垂直布局并设置为标签页的布局
            layout = QVBoxLayout(tab)
            layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
            
            # 创建列表控件，命名与标签页文本保持一致
            list_widget = QListWidget()
            list_widget.setObjectName(f"listWidget_{location['vehicle_number']}")
            self.parking_list_widgets[location['vehicle_number']] = list_widget
            list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
            
            # 将列表控件添加到布局中
            layout.addWidget(list_widget)
            

    # 初始化时间相关控件
    def init_time_controls(self):
        self.dateEdit.setDate(QDate.currentDate())
        current_time = QTime.currentTime()
        if current_time < QTime(8, 30):
            self.comboBox.setCurrentIndex(2)
        elif current_time < QTime(16, 30):
            self.comboBox.setCurrentIndex(0)
        else:
            self.comboBox.setCurrentIndex(1)
    
    # 更新所有数据
    def update_all(self,according_to_time=False):
        # 根据数据库数据更新车辆分布
        according_to_time_exist = True
        for shovel in self.shovel_list_widgets.values():
            shovel.clear()
        for parking in self.parking_list_widgets.values():
            parking.clear()
         # 更新车辆列表
        for type,type_tree in self.vehicle_tree_widgets.items():
            vehicle_type = self.database.get_vehicle_data(vehicle_type=type, vehicle_available=1)
            type_tree.clear()
            for vehicle in vehicle_type:
                if according_to_time:
                    vehicle_data = self.database.get_vehicle_records(date=self.dateEdit.date().toString("yyyy-MM-dd"), 
                                                                    shift=self.comboBox.currentText(),
                                                                    vehicle_number=vehicle['vehicle_number'])
                    if not vehicle_data:
                        according_to_time_exist=False
                        vehicle_data = self.database.get_vehicle_lastestrecord(vehicle_number=vehicle['vehicle_number'])
                else:
                    vehicle_data = self.database.get_vehicle_lastestrecord(vehicle_number=vehicle['vehicle_number'])
                # 若有相关记录，则添加
                if vehicle_data:
                    # 状态栏更新                   
                    item = QTreeWidgetItem(type_tree)
                    item.setText(0, vehicle_data['vehicle_number'])
                    item.setText(1, vehicle_data['vehicle_status'])
                    item.setText(2, vehicle_data['shovel_id'])
                    item.setText(3, vehicle_data['vehicle_parking_location'])
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(0, Qt.CheckState.Unchecked)
                    # 电铲更新
                    if vehicle_data['shovel_id'] in self.shovel_list_widgets.keys():
                        item = QListWidgetItem()
                        item.setText(vehicle_data['vehicle_number'])
                        item.setCheckState(Qt.CheckState.Unchecked)
                        self.shovel_list_widgets[vehicle_data['shovel_id']].addItem(item)
                    # 停车地点更新
                    if vehicle_data['vehicle_parking_location'] in self.parking_list_widgets.keys():
                        item = QListWidgetItem()
                        item.setText(vehicle_data['vehicle_number'])
                        item.setCheckState(Qt.CheckState.Unchecked)
                        self.parking_list_widgets[vehicle_data['vehicle_parking_location']].addItem(item)
                # 若没有相关记录，则添加默认记录
                else:
                    item = QTreeWidgetItem(type_tree)
                    item.setText(0, vehicle['vehicle_number'])
                    item.setText(1, "未确认")
                    item.setText(2, "待令")
                    item.setText(3, "待确认")
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(0, Qt.CheckState.Unchecked)
        if according_to_time and not according_to_time_exist:
            QMessageBox.information(self, "提示", "所选时间和班次无数据，已切换为最新数据")
            self.save_all_to_database()
                        
    # 连接信号和槽
    def setup_connections(self):
        """连接信号和槽"""
        self.pushButton_2.clicked.connect(self.update_display_add)
        self.pushButton_3.clicked.connect(self.update_display_remove)
        self.pushButton.clicked.connect(self.save_all_to_database)
        for tree_widget in self.vehicle_tree_widgets.values():
            tree_widget.itemDoubleClicked.connect(self.edit_vehicle_status)
        self.pushButton_search.clicked.connect(lambda: self.update_all(according_to_time=True))
        
    #分配时上传所述电铲、停车区数据
    def update_display_add(self):
        #获取当前所选择的是电铲还是停车区
        selected_model = self.tabWidget_2.currentWidget()
        #获取当前所选择的车辆
        tabs=self.tabWidget.findChildren(QWidget)
        selected_vehicles = []
        for tab in tabs:
            #多个时使用findChildren
            tree_widget = tab.findChild(QTreeWidget)
            if tree_widget:
                selected_vehicles.extend(self.on_confirm_treeweight_selection(tree_widget))
        if selected_model == self.tab_shovel:  # 电铲
            # 确认当前所选择的具体电铲
            selected_shovel = self.tabWidget_shovelSelect.currentWidget()
            current_index = self.tabWidget_shovelSelect.currentIndex()
            # 提交数据库
            if True:
                for vehicle in selected_vehicles:
                    self.database.insert_vehicle_record(vehicle_number=vehicle,date=self.dateEdit.date().toString("yyyy-MM-dd"),
                                                        shovel_id=self.tabWidget_shovelSelect.tabText(current_index),shift=self.comboBox.currentText())
                self.update_all()
        elif selected_model == self.tab_parking:  # 停车区
            # 确认当前所选择的具体停车区
            selected_parking = self.tabWidget_parkingSelect.currentWidget()
            current_index = self.tabWidget_parkingSelect.currentIndex()
            # 提交数据库
            if True:
                for vehicle in selected_vehicles:
                    self.database.insert_vehicle_record(vehicle_number=vehicle,
                                                        date=self.dateEdit.date().toString("yyyy-MM-dd"),
                                                        vehicle_parking_location=self.tabWidget_parkingSelect.tabText(current_index),
                                                        shift=self.comboBox.currentText())
                self.update_all()
        return True
                                          
    # 遍历treeweight中所有被勾选的节点
    def on_confirm_treeweight_selection(self, tree_widget):
        selected_vehicles = []
        root = tree_widget.invisibleRootItem()
        # 首先遍历一级节点，
        for i in range(root.childCount()):
            top_level_item = root.child(i)
            # 若被勾选则添加所有子节点
            if top_level_item.checkState(0) == Qt.CheckState.Checked:
                selected_vehicles.append(top_level_item.text(0))
        return selected_vehicles
            
    #移除时上传所述电铲、停车区数据
    def update_display_remove(self):
        #获取当前所选择的是电铲还是停车区
        selected_model = self.tabWidget_2.currentWidget()
        if selected_model == self.tab_shovel:  # 电铲
            for i in range(self.tabWidget_shovelSelect.count()):
                list_widget = self.tabWidget_shovelSelect.widget(i).findChild(QListWidget)
                if list_widget:
                    for item in list_widget.selectedItems():
                        vehicle_number = item.text()
                        self.database.insert_vehicle_record(vehicle_number=vehicle_number, 
                                                            date=self.dateEdit.date().toString("yyyy-MM-dd"), 
                                                            shovel_id = "待令",
                                                            shift=self.comboBox.currentText())
            self.update_all()
        elif selected_model == self.tab_parking:  # 停车区
            for i in range(self.tabWidget_parkingSelect.count()):
                list_widget = self.tabWidget_parkingSelect.widget(i).findChild(QListWidget)
                if list_widget:
                    for i in range(list_widget.count()):
                        item = list_widget.item(i)
                        if item and item.checkState() == Qt.CheckState.Checked:
                            vehicle_number = item.text()
                            self.database.insert_vehicle_record(vehicle_number=vehicle_number, 
                                                                date=self.dateEdit.date().toString("yyyy-MM-dd"), 
                                                                vehicle_parking_location = "待确认",
                                                            shift=self.comboBox.currentText())
            self.update_all()
        return True
        #获取当前所选择的车辆
    
    # 设置车辆状态
    def edit_vehicle_status(self, item):
        
        dialog = CustomDialog(self)
        double_validator = QDoubleValidator(0.0, 8.0, 2)  # 范围 0.0-8.0，小数点后2位
        dialog.lineEdit_2.setValidator(double_validator)
        def on_accept():
            self.database.insert_vehicle_record(vehicle_number=item.text(0),
                                                date=self.dateEdit.date().toString("yyyy-MM-dd"),
                                                vehicle_status=dialog.comboBox.currentText(), 
                                                vehicle_fault_type=dialog.comboBox.currentText(),
                                                vehicle_fault_description=dialog.lineEdit.text(),
                                                vehicle_fault_solution=dialog.textEdit.toPlainText(), 
                                                vehicle_fault_duration=dialog.lineEdit_2.text(),
                                                shift=self.comboBox.currentText())
            self.update_all()
            dialog.close()
        dialog.buttonBox.accepted.connect(on_accept)
        
        dialog.buttonBox.rejected.connect(dialog.close)
        dialog.exec()

    # 将ui所有信息上传到数据库，防止引用最新且非当前数据时未进行调制的部分没有数据上传
    # 只需将车辆状态上传即可完成覆盖
    def save_all_to_database(self):
        for type,type_tree in self.vehicle_tree_widgets.items():
            root = type_tree.invisibleRootItem()
            for i in range(root.childCount()):
                top_level_item = root.child(i)
                self.database.insert_vehicle_record(vehicle_number=top_level_item.text(0),
                                                    date=self.dateEdit.date().toString("yyyy-MM-dd"),
                                                    vehicle_status=top_level_item.text(1),
                                                    shovel_id=top_level_item.text(2),
                                                    vehicle_parking_location=top_level_item.text(3),
                                                    shift=self.comboBox.currentText())
        self.update_all()
        

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
            