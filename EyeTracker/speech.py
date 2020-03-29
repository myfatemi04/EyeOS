import globals
import subprocess
import platform

custom_keys = {
    "pipe": "|",
    "or": "|",
    "at": "@",
    "dollarsign": "$",
    "opensquarebracket": "[",
    "closesquarebracket": "]",
    "openparentheses": "(",
    "closeparentheses": ")",
    "dot": ".",
    "period": ".",
    "point": ".",
    "exclamationmark": "!",
    "questionmark": "?",
    "equals": "=",
    "greaterthan": ">",
    "lessthan": "<",
    "backslash": "\\",
    "slash": "/",
    "caret": "^",
    "carrot": "^",
    "ampersand": "&",
    "and": "&",
    "percent": "%",
    "percentsign": "%",
    "hash": "#",
    "pound": "#",
    "hashtag": "#",
    "tilde": "~",
    "tilda": "~",
    "backquote": "`",
    "dash": "-",
    "hyphen": "-",
    "minus": "-",
    "underscore": "_",
    "plus": "+",
    "opencurlybrace": "{",
    "closecurlybrace": "}",
    "semicolon": ";",
    "colon": ":",
    "comma": ",",
    "apostrophe": "'",
    "quote": "\"",
    "quotationmark": "\"",
    "doublequote": "\"",
    "singlequote": "\'",
    "star": "*",
    "asterisk": "*",
    "space": " ",
    "spacebar": " ",
    "return": "\r",
    "newline": "\n",
    "enter": "\n"
}

def speech_to_text():
    import main
    import pyautogui as g
    import speech_recognition as sr
    import webbrowser
    import os
    import start_menu
    
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
                lower = text.lower()
                if text == "spacebar":
                    g.press(" ")
                elif text.startswith("type "):
                    _, rest = text.split(" ", maxsplit=1)
                    g.typewrite(rest)
                elif "calibrate" in lower:
                    print("Recalibrating...")
                    globals.should_calibrate = True
                    globals.has_bottomright = False
                    globals.has_topleft = False
                    globals.msg_bottomright = False
                    globals.msg_topleft = False
                    globals.has_nose_center = False
                    globals.has_nose_move = False
                    globals.msg_center = False
                    globals.msg_movenose = False
                elif lower in ["exit", "stop", "quit"]:
                    print("You indicated that you wanted to stop...")
                    globals.should_stop = True
                elif lower.startswith("website "):
                    webbrowser.open('http://' + lower.split(" ", maxsplit=1)[1].replace(" ", ""))
                elif lower in ['done', 'complete', 'completed', 'dime']:
                    globals.said_done = True
                elif lower == "click": 
                    g.leftClick()
                elif lower == "right click":
                    g.rightClick()
                elif lower == "left click":
                    g.leftClick()
                elif lower == "double click":
                    g.doubleClick()
                elif lower == "scroll down":
                    g.scroll(-last_scrolldown)
                    if last_scrolldown < 3200:
                        last_scrolldown *= 2
                elif lower == "scroll up":
                    g.scroll(last_scrollup)
                    if last_scrollup < 3200:
                        last_scrollup *= 2
                elif lower.startswith("press "):
                    key = text[6:]
                    slug = key.replace(" ", "").lower()
                    if slug in custom_keys:
                        key_symbol = custom_keys[slug]
                        g.press(key_symbol)
                    elif slug in g.KEY_NAMES:
                        g.press(slug)
                    else:
                        print("Key not found: ", key)
                elif lower.startswith("hold "):
                    key = text[5:]
                    slug = key.replace(" ", "").lower()
                    if slug in custom_keys:
                        key_symbol = custom_keys[slug]
                        g.keyDown(key_symbol)
                    elif slug in g.KEY_NAMES:
                        g.keyDown(slug)
                    else:
                        print("Key not found: ", key)
                elif lower.startswith("release "):
                    key = text[8:]
                    slug = key.replace(" ", "").lower()
                    if slug in custom_keys:
                        key_symbol = custom_keys[slug]
                        g.keyDown(key_symbol)
                    elif slug in g.KEY_NAMES:
                        g.keyDown(slug)
                    else:
                        print("Key not found: ", key)
                elif text.startswith("open "):
                    o, search = text.split(" ", maxsplit=1)
                    found = start_menu.find_links(search)
                    if not found:
                        print("No files found!")
                    else:
                        best_file, _ = found[0]
                        print(best_file)
                        if platform.system() == "Windows":
                            os.system(f"start \"\" \"{best_file}\"")
                        
                elif "backspace" in lower:
                    g.press("backspace")
                elif 'center' in lower or 'censor' in lower:
                    globals.said_centered = True
                elif lower.replace(" ", "") == 'fullscreen':
                    g.press('f11')
                elif lower == 'eye mode' or lower == 'i mode':
                    globals.mode = 'eye'
                    globals.should_calibrate = True
                elif lower in ['nose mode', 'snooze mode']:
                    globals.mode = 'nose'
                    globals.should_calibrate = True
                elif "control" in lower or "shift" in lower or "ctrl" in lower or "alt" in lower:
                    keys = text.split()
                    keys = ["ctrl" if key=="control" else key for key in keys]
                    g.hotkey(*keys)
                elif lower.replace(" ", "") in custom_keys:
                    g.press(custom_keys[lower.replace(" ", "")])
                elif lower.replace(" ", "") in g.KEY_NAMES:
                    g.press(lower.replace(" ", ""))
                
                if lower != 'scroll up':
                    last_scrollup = 400
                if lower != 'scroll down':
                    last_scrolldown = 400

if __name__ == "__main__":
    speech_to_text()