import globals
import query

def speech_to_text():
    import main
    import pyautogui as g
    import speech_recognition as sr
    import webbrowser
    import os
    
    last_scrollup = 400
    last_scrolldown = 400

    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            audio = r.listen(source)
            try:
                text = r.recognize_google_cloud(audio, credentials_json=open("google-credentials.json").read()).strip()
            except sr.UnknownValueError as e:
                pass
            else:
                print(f'"{text}"')
                if text == "spacebar":
                    g.press(" ")
                elif text.startswith("type "):
                    _, rest = text.split(" ", maxsplit=1)
                    g.typewrite(rest)
                elif "calibrate" in text.lower():
                    print("Recalibrating...")
                    globals.should_calibrate = True
                    globals.has_bottomright = False
                    globals.has_topleft = False
                    globals.msg_bottomright = False
                    globals.msg_topleft = False
                elif text.lower() in ["exit", "stop", "quit"]:
                    print("You indicated that you wanted to stop...")
                    globals.should_stop = True
                elif text.lower().startswith("website "):
                    webbrowser.open('http://' + text.lower().split()[1])
                elif text.lower() in ['done', 'complete']:
                    globals.said_done = True
                elif text.lower() == "click": 
                    g.click()
                elif text.lower() == "right click":
                    g.rightClick()
                elif text.lower() == "left click":
                    g.leftClick()
                elif text.lower() == "double click":
                    g.doubleClick()
                elif text.lower() == "scroll down":
                    g.scroll(-last_scrolldown)
                    if last_scrolldown < 3200:
                        last_scrolldown *= 2
                elif text.lower() == "scroll up":
                    g.scroll(last_scrollup)
                    if last_scrollup < 3200:
                        last_scrollup *= 2
                elif text.lower() == "discord":
                    os.system("Discord.exe")
                elif text.lower() == "minecraft":
                    os.system("Minecraft.exe")
                elif text.lower() == "pie charm":
                    os.system("Pycharm.exe")
                elif text.lower().startswith("query"):
                    print(' '.join(query.webQuery(text.lower.split()[1:]))

                if text.lower() != 'scroll up':
                    last_scrollup = 400
                if text.lower() != 'scroll down':
                    last_scrolldown = 400
