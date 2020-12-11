# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, redirect, request, send_from_directory, jsonify
import glob, os
import time
import threading
from pydub import AudioSegment


app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/render_audio')
def render_audio(path):
    sound1 = AudioSegment.from_mp3("static/sample/sample1.mp3")
    sound2 = AudioSegment.from_mp3("static/sample/sample2.mp3")

    # mix sound2 with sound1, starting at 200ms into sound1
    output = sound1.overlay(sound2, position=200)

    # save the result
    output.export("export.mp3", format="mp3")
    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
