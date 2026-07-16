import pygame
import sys
sys.path.insert(0, "/opt/pygui/")
from lib.uiapi import *
from lib.server import *

class app:
    def __init__(self, title="About PythOS", w=300, h=400, x=None, y=None):
        self.title = title
        self.w = w
        self.h = h
        self.x = x if x is not None else pygame
    
    def main(self):
        pass
if __name__ == "__main__":
    mainProc = app()
    mainProc.main()
