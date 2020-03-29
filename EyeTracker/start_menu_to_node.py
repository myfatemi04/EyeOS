import start_menu
import collections 
import sys


def main():
  apps = sorted(start_menu.start_menu_index.items())
  for app in apps:
    if(len(sys.argv) > 1):
      if app[0].find(sys.argv[1]) == 0:
        print(app[0] + "<>" + list(app[1])[0])
    elif app[0] != "":
      print(app[0] + "<>" + list(app[1])[0])

if __name__ == "__main__":
  main()
