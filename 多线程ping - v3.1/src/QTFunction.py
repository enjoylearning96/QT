'''
Author: 李晓乐
Date: 2025-03-29 22:28:49
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-04-28 13:27:26
FilePath: \多线程ping - v3.1\QTFunction.py
Description: UI界面相关操作

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''

from time import sleep
from PyQt6.QtCore import Qt,QThread, pyqtSignal
from PyQt6.QtGui import QIcon,QDoubleValidator
from PyQt6.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem,QMainWindow,QLabel,QVBoxLayout
from PyQt6 import uic
from YamlFunction import read_yaml,write_yaml
from Function import ping_action

class Worker(QThread):
    update_signal = pyqtSignal(str)  

    def __init__(self, thread_id,ping_name,ping_ip,waittime,loggingStatus):
        super().__init__()
        self.thread_id = thread_id
        self.ping_name=ping_name
        self.ping_ip=ping_ip
        self.waittime=waittime
        self.loggingStatus=loggingStatus
        self.is_running = True  

    def run(self):
        while self.is_running:
            ping_return=ping_action(self.ping_name,self.ping_ip,self.loggingStatus)
            update_content = f"线程 {self.thread_id}:{ping_return}"            
            self.update_signal.emit(update_content)
            sleep(float(self.waittime))

    def stop(self):
        self.update_signal.emit(f"线程 {self.thread_id}: " )
        self.is_running = False 
        
        
        
class DynamicUI(QMainWindow):
    
    def __init__(self,targetuiFile,targetparaFile):
        super(DynamicUI, self).__init__()
        
        self.ui=uic.loadUi(targetuiFile,self)
        
        parameterConfiguration=read_yaml(targetparaFile)
        self.title=parameterConfiguration["title"]
        
        self.myTreeWidget=self.init_treewidget("cheliangxinxicunchu",self.title)
        
        for key in parameterConfiguration["database"]:
            Type1=self.addAFirstLevelNode(self.myTreeWidget,str(key),0)
            for key2 in parameterConfiguration["database"][key]:
                self.addASecondLevelNode(
                    Type1,parameterConfiguration["database"][key][key2]["status"],
                    str(key2),
                    parameterConfiguration["database"][key][key2]["ip"]
                    )
        self.Button_begin.clicked.connect(self.ping_start)
        self.Button_stop.clicked.connect(self.ping_stop)#注意connect（）内不要加括号
        self.lineEdit_jiange.setText("1")
        self.lineEdit_jiange.setValidator(QDoubleValidator())
        self.lineEdit_jiange.setPlaceholderText("请输入小数")
    
    def ping_start(self):
        self.workers=[]
        self.Childs=[]
        loggingStatus=self.radioButton.isChecked()
        waittime=self.lineEdit_jiange.text()   
        # if not waittime:
        #     self.QMessageBox.critical( "错误", "输入不能为空！")
        # run_status=True
        
        number=0            
        for i in range(self.myTreeWidget.topLevelItemCount()):
            root_item = self.myTreeWidget.topLevelItem(i)
            root_check=root_item.checkState(0)
            if root_check.value == 2:
                for j in range(root_item.childCount()):
                    child_item=root_item.child(j)
                    ping_name=child_item.text(1)
                    ping_ip=child_item.text(2)#取决于ip所在位置
                    self.Childs.append(child_item)
                    worker=Worker(thread_id=number,
                                  ping_name=ping_name,
                                  ping_ip=ping_ip,
                                  waittime=waittime,
                                  loggingStatus=loggingStatus)
                    worker.update_signal.connect(self.Display_update)
                    worker.start()
                    self.workers.append(worker)
                    number+=1
                    
            else:
                for j in range(root_item.childCount()):
                    child_item=root_item.child(j)
                    child_check=child_item.checkState(0)
                    if child_check.value == 2:
                        child_item=root_item.child(j)
                        ping_name=child_item.text(1)
                        ping_ip=child_item.text(2)
                        self.Childs.append(child_item)
                        worker=Worker(thread_id=number,
                                  ping_name=ping_name,
                                  ping_ip=ping_ip,
                                  waittime=waittime,
                                  loggingStatus=loggingStatus)
                        worker.update_signal.connect(self.Display_update)
                        worker.start()
                        self.workers.append(worker)
                        number+=1
        return 0
                    
    def ping_stop(self):
        for worker in self.workers:
            worker.stop()
            worker.wait() # 等待线程结束            
        return 0
    
    '''
    description: 设置列标题
    param {*} self
    param {*} targetui
    param {*} targetTreeWidget
    return {*}
    '''
    def init_treewidget(self,targetTreeWidget,columnHeadings):
        columnHeadings=columnHeadings+["ping"]
        myTreeWidget: QTreeWidget = getattr(self.ui,targetTreeWidget)
        myTreeWidget.setHeaderLabels(columnHeadings) 
        return myTreeWidget
        
    '''
    description: 生成复选框并设置状态
    param {*} self
    param {*} targetType
    param {*} status
    return {*}
    '''
    def checkboxSettings(self,targetType,status):
        if status==0:
            targetType.setCheckState(0, Qt.CheckState.Unchecked)  # 为节点设置复选框 不选中
        else:
            targetType.setCheckState(0, Qt.CheckState.Checked)  # 为节点设置复选框 选中
        return 0
        
    '''
    description: 创建一级节点
    param {*} self
    param {*} targetTreeWidget
    param {*} nodeName节点名称
    param {*} status节点勾选状态,0未选中,1选中
    return {*}
    '''
    def addAFirstLevelNode(self,targetTreeWidget,nodeName,status):
        Type1 = QTreeWidgetItem(targetTreeWidget)  
        Type1.setText(0, nodeName)
        self.checkboxSettings(Type1,status)
        return Type1           
        
    '''
    description: 创建二级节点
    param {*} self
    param {*} Type1一级节点
    param {*} nodename
    param {*} nodeSupplementaryInformation
    param {*} nodeSupplementaryInformation2
    param {*} status节点勾选状态,0未选中,1选中
    return {*}
    '''
    def addASecondLevelNode(self,Type1,status,*args):
        Type1Child1 = QTreeWidgetItem(Type1)
        Type1Child1.setText(0, '')
        i=0
        for member in args:            
            Type1Child1.setText(i+1, args[i])
            i=i+1
        self.checkboxSettings(Type1Child1,status)
        return 0
    
    
    '''
    description: 更新数据
    param {*} self
    param {*} content
    return {*}
    '''
    def Display_update(self,content):
        
        thread_id = int(content.split(':')[0].split(' ')[1])        
        if thread_id < len(self.Childs):
            child=self.Childs[thread_id]
            child.setText(3,content.split(':')[1])
        return 0
