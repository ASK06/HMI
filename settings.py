"""
ThermoKing Corporation Ownership Disclaimer
This file contains proprietary and confidential information
that is the sole property of ThermoKing Corporation. Any
re-use, copying or distribution of this material, either in
whole or in part, without the express written consent of
ThermoKing Corporation is strictly forbidden.

Created On: 29/09/2023
"""
__author__ = "Durga Prasad"
__version__ = "1.0"
__copyright__ = "Copyright 2021 by Thermo King Corp. All rights reserved"

import os
from view.utilities import Utilities


class Setting:
    current_wd = None

    class ScreenRecodingSetting:
        fps = 4
        # 3
        size = (800, 480)
        delay = 0.25
        videoWrite = None

    class SaveOption:
        SaveImage = False
        SaveVideo = True

    class SSHServer:
        ssh_host_name = 'root'
        ssh_host_address = '192.168.44.30'
        ssh_host_port = '22'
        ssh_password = "Tkmac@231#"
        ssh_folder_name_main = "HATServer"
        ssh_folder_name_scripts = "Scripts"
        ssh_server_file_name = "server.py"
        ssh_python_id = 0
        valid_keys = ['F1_KEY', 'F2_KEY', 'F3_KEY', 'UP_KEY', 'DOWN_KEY', 'LEFT_KEY', 'RIGHT_KEY', 'CENTER_KEY',
                      'DF_KEY', 'CC_KEY', 'GA_KEY', 'MMP_KEY']

    class FilePaths:
        gui_connection_manager = None
        image_hat_current_image = None
        image_hat_server_down = None
        # 4
        image_hat_default = None
        image_hat_watermark = None
        gif_starting_screen_gif = None
        ssh_key_known_host = None

    class FolderPaths:
        ssh_remote_location_download = None
        ssh_local_file_location_upload = None
        ssh_remote_main_location = None
        test_results = None
        screen_recordings = None
        screen_screenshots = None
        default_hmi_screen = None
        test_scripts = None

    class ModelViewConnector:
        # 1
        ssh_connection_handler = None

    class ErrorStatus:
        main_gui_error = False

    class ViewModelConnector:
        gui_main_handler = None

    class ActivityStatus:
        ssh_connection_connected_status = False
        ssh_connection_alive_status = False
        # 2
        ssh_initialization = False
        ssh_python_server = False
        screen_recording = False
        screen_capture = False
        script_recording = False
        screen_recording_live_monitoring = False
        ssh_running_status = 'disconnected'

    class LabelStatus:
        main_gui_default_status = "HMI Automation Test Tool"
        main_gui_current_status = main_gui_default_status
        main_gui_time_elapsed_status = ""
        main_gui_time_elapsed_counter = 0

    @staticmethod
    def load_settings():
        """

        :return:
        """
        try:
            # Current Working directory
            Setting.current_wd = os.getcwd()

            # Current Image Save Location Path & Display same in screen #
            static_folder = "static"
            image_folder = "assets"
            server_folder = "server"

            # cwd\static\images
            Setting.FolderPaths.default_hmi_screen = f"{Setting.current_wd}\\{static_folder}\\{image_folder}"

            # f"cwd/Test Results"
            Setting.FolderPaths.test_results = f"{Setting.current_wd}\\Test Results"

            # f"cwd/Test Results/Recordings"
            Setting.FolderPaths.screen_recordings = f"{Setting.FolderPaths.test_results}\\Recordings"

            # f"cwd/Test Results/Screenshots"
            Setting.FolderPaths.screen_screenshots = f"{Setting.FolderPaths.test_results}\\Screenshots"

            # f"cwd/Test Results/Test Scripts"
            Setting.FolderPaths.test_scripts = f"{Setting.FolderPaths.test_results}\\Test Scripts"

            # f"cwd\server"
            Setting.FolderPaths.ssh_local_file_location_upload = f"{Setting.current_wd}\\{server_folder}"

            # f"/home/root/HATServer"
            Setting.FolderPaths.ssh_remote_main_location = f"/home/root/{Setting.SSHServer.ssh_folder_name_main}"

            # f"/home/root/HATServer/Scripts"
            Setting.FolderPaths.ssh_remote_location_download = \
                f"{Setting.FolderPaths.ssh_remote_main_location}/{Setting.SSHServer.ssh_folder_name_scripts}"

            # Default HMI screen
            # f"cwd/static/images/hat_server_down.jpg"
            Setting.FilePaths.image_hat_server_down = f"{Setting.FolderPaths.default_hmi_screen}\\hat_server_down.jpg"

            # f"cwd/static/images/default_screen.png"
            Setting.FilePaths.image_hat_default = f"{Setting.FolderPaths.default_hmi_screen}\\default_screen.png"

            # f"cwd/static/images/hat_current_image.jpg"
            Setting.FilePaths.image_hat_current_image = \
                f"{Setting.FolderPaths.default_hmi_screen}\\hat_current_image.jpg"

            # f"cwd/static/images/hat_v6_watermark.png"
            Setting.FilePaths.image_hat_watermark = f"{Setting.FolderPaths.default_hmi_screen}\\hat_watermark.png"

            # f"cwd/static/images/loading2.gif"
            Setting.FilePaths.gif_hat_loading2_gif = f"{Setting.FolderPaths.default_hmi_screen}\\loading.gif"

            # f"cwd/static/images/StartingScreen.gif"
            Setting.FilePaths.gif_starting_screen_gif = f"{Setting.FolderPaths.default_hmi_screen}\\starting_screen.gif"
            Setting.FilePaths.ssh_key_known_host = f"C:/Users/{os.getlogin()}/.ssh/Known_hosts"
            Utilities.create_repository(folder_list=[Setting.FolderPaths.test_results,
                                                     Setting.FolderPaths.screen_recordings,
                                                     Setting.FolderPaths.screen_screenshots,
                                                     Setting.FolderPaths.test_scripts])
            return True
        except Exception as e:
            print(f"Error {e}")
            return False

    @staticmethod
    def get_image_name():
        return Utilities.add_current_date(file_path=Setting.FolderPaths.screen_screenshots,
                                          file_name="HMIScreenshot", file_ext=".jpg")

    @staticmethod
    def get_screen_record_name():
        return Utilities.add_current_date(file_path=Setting.FolderPaths.screen_recordings,
                                          file_name="HMIScreenRecording", file_ext=".mp4")


class SSHServer:
    def __init__(self, host_name, host_port, host_address, host_password):
        """

        :param host_name:
        :param host_port:
        :param host_address:
        :param host_password:
        """
        self.host_name = host_name
        self.host_port = host_port
        self.host_address = host_address
        self.host_password = host_password


if __name__ == '__main__':
    Setting.load_settings()
