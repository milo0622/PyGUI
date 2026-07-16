import sys
sys.path.insert(0, "/opt/pygui")
from lib. baseuiapi import *

class SysServer:
    def __init__(self, pygame:pygame, targetSurface, screenw=800, screenh=600):
        self.pygame = pygame
        self.tS = targetSurface
        self.w = screenw
        self.h = screenh

        self.windows = {}
        self.nextID = 0

        self.buttons = []

        self.x, self.y = 0,0

        self.tempFade = 255
        self.fadeOverlay = self.pygame.Surface((self.w, self.h), self.pygame.SRCALPHA)
        
    def drawWallpaper(self, color:tuple=(0, 128, 128)):
        self.tS.fill(color)
        pythOSlogo = self.pygame.image.load("/opt/pygui/assets/PythOS.png").convert_alpha()
        imageMask = self.pygame.mask.from_surface(pythOSlogo).to_surface(setcolor=(0,0,0, 255), unsetcolor=(0,0,0,0))
        logow = pythOSlogo.get_width()
        logoh = pythOSlogo.get_height()
        targetX = self.w - logow - (logow * .1)
        targetY = self.h - logoh - (logoh * .1)
        self.tS.blit(imageMask, (targetX + logow * 0.03, targetY + logoh * 0.03))
        self.tS.blit(pythOSlogo, (targetX, targetY))

    def initWindow(self, w=400, h=300, title="window", x=None, y=None, close=True, fontPath=None, tbHeight=25, tbColor=[0,0,128]):
        if not x and not y:
            if self.w is None and self.h is None:
                x, y = 0,0
            else:
                x, y = ((self.w - w) // 2), ((self.h - h) // 2)

        window = WindowAPI(sysServer=self, targetSurface=self.tS, x=x, y=y, width=w, height=h, title=title, close=close, fontPath=fontPath, tbHeight=tbHeight, tbColor=tbColor)
        self.windows[self.nextID] = window
        currentID = self.nextID
        window.ID = currentID

        self.nextID += 1

        return window, currentID
    
    def bootFade(self, speed=0.5):
        if self.tempFade > 0:
            self.fadeOverlay.fill((0,0,0,self.tempFade))
            self.tS.blit(self.fadeOverlay, (0,0))

            self.tempFade -= 255/(speed * 60)
            if self.tempFade < 0:
                self.tempFade = 0
                del self.fadeOverlay
    
    def obtainScreenSize(self):
        displayInfo = self.pygame.display.Info()
        self.w, self.h = displayInfo.current_w, displayInfo.current_h
        return self.w, self.h

class SysTaskbar:
    def __init__():
        pass
