'''
Author: 李晓乐
Date: 2025-04-29 13:22:28
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-04-29 13:22:51
FilePath: \多线程ping - v3.1\setup.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
from cx_Freeze import setup, Executable
import os

# 静态文件路径
data_files = [("data", os.path.join("data", "config.json"))]

# 依赖项优化配置
build_options = {
    "excludes": ["tkinter", "test", "http", "email", "xml"],
    "includes": ["requests"],  # 假设主程序动态导入了 requests
    "include_files": data_files,
    "zip_include_packages": ["encodings", "logging"],
    "optimize": 2
}

executables = [Executable(
    os.path.join("src", "main.py"),
    base="Win32GUI",
    target_name="MyApp.exe",
    icon="icon.ico"
)]

setup(
    name="MyApp",
    version="1.0",
    options={"build_exe": build_options},
    executables=executables
)