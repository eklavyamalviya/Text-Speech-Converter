from flask import Flask,json,request, jsonify, request, send_file, make_response,render_template,redirect,url_for,session
from werkzeug.exceptions import RequestURITooLarge
from werkzeug.wrappers import Response
import youtube_dl
from flask_cors import CORS
import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os
import json
from json import JSONEncoder
import subprocess
from googletrans import Translator
import googletrans
from gtts import gTTS

app = Flask(__name__)
app.secret_key = "your secret secret key"
CORS(app)

translator = Translator()

@app.route('/')
def home():
    a=googletrans.LANGUAGES
    return render_template('demo.html',sdata=a.items())

@app.route('/home')
def home1():
    a=googletrans.LANGUAGES
    return render_template('demo.html',sdata=a.items())
@app.route('/feed')
def feedback():
    return render_template('demo4.html')

@app.route('/about')
def about():
    return render_template('demo5.html')


r = sr.Recognizer()

silence_thresh= -16.0
def db_to_float(db, using_amplitude=True):
    i=0
    db = float(db)
    if using_amplitude:
        return 10**(db / 20)
    else:  # using power
        return 10**(db / 10)
def get_large_audio_transcription():
    command = 'ffmpeg -i song.m4a -vn -ar 44100 -ac 2 -b:a 192k -y song.mp3'
    subprocess.call(command,shell=True)
    sound = AudioSegment.from_file("./song.mp3")
    chunks = split_on_silence(sound,
        min_silence_len =570,                              
        silence_thresh = sound.dBFS-16,
        keep_silence=400,
    )
    folder_name = "Desktop"
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    whole_text = ""
    for i, audio_chunk in enumerate(chunks, start=1):
        chunk_filename = os.path.join(folder_name, "Desktop")
        audio_chunk.export(chunk_filename, format="wav")
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = r.record(source)
            try:
                text = r.recognize_google(audio_listened)
            except sr.UnknownValueError as e:
                i+=1
                print("Error:", str(e),i)
            else:
                text = f"{text.capitalize()}. "
                whole_text += text
    t = translator.translate(whole_text,dest=session['lang'])
    return t.text


class EmployeeEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__

@app.route('/ekl',methods=['POST','GET'])
def download():
    f = session['f']
    t=session['t']
    if f == 'voice':
        mytext = t
        language = session['lang']
        myobj = gTTS(text=mytext,slow=True)
        myobj.save("welcome.mp3")
        resp = make_response(send_file("./welcome.mp3", mimetype='audio/wav', as_attachment=True, attachment_filename="converted.mp3"))
        return resp
    elif f == 'text':
        res = Response(t,mimetype="text/csv",headers={"Content-disposition":"attachment; filename=converted.txt"})
        return res

@app.route('/down',methods=['POST','GET'])
def down():
    url = session['url']
    mp3_file_name = get_mp3(url)
    t=get_large_audio_transcription()
    session['t']=t
    return jsonify(t)

def get_mp3(url):
  try:
    os.remove('song.m4a')
  except:
    pass  
  video_info = youtube_dl.YoutubeDL().extract_info(url, download=False)
  file_name = "song.m4a"
  options = {'format': 'bestaudio/best','keepvideo': False,'outtmpl': file_name,'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'm4a','preferredquality': '192',}]}
  with youtube_dl.YoutubeDL(options) as download:
    download.download([url])
  return file_name

@app.route('/audio', methods=['POST','GET'])
def download_mp3():
    session['url'] = request.form['link']
    session['f'] = request.form['for']
    session['lang'] = request.form['lang']
    return render_template('demo3.html')

if __name__ == '__main__':
    app.run(debug=True)