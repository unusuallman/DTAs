# -*- coding: utf-8 -*-
"""
Created on: 2024/06/19 12:03
Author: 空门兰卡
"""

import re
import shutil
from pathlib import Path
import traceback
from zipfile import ZipFile, ZIP_DEFLATED


class Compress:
    def __init__(self, project_pattern=None, keep_flag=True):
        self.project_pattern = re.compile(
            project_pattern) if project_pattern else re.compile(r'(.*?)_')
        self.keep_flag = keep_flag

    def __close__(self):
        del self.folder_path
        del self.folder_path_count
        del self.keep_flag
        del self.project_pattern

    def __enter__(self):
        if hasattr(self, 'folder_path'):
            del self.folder_path
        if hasattr(self, 'folder_path_count'):
            del self.folder_path_count
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            tb_str = '\n'.join(traceback.format_tb(exc_tb))
            raise exc_type(f"""
                           ==> Traceback {exc_val} <==
                           {tb_str}
                           ==> Traceback End <==
                           """)
        else:
            self.__close__()

    def load_folder(self, path):
        self.folder_path = Path(path)
        if not self.folder_path.exists():
            raise FileNotFoundError(f"Error: '{self.folder_path}' not found.")
        self.folder_path_count = len(
            [p for p in self.folder_path.rglob('*') if p.is_file()])

    def compress_folder(self):
        if not self.folder_path.is_dir():
            raise NotADirectoryError(
                f"Error: '{self.folder_path}' is not a folder.")
        zip_file_name = self.folder_path.with_suffix('.zip')
        with ZipFile(zip_file_name, 'w', ZIP_DEFLATED) as zips:
            for file in self.folder_path.rglob('*'):
                if file.is_file():
                    arc_name = file.relative_to(self.folder_path)
                    zips.write(file, arcname=arc_name)

    def delete_folder(self):
        if not self.folder_path.is_dir():
            raise NotADirectoryError(
                f"Error: '{self.folder_path}' is not a folder.")
        shutil.rmtree(self.folder_path)
        del self.folder_path
        del self.folder_path_count
