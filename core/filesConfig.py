# -*- coding: utf-8 -*-
"""
Created on: 2024/06/17 11:34
Author: 空门兰卡
"""

import os
import yaml
import json
from configparser import ConfigParser
from filesLog import Relog


class Reconfig:
    def __init__(self):
        self.config_dir = f'{os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))}/cfg'
        self.logger = Relog('config').logger
        self.config = ConfigParser()

    def read(self, config_file):
        self.config_file = config_file
        try:
            self.config.read(
                f'{self.config_dir}/{config_file}.ini', encoding='utf-8')
        except FileNotFoundError:
            self.logger.error(f'Error reading config file: {config_file}.ini')
            raise

    def txt_cfg(self, config_file):
        try:
            with open(f'{self.config_dir}/{config_file}.txt', 'r') as txt_file:
                return [line.strip() for line in txt_file.readlines()]
        except FileNotFoundError:
            self.logger.error(f'Error reading config file: {config_file}.txt')
            raise

    def json_cfg(self, config_file):
        try:
            with open(f'{self.config_dir}/{config_file}.json', 'r') as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            self.logger.error(f'Error reading config file: {config_file}.json')
            raise

    def yaml_cfg(self, config_file):
        try:
            with open(f'{self.config_dir}/{config_file}.yaml', 'r') as yaml_file:
                return yaml.safe_load(yaml_file)
        except FileNotFoundError:
            self.logger.error(f'Error reading config file: {config_file}.yaml')
            raise

    @staticmethod
    def config_wapper(func):
        def wrapper(cls:Reconfig, *args):
            result = func(cls, *args)
            if not result:
                cls.logger.error(
                    f'config file [{cls.config_file}.ini] has empty value at key [{args[0]}]')
                result = None
            else:
                for section in result:
                    for key, value in result[section].items():
                        if not value:
                            cls.logger.error(f'config file [{cls.config_file}.ini] has empty value at key \
                                             [{key}] in section [{section}]')
                    cls.logger.info(
                        f'config file [{cls.config_file}.ini] loaded section [{section}]')
            return result
        return wrapper

    @config_wapper
    def items(self):
        __items__ = {}
        try:
            for section in self.config.sections():
                __items__.update({
                    section: {
                        key: value for key, value in self.config.items(section)
                    }
                })
            return __items__
        except ValueError:
            self.logger.error(f'Error getting config items')
            raise

    def clear(self):
        self.config.clear()
