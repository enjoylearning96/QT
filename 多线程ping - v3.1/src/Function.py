'''
Author: 李晓乐
Date: 2025-04-15 11:58:08
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-04-28 13:40:47
FilePath: \多线程ping - v3.1\Function.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os
import subprocess
from re import search
from datetime import datetime

'''
description: 
param {*} content
param {*} targetFile
return {*}
'''
def write_to_file(content,targetFile):
    # 获取当前日期和时间
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")  # 格式化为YYYY-MM-DD
    time_str = now.strftime("%H")  # 格式化为HH

    # 创建文件路径
    directory = os.path.join("log",date_str, time_str)
    filename = f"{targetFile}.txt"
    filepath = os.path.join(directory, filename)

    # 确保目录存在
    os.makedirs(directory, exist_ok=True)

    # 以附加模式打开文件并写入内容
    with open(filepath, 'a', encoding='utf-8') as file:
        file.write(content + '\n')  # 添加内容并换行
        
'''
description: 执行ping操作并返回结果
param {*} ping_ip
param {*} loggingStatus
return {*}
'''
def ping_action(ping_name,ping_ip,loggingStatus):
    # -c 1 表示发送 1 次 ping 请求（对于 Windows 使用 -n 1）
    # stdout 和 stderr 需要为 subprocess.PIPE，以便我们能读取输出
        result = subprocess.run(
        ['ping', '-n', '1', ping_ip],  # Linux/Mac 使用 '-c'
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True  # 输出为字符串而非字节
        )

        output = result.stdout
        
        if result.returncode == 0:
            match = search(r'时间=(\d+)ms', output)
            if match:
                latency =f"{match.group(1)}ms"
            else:
                  latency =f" error"
        else:
            latency =f"error"
        if loggingStatus==True:
            write_to_file(latency,ping_name)
        return latency