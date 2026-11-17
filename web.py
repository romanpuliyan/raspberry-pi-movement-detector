from flask import Flask
import os

CAMERA_FOLDER_PATH = "path_to_folder_with_photos"
LOG_FILE_NAME = CAMERA_FOLDER_PATH + "/photo_logs.txt"
previous_line_counter = 0

app = Flask(
    __name__,
    static_url_path=CAMERA_FOLDER_PATH,
    static_folder=CAMERA_FOLDER_PATH
)


@app.route("/")
def index():
    return "Hello from Flask"


@app.route("/check-photos")
def check_photos():
    global previous_line_counter
    line_counter = 0
    if os.path.exists(LOG_FILE_NAME):
        last_photo_filename = ""
        with open(LOG_FILE_NAME, "r") as f:
            for line in f:
                line_counter += 1
                last_photo_filename = line.rstrip()
        difference = line_counter - previous_line_counter
        previous_line_counter = line_counter
        message = str(difference) + " new photos since you last checked<br/>"
        message += "Last photo: " + last_photo_filename + "<br/>"
        message += "<img src='" + last_photo_filename + "'>"
        return message
    else:
        return "No photo available"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
