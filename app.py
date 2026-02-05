from flask import Flask, render_template, request, jsonify
import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import pyttsx3
from playsound import playsound
import time
import os

app = Flask(__name__)
LANGUAGES = {
    "English":   {"stt": "en-IN", "tts": "en"},
    "Tamil":     {"stt": "ta-IN", "tts": "ta"},
    "Hindi":     {"stt": "hi-IN", "tts": "hi"},
    "Telugu":    {"stt": "te-IN", "tts": "te"},
    "Malayalam": {"stt": "ml-IN", "tts": "ml"},
    "Kannada":   {"stt": "kn-IN", "tts": "kn"},
    "French":    {"stt": "fr-FR", "tts": "fr"},
    "Spanish":   {"stt": "es-ES", "tts": "es"},
    "German":    {"stt": "de-DE", "tts": "de"},
    "Chinese":   {"stt": "zh-CN", "tts": "zh-CN"},
    "Japanese":  {"stt": "ja-JP", "tts": "ja"},
    "Korean":    {"stt": "ko-KR", "tts": "ko"},
}
def speak(text, lang, voice):
    if lang == "en":
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")

        # Windows default voices:
        # 0 → Male (David)
        # 1 → Female (Zira)

        if voice == "Male":
            engine.setProperty("voice", voices[0].id)
        else:
            engine.setProperty("voice", voices[1].id)

        engine.setProperty("rate", 160)
        engine.say(text)
        engine.runAndWait()
    else:
        filename = f"voice_{int(time.time())}.mp3"

        tts = gTTS(text=text, lang=lang)
        tts.save(filename)

        playsound(filename)     # NO media player popup
        os.remove(filename)
@app.route("/")
def index():
    return render_template("index.html", languages=LANGUAGES.keys())


@app.route("/translate", methods=["POST"])
def translate():
    try:
        data = request.json

        src = data["source"]
        tgt = data["target"]
        duration = int(data["duration"])
        voice = data["voice"]

        fs = 16000
        wavfile = "input.wav"
        recording = sd.rec(
            int(duration * fs),
            samplerate=fs,
            channels=1,
            dtype="int16"
        )
        sd.wait()

        wav.write(wavfile, fs, recording)
        recognizer = sr.Recognizer()

        with sr.AudioFile(wavfile) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(
            audio,
            language=LANGUAGES[src]["stt"]
        )
        translated = GoogleTranslator(
            source=LANGUAGES[src]["tts"],
            target=LANGUAGES[tgt]["tts"]
        ).translate(text)
        speak(translated, LANGUAGES[tgt]["tts"], voice)

        return jsonify({
            "input": text,
            "output": translated
        })

    except Exception as e:
        return jsonify({"error": str(e)})
if __name__ == "__main__":
    app.run(debug=True)
