import os

pyguiDir = "/opt/pygui"

def fbPreload():
    os.environ["SDL_VIDEODRIVER"] = "kmsdrm"
    os.environ["SDL_FBDEV"] = "/dev/dri/card0"

    os.environ["SDL_MOUSEDRV"] = "TSLIB"
    os.environ["SDL_MOUSEDEV"] = "/dev/input/mice"

class init:
    def __init__(self, pygame, mS=2.5):
        self.pygame = pygame
        self.mS = mS
        
        self.w = 800
        self.h = 600

    def initPyGame(self):
        self.pygame.display.init()
        displayInfo = self.pygame.display.Info()

        self.w, self.h = displayInfo.current_w, displayInfo.current_h

        print(f"Framebuffer mode: {self.w}x{self.h}")

        self.pygame.init()
        return self.pygame.display.set_mode((self.w, self.h)), self.w, self.h

    def initMouse(self):
        cursor = self.pygame.image.load(f"{pyguiDir}/assets/curs.png")
        self.pygame.mouse.set_cursor(self.pygame.cursors.Cursor((0,0), cursor))

        X = self.w // 2
        Y = self.h // 2

        self.pygame.mouse.set_pos((X, Y))

        return (X, Y)
