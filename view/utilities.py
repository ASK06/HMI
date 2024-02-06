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
import datetime
import cv2


class Utilities:

    @staticmethod
    def create_repository(folder_list):
        """

        :param folder_list:
        :return:
        """
        [os.mkdir(folder) for folder in folder_list if folder is not None and not os.path.exists(folder)]

    @staticmethod
    def remove_repository_(paths, folder_flag=False):
        """

        :return:
        """
        try:
            if folder_flag:
                [os.rmdir(path) for path in paths if os.path.exists(path)]
            else:
                [os.remove(path) for path in paths if os.path.exists(path)]
            return True
        except Exception as e:
            print(f"Error in deleting the file/folder.. {e}")
            return False

    @staticmethod
    def get_image_size(file_path):
        """

        :param file_path:
        :return:
        """
        height, width, _ = cv2.imread(filename=file_path).shape
        return width, height

    @staticmethod
    def add_current_date(file_path, file_name=None, file_ext=None):
        """

        :param file_path:
        :param file_name:
        :param file_ext:
        :return:
        """
        return f"{file_path}\\{file_name}_{datetime.datetime.now().strftime('%d-%m-%y_%H:%M:%S').replace(':', '_')}" \
               f"{file_ext}"

    @staticmethod
    def secs_to_mins_hours(counter):
        """

        :param counter:
        :return:
        """
        secs = int(counter / 5)
        hours = 0
        minutes = 0
        if secs > 60:
            minutes, secs = divmod(secs, 60)
            if minutes > 60:
                hours, minutes = divmod(minutes, 60)
        return [hours, minutes, secs]


if __name__ == '__main__':
    print("Utilities_Handler")
