import sys
sys.path.insert(0, "/opt/pygui")
from lib.guiSDK import *
import time

def main():
    app = App(title="About PythOS", w=300, h=400)
    app.initWindow()

    app.Button(text="Hi", x=10,y=30, autoResize=True, padding=3, fontSize=30, callback=app.destroyWindow)

if __name__ == "__main__":
    main()
