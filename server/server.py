from flask import Flask, jsonify, request
import subprocess
import zlib
import os
import sys
import time
from api import API, KeyCode
import threading
import datetime

app = Flask(__name__)
record_enable = False
script_file_name = None


@app.route('/grab_screen')
def grab_screen():
    try:
        result = subprocess.check_output(['cat', '/dev/fb0'])
        if result:
            compressed_result = zlib.compress(result)
            # print(len(compressed_result))
            return compressed_result
            # return jsonify(status='Success', frame_buffer=compressed_result.decode('utf-8'))
        else:
            return jsonify(status='Error', message='No frame grabbed')
    except Exception as ex:
        return jsonify(status='Error', message=ex)


@app.route('/record_buttons', methods=['POST'])
def record_buttons():
    global record_enable, script_file_name
    rec = request.args.get('record_enable')
    if rec == 'y':
        script_file_name = script_file_name = './HATServer/Scripts/HMI_button_tracer_' + datetime.datetime.now(). \
            strftime('%d-%m-%y_%H:%M:%S').replace(':', '_') + ".hmi"
        record_enable = True
    elif rec == 'n':
        record_enable = False
        script_file_name = None
    return jsonify(status='Success')


record_thread = None


def record():
    global record_enable, record_thread, script_file_name
    dev = os.open("/dev/input/event0", os.O_RDWR)
    timer_status = False
    start_timer = 0
    wait_timer = 0
    try:
        while True:
            response = os.read(dev, 24)
            code = int.from_bytes(response[10:12], 'little')
            value = int.from_bytes(response[12:], 'little')
            print("Code Name: " + str(code))
            print("Value Name: " + str(value))
            if value == 1:
                message = 'PRESSED {}'.format(KeyCode(code).name)
                if record_enable:
                    print(message)
                    if timer_status:
                        stop_timer = time.time()
                        wait_timer = int(stop_timer - start_timer)
                        timer_status = False
                    with open(script_file_name, 'a') as script:
                        if wait_timer >= 1:
                            script.write("WAIT " + str(wait_timer) + '\n')
                        script.write(KeyCode(code).name + '\n')
            else:
                if not timer_status:
                    start_timer = time.time()
                    timer_status = True
    except Exception as ex:
        print(ex)


@app.route('/emulate_button', methods=['POST'])
def emulate_button():
    button = request.args.get('b')
    if button is not None:
        dev = None
        try:
            dev = os.open("/dev/input/event0", os.O_RDWR)
            if button == 'MMP_KEY':
                for seq in API.MMP_KEY_seq1:
                    os.write(dev, seq)
                time.sleep(5)
                for seq in API.MMP_KEY_seq2:
                    os.write(dev, seq)
            elif button == 'GA_KEY':
                for seq in API.GA_KEY_seq1:
                    os.write(dev, seq)
                time.sleep(5)
                for seq in API.GA_KEY_seq2:
                    os.write(dev, seq)
            else:
                key_sequence = eval('API.{0}'.format(button))
                for sequence in key_sequence:
                    os.write(dev, sequence)
            os.close(dev)
            return jsonify(status='Success')
        except Exception as ex:
            print(ex)
            if dev is not None:
                os.close(dev)
            return jsonify(status='Error', message=ex)
    return jsonify(status='Error', message='No Button Request')


def __configure_app():
    """
    This function reads configuration for Flask from the config.py Python file

    :return: None

    """
    if getattr(sys, 'freeze', False):
        # running as bundle (aka frozen)
        #  MEIPASS is a temporary folder for pyinstalller
        bundle_dir = sys._MEIPASS
    else:
        # running live
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    # loads configuration data from config.py
    app.config.from_pyfile(os.path.join(bundle_dir, 'config.py'), silent=True)


def main():
    global record_thread
    __configure_app()
    record_thread = threading.Thread(target=record, name='record_button_thread')
    record_thread.setDaemon(True)
    record_thread.start()
    print('HAT Server Version {0} listening to incoming connections...'.format(app.config['VERSION']))
    app.run(host='192.168.44.30', port=9046)


if __name__ == '__main__':
    main()
