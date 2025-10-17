'''
Author: 李晓乐
Date: 2025-08-05 18:25:05
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-10-18 03:31:55
FilePath: \QT\报表生成\src\QT_Function_v2.py
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
from QT_shovel_plan import ShovelPlan
# from Report_Function import ReportGenerator
from pathlib import Path
import re
import time

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
        ui_path_main = (Path(__file__).parent.parent / "ui" / "main_v2.ui")
        self.ui_tab_example = (Path(__file__).parent.parent / "ui" / "tab_example.ui")
        style_path=(Path(__file__).parent.parent / "ui" / "Ubuntu.qss")
        self.style = load_stylesheet(style_path)
        self.ui_main=uic.loadUi(ui_path_main,self)
        self.ui_main.setStyleSheet(self.style)
        # 用作tab范本
        self.database=DatabaseManager()
        self.path_report=(Path(__file__).parent.parent / "log")
        self.init_shift_dic()        
        self.connectload()

        self.init_time()
        self.ui_main_update()
        self.statusbar=self.ui_main.statusbar
        
        
        
        #重定向
        # self.emitter=Emitter()
        # self.emitter.text_written.connect(self.update_status_bar)
        # sys.stdout = self.emitter
        self.ui_main.show()
        
    # 初始化班次控件字典
    def init_shift_dic(self):
        self.shifts = {
            
            "二班" : {
                    "tabWidget" : self.tabWidget_shift2, 
                    "dateEdit": self.dateEdit,
                    "lineEdit_foreman" : self.lineEdit_foreman,
                    "pushButton_save" : self.pushButton_save,
                    "lineEdit_shift" : self.lineEdit_shift_1,
                    "pushButton_distribution" : self.pushButton_distribution,
                    "pushButton_report" : self.pushButton_report_1,
                    "shovels_used" : {}
                    },
            
            "三班" : {
                    "tabWidget" : self.tabWidget_shift3, 
                    "dateEdit": self.dateEdit_2,
                    "lineEdit_foreman" : self.lineEdit_foreman_2,
                    "pushButton_save" : self.pushButton_save_2,
                    "lineEdit_shift" : self.lineEdit_shift_2,
                    "pushButton_distribution" : self.pushButton_distribution_2,
                    "pushButton_report" : self.pushButton_report_2,
                    "shovels_used" : {}
                    },
            
            "一班" : {
                    "tabWidget" : self.tabWidget_shift1, 
                    "dateEdit": self.dateEdit_3,
                    "lineEdit_foreman" : self.lineEdit_foreman_3,
                    "pushButton_save" : self.pushButton_save_3,
                    "lineEdit_shift" : self.lineEdit_shift_3,
                    "pushButton_distribution" : self.pushButton_distribution_3,
                    "pushButton_report" : self.pushButton_report_3,
                    "shovels_used" : {}
                    }
        }
                  
    #建立控件间的链接
    def connectload(self):
        self.action_2.triggered.connect(self.show_vehicle_manager)
        self.action.triggered.connect(self.show_vehicle_distribution)
        self.action_shovel_plan.triggered.connect(self.show_shovel_plan)
        for shift, info in self.shifts.items():
            info['pushButton_save'].clicked.connect(self.save_to_database)
            info['pushButton_distribution'].clicked.connect(self.show_vehicle_distribution)
            info['dateEdit'].dateChanged.connect(self.ui_main_update)
            # info['pushButton_report'].clicked.connect(self.generate_report,date=info['dateEdit'].date().toString("yyyy-MM-dd"),shift=shift)
            
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
    
    # 创建tab实例
    def create_new_tab(self):
        tab = QWidget()
        uic.loadUi(self.ui_tab_example, tab)
        return tab
    
    
    # 根据数据库更新界面
    def ui_main_update(self):         
        # 清空所有tab

        shovels = self.database.get_vehicle_data(vehicle_type="电铲", vehicle_available=1)        
                
        for shift, info in self.shifts.items():
            tabwidget = info['tabWidget']
            tabwidget.clear()  # 清空现有的标签页
            dateEdit = info['dateEdit']
            date = dateEdit.date().toString("yyyy-MM-dd")
            self.shifts[shift]['shovels_used'] = {}

            for shovel in shovels:
                # 检测是否使用该电铲
                
                is_used = self.database.get_vehicle_records(date = date, shovel_id=shovel['vehicle_number'], shift=shift)
                if is_used:
                    vehicle_available_count = len(is_used)
                    self.database.insert_shift_record(
                        date=date,
                        shift=shift,
                        shovel_id=shovel['vehicle_number'],
                        vehicle_available_count=vehicle_available_count
                    )
                    tab = self.create_new_tab()
                    tabwidget.addTab(tab, f"{shovel['vehicle_number']}")
                    self.shifts[shift]['shovels_used'][shovel['vehicle_number']] = tab                     
                    
                    # 获取数据
                    shift_datas = self.database.get_shift_records(date=date, shift=shift, shovel_id=shovel['vehicle_number'])
                    for shift_data in shift_datas:
                    # 若存在，则呈现在界面上
                        if shift_data:
                            info['lineEdit_foreman'].setText(shift_data['foreman']) 
                            tab.lineEdit_vehicle_count.setText(str(shift_data['vehicle_count']))
                            tab.lineEdit_operting_time.setText(str(shift_data['operating_time']))
                            tab.lineEdit_opertinglength.setText(str(shift_data['operating_length']))
                            tab.lineEdit_vehicle_available_count.setText(str(shift_data['vehicle_available_count']))
                            tab.lineEdit_production.setText(str(shift_data['production']))
                            tab.textEdit_dig.setPlainText(shift_data['loading_area_status'])
                            tab.textEdit_parkingandroad.setPlainText(shift_data['parkingandroad_area_status'])
                            tab.textEdit_dump.setPlainText(shift_data['unloading_area_status'])
                            tab.textEdit_opertingstatus.setPlainText(shift_data['operating_status'])
                            tab.textEdit_opertingstatus.textChanged.connect(lambda: self.on_text_changed(tab.textEdit_opertingstatus.toPlainText(), tab.lineEdit_operting_time))
                            tab.textEdit_other.setPlainText(shift_data['other_matters'])
                            tab.lineEdit_vehicle_available_count.setText(str(shift_data['vehicle_available_count']))
                            # 用于存储影响因素
                            info['lineEdit_shift'].setText(shift_data['operating_effect_factor'])


    # 保存界面数据至数据库
    def save_to_database(self):
        for shift, info in self.shifts.items():
            for shovel_id, elements in info['shovels_used'].items():
                date = info['dateEdit'].date().toString("yyyy-MM-dd")
                foreman = info['lineEdit_foreman'].text().strip()
                vehicle_count = elements.lineEdit_vehicle_count.text().strip()
                operating_time = elements.lineEdit_operting_time.text().strip()
                operating_length = elements.lineEdit_opertinglength.text().strip()
                vehicle_available_count = elements.lineEdit_vehicle_available_count.text().strip()
                production = elements.lineEdit_production.text().strip()
                daily_accumulated_production = self.get_daily_accumulated_production(shift.date)
                loading_area_status = elements.textEdit_dig.toPlainText().strip()
                parkingandroad_area_status = elements.textEdit_parkingandroad.toPlainText().strip()
                unloading_area_status = elements.textEdit_dump.toPlainText().strip()
                operating_status = elements.textEdit_opertingstatus.toPlainText().strip()
                other_matters = elements.textEdit_other.toPlainText().strip()
                operating_effect_factor = info['lineEdit_shift'].text().strip()
                self.database.insert_shift_record(
                    date=date,
                    shift=shift,
                    shovel_id=shovel_id,
                    foreman=foreman,                    
                    vehicle_count=int(vehicle_count) if vehicle_count.isdigit() else 0,
                    operating_time=float(operating_time) if operating_time.replace('.','',1).isdigit() else 0.0,
                    operating_length=float(operating_length) if operating_length.replace('.','',1).isdigit() else 0.0,
                    vehicle_available_count=int(vehicle_available_count) if vehicle_available_count.isdigit() else 0,
                    production=float(production) if production.replace('.','',1).isdigit() else 0.0,
                    daily_accumulated_production = float(daily_accumulated_production) if daily_accumulated_production.replace('.','',1).isdigit() else 0.0,
                    loading_area_status=loading_area_status,
                    parkingandroad_area_status=parkingandroad_area_status,
                    unloading_area_status=unloading_area_status,
                    operating_status=operating_status,
                    other_matters=other_matters,
                    operating_effect_factor=operating_effect_factor
                )

    # 加载车辆分配窗口
    def show_vehicle_distribution(self):
        window_vehicle_distribution = VehicleDistribution(self.database)
        window_vehicle_distribution.show()
        window_vehicle_distribution.pushButton.clicked.connect(self.ui_main_update)


    #加载车辆管理窗口    
    def show_vehicle_manager(self):
        window_vehicle_manager = VehicleManager(self.database)
    
    # 加载电铲计划窗口
    def show_shovel_plan(self):
        window_shovel_plan = ShovelPlan(self.database)
        
    # 报表生成
    def generate_report(self,date,shift):
        pass
        # report = ReportGenerator(self.database,date,shift,filename=self.path_report / f"{date}_{shift}_报表.xlsx")
        # QMessageBox.information(self, "提示", "报表生成中，敬请期待！")
        
    # 运行时长判断
    def on_text_changed(self, operating_status, destination):
        try:
            lines = operating_status.split('\n')
            total_minutes = 0
            for line in lines:
                if "安全员" in line:
                    time_match = re.match(r'(\d{2}:\d{2})-(\d{2}:\d{2})', line)
                    if time_match:
                        start = time_match.group(1)
                        end = time_match.group(2)
                        start_minutes = int(start[:2]) * 60 + int(start[3:])
                        end_minutes = int(end[:2]) * 60 + int(end[3:])
                        total_minutes += (end_minutes - start_minutes)
            total_hours = round(total_minutes / 60, 1)
            destination.setText(str(total_hours))
            return True
        except Exception as e:
            print(f"运行时长计算错误: {e}")
            return False
    # 更新状态栏显示    
    def update_status_bar(self, text):        
        self.statusbar.showMessage(text.strip())
        
    # 恢复标准输出    
    # def closeEvent(self, event):
    #     sys.stdout = sys.__stdout__
    #     super().closeEvent(event)