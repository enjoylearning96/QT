# QTfunction.py
import pandas as pd
from PyQt6.QtWidgets import QFileDialog
from openpyxl import Workbook


class QTFunctions:
    def __init__(self):
        self.df = pd.DataFrame(columns=['参数', '一班', '二班', '三班', '总计'])  # 初始化DataFrame

    def select_excel_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(None, "选择Excel文件", "", "Excel Files (*.xlsx *.xls);;All Files (*)", options=options)
        return file_name

    def read_excel_to_dataframe(self, file_path):
        try:
            self.df = pd.read_excel(file_path)  # 读取Excel到DataFrame
            return True
        except FileNotFoundError:
            print("文件未找到")
            return False
        except Exception as e:
            print(f"读取Excel文件出错: {e}")
            return False


    def add_data_to_dataframe(self, param_key, value, class_column='一班'): # 添加数据到DataFrame, 默认添加到'一班'列
        new_row = pd.DataFrame({'参数': [param_key], class_column: [value], '二班': [0], '三班': [0], '总计': [value]})
        self.df = pd.concat([self.df, new_row], ignore_index=True)


    def save_dataframe_to_excel(self, file_path):
        try:
            self.df.to_excel(file_path, index=False)  # 保存DataFrame到Excel，不保存索引
            return True
        except Exception as e:
            print(f"保存Excel文件出错: {e}")
            return False