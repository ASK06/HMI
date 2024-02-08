import os

from flask import Flask, render_template

app = Flask(__name__, static_folder=os.path.abspath("static"), template_folder=os.path.abspath("templates"))
app.secret_key = 'your_secret_key'  # Change this to a secure secret key
create_path = os.getcwd()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/connect_hmi', methods=['POST'])
def hmi_connect_handler():
    # Your implementation for hmi_connect_handler
    pass


@app.route('/disconnect_hmi', methods=['POST'])
def hmi_disconnect_handler():
    # Your implementation for hmi_disconnect_handler
    pass


@app.route('/static/images/hat_current_image.jpg')
def get_current_image():
    # Your implementation for get_current_image
    pass


@app.route('/record', methods=['POST'])
def start_record():
    # Your implementation for start_record
    pass


@app.route('/downloadScript')
def download_script():
    # Your implementation for download_script
    pass
