"""
ThermoKing Corporation Ownership Disclaimer
This file contains proprietary and confidential information
that is the sole property of ThermoKing Corporation. Any
re-use, copying or distribution of this material, either in
whole or in part, without the express written consent of
ThermoKing Corporation is strictly forbidden.

Created On: 2/5/2022
"""
__author__ = "Faisal Ahmed"
__version__ = "1.0.0"
__copyright__ = "Copyright 2021 by Thermo King Corp. All rights reserved"

import os
from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException
from scp import SCPClient, SCPException


class SSHConnectionManager:
    def __init__(self):
        self.stdout = None
        self.stdin = None
        self.ssh_client = None
        self.scp_client = None

    def ssh_connect(self, host_name, host_address, host_port, host_password):
        """

        :param host_name:
        :param host_address:
        :param host_port:
        :param host_password:
        :return:
        """
        print(f"Connection with Server...HostName: {host_name} {host_address} {host_port} {host_password}")
        if self.ssh_client is None and self.scp_client is None:
            try:
                self.ssh_client = SSHClient()
                self.ssh_client.load_system_host_keys()
                self.ssh_client.set_missing_host_key_policy(AutoAddPolicy)
                self.ssh_client.connect(hostname=host_address, port=host_port, username=host_name,
                                        password=host_password, timeout=5)
                self.scp_client = SCPClient(self.ssh_client.get_transport())
                channel = self.ssh_client.invoke_shell()
                self.stdin = channel.makefile('wb')
                self.stdout = channel.makefile('r')
                return True
            except AuthenticationException as e:
                print(f"{e}")
                return False

    @staticmethod
    def __get_ssh_key(ssh_key_file_path):
        """
        This function will do something... Wait for this amazing function...
        param ssh_key_file_path:
        :return:
        """
        # TODO use this function
        try:
            return RSAKey.from_private_key_file(ssh_key_file_path)
        except SSHException as error:
            print(error)
            return False

    def execute_command(self, commands, server_command=False, timeout=10):
        """

        param commands:
        param server_command:
        param timeout:
        return:
        """
        print(f"Sending the command to server: {commands}")
        response = None
        # TODO utilize map function
        if type(commands) == list:
            for data in commands:
                stdin, stdout, stderr = self.ssh_client.exec_command(data, timeout=timeout)
                if not server_command:
                    stdout.channel.recv_exit_status()
                    response = stdout.readline()
                    print(f"Response from SSH server: {response}")
            return response
        else:
            stdin, stdout, stderr = self.ssh_client.exec_command(commands, timeout=timeout)
            if not server_command:
                stdout.channel.recv_exit_status()
                response = stdout.readline()
                print(f"Response from SSH server: {response}")
            return response

    def kill_server_process(self, process_id):
        """

        :param process_id:
        :param ssh_client_status:
        :return:
        """
        if self.ssh_client.get_transport().is_active():
            self.execute_command(commands=[f"kill {process_id}"], timeout=5)
            return True
        return False

    def ssh_disconnect(self):
        """
        Python server has to be killed before disconnecting the SSH Client.
        :return:
        """
        print("Disconnecting with server...")
        if self.ssh_client is not None and self.scp_client is not None:
            self.ssh_client.close()
            self.scp_client.close()
            self.ssh_client, self.scp_client = None, None

    def upload_download_file(self, server_file_location, local_file_store_location,
                             download=False, upload=False):
        """

        param server_file_location:
        param local_file_store_location:
        param download:
        param upload:
        return:
        """
        if self.ssh_client is not None and self.scp_client is not None:
            print(server_file_location, local_file_store_location)
            try:
                if download:
                    self.scp_client.get(remote_path=server_file_location, local_path=local_file_store_location,
                                        recursive=True)
                    return True
                if upload:
                    for file in os.listdir(path=local_file_store_location):
                        self.scp_client.put(files=f"{local_file_store_location}\\{file}",
                                            remote_path=server_file_location, recursive=True)
                    return True
            except SCPException as error:
                print(f"Error is downloading/uploading files from/to server. Please try again...{error}")
                return False
        return False

    def remove_file_folder(self, file_folder_location, recursive=False):
        print(file_folder_location)
        string = "rm"
        if recursive:
            string = "rm -r"
        if type(file_folder_location) == list:
            for location in file_folder_location:
                self.execute_command(commands=[f"{string} {location}"])
        else:
            self.execute_command(commands=[f"{string} {file_folder_location}"])

    def make_file_folder(self, folder_location_list):
        if self.ssh_client.get_transport().is_alive():
            for folder_location in folder_location_list:
                self.execute_command(commands=[f"mkdir {folder_location}"])
            return True
        else:
            return False


if __name__ == '__main__':
    test_1 = SSHConnectionManager()
    print(test_1.ssh_connect(host_name="root", host_address="192.168.44.30", host_port=22, host_password="Tkmac@231#"))
    # print(test_1.ssh_client.get_transport().is_active())
    # print(test_1.execute_command(commands=["rm -r /home/root/HATServer"]))
    # print(test_1.execute_command(commands=["mkdir /home/root/HATServer"]))
    # test_1.upload_download_file(server_file_location="/home/root/HATServer", local_file_store_location=
    # r"D:\irghle\Automation\HAT\HAT_6.0.0\Configuration Files\Server Files\Upload", upload=True)
    # test_1.upload_download_file(server_file_location="/home/root/HATServer/",
    #                             local_file_store_location="D:\\", download=True)
    # test_1.remove_file_folder(file_folder_location="/home/root/HATServer/api.py")
    # test_1.remove_file_folder(file_folder_location="/home/root/HATServer", recursive=True)
    # print(test_1.ssh_client.get_transport().is_active())
    test_1.ssh_disconnect()
