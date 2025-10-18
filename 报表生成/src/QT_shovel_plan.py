'''
Author: 李晓乐
Date: 2025-10-18 01:25:48
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-10-18 10:43:25
FilePath: \QT\报表生成\src\QT_shovel_plan.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTreeWidget,QTreeWidgetItem,
                            QCheckBox,QVBoxLayout,QWidget,)
from PyQt6.QtCore import Qt, QDate
from PyQt6 import uic
from pathlib import Path
import time

class ShovelPlan(QMainWindow):
    def __init__(self,database):
        super().__init__()
        # 加载 UI 文件
        ui_path = (Path(__file__).parent.parent / "ui" / "tab_example_plan.ui")
        style_path = (Path(__file__).parent.parent / "ui" / "Ubuntu.qss")
        self.ui=uic.loadUi(ui_path, self)
        with open(style_path, "r") as style_file:
            self.setStyleSheet(style_file.read())
        # 初始化变量
        self.database = database
        self.shovel_add()
        self.dateEdit.setDate(QDate.currentDate())
        self.update()
        self.dateEdit.dateChanged.connect(self.update)
        self.comboBox.currentIndexChanged.connect(self.update)
        self.pushButton.clicked.connect(self.save)
        self.show()
        
    def shovel_add(self):
        self.comboBox.clear()
        shovels = self.database.get_vehicle_data(vehicle_type="电铲",vehicle_available=1)
        if shovels:
            for shovel in shovels:
                self.comboBox.addItem(shovel['vehicle_number'])
            self.comboBox.setCurrentIndex(0)
            self.update()
        
    def update(self):
        date = self.dateEdit.date().toString("yyyy-MM-dd")
        shovel_number = self.comboBox.currentText()
        line_edit_dic={
            'daily_plan' : self.lineEdit_daily_plan,
            'daily_accumulated_production' : self.lineEdit_daily_accumulated_production,
            'daily_end' : self.lineEdit_daily_end,
            'monthly_plan' : self.lineEdit_monthly_plan,
            'monthly_accumulated_production' : self.lineEdit_monthly_accumulated_production,
            'monthly_end' : self.lineEdit_monthly_end,
            'monthly_end_per' : self.lineEdit_monthly_end_per,
            'yearly_accumulated_vehicle_count' : self.lineEdit_yearly_accumulated_vehicle_count,
            'yearly_accumulated_production' : self.lineEdit_yearly_accumulated_production,
            'yearly_accumulated_operating_time' : self.lineEdit_yearly_accumulated_operating_time,
        }
        datas = self.database.get_shift_records(date=date, shovel_id=shovel_number,shift="一班")
        for data in datas:
            if data:
                for key , line_edit in line_edit_dic.items():
                    if key == 'daily_end':
                        line_edit.setText(str(round(data['daily_accumulated_production'] - data['daily_plan'],4)))
                    elif key == 'monthly_end':
                        line_edit.setText(str(round(data['monthly_accumulated_production'] - data['monthly_plan'],4)))
                    elif key == 'monthly_end_per':
                        if data['monthly_plan'] != 0:
                            per = data['monthly_accumulated_production'] / data['monthly_plan'] * 100
                        else:
                            per = 0
                        line_edit.setText(f"{per:.2f}%")
                    else:
                        line_edit.setText(str(data[key]))
                        
    def save(self):
        date = self.dateEdit.date().toString("yyyy-MM-dd")
        shovel_number = self.comboBox.currentText()
        data_to_save = {
            'daily_plan' : float(self.lineEdit_daily_plan.text()) if self.lineEdit_daily_plan.text() else 0,
            'daily_accumulated_production' : float(self.lineEdit_daily_accumulated_production.text()) if self.lineEdit_daily_accumulated_production.text() else 0,
            'monthly_plan' : float(self.lineEdit_monthly_plan.text()) if self.lineEdit_monthly_plan.text() else 0,
            'monthly_accumulated_production' : float(self.lineEdit_monthly_accumulated_production.text()) if self.lineEdit_monthly_accumulated_production.text() else 0,
            'yearly_accumulated_vehicle_count' : float(self.lineEdit_yearly_accumulated_vehicle_count.text()) if self.lineEdit_yearly_accumulated_vehicle_count.text() else 0,
            'yearly_accumulated_production' : float(self.lineEdit_yearly_accumulated_production.text()) if self.lineEdit_yearly_accumulated_production.text() else 0,
            'yearly_accumulated_operating_time' : float(self.lineEdit_yearly_accumulated_operating_time.text()) if self.lineEdit_yearly_accumulated_operating_time.text() else 0,
        }
        self.database.update_shift_record(date=date, shovel_id=shovel_number, shift="一班", **data_to_save)
        self.update()