import sys
sys.path.insert(0, "/opt/pygui")
from lib.guiSDK import *
import time

def main():
    app = App(title="About PythOS", w=300, h=400)
    app.initWindow()

    app.Text("About PythOS", x=10, y=10, fontSize=35)
    app.Button(text="Hi", x=10,y=20, w=10, h=5, fontSize=10, callback=None)

if __name__ == "__main__":
    main()
