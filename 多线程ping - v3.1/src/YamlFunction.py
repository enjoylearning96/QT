'''
Author: 李晓乐
Date: 2025-04-28 13:10:50
LastEditors: enjoylearning96 148044540+enjoylearning96@users.noreply.github.com
LastEditTime: 2025-04-28 13:21:53
FilePath: \多线程ping - v3.1\YamlFunction.py
Description: 

Copyright (c) 2025 by ${git_name_email}, All Rights Reserved. 
'''
import os
from yaml import safe_load,safe_dump,dump,safe_load_all,safe_dump_all,safe_dump_all
from typing import Any, Union, Generator, List, Dict

def read_yaml(file_path: str) -> Union[dict, list]:
    """
    读取YAML文件并返回解析后的Python对象
    
    :param file_path: YAML文件路径
    :return: 解析后的字典或列表
    :raises FileNotFoundError: 当文件不存在时引发
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return safe_load(f)

def write_yaml(data: Any, file_path: str, overwrite: bool = True, safe_mode: bool = True, **kwargs) -> None:
    """
    将Python对象写入YAML文件
    
    :param data: 要写入的Python对象
    :param file_path: 目标文件路径
    :param overwrite: 是否覆盖已存在文件（默认False）
    :param safe_mode: 使用安全模式（默认True）
    :param kwargs: 传递给yaml.dump的额外参数
    :raises FileExistsError: 当文件已存在且未启用覆盖时引发
    """
    if os.path.exists(file_path) and not overwrite:
        raise FileExistsError(f"文件 {file_path} 已存在且未启用覆盖模式")
    
    # os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    kwargs.setdefault('allow_unicode', True)  # 保留Unicode字符
    kwargs.setdefault('default_flow_style', None)  # 自动选择样式
    
    with open(file_path, 'w', encoding='utf-8') as f:
        if safe_mode:
            safe_dump(data, f, **kwargs)
        else:
            dump(data, f, **kwargs)

def yaml_str_to_dict(yaml_str: str) -> Union[dict, list]:
    """
    将YAML字符串解析为Python对象
    
    :param yaml_str: YAML格式字符串
    :return: 解析后的字典或列表
    """
    return safe_load(yaml_str)

def dict_to_yaml_str(data: Any, safe_mode: bool = True, **kwargs) -> str:
    """
    将Python对象转换为YAML格式字符串
    
    :param data: 要转换的Python对象
    :param safe_mode: 使用安全模式（默认True）
    :param kwargs: 传递给yaml.dump的额外参数
    :return: YAML格式字符串
    """
    kwargs.setdefault('allow_unicode', True)
    kwargs.setdefault('default_flow_style', None)
    
    if safe_mode:
        return safe_dump(data, **kwargs)
    return dump(data, **kwargs)

def read_yaml_all(file_path: str) -> Generator:
    """
    读取包含多个YAML文档的文件
    
    :param file_path: YAML文件路径
    :return: 生成器，逐个生成每个文档
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        yield from safe_load_all(f)

def write_yaml_all(data_list: List[Any], file_path: str, overwrite: bool = False, safe_mode: bool = True, **kwargs) -> None:
    """
    将多个Python对象写入YAML文件（多文档格式）
    
    :param data_list: 包含多个Python对象的列表
    :param file_path: 目标文件路径
    :param overwrite: 是否覆盖已存在文件（默认False）
    :param safe_mode: 使用安全模式（默认True）
    :param kwargs: 传递给yaml.dump_all的额外参数
    """
    if os.path.exists(file_path) and not overwrite:
        raise FileExistsError(f"文件 {file_path} 已存在且未启用覆盖模式")
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    kwargs.setdefault('allow_unicode', True)
    kwargs.setdefault('default_flow_style', None)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        if safe_mode:
            safe_dump_all(data_list, f, **kwargs)
        else:
            dump_all(data_list, f, **kwargs)