def speech_to_text():
    import pyautogui as g
    import speech_recognition as sr

    r = sr.recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        text = r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS)

        if text == "spacebar":
            g.press(" ")

        if text == "recalibrate":
            recalibrate()

        else:
            g.typewrite(text)
            
