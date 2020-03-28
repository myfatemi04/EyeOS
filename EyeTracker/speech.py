import main
import pyautogui as g
import speech_recognition as sr

def speech_to_text():

    r = sr.recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        text = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)

        if text == "spacebar":
            g.press(" ")
        elif text == "recalibrate":
            main.recalibrate()
        elif text == "exit":
            main.should_stop = True
        else:
            g.typewrite(text)
