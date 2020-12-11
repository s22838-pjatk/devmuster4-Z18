# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, redirect, request, send_from_directory, jsonify, session
import glob, os
import time
import threading
from pydub import AudioSegment
from midi2audio import FluidSynth
from mido import Message, MidiFile, MidiTrack


app = Flask(__name__)

fs = FluidSynth('/Users/piotrek/Library/Audio/Sounds/Banks/fluid_r3_gm.sf2')


@app.route("/")
def index():
    if not session.get('logged_in'):
        return redirect('/login')
    else:
        return render_template('index.html')


@app.route("/get_note")
def get_note():
    pitch = request.args.get('pitch')
    length = request.args.get('length')

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(Message('note_on', note=int(pitch), velocity=127, time=0))
    track.append(Message('note_off', note=int(pitch), velocity=127, time=int(length)))

    mid.save(session.get('username/')+str(pitch)+'_'+str(length)+'.mid')

    # using the default sound font in 44100 Hz sample rate
    fs.midi_to_audio(
        session.get('username/')+str(pitch)+'_'+str(length)+'.mid',
        session.get('username/')+str(pitch)+'_'+str(length)+'.wav'
    )

    return render_template('index.html')


@app.route("/login")
def login():
    if session.get('logged_in'):
        return redirect('/')
    else:
        session['logged_in'] = True
        session['name'] = request.args.get('name')
        return redirect('/')


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
