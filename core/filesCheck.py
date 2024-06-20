# -*- coding: utf-8 -*-
"""
Created on: 2024/06/17 11:34
Author: 空门兰卡
"""

import os
try:
    import paramiko
    from apscheduler.schedulers.blocking import BlockingScheduler
except ModuleNotFoundError:
    os.system('pip install paramiko apscheduler -i https://mirrors.aliyun.com/pypi/simple')
    import paramiko
    from apscheduler.schedulers.blocking import BlockingScheduler


UPLOAD_LOCAL = '本机文件位置'
UPLOAD_TEMP_REOMTE = '目标接收位置(远程接收时保存路径)'
UPLOAD_DONE_REOMTE = '目标存储位置(远程接收完整后的存储路径)'
UPLOAD_HOST = '主机IP'
UPLOAD_PORT = '主机端口'
UPLOAD_USER = '主机用户'
UPLOAD_PASS = '主机密码'

DOWNLOAD_REOMTE = '来源文件位置'
DOWNLOAD_TEMP_LOCAL = '本机接收位置(下载的保存路径)'
DOWNLOAD_DONE_LOCAL = '本机存储位置(下载完成后的存储路径)'
DOWNLOAD_HOST = '主机IP'
DOWNLOAD_PORT = '主机端口'
DOWNLOAD_USER = '主机用户'
DOWNLOAD_PASS = '主机密码'


def sftp_connect(host, port, user, password):
    """
    建立SFTP连接并返回SFTP对象。

    参数：
    - host：SFTP服务器的主机名或IP地址。
    - port：SFTP服务器的端口号。
    - user：SFTP服务器的用户名。
    - password：SFTP服务器的密码。

    返回：
    - sftp：已建立的SFTP连接对象。

    异常：
    - paramiko.SSHException：如果建立SSH连接失败。
    - paramiko.AuthenticationException：如果身份验证失败。
    - paramiko.SFTPError：如果建立SFTP连接失败。
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, user, password)
    sftp = ssh.open_sftp()
    return sftp


def sftp_check(sftp: paramiko.SFTPClient, direction, few_dict:dict, many_dict:dict, reomte_path, local_path):
    """
    检查文件同步情况并执行相应操作。

    参数：
    sftp (paramiko.SFTPClient): SFTP客户端对象。
    few_dict (dict): 包含少量文件的字典，键为文件名，值为文件的大小。
    many_dict (dict): 包含大量文件的字典，键为文件名，值为文件的大小。
    reomte_path (str): 远程路径。
    local_path (str): 本地路径。
    direction (bool): 文件同步方向，True表示从本地到远程，False表示从远程到本地。

    异常：
    paramiko.SFTPError: 如果SFTP操作失败。
    """
    for file in few_dict.keys():
        try:
            if few_dict[file] != many_dict[file]:
                print(f' File not Equal {file} '.center(50,'='))
                continue
        except KeyError:
            print(f' File not Exist {file} '.center(50,'='))
            continue
        print(f' File is  Equal {file} '.center(50,'='))
        if direction:        
            try:
                sftp.rename(f'{reomte_path}/{file}', f'{UPLOAD_DONE_REOMTE}/{file}')
            except OSError:
                if sftp.stat(f'{UPLOAD_DONE_REOMTE}/{file}').st_size != many_dict[file]:
                    sftp.remove(f'{UPLOAD_DONE_REOMTE}/{file}')
                    sftp.rename(f'{reomte_path}/{file}', f'{UPLOAD_DONE_REOMTE}/{file}')
            os.remove(f'{local_path}/{file}')
            continue
        try:
            os.rename(f'{local_path}/{file}', f'{DOWNLOAD_DONE_LOCAL}/{file}')
        except FileExistsError:
            if os.path.getsize(f'{DOWNLOAD_DONE_LOCAL}/{file}') != many_dict[file]:
                os.remove(f'{DOWNLOAD_DONE_LOCAL}/{file}')
                os.rename(f'{local_path}/{file}', f'{DOWNLOAD_DONE_LOCAL}/{file}')
        sftp.remove(f'{reomte_path}/{file}')


def sftp_dicts(sftp: paramiko.SFTPClient, reomte_path: str, local_path: str, direction: bool):
    """
    获取本地文件夹和远程文件夹中以'.zip'结尾的文件的字典。

    参数：
    - sftp (paramiko.SFTPClient): SFTP客户端对象。
    - reomte_path (str): 远程文件夹路径。
    - local_path (str): 本地文件夹路径。
    - direction (bool): 文件同步方向，True表示从本地到远程，False表示从远程到本地。

    返回：
    - sftp：SFTP客户端对象。
    - few_dict：包含少量文件的字典，键为文件名，值为文件的大小。
    - many_dict：包含大量文件的字典，键为文件名，值为文件的大小。
    - reomte_path：远程文件夹路径。
    - local_path：本地文件夹路径。
    - direction：文件同步方向，True表示从本地到远程，False表示从远程到本地。

    异常：
    paramiko.SFTPError: 如果SFTP操作失败。
    """
    local_file_dict = {file: size for file in os.listdir(local_path)
                       if isinstance(file, str) and file.endswith('.zip') and isinstance((size := os.path.getsize(f'{local_path}/{file}')), int)}
    remote_file_dict = {file: size for file in sftp.listdir(reomte_path)
                        if file.endswith('.zip') and isinstance((size := sftp.stat(f'{reomte_path}/{file}').st_size), int)}
    if direction:
        few_dict = remote_file_dict
        many_dict = local_file_dict
    else:
        few_dict = local_file_dict
        many_dict = remote_file_dict
    return {'sftp': sftp, 'few_dict': few_dict, 'many_dict': many_dict, 'reomte_path': reomte_path, 'local_path': local_path, 'direction': direction}


def sftp_run(direction):
    """
    主函数。

    参数：
    - direction (bool): 文件同步方向，True表示从本地到远程，False表示从远程到本地。
    """
    if direction:
        print(' UpLoad Check Start '.center(50,'='))
        sftp = sftp_connect(UPLOAD_HOST, UPLOAD_PORT, UPLOAD_USER, UPLOAD_PASS)
        sftp_check(**sftp_dicts(sftp, UPLOAD_TEMP_REOMTE, UPLOAD_LOCAL, direction))
        sftp.close()
        print(' UpLoad Check Done '.center(50,'='),end='\n\n')
    else:
        print(' DownLoad Check Start '.center(50,'='))
        sftp = sftp_connect(DOWNLOAD_HOST, DOWNLOAD_PORT, DOWNLOAD_USER, DOWNLOAD_PASS)
        sftp_check(**sftp_dicts(sftp, DOWNLOAD_REOMTE, DOWNLOAD_TEMP_LOCAL, direction))
        sftp.close()
        print(' DownLoad Check Done '.center(50,'='),end='\n\n')


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    sftp_run(True)
    scheduler.add_job(sftp_run, 'interval', minutes=10, args=[True])
    sftp_run(False)
    scheduler.add_job(sftp_run, 'interval', minutes=10, args=[False])
    # 每10分钟执行一次
    scheduler.start()