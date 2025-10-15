'''
Author: 李晓乐
Date: 2025-08-05 18:25:05
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-10-12 23:04:38
FilePath: \QT\报表生成\src\QT_Function.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox,QTabWidget, QDateEdit, QTextEdit,QWidget,QVBoxLayout
from PyQt6.QtCore import QObject, pyqtSignal, QDate, QTime
from PyQt6 import uic
from Database_Function import DatabaseManager
from QT_vehicle_distribution_v2 import VehicleDistribution
from QT_vehicle_manager import VehicleManager
from pathlib import Path

# 自定义一个继承自QObject的类，用于重定向stdout
# class Emitter(QObject):
#     text_written = pyqtSignal(str)  # 定义一个信号，用于传递文本

#     def write(self, text):
#         self.text_written.emit(text) 
#     def flush(self):
#         pass  
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
        self.database=DatabaseManager()        
        self.connectload()
        self.init_time()
        self.ui_main_update()
        self.statusbar=self.ui_main.statusbar
        
        #重定向
        # self.emitter=Emitter()
        # self.emitter.text_written.connect(self.update_status_bar)
        # sys.stdout = self.emitter
        self.ui_main.show()
        
    
    #建立控件间的链接
    def connectload(self):
        self.action_2.triggered.connect(self.show_vehicle_manager)
        self.action.triggered.connect(self.show_vehicle_distribution)
        self.pushButton.clicked.connect(self.show_vehicle_distribution)
        self.pushButton_2.clicked.connect(self.show_vehicle_distribution)
        self.pushButton_5.clicked.connect(self.show_vehicle_distribution)
        
    
    #初始化时间
    def init_time(self):
        current_time = QTime.currentTime()
        # 若为一班，二班三班时间应为昨天
        if current_time < QTime(8, 30):
            self.dateEdit_2.setDate(QDate.currentDate().addDays(-1))
            self.dateEdit.setDate(QDate.currentDate().addDays(-1))
            self.dateEdit_3.setDate(QDate.currentDate())
        else:
            self.dateEdit_2.setDate(QDate.currentDate())
            self.dateEdit.setDate(QDate.currentDate())
            self.dateEdit_3.setDate(QDate.currentDate())
            
    # 初始化创建/根据数据库更新界面
    def ui_main_update(self):         
        # 清空所有tab

        shovels = self.database.get_vehicle_data(vehicle_type="电铲", vehicle_available=1)
        
        self.shifts = {
            
            "二班" : {
                    "tabWidget" : self.tabWidget_shift2, 
                    "dateEdit": self.dateEdit,
                    "lineEdit_foreman" : self.lineEdit_foreman,
                    "lineEdit_production" : self.lineEdit__production,
                    "lineEdit_vehicle_count" : self.lineEdit_vehicle_count,
                    "textEdit_dig" : self.textEdit_dig,
                    "textEdit_dump" : self.textEdit_dump,
                    "textEdit_parkingandroad" : self.textEdit_parkingandroad,
                    "textEdit_other" : self.textEdit_other,
                    "lineEdit_shift" : self.lineEdit_shift_1,
                    "pushButton_save" : self.pushButton_save,
                    },
            
            "三班" : {
                    "tabWidget" : self.tabWidget_shift3, 
                    "dateEdit": self.dateEdit_2,
                    "lineEdit_foreman" : self.lineEdit_foreman_2,
                    "lineEdit_production" : self.lineEdit__production_2,
                    "lineEdit_vehicle_count" : self.lineEdit_vehicle_count_2,
                    "textEdit_dig" : self.textEdit_dig_2,
                    "textEdit_dump" : self.textEdit_dump_2,
                    "textEdit_parkingandroad" : self.textEdit_parkingandroad_2,
                    "textEdit_other" : self.textEdit_other_2,
                    "lineEdit_shift" : self.lineEdit_shift_2,
                    "pushButton_save" : self.pushButton_save_2,
                    },
            
            "一班" : {
                    "tabWidget" : self.tabWidget_shift1, 
                    "dateEdit": self.dateEdit_3,
                    "lineEdit_foreman" : self.lineEdit_foreman_3,
                    "lineEdit_production" : self.lineEdit__production_3,
                    "lineEdit_vehicle_count" : self.lineEdit_vehicle_count_3,
                    "textEdit_dig" : self.textEdit_dig_3,
                    "textEdit_dump" : self.textEdit_dump_3,
                    "textEdit_parkingandroad" : self.textEdit_parkingandroad_3,
                    "textEdit_other" : self.textEdit_other_3,
                    "lineEdit_shift" : self.lineEdit_shift_3,
                    "pushButton_save" : self.pushButton_save_3,
                    }
        }
        
        
        for shift, info in self.shifts.items():
            tabwidget = info['tabWidget']
            tabwidget.clear()  # 清空现有的标签页
            dateEdit = info['dateEdit']
            date = dateEdit.date().toString("yyyy-MM-dd")
            production = ""
            vehicle_count = ""
            shovelss = {}

            for shovel in shovels:
                # 检测是否使用该电铲
                
                is_used = self.database.get_vehicle_records(date = date, shovel_id=shovel['vehicle_number'], shift=shift)
                if is_used:
                    shovelss[shovel['vehicle_number']] = {}
                    tab = QWidget()
                    tabwidget.addTab(tab, shovel['vehicle_number'])
                    # 创建垂直布局并设置为标签页的布局
                    layout = QVBoxLayout(tab)
                    layout.setContentsMargins(0, 0, 0, 0)  
                    # 移除边距
                    # 创建QTextEdit并添加到布局中
                    plain_text_edit = QTextEdit()
                    layout.addWidget(plain_text_edit)
                    tab.setLayout(layout)
                    
                    shovelss[shovel['vehicle_number']]['plain_text_edit'] = plain_text_edit
                    # 获取数据
                    shift_data = self.database.get_shift_records(date=date, shift=shift, shovel_id=shovel['vehicle_number'])
                    # 若存在，则呈现在界面上
                    if shift_data:
                        info['lineEdit_foreman'].setText(shift_data['foreman']) 
                        info['lineEdit_production'].setText(str(shift_data['production']))
                        production += str(shift_data['production']) + " "
                        vehicle_count += str(shovel['vehicle_count']) + " "
                        # 现场情况，每个电铲都上传所有数据
                        info['textEdit_dig'].setPlainText(shift_data['loading_area_status'])
                        info['textEdit_dump'].setPlainText(shift_data['unloading_area_status'])
                        info['textEdit_parkingandroad'].setPlainText(shift_data['transportation_area_status'])
                        info['textEdit_other'].setPlainText(shift_data['other_matters'])
                        # 用于存储影响因素
                        info['lineEdit_shift'].setText(shift_data['vehicle_status'])
                        # 用于存储具体生产状况
                        plain_text_edit.setPlainText(shift_data['standby_area_status'])

                    info['lineEdit_vehicle_count'].setText(vehicle_count)
                    info['lineEdit_production'].setText(production)
            info['shovelss'] = shovelss

    # 保存界面数据至数据库
    def save_to_database(self):
        for shift, info in self.shifts.items():
            i=0
            for shovel_id, elements in info[shovelss].items():
                date = info['dateEdit'].date().toString("yyyy-MM-dd")
                foreman = info['lineEdit_foreman'].text().strip()
                production = info['lineEdit_production'].text().split()[i].strip()  # 取第一个电铲的产量
                vehicle_count = info['lineEdit_vehicle_count'].text().split()[i].strip()  # 取第一个电铲的车辆数
                loading_area_status = info['textEdit_dig'].toPlainText().strip()
                unloading_area_status = info['textEdit_dump'].toPlainText().strip()
                transportation_area_status = info['textEdit_parkingandroad'].toPlainText().strip()
                other_matters = info['textEdit_other'].toPlainText().strip()
                vehicle_status = info['lineEdit_shift'].text().strip()
                standby_area_status = elements['plain_text_edit'].toPlainText().strip()
                self.database.insert_shift_record(
                    date=date,
                    shift=shift,
                    shovel_id=shovel_id,
                    vehicle_count=int(vehicle_count) if vehicle_count.isdigit() else 0,
                    production=float(production) if self.is_float(production) else 0.0,
                    loading_area_status=loading_area_status,
                    unloading_area_status=unloading_area_status,
                    transportation_area_status=transportation_area_status,
                    other_matters=other_matters,
                    foreman=foreman,
                    vehicle_status=vehicle_status,
                    standby_area_status=standby_area_status
                )

    # 加载车辆分配窗口
    def show_vehicle_distribution(self):
        window_vehicle_distribution = VehicleDistribution(self.database)
        window_vehicle_distribution.show()
        window_vehicle_distribution.pushButton.clicked.connect(self.ui_main_update)


    #加载车辆管理窗口    
    def show_vehicle_manager(self):
        window_vehicle_manager = VehicleManager(self.database)
        window_vehicle_manager.show()
    # 更新状态栏显示    
    def update_status_bar(self, text):        
        self.statusbar.showMessage(text.strip())
        
    # 恢复标准输出    
    # def closeEvent(self, event):
    #     sys.stdout = sys.__stdout__
    #     super().closeEvent(event)