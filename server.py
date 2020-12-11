# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, redirect, request, send_from_directory, jsonify
import glob, os
import time
import threading


app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
