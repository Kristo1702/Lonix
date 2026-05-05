# pyinstaller --onedir --windowed --icon="C:\Users\Krist\AppData\Local\lønix\logo.png" --add-data "C:\Users\Krist\AppData\Local\lønix\logo.png;." --name="Lønix" main.py


import sys

from gui import run


if __name__ == "__main__":
    sys.exit(run())