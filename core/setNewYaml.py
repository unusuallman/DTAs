# -*- coding: utf-8 -*-
"""
Created on: 2024/06/21 16:06
Author: 空门兰卡
"""

import yaml


def setNewYaml(yamlPath, data):
    with open(yamlPath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    return True


def changeYamlValue(yamlPath, key, value):
    with open(yamlPath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    data[key] = value
    with open(yamlPath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    return True


def createYaml(yamlPath):
    with open(yamlPath, 'w', encoding='utf-8') as f:
        data = {
            'IPS': ['xxx.xxx.xxx.xxx', 'xxx.xxx.xxx.xxx'],
            'PORT': 22,
            'USER': 'root',
            'PASS': 'root_password',
            'TIMEOUT': 5,
            'THREADS': 10,
            'TASK_PATH': '远程目标路径',
            'SAVE_PATH': '本地保存路径',
            'TEMP_PATH': '临时文件路径',
        }

        # 将字典转换为 YAML 格式的字符串，每一行都有四个空格的缩进
        yaml.dump(data, f, indent=4, default_flow_style=False, allow_unicode=True)

    return True