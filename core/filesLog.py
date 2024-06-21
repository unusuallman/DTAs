# -*- coding: utf-8 -*-
"""
Created on: 2024/06/17 11:34
Author: 空门兰卡
"""

from logging import INFO, getLogger, Formatter
from logging.handlers import RotatingFileHandler as handler
import logging
import os


class Relog:
    def __init__(self, log_name: str | None = None, stream=False) -> None:
        log_path = f'{os.path.dirname(os.path.dirname(
            os.path.abspath(__file__)))}/log/{log_name}.log'
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        logger = getLogger(log_name)
        logger.setLevel(INFO)
        file_handler = handler(log_path, maxBytes=1024**3, backupCount=5)
        file_handler.setFormatter(
            Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S',))
        logger.addHandler(file_handler)
        if stream:
            logger.addHandler(logging.StreamHandler())
        self.logger = logger
