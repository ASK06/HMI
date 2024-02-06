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

import time
from view.utilities import Utilities
from settings import Setting, SSHServer
from model.client_handler import ClientHandler
from model.connection_manager import SSHConnectionManager


class V2MHATMainWebApp:
    @staticmethod
    def ssh_connect():
        """

        :return:
        """
        Setting.ModelViewConnector.ssh_connection_handler = SSHConnectionManager()
        ssh_details = V2MHATMainWebApp.get_ssh_details()
        try:
            Setting.LabelStatus.main_gui_current_status = "Initializing the tool. Creating SSH Connection..."
            if Setting.ModelViewConnector.ssh_connection_handler.ssh_connect(host_name=ssh_details.host_name,
                                                                             host_port=ssh_details.host_port,
                                                                             host_password=ssh_details.host_password,
                                                                             host_address=ssh_details.host_address):
                if not Setting.ActivityStatus.ssh_initialization:
                    Setting.ScreenRecodingSetting.size = Utilities.get_image_size(
                        file_path=Setting.FilePaths.image_hat_default)
                    print("Removing the old server files...")
                    Setting.ModelViewConnector.ssh_connection_handler.remove_file_folder(file_folder_location=[
                        Setting.FolderPaths.ssh_remote_main_location], recursive=True)
                    Setting.ModelViewConnector.ssh_connection_handler.make_file_folder(folder_location_list=[
                        r"/home", r"/home/root", Setting.FolderPaths.ssh_remote_main_location,
                        Setting.FolderPaths.ssh_remote_location_download])
                    print("Updating new files to server...")
                    V2MHATMainWebApp.ssh_upload()
                Setting.LabelStatus.main_gui_current_status = "Initializing the tool. Starting the HAT server..."
                running_python_sever = f"python3 {Setting.FolderPaths.ssh_remote_main_location}/" \
                                       f"{Setting.SSHServer.ssh_server_file_name}"
                counter = 0
                while counter < 3:
                    print(f"Sending the command to run the server: {running_python_sever}")
                    Setting.ModelViewConnector.ssh_connection_handler.execute_command(commands=running_python_sever,
                                                                                      server_command=True)
                    time.sleep(2)
                    Setting.SSHServer.ssh_python_id = Setting.ModelViewConnector.ssh_connection_handler. \
                        execute_command(commands=f"pidof {running_python_sever}")
                    if Setting.SSHServer.ssh_python_id is not None:
                        Setting.SSHServer.ssh_python_id = Setting.SSHServer.ssh_python_id.split(" ")
                        if int(Setting.SSHServer.ssh_python_id[0].replace("\n", "")) != 0:
                            print("Python Server has been started successfully...")
                            print("Loading the current screen...")
                            counter = 45
                            while int(counter / 5) >= 1:
                                Setting.LabelStatus.main_gui_current_status = f"Initializing the tool. Capturing " \
                                                                              f"the image.... Please wait for" \
                                                                              f" {int(counter / 5)} seconds " \
                                                                              f"{' ' * counter}"
                                time.sleep(0.2)
                                counter -= 1
                            Setting.ActivityStatus.ssh_python_server = True
                            Setting.ActivityStatus.ssh_initialization = True
                            Setting.ViewModelConnector.gui_main_handler.update_image()
                            return True
                        else:
                            print("Trying again to start the python server...")
                    counter += 1
                Setting.ActivityStatus.ssh_python_server = False
                Setting.ActivityStatus.ssh_initialization = False
                Setting.LabelStatus.main_gui_current_status = "Error in starting the server. Please try again..."
                V2MHATMainWebApp.fail_server_start()
            else:
                Setting.SSHServer.ssh_python_id = 0
                Setting.LabelStatus.main_gui_current_status = "Error in starting the server. Please try again..."
                Setting.ErrorStatus.main_gui_error = True
                V2MHATMainWebApp.fail_server_start()
        except Exception as e:
            print(e)
            Setting.LabelStatus.main_gui_current_status = "Error in starting the server. Please try again..."
            Setting.ErrorStatus.main_gui_error = True
            V2MHATMainWebApp.fail_server_start()

    @staticmethod
    def fail_server_start():
        V2MHATMainWebApp.ssh_disconnect()
        Setting.ModelViewConnector.ssh_connection_handler = None

    @staticmethod
    def ssh_disconnect():
        """

        :return:
        """
        Setting.LabelStatus.main_gui_current_status = "Disconnecting with python server..."
        if Setting.ModelViewConnector.ssh_connection_handler is not None:
            if Setting.ActivityStatus.ssh_python_server:
                for pids in Setting.SSHServer.ssh_python_id:
                    Setting.ModelViewConnector.ssh_connection_handler.kill_server_process(process_id=pids)
                Setting.ActivityStatus.ssh_python_server = False
                Setting.SSHServer.ssh_python_id = None
                Setting.ActivityStatus.ssh_connection_connected_status = False
            Setting.ModelViewConnector.ssh_connection_handler.ssh_disconnect()

    @staticmethod
    def get_ssh_details():
        """

        :return:
        """
        ssh_host_name = Setting.SSHServer.ssh_host_name
        ssh_host_address = Setting.SSHServer.ssh_host_address
        ssh_host_port = Setting.SSHServer.ssh_host_port
        ssh_password = Setting.SSHServer.ssh_password
        return SSHServer(host_name=ssh_host_name,
                         host_address=ssh_host_address,
                         host_port=ssh_host_port,
                         host_password=ssh_password)

    @staticmethod
    def ssh_download():
        """

        :return:
        """
        Setting.LabelStatus.main_gui_current_status = "Downloading the test scripts from MAC..."
        if Setting.ActivityStatus.ssh_python_server and Setting.ActivityStatus.ssh_connection_connected_status:
            Setting.ModelViewConnector.ssh_connection_handler.upload_download_file(
                server_file_location=Setting.FolderPaths.ssh_remote_location_download,
                local_file_store_location=Setting.FolderPaths.test_scripts, download=True)

    @staticmethod
    def ssh_upload():
        """

        :return:
        """
        Setting.ModelViewConnector.ssh_connection_handler.upload_download_file(
            server_file_location=Setting.FolderPaths.ssh_remote_main_location,
            local_file_store_location=Setting.FolderPaths.ssh_local_file_location_upload,
            upload=True)


class V2MClientHandler(ClientHandler):
    def __init__(self):
        super().__init__()
