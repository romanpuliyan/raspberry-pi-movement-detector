from gpiozero import MotionSensor, LED, Button
from picamzero import Camera
from signal import pause
import yagmail
import time
import os

# Global variables
MOVEMENT_DETECTED_TRESHOLD = 3.0
MIN_DURATION_BETWEEN_PHOTOS = 30.0
CAMERA_FOLDER_PATH = "path_to_folder_with_photos"
LOG_FILE_NAME = CAMERA_FOLDER_PATH + "/photo_logs.txt"
timeMotionStarted = time.time()
lastTimePhotoTaken = 0

# Setup email
password = ""
# password from gmail application saved in hidden file
with open("path_to_file_with_email_application_password", "r") as f:
    password = f.read().rstrip()
yag = yagmail.SMTP("sender_email@gmail.com", password)
print("Email setup OK")

# Setup Camera
camera = Camera()
camera.still_size = (1536, 864)
# camera.flip_camera(vflip=True, hflip=True)
time.sleep(2)  # Delay for correct camera setup
if not os.path.exists(CAMERA_FOLDER_PATH):
    os.mkdir(CAMERA_FOLDER_PATH)
print("Camera setup OK")

# Setup GPIO
pir = MotionSensor(4)
ledRed = LED(17)
ledGreen = LED(27)
ledYellow = LED(22)
button = Button(26, bounce_time=0.05)
print("GPIOs setup OK")


def take_photo(camera, folderPath):
    fileName = folderPath + "/img_" + str(get_current_timestamp()) + ".jpg"
    camera.take_photo(fileName)
    return fileName


def remove_log_file(logFileName):
    if os.path.exists(logFileName):
        os.remove(logFileName)
        print("Previous log file removed")


def update_photo_log_file(logFileName, photoFileName):
    with open(logFileName, "a") as f:
        f.write(photoFileName)
        f.write("\n")


def send_photo_by_email(yagmailClient, fileName):
    yagmailClient.send(
        to="receiver_email@gmail.com",
        subject="New photo from Raspberry Pi",
        contents="Check out new photo",
        attachments=fileName
    )


def leds_on():
    ledRed.on()
    ledGreen.on()
    ledYellow.on()


def leds_off():
    ledRed.off()
    ledGreen.off()
    ledYellow.off()


def get_current_timestamp():
    return time.time()


def motion_detected():
    global timeMotionStarted
    print("Starting motion timer")
    timeMotionStarted = get_current_timestamp()
    leds_on()


def motion_finished():
    global lastTimePhotoTaken
    leds_off()
    motionDuration = get_current_timestamp() - timeMotionStarted
    print(motionDuration)
    if motionDuration > MOVEMENT_DETECTED_TRESHOLD:
        if get_current_timestamp() - lastTimePhotoTaken > MIN_DURATION_BETWEEN_PHOTOS:
            lastTimePhotoTaken = get_current_timestamp()
            print("Taking a photo and sending it by email")
            photoFileName = take_photo(camera, CAMERA_FOLDER_PATH)
            update_photo_log_file(LOG_FILE_NAME, photoFileName)
            send_photo_by_email(yag, photoFileName)


def finish_program():
    leds_off()
    print("Program finished")
    os._exit(0)


try:
    remove_log_file(LOG_FILE_NAME)
    leds_off()

    pir.when_motion = motion_detected
    pir.when_no_motion = motion_finished
    button.when_pressed = finish_program

    pause()
except KeyboardInterrupt:
    print("\nProgramm stopped")
