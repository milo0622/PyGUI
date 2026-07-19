import sys
sys.path.insert(0, "/opt/pygui")
from lib. baseuiapi import *
import socket
from pathlib import Path
import os
import json

class SysServer:
    def __init__(self, pygame:pygame, targetSurface, screenw=800, screenh=600, serverAddr="/tmp/pygui.sock"):
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

        self.serverAddr = serverAddr

        self.pythOSlogo = self.pygame.image.load("/opt/pygui/assets/PythOS.png").convert_alpha()

        if Path(self.serverAddr).exists():
            os.remove(self.serverAddr)
        self.compositor = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.compositor.bind(self.serverAddr)
        self.compositor.listen(1)
        self.compositor.setblocking(False)
        self.clientSocket = None

    def drawWallpaper(self, color:tuple=(0, 128, 128)):
        self.tS.fill(color)
        imageMask = self.pygame.mask.from_surface(self.pythOSlogo).to_surface(setcolor=(0,0,0, 255), unsetcolor=(0,0,0,0))
        logow = self.pythOSlogo.get_width()
        logoh = self.pythOSlogo.get_height()
        targetX = self.w - logow - (logow * .1)
        targetY = self.h - logoh - (logoh * .1)
        self.tS.blit(imageMask, (targetX + logow * 0.03, targetY + logoh * 0.03))
        self.tS.blit(self.pythOSlogo, (targetX, targetY))
    
    def bootFade(self, speed=0.5):
        if self.tempFade > 0:
            self.fadeOverlay.fill((0,0,0,self.tempFade))
            self.tS.blit(self.fadeOverlay, (0,0))

            self.tempFade -= 255/(speed * 60)
            if self.tempFade < 0:
                self.tempFade = 0
                del self.fadeOverlay
    
    @staticmethod
    def obtainScreenSize():
        displayInfo = self.pygame.display.Info()
        self.w, self.h = displayInfo.current_w, displayInfo.current_h
        return self.w, self.h
    
    def acceptMessage(self):
        if self.clientSocket is None:
            try:
                self.clientSocket, addr = self.compositor.accept()
                self.clientSocket.setblocking(False)
            except BlockingIOError:
                return None
        
        try:
            data = self.clientSocket.recv(1024)
            if not data:
                self.clientSocket.close()
                self.clientSocket = None
                return None
            
            payload = data.decode("utf-8")
            return payload
        except BlockingIOError:
            return None
        except ConnectionResetError:
            self.clientSocket.close()
            self.clientSocket = None
            return None

    def sendMessage(self, reply:str):
        if self.clientSocket is None:
            return None
        try:
            self.clientSocket.sendall(reply.encode("utf-8"))
            return None
        except BlockingIOError:
            return None
        except json.JSONDecodeError:
            return None

    def decodeMessage(self, message:str):
        try:
            return json.loads(message)
        except json.JSONDecodeError:
            return None
    def initWindow(self, title="window", x=None, y=None, w=400, h=300, tbHeight=25, tbColor=[0,0,128],  close=True, fontPath="/opt/pygui/assets/defaultFont.ttf"):
        print("init window")
        currentID = self.nextID
        window = WindowAPI(self, self.tS, x, y, w, h, title, close, fontPath, tbHeight, tbColor)
        window.ID = currentID
        self.windows[currentID] = window
        self.nextID += 1

        return currentID
    
    def destroyWindow(self, windowID):
        print(f"{type(windowID)}, {windowID}")
        if windowID in self.windows:
            self.windows.pop(windowID)
            return windowID, "Success"
        return windowID, "Failed"

class Taskbar:
    def __init__(self, targetSurface:pygame.Surface, color=[212, 208, 200], height=30):
        self.tS = targetSurface
        self.bgColor = color
        self.height = height

        self.screenw, _ = SysServer.obtainScreenSize()
        self.h = height if height else 30

        self.tbSurface = pygame.Surface((self.screenw, self.h))
        self.tbSurface.fill(self.bgColor)

        self.buttons = []

    def drawTaskbar(self):
        