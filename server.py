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
        session['level'] = 1
        return render_template('master.html', username=session.get('name'), tracks=session.get('tracks'))
    else:
        return redirect('/')


@app.route("/new_track")
def new_track():
    if session.get('guide_passed') and session.get('logged_in'):
        if len(session.get('tracks'))<4:
            type = request.args.get('type')
            length = request.args.get('length')
            session_tracks = session.get('tracks')
            track_nrs = []
            for i in session_tracks:
                track_nrs.append(i[0])
            print(session_tracks)
            for i in range(1,5):
                if i not in track_nrs:
                    session_tracks.append([i, 'Taśma '+str(i),int(type),[], int(length)])
                    print(session_tracks)
                    session['tracks'] = session_tracks
                    break
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
    session_tracks[data['track']-1][3].append([int(data['append0']), int(data['append1']), int(data['time']), 0])
    session['tracks'] = session_tracks
    return redirect("/master_tape")

@app.route("/sync_2", methods=['POST'])
def sync_2():
    result = []
    data = request.get_json()
    session_tracks = session.get('tracks')
    session_tracks[data['track']-1][3].remove([int(data['remove0']), int(data['remove1']), int(data['time']), 0])
    session['tracks'] = session_tracks
    return redirect("/master_tape")

@app.route("/sync_3", methods=['POST'])
def sync_3():
    result = []
    data = request.get_json()
    session_tracks = session.get('tracks')
    session_tracks[data['track']-1][3].append([int(data['append0']), int(data['append1']), int(data['time']), 1])
    session['tracks'] = session_tracks
    return redirect("/master_tape")


@app.route("/del_track")
def del_track():
    no = request.args.get('no')
    if session.get('logged_in'):
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
    if session.get('logged_in'):
        session['guide_passed'] = True
        session['tracks'] = []
        return redirect('/master_tape')
    else:
        return redirect('/')

@app.route("/guide")
def guide():
    if session.get('logged_in'):
        return render_template('guide.html', username=session.get('name'))


@app.route("/get_note")
def get_note():
    length = int(request.args.get('length'))

    for i in range(24):
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        track.append(Message('control_change', control=32, value=127, time=0))
        track.append(Message('program_change', program=25, time=0))
        track.append(Message('note_on', note=48+i, velocity=90, time=0))
        track.append(Message('note_off', note=48+i, velocity=90, time=length))
        track.append(Message('note_off', note=48+i, velocity=90, time=2*length))

        mid.save('temp.mid')

        fs = FluidSynth('/Users/piotrek/Library/Audio/Sounds/Banks/fluid_r3_gm.sf2')
        fs.midi_to_audio('temp.mid', "static/audio/guitar/"+str(i)+"_"+str(length)+'.wav')

    return redirect('/')


@app.route("/login", methods=['POST', 'GET'])
def login():
    if session.get('logged_in'):
        return redirect('/')
    else:
        session['logged_in'] = True
        session['name'] = request.form['name']
        return redirect('/')

@app.route("/end_game")
def end():
    if session.get('logged_in'):
        session['logged_in'] = False
        session['guide_passed'] = False
        session['tracks'] = []
        return redirect('/')
    else:
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
