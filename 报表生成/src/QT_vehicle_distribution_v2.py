import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QListWidgetItem, QMessageBox,QTreeWidget,QTreeWidgetItem,
                            QInputDialog, QCheckBox,QListWidget,QTabWidget,QVBoxLayout,QWidget, QMessageBox)
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
        
        # 初始化车辆列表
        self.vehicle_tree_widgets = {
            "矿卡-930E": self.treeWidget_930E,
            "矿卡-830E": self.treeWidget_830E,
            "矿卡-NTE330": self.treeWidget_NTE330,
            "矿卡-NTE360": self.treeWidget_NTE360,
            "矿卡-33900": self.treeWidget_33900
        }
        self.init_vehicle_list()
        
        # 初始化时间相关控件
        self.init_time_controls()
        
        # 更新数据
        self.update_all()

        # 连接信号
        self.setup_connections()
               
        self.ui.show()
    
    # 初始化电铲选择列表
    def init_shovel_selection(self):
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
            
            # 将列表控件添加到布局中
            layout.addWidget(list_widget)
            

    # 初始化车辆列表
    def init_vehicle_list(self):
        types = ["矿卡-930E","矿卡-830E","矿卡-NTE330","矿卡-NTE360","矿卡-33900"]
        for type in types:
            vehicle_data = self.database.get_vehicle_data(vehicle_type=type, vehicle_available=1)
            for vehicle in vehicle_data:
                self.vehicle_tree_widgets[type].clear()
                item = QTreeWidgetItem(self.vehicle_tree_widgets[type])
                item.setText(0, vehicle['vehicle_number'])
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(0, Qt.CheckState.Unchecked)

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
        self.update_distribution()
        self.update_status()
        
        # 根据数据库数据更新车辆分布
        def update_distribution(self):
            shovel_ok= False
            parking_ok=False
            def update_distribution_shovel(self):
                # 清空各电铲所属车辆
                # 添加所属车辆
                for shovel_tab in self.tabWidget_shovelSelect.findChildren(QWidget):
                    shovel_list_widget = shovel_tab.findChild(QListWidget)
                    if shovel_list_widget:
                        if according_to_time:
                            vehicles_data = self.database.get_vehicle_record(date=self.dateEdit.date().toString("yyyy-MM-dd"), 
                                                                            shift=self.comboBox.currentText(),
                                                                            shovel_id=shovel_tab.objectName())
                            if not vehicles_data:
                                # 弹出提示框
                                QMessageBox.warning(
                                    self,
                                    '警告',
                                    '未找到指定日期和班次的车辆分配记录，默认加载最新记录！',
                                    QMessageBox.StandardButton.Yes
                                )
                                vehicles_data = self.database.get_vehicle_lastestrecord(shovel_id=shovel_tab.objectName())
                        else:
                            vehicles_data = self.database.get_vehicle_lastestrecord(shovel_id=shovel_tab.objectName())
                        if vehicles_data:
                            shovel_list_widget.clear()
                            for vehicle in vehicles_data:
                                item = QListWidgetItem()
                                item.setText(vehicle['vehicle_number'])
                                item.setCheckState(Qt.CheckState.Unchecked)
                                shovel_list_widget.addItem(item)
                return True
            shovel_ok=update_distribution_shovel()
            
            def update_distribution_parking(self):
                # 清空各停车地点所属车辆
                for parking_tab in self.tabWidget_parkingSelect.findChildren(QWidget):
                    parking_list_widget = parking_tab.findChild(QListWidget)
                    if parking_list_widget:
                        if according_to_time:
                            vehicles_data = self.database.get_vehicle_record(date=self.dateEdit.date().toString("yyyy-MM-dd"), 
                                                                            shift=self.comboBox.currentText(),
                                                                            vehicle_parking_location=parking_tab.objectName())
                            if not vehicles_data:
                                # 弹出提示框
                                QMessageBox.warning(
                                    self,
                                    '警告',
                                    '未找到指定日期和班次的车辆分配记录，默认加载最新记录！',
                                    QMessageBox.StandardButton.Yes
                                )
                                vehicles_data = self.database.get_vehicle_lastestrecord(vehicle_parking_location=parking_tab.objectName())
                        else:
                            vehicles_data = self.database.get_vehicle_lastestrecord(vehicle_parking_location=parking_tab.objectName())                    
                        if vehicles_data:
                            parking_list_widget.clear()
                            for vehicle in vehicles_data:
                                item = QListWidgetItem()
                                item.setText(vehicle['vehicle_number'])
                                item.setCheckState(Qt.CheckState.Unchecked)
                                parking_list_widget.addItem(item)                        
                return True
            parking_ok=update_distribution_parking()
            if shovel_ok and parking_ok:
                return True
            else:
                return False

        # 更新状态栏
        def update_status(self):
            for type,type_tree in vehicle_tree_widgets.items():
                if according_to_time:
                    vehicles_data = self.database.get_vehicle_record(date=self.dateEdit.date().toString("yyyy-MM-dd"), 
                                                                    shift=self.comboBox.currentText(),
                                                                    type=type)
                    if not vehicles_data:
                        # 弹出提示框
                        QMessageBox.warning(
                            self,
                            '警告',
                            '未找到指定日期和班次的车辆分配记录，默认加载最新记录！',
                            QMessageBox.StandardButton.Yes
                        )
                        vehicles_data = self.database.get_vehicle_lastestrecord(type=type)
                else:
                    vehicles_data = self.database.get_vehicle_lastestrecord(type=type) 
                if vehicles_data:
                    type_tree.clear()
                    for vehicle in vehicles_data:
                        item = QTreeWidgetItem(type_tree)
                        item.setText(0, vehicle['vehicle_number'])
                        item.setText(1, vehicle['vehicle_status'])
                        item.setText(2, vehicle['shovel_id'])
                        item.setText(3, vehicle['vehicle_parking_location'])
                        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                        item.setCheckState(0, Qt.CheckState.Unchecked)
                        


    def setup_connections(self):
        """连接信号和槽"""
        self.pushButton_2.clicked.connect(self.update_display_add)
        self.pushButton_3.clicked.connect(self.update_display_remove)
        self.pushButton.clicked.connect(self.update_all)
        for i in range(self.tabWidget.count()):
            tab = self.tabWidget.widget(i)  # 获取标签页            
            # 在标签页中查找所有的 ListWidget
            for tree_widget in tab.findChildren(QTreeWidget):
                tree_widget.itemDoubleClicked.connect(self.edit_vehicle_status)


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
            # 提交数据库
            if selected_shovel:
                for vehicle in selected_vehicles:
                    self.database.insert_vehicle_record(vehicle_number=vehicle,date=dateEdit.date().toString("yyyy-MM-dd"),
                                                        shovel_id=selected_shovel.objectName(),shift=self.comboBox.currentText())
                self.update_all()
        elif selected_model == self.tab_parking:  # 停车区
            # 确认当前所选择的具体停车区
            selected_parking = self.tabWidget_parkingSelect.currentWidget()
            # 提交数据库
            if selected_parking:
                for vehicle in selected_vehicles:
                    self.database.insert_vehicle_record(vehicle_number=vehicle,
                                                        date=dateEdit.date().toString("yyyy-MM-dd"),
                                                        vehicle_parking_location=selected_parking.objectName(),
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
                for j in range(top_level_item.childCount()):
                    child_item = top_level_item.child(j)
                    selected_vehicles.append(child_item.text(0))
            # 若为被勾选则遍历二级节点，若被勾选则添加该节点
            else:
                for j in range(top_level_item.childCount()):
                    child_item = top_level_item.child(j)
                    if child_item.checkState(0) == Qt.CheckState.Checked:
                        selected_vehicles.append(child_item.text(0))
        return selected_vehicles
            
        

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
                    for item in list_widget.selectedItems():
                        vehicle_number = item.text()
                        self.database.insert_vehicle_record(vehicle_number=vehicle_number, 
                                                            date=self.dateEdit.date().toString("yyyy-MM-dd"), 
                                                            vehicle_parking_location = "待确认",
                                                            shift=self.comboBox.currentText())
            self.update_all()
        return True
        #获取当前所选择的车辆

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
            