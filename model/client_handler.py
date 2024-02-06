"""
ThermoKing Corporation Ownership Disclaimer
This file contains proprietary and confidential information
that is the sole property of ThermoKing Corporation. Any
re-use, copying or distribution of this material, either in
whole or in part, without the express written consent of
ThermoKing Corporation is strictly forbidden.

Created On:  
"""
__author__ = 'Durga Prasad'
__version__ = "1.0."
__copyright__ = "Copyright 2021 by Thermo King Corp. All rights reserved"

import requests
from PIL import Image
import zlib
from settings import Setting
import cv2
import threading
import datetime


class RunScriptHandler(threading.Thread):

    def __init__(self):
        super().__init__()


class HATCommands(object):
    GRAB_SCREEN = 'http://192.168.44.30:9046/grab_screen'
    EMULATE_BUTTON = 'http://192.168.44.30:9046/emulate_button'
    RECORD_BUTTONS = 'http://192.168.44.30:9046/record_buttons'


class ClientHandler:

    @staticmethod
    def emulate_button_press(key_info):
        """

        """
        if key_info in Setting.SSHServer.valid_keys:
            response = requests.post('{0}?b={1}'.format(HATCommands.EMULATE_BUTTON, key_info), timeout=10)
            print(response.json()['status'])
            print(datetime.datetime.now(), 'emulate_button_press')
            return True
        else:
            print('Invalid Key!')
            return False

    @staticmethod
    def record_buttons(recording_status):
        """

        """
        if recording_status:
            print("Starting the script recording")
            response = requests.post('{0}?record_enable={1}'.format(HATCommands.RECORD_BUTTONS, 'y'), timeout=5)
            print(response.json()['status'])
        else:
            print("Stopping the script recording")
            response = requests.post('{0}?record_enable={1}'.format(HATCommands.RECORD_BUTTONS, 'n'), timeout=5)
            print(response.json()['status'])

    @staticmethod
    def get_screen(screen_grab=False, video_grab=False):
        """

        """
        try:
            response = requests.get(HATCommands.GRAB_SCREEN, timeout=10)
            if response:
                decompressed_response = zlib.decompress(response.content)
                captured_image = Image.frombytes('RGB', (800, 480), decompressed_response, 'raw', 'BGRX')
                # saving current image to display in gui window
                captured_image.save(Setting.FilePaths.image_hat_current_image)
                print(datetime.datetime.now(), 'imagegrab')
                if screen_grab:
                    # saving current image in test result/screenshots folder
                    captured_image.save(Setting.get_image_name())
                if Setting.ActivityStatus.screen_recording and video_grab:
                    # converting frame to video for video recorder
                    ClientHandler.convert_frames_to_video(input_file=Setting.FilePaths.image_hat_current_image,
                                                          output_file=Setting.ScreenRecodingSetting.videoWrite)
                return True
            return False
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def convert_frames_to_video(input_file, output_file=None):
        """

        """
        img = cv2.imread(input_file)
        height, width, _ = img.shape
        Setting.ScreenRecodingSetting.size = (width, height)
        if output_file is not None:
            output_file.write(img)
