import platform
import os

start_menu_index = {

}

def pure_filename(lnk_filename):
    return lnk_filename.replace(".lnk", "").replace(".url", "")

def sanitize_and_add(name, lastpath, root):
    for token in name.split():
        token = ''.join(char for char in token if char.isalnum())
        token = token.lower()
        if token not in start_menu_index:
            start_menu_index[token] = {os.path.join(root, lastpath)}
        else:
            start_menu_index[token].add(os.path.join(root, lastpath))

def proccess_linux_name(path):
    with open(path, "r") as file:
        data = file.read()
        data = data.split("\n")
        name = execpath = ""
        for line in data:
            if line.find("Name=") == 0:
                name = line[5:]
            if line.find("Exec=") == 0:
                execpath = line[5:]
        return name, execpath
        


def walk_folder(start_menu_folder, win=False, darwin=False, linux=False):
    assert(
        (not win and not darwin and linux) or 
        (win and not darwin and not linux) or 
        (not win and darwin and not linux))

    for root, dirs, files in os.walk(start_menu_folder):
        for file in files:
            pure_f = pure_filename(file)
            if pure_f != 'desktop.ini' and win:
                sanitize_and_add(pure_f, file, root)
        if darwin:
            for dir in dirs:
                if dir.split(".")[-1] == ".app":
                    sanitize_and_add(dir, dir, root)
        if linux:
            for file in files:
                _, ext = os.path.splitext(file)
                if ext == ".desktop":
                    name, execpath = proccess_linux_name(os.path.join(root, file))
                    if name:
                        sanitize_and_add(name, execpath, root)
        

if not start_menu_index:
    if platform.system() == "Windows":
        user_path = os.path.expanduser("~")
        start_menu_folders = [
            os.path.join(user_path, "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs"),
            "C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs"
        ]
        for folder in start_menu_folders:
            walk_folder(folder, win=True)
    
    if platform.system() == "Darwin":
        start_menu_folder = "/Applications"
        walk_folder(start_menu_folder, darwin=True)
    
    if platform.system() == "Linux":
        user_path = os.path.expanduser("~")
        start_menu_folders = [
            "/usr/share/applications",
            "/usr/local/share/applications",
            os.path.join(user_path, ".local", ".share", "applications")
        ]
        for folder in start_menu_folders:
            walk_folder(folder, linux=True)

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
