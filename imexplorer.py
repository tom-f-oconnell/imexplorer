#!/usr/bin/env python3

import time
import io
import threading

from flask import Flask, render_template, Response

import numpy as np
from PIL import Image

app = Flask(__name__)

class Video(object):
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera

    def initialize(self):
        if Video.thread is None:
            # start background frame thread
            Video.thread = threading.Thread(target=self._thread)
            Video.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self):
        Video.last_access = time.time()
        self.initialize()
        return self.frame

    @classmethod
    def _thread(cls):
        shape = (128, 128)

        # TODO what do stream calls do?
        while True:
            img_byte_arr = io.BytesIO()
            Image.fromarray(np.uint8(np.random.rand(*shape) * 255)).save(img_byte_arr, format='JPEG')
            cls.frame = img_byte_arr.getvalue()

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds stop the thread
            if time.time() - cls.last_access > 10:
                break
            time.sleep(0.1)

        cls.thread = None

@app.route('/')
def index():
    return render_template('index.html')

def gen(video):
    while True:
        frame = video.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(Video()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

