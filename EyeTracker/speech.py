def speech_to_text():
    import main
    import pyautogui as g
    import speech_recognition as sr
    
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio)
            except sr.UnknownValueError:
                print("No text input was supplied")
            else:
                print(text)
                if text == "spacebar":
                    g.press(" ")
                elif text == "recalibrate":
                    main.recalibrate()
                elif text == "exit":
                    main.should_stop = True
                else:
                    g.typewrite(text)