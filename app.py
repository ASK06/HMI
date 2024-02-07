import os
import cv2
import time
import threading
from io import BytesIO
from settings import Setting
from view.interface_view_to_model import V2MHATMainWebApp, V2MClientHandler
from flask import Flask, render_template, jsonify, send_from_directory, make_response, request, session, send_file

app = Flask(__name__, static_folder=os.path.abspath("static"), template_folder=os.path.abspath("templates"))
app.secret_key = 'your_secret_key'  # Change this to a secure secret key
create_path = os.getcwd()


class WebApplication:
    def __init__(self):
        self.thread_video_record = None
        self.thread_ssh_connection = None
        self.thread_label_update = None
        self.thread_image_update = None
        self.thread_ssh_status = None
        self.thread_enable_disable_web_buttons = None
        self.backend_threads()
        self.setup_routes()

    def backend_threads(self):
        self.thread_ssh_status = threading.Thread(target=self.get_ssh_status, name="get and update ssh status...")
        self.thread_ssh_status.start()

    def setup_routes(self):
        app.add_url_rule('/', 'index', view_func=self.index)
        app.add_url_rule('/connect_hmi', 'hmi_connect', view_func=self.hmi_connect_handler,
                         methods=['POST'])
        app.add_url_rule('/disconnect_hmi', 'hmi_disconnect', view_func=self.hmi_disconnect_handler,
                         methods=['POST'])
        app.add_url_rule('/static/images/hat_current_image.jpg', view_func=self.get_current_image)
        app.add_url_rule('/update_image_route', view_func=self.update_image,
                         methods=['POST'])
        app.add_url_rule('/save_image_route', view_func=self.save_image,
                         methods=['POST'])
        app.add_url_rule('/start_video_recording', view_func=self.start_video_recorder,
                         methods=['POST'])
        app.add_url_rule('/stop_video_recording', view_func=self.stop_video_recorder,
                         methods=['POST'])
        app.add_url_rule('/press_key_route', view_func=self.press_key,
                         methods=['POST'])
        app.add_url_rule('/get_ssh_status', view_func=self.get_ssh_status,
                         methods=['GET'])
        app.add_url_rule('/record', view_func=self.start_record, methods=['POST'])
        app.add_url_rule('/downloadScript', view_func=self.download_script)

    def get_ssh_status(self):
        with app.app_context():
            try:
                if Setting.ModelViewConnector.ssh_connection_handler is not None and \
                        Setting.ModelViewConnector.ssh_connection_handler.ssh_client is not None and \
                        Setting.ModelViewConnector.ssh_connection_handler.ssh_client.get_transport() is not None:
                    Setting.ActivityStatus.ssh_connection_connected_status = \
                        Setting.ModelViewConnector.ssh_connection_handler.ssh_client.get_transport().is_active()

                if Setting.ActivityStatus.ssh_python_server and (
                        not Setting.ActivityStatus.ssh_connection_connected_status):
                    Setting.ActivityStatus.ssh_python_server = False
                    Setting.ActivityStatus.ssh_connection_connected_status = False
                    Setting.ModelViewConnector.ssh_connection_handler.ssh_client = None
                    Setting.ActivityStatus.script_recording = False
                    self.stop_video_recording()
                    V2MHATMainWebApp.ssh_disconnect()
                    if self.thread_ssh_connection is not None:
                        self.thread_ssh_connection.join()
                return jsonify(result=Setting.ActivityStatus.ssh_connection_connected_status,
                               server=Setting.ActivityStatus.ssh_python_server)
            except Exception as e:
                return jsonify({"result": False, "error": str(e)})

    @staticmethod
    def press_key():
        try:
            key_name = request.json.get("key_name")
            Setting.LabelStatus.keypad_current_keypress = key_name
            V2MClientHandler.emulate_button_press(key_info=key_name)
            return jsonify({"result": True})
        except Exception as e:
            return jsonify({"result": False, "error": str(e)})

    def start_video_recorder(self):
        with app.app_context():
            try:
                Setting.ActivityStatus.screen_recording = True
                if Setting.SaveOption.SaveVideo:
                    Setting.ScreenRecodingSetting.videoWrite = cv2.VideoWriter(Setting.get_screen_record_name(),
                                                                               cv2.VideoWriter_fourcc(*'mp4v'),
                                                                               Setting.ScreenRecodingSetting.fps,
                                                                               Setting.ScreenRecodingSetting.size)
                print("Starting the video thread...")
                self.thread_video_record = threading.Thread(target=self.live_monitoring,
                                                            name="Video Record Thread...")
                self.thread_video_record.start()
                return jsonify({"status": "success"})
            except Exception as e:
                print(e)

    def stop_video_recorder(self):
        Setting.ActivityStatus.screen_recording = False
        print("Stopping the video recording...Killing the thread..")
        if self.thread_video_record is not None:
            self.thread_video_record.join()
        return jsonify({"status": "success"})

    @staticmethod
    def update_image():
        with app.app_context():
            Setting.ActivityStatus.screen_capture = True
            if V2MClientHandler.get_screen():
                Setting.ActivityStatus.screen_capture = False
            return jsonify({"status": "success"})

    @staticmethod
    def save_image():
        with app.app_context():
            Setting.ActivityStatus.screen_capture = True
            if V2MClientHandler.get_screen(screen_grab=True):
                Setting.ActivityStatus.screen_capture = False
            return jsonify({"status": "success"})

    @staticmethod
    def run():
        if Setting.load_settings():
            app.run(debug=True)
        else:
            print("Error in loading application")

    @app.route('/')
    def index(self):
        return render_template('index.html')

    def hmi_connect_handler(self):
        with app.app_context():
            self.thread_ssh_connection = threading.Thread(target=V2MHATMainWebApp.ssh_connect, name="SSH Connection...")
            self.thread_ssh_connection.start()
            return jsonify(result="Connecting")

    def hmi_disconnect_handler(self):
        V2MHATMainWebApp.ssh_disconnect()
        if self.thread_ssh_connection is not None:
            self.thread_ssh_connection.join()
        return jsonify(result="Disconnected")

    @staticmethod
    def get_current_image():
        image_path = os.path.join(app.root_path, 'static', 'images')
        response = make_response(send_from_directory(image_path, 'hat_current_image.jpg'))
        response.headers['Cache-Control'] = 'no cache, no-store, must-revalidate'
        response.headers['Expires'] = '0'
        return response

    @staticmethod
    def live_monitoring():
        """

        :return:
        """
        print("Starting the live monitoring...")
        # Setting.ActivityStatus.screen_recording_live_monitoring = True
        try:
            while Setting.ActivityStatus.screen_recording:
                if not V2MClientHandler.get_screen(screen_grab=Setting.SaveOption.SaveImage,
                                                   video_grab=Setting.SaveOption.SaveVideo):
                    Setting.ErrorStatus.main_gui_error = True
                time.sleep(Setting.ScreenRecodingSetting.delay - 0.2)  # 0.2s  tolerance for recording the screens
                if not Setting.ActivityStatus.screen_recording:
                    break
        except Exception as e:
            print(e)
        finally:
            print("breaking the while loop...\nExiting the live monitoring...")
            if Setting.SaveOption.SaveVideo:
                for i in range(0, 5):
                    V2MClientHandler.convert_frames_to_video(input_file=f"{Setting.FilePaths.image_hat_watermark}",
                                                             output_file=Setting.ScreenRecodingSetting.videoWrite)
                Setting.ScreenRecodingSetting.videoWrite.release()
                Setting.ScreenRecodingSetting.videoWrite.release()

    def kill_all_thread(self):
        """
        kill_all_thread: kill all the running threads while turning off server.
        :return:
        """

        if self.thread_ssh_connection is not None:
            self.thread_ssh_connection.join()
            print("ssh thread closed")
        if self.thread_video_record is not None:
            self.thread_video_record.join()
            print("video record thread closed")
        # ThreadsHandler
        if self.thread_image_update is not None:
            self.thread_image_update.join()
            print("image update thread closed")
        if self.thread_label_update is not None:
            self.thread_label_update.join()
            print("label updated thread closed")
        if self.thread_enable_disable_web_buttons is not None:
            self.thread_enable_disable_web_buttons.join()
            print("enable disable web buttons thread closed")
        if self.thread_ssh_status is not None:
            print("thread_ssh_status closed")
            self.thread_ssh_status.join()

    def start_record(self):
        data = request.form
        project_name = data.get('projectName')
        test_name = data.get('testName')

        if project_name and test_name:
            # Store project and test names in Flask session
            session['project_name'] = project_name
            session['test_name'] = test_name

            # Create a directory in the project directory
            project_path = os.path.join(create_path, project_name, test_name, 'images')
            os.makedirs(project_path, exist_ok=True)

            return jsonify({'message': 'Record started successfully'})
        else:
            return jsonify({'error': 'Project Name and Test Name are required'}), 400

    def download_script(self):
        project_name = session.get('project_name')
        test_name = session.get('test_name')

        if project_name and test_name:
            # Path to the test name directory
            test_directory = os.path.join(create_path, project_name, test_name)

            # Path to the script file inside the test name directory
            script_path = os.path.join(test_directory, 'script.robot')

            # Generate script content (customize as needed)
            script_content = f"Your script content for {test_name}."

            # Write script content to the file
            with open(script_path, 'w') as script_file:
                script_file.write(script_content)

            # Return the file as an attachment
            return send_file(script_path, download_name=f"{test_name}_script.txt", as_attachment=True)

        return jsonify({'error': 'Project Name and Test Name not provided'}), 400


def main_app():
    Setting.ViewModelConnector.gui_main_handler = WebApplication()
    try:
        Setting.ViewModelConnector.gui_main_handler.run()
    except Exception as e:
        print(f"An exception occurred: {e}")
    finally:
        if Setting.ViewModelConnector.gui_main_handler is not None:
            print("Cleaning up...")
            Setting.ViewModelConnector.gui_main_handler.kill_all_thread()


if __name__ == '__main__':
    main_app()
