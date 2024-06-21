# -*- coding: utf-8 -*-
"""
Created on: 2024/06/17 11:34
Author: 空门兰卡
"""

try:
    import paramiko
    import traceback
    from apscheduler.schedulers.blocking import BlockingScheduler
except ImportError:
    import os
    os.system("pip install apscheduler paramiko")
    import paramiko
    import traceback
    from apscheduler.schedulers.blocking import BlockingScheduler
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

import setNewYaml
from filesConfig import Reconfig
from filesLog import Relog


def relog(log_name: str, stream=False):
    return Relog(log_name, stream).logger


def load_config():
    global IPS, PORT, USER, PASSWORD, TASK_PATH, TEMP_PATH, SAVE_PATH
    config = Reconfig()
    yaml_file = Path(input("The yaml config file path which in cfg: "))
    if not yaml_file.exists():
        print(f"Error: {yaml_file} not found")
        if input(f"Create a new yaml file in {yaml_file}? (y/n): ") == "y":
            setNewYaml.createYaml(yaml_file)
            print(f"Create a new yaml file in {yaml_file} success")
        else:
            print("Exit")
            exit()
    yaml_file_name = yaml_file.stem        
    yaml_config = config.yaml_cfg(yaml_file_name)
    IPS = yaml_config["IPS"]
    PORT = yaml_config["PORT"]
    USER = yaml_config["USER"]
    PASSWORD = yaml_config["PASSWORD"]
    TASK_PATH = yaml_config["TASK_PATH"]
    TEMP_PATH = yaml_config["TEMP_PATH"]
    SAVE_PATH = yaml_config["SAVE_PATH"]


def sftpclient_connect(ip):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, PORT, USER, PASSWORD)
    sftp = ssh.open_sftp()

    class SFTPClientWrapper:
        def __init__(self, sftp: paramiko.SFTPClient, ssh: paramiko.SSHClient):
            self.sftp = sftp
            self.ssh = ssh

        def __enter__(self):
            return self.sftp

        def __close__(self):
            self.sftp.close()
            self.ssh.close()

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                tb_str = '\n'.join(traceback.format_tb(exc_tb))
                raise exc_type(
                    f"\n==> Traceback {exc_val} Error <=="
                    f"\n{tb_str}"
                    f"\n==> Traceback {exc_val} End <==")
            else:
                self.__close__()

    return SFTPClientWrapper(sftp, ssh)


def download_file(ip: str, remote_file_path: str, local_file_path: str):
    global LOGS, SAVE_PATH
    log = LOGS[ip]
    try:
        log.info(f"[#] {ip} Connect start")
        Path(local_file_path).parent.mkdir(parents=True, exist_ok=True)
        with sftpclient_connect(ip) as sftp:
            log.info(f"[*] {remote_file_path} download start")
            sftp.get(remote_file_path, local_file_path)
            log.info(f"[*] {remote_file_path} download finished")
            # Path(local_file_path).replace(
            #     str(local_file_path).replace(TEMP_PATH, SAVE_PATH))
            finished_file = SAVE_PATH / Path(local_file_path).name
            moved_file = Path(local_file_path).replace(finished_file)
            log.info(f"[>>] {local_file_path} move to " +
                     str(moved_file))
            sftp.remove(remote_file_path)
            log.info(f"[<<] {remote_file_path} remote delete finished")
        log.info(f"[#] {ip} Connect close")
    except Exception as e:
        log.error(f"[@] {remote_file_path} {e}")


def download_finder(sftp: paramiko.SFTPClient, remote_path):
    global MAX_WORKERS
    sftp.chdir(remote_path)
    files = sftp.listdir()
    files_list = []
    for file in files:
        remote_file = str(Path(remote_path) / file)
        if sftp.stat(remote_file).st_mode != 16877:
            local_file = Path(TEMP_PATH) / file
            files_list.append((remote_file, local_file))
            if len(files_list) >= MAX_WORKERS:
                break
    return files_list


def sftpToDmz(ip: str):
    global LOGS
    log = LOGS[ip]
    log.info(f"==> check files start <==")
    try:
        with sftpclient_connect(ip) as sftp:
            files_list = download_finder(sftp, TASK_PATH)
    except Exception as e:
        log.error(f"[@] {ip} {e}")
        files_list = []
    log.info(f"==> check files finished <==")
    return files_list


def download_all_files():
    global IPS
    files_dict = {ip: sftpToDmz(ip) for ip in IPS}
    with ProcessPoolExecutor(max_workers=MAX_WORKERS*int(len(IPS))) as executor:
        for ip in files_dict:
            for remote_file, local_file in files_dict[ip]:
                executor.submit(download_file, ip, remote_file, local_file)


if __name__ == "__main__":
    MAX_WORKERS = 2
    LOGS = {IP: relog(IP.split(".")[-1]) for IP in IPS}
    scheduler = BlockingScheduler()
    scheduler.add_job(
        download_all_files, "interval",
        seconds=5, args=[MAX_WORKERS])
    scheduler.start()
