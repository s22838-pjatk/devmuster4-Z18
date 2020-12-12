# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, redirect, request, send_from_directory, jsonify, session
import glob
import time
import json
from pydub import AudioSegment
from midi2audio import FluidSynth
from mido import Message, MidiFile, MidiTrack


app = Flask(__name__)
with open("secret.key", "rb") as f:
    app.secret_key = f.read()

fs = FluidSynth('/Users/piotrek/Library/Audio/Sounds/Banks/fluid_r3_gm.sf2')


@app.route("/")
def index():
    if not session.get('logged_in'):
        return render_template('loading.html')
    else:
        return redirect('/master_tape')


@app.route("/master_tape")
def master_tape():
    if not session.get('guide_passed') and session.get('logged_in'):
        return render_template('guide.html', username=session.get('name'))
    elif session.get('guide_passed') and session.get('logged_in'):
        return render_template('master.html', username=session.get('name'), tracks=session.get('tracks'))
    else:
        return redirect('/')


@app.route("/new_track")
def new_track():
    if session.get('guide_passed') and session.get('logged_in'):
        if len(session.get('tracks'))<4:
            type = request.args.get('type')
            session_tracks = session.get('tracks')
            track_nrs = []
            for i in session_tracks:
                track_nrs.append(i[0])
            if track_nrs != []:
                val = max(track_nrs)+1
            else:
                val = 1
            session_tracks.append([val, 'Taśma '+str(val),int(type),[]])
            session['tracks'] = session_tracks
            return redirect("/master_tape")
        else:
            return render_template('master.html', username=session.get('name'), tracks=session.get('tracks'), err=1)
    else:
        return redirect('/')


@app.route("/sync", methods=['POST'])
def sync():
    result = []
    data = request.get_json()
    session_tracks = session.get('tracks')
    session_tracks[data['track']-1][3].append([int(data['append0']), int(data['append1'])])
    session['tracks'] = session_tracks
    return redirect("/master_tape")


@app.route("/del_track")
def del_track():
    no = request.args.get('no')
    if session.get('guide_passed') and session.get('logged_in'):
        session_tracks = session.get('tracks')
        for i in session_tracks:
            if i[0]==int(no):
                session_tracks.remove(i)
        session['tracks'] = session_tracks
        return redirect("/master_tape")
    else:
        return redirect('/')


@app.route("/guide_done")
def guide_done():
    if not session.get('guide_passed') and session.get('logged_in'):
        session['guide_passed'] = True
        session['tracks'] = []
        return redirect('/master_tape')
    else:
        return redirect('/')


@app.route("/get_note")
def get_note():
    pitch = request.args.get('pitch')
    length = request.args.get('length')

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)
    track.append(Message('note_on', note=int(pitch), velocity=127, time=0))
    track.append(Message('note_off', note=int(pitch), velocity=127, time=int(length)))

    mid.save(session.get('username')+"/"+str(pitch)+'_'+str(length)+'.mid')

    # using the default sound font in 44100 Hz sample rate
    fs.midi_to_audio(
        session.get('username')+"/"+str(pitch)+'_'+str(length)+'.mid',
        session.get('username')+"/"+str(pitch)+'_'+str(length)+'.wav'
    )

    return render_template('index.html')


@app.route("/login", methods=['POST', 'GET'])
def login():
    if session.get('logged_in'):
        return redirect('/')
    else:
        session['logged_in'] = True
        session['name'] = request.form['name']
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
