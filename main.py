#!/usr/bin/env python3


import os
import datetime
import calendar
import cv2
import time
import random
from datetime import timedelta
from string import ascii_letters
from imutils.video import VideoStream
from flask import Flask, Response, render_template, url_for, session, redirect, request, send_from_directory
from dotenv import load_dotenv
from flask_socketio import SocketIO, emit

load_dotenv()

PASSWORD = os.getenv('PASSWORD')
LOCAL_IP = os.getenv('LOCAL_IP')

MESSAGES = []
MAX_MESSAGES_TO_DISPLAY = 100

TAKE_SCREENSHOT = False
RECORD_VIDEO = False



# Creating a video streaming object to get frames
vs = VideoStream(src=1).start()

fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
# out = cv2.VideoWriter('videos/out.mp4', fourcc, 20.0, (1920, 1080))
out = None

# Builtin camera stream object creating.
# vs_builtin = VideoStream(src=1).start()

connected_users = 0

app = Flask(__name__)
app.config['SECURITY_KEY'] = 'VerySecretKey!'
app.secret_key = 'key'
app.permanent_session_lifetime = timedelta(hours=10)
socketio = SocketIO(app)


# Video class
# -----------------------------------------------------------------------------

# Not implemented

# Utilities
# -----------------------------------------------------------------------------
def date_to_string(year, month, day):

    date = datetime.datetime(year, month, day)
    month_name = calendar.month_name[month]
    day_name = calendar.day_name[date.weekday()]

    return f'{day_name}, {day} {month_name} {year}'


def random_name(length):
    return ''.join(random.choice(ascii_letters) for _ in range(length))




# Socket IO block. Real time interaction with the client side
# -----------------------------------------------------------------------------
@socketio.on('connect')
def on_connect():
    global connected_users
    connected_users += 1
    client_id = request.sid  # type: ignore
    emit('name_announce', session['name'], room=client_id)
    on_message('<CONNECTED>')


@socketio.on('disconnect')
def on_disconnect():
    global connected_users
    connected_users -= 1

    on_message('<DISCONNECTED>')


@socketio.on('message')
def on_message(message):
    global TAKE_SCREENSHOT, RECORD_VIDEO, out


    if message == '<CONNECTED>':
        MESSAGES.append(f'\n{time.strftime("%H:%M:%S")}:USER - Anonymous : "{session["name"]}" CONNECTED !!!\n')

    elif message == '<DISCONNECTED>':
        MESSAGES.append(f'\n{time.strftime("%H:%M:%S")}:USER - Anonymous : "{session["name"]}" DISCONNECTED !!!\n')

    elif message == '<SCREENSHOT>':
        TAKE_SCREENSHOT = True
        return

    elif message == '<START_RECORD>':
        out = cv2.VideoWriter(f'videos/{time.strftime("%Y%m%d_%H%M%S")}.mp4', fourcc, 20.0, (1920, 1080))
        RECORD_VIDEO = True
        print(f'[INFO] START RECORD message received {RECORD_VIDEO=}')
        return

    elif message == '<STOP_RECORD>':
        RECORD_VIDEO = False
        print(f'[INFO] STOP RECORD message received {RECORD_VIDEO=}')
        return

    else:
        MESSAGES.append(f'{time.strftime("%H:%M:%S")} {session["name"]}:  {message}')

    data = '\n'.join(MESSAGES) if len(MESSAGES) <= MAX_MESSAGES_TO_DISPLAY else \
        '\n'.join(MESSAGES[-MAX_MESSAGES_TO_DISPLAY:])

    emit('display_messages', {'chat': data}, broadcast=True)


# Function yields frames from the webcam
# -----------------------------------------------------------------------------

def stream_from_webcam():

    global TAKE_SCREENSHOT, RECORD_VIDEO, out


    while True:

        frame = vs.read()  


        if TAKE_SCREENSHOT:

            cv2.imwrite(f'screenshots/{time.strftime("%Y%m%d_%H%M%S")}.jpg', frame)   # type: ignore
            TAKE_SCREENSHOT = False
            print('[INFO] Took a Screenshot')

        timestamp = datetime.datetime.now()
        cv2.putText(frame, f'{timestamp.strftime("%Y-%m-%d %H:%M:%S")}{" " * 3}Viewers: {connected_users}',  # type: ignore
                    (10, frame.shape[0] - 10),  # type: ignore
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 0, 255), 2)


        if RECORD_VIDEO:
            out.write(frame)  # type: ignore
        else:
            if out:
                out.release()
                out = None



        encodedImage = cv2.imencode(".jpg", frame)[1].tobytes()     # type: ignore

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')





# HTML pages
# -----------------------------------------------------------------------------
@app.route("/video_from_external_webcam")
def external_cam_video():

    # return the response generated along with the specific media
    # type (mime type)

    return Response(stream_from_webcam(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route('/screenshots/<file_name>')
def show_photo(file_name):
    return send_from_directory('screenshots', file_name)


@app.route("/")
def index():
    # return the rendered template
    if not session.get('name', 0):

        session.permanent = True
        session['name'] = random_name(7)

    return render_template("index.html")


@app.route('/screenshots')
def screenshots():

    cwd = os.getcwd()

    file_names = os.listdir(f'{cwd}{os.sep}screenshots')
    dates_files = [(os.path.getctime(f'{cwd}{os.sep}screenshots{os.sep}{file_name}'), file_name) for file_name in file_names]
    dates_files.sort(reverse=True)

    images = [dt[1] for dt in dates_files]



    # days = sorted(set([int(name[:8]) for name in file_names]), reverse=True)
    #
    # by_days = {str(day): [name for name in file_names if name.startswith(str(day))] for day in days}
    #
    # full_dates = {date_to_string(int(day[:4]), int(day[4:6]), int(day[6:])): by_days[day] for day in by_days}

    return render_template("screenshots.html", full_dates=images)



@app.route('/gallery/<file_name>')
def gallery(file_name):

    cwd = os.getcwd()

    file_names = os.listdir(f'{cwd}{os.sep}screenshots')
    dates_files = [(os.path.getctime(f'{cwd}{os.sep}screenshots{os.sep}{file_name}'), file_name) for file_name in
                   file_names]
    dates_files.sort(reverse=True)

    images = [row[1] for row in dates_files]
    image_index = images.index(file_name)


    # images = os.listdir(f'{os.getcwd()}/screenshots')
    # image_index = images.index(file_name)

    return render_template('gallery.html', images=images, image_index=image_index)



def run_server():
    socketio.run(app, host='localhost', port=9999, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)



if __name__ == '__main__':
    try:
        run_server()
    except Exception as ex:
        print(f'\033[31m[ERROR]\033[0m Occurred Exception => {ex}')
        run_server()




# Releasing Video Streaming pointer
vs.stop()
if out:
    out.release()
cv2.destroyAllWindows()

