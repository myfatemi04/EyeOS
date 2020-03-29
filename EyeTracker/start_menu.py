import platform
import os

start_menu_index = {

}

def pure_filename(lnk_filename):
    return lnk_filename.replace(".lnk", "").replace(".url", "")

def walk_folder(start_menu_folder):
    for root, dirs, files in os.walk(start_menu_folder):
        for file in files:
            pure_f = pure_filename(file)
            if pure_f != 'desktop.ini':
                for token in pure_f.split():
                    token = ''.join(char for char in token if char.isalnum())
                    token = token.lower()
                    if token not in start_menu_index:
                        start_menu_index[token] = {os.path.join(root, file)}
                    else:
                        start_menu_index[token].add(os.path.join(root, file))

if not start_menu_index:
    if platform.system() == "Windows":
        user_path = os.path.expanduser("~")
        start_menu_folders = [
            os.path.join(user_path, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs"),
            "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs"
        ]
        
        for folder in start_menu_folders:
            walk_folder(folder)

def find_links(search):
    highest_scores = {}
    for tkn in search.lower().split():
        if tkn in start_menu_index:
            links = start_menu_index[tkn]
            for link in links:
                if link not in highest_scores:
                    highest_scores[link] = 1
                else:
                    highest_scores[link] += 1

    return sorted(highest_scores.items(), key=lambda x: (x[1], x[0]), reverse=True)
