import sys
sys.path.insert(0, "/opt/pygui")
from lib.baseuiapi import *
import socket
from pathlib import Path
import os
import json
import pygame

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

        self.taskbar = Taskbar(self.tS)

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
        currentID = self.nextID
        window = WindowAPI(self, self.tS, x, y, w, h, title, close, fontPath, tbHeight, tbColor)
        window.ID = currentID
        self.windows[currentID] = window
        self.nextID += 1

        return currentID
    
    def destroyWindow(self, windowID):
        if windowID in self.windows:
            self.windows.pop(windowID)
            return windowID, "Success"
        return windowID, "Failed"

    def UIText(self, windowID, text, x=None, y=None, fontSize=20, fontPath="/opt/pygui/assets/defaultFont.ttf", fontColor:list=[0,0,0]):
        if windowID not in self.windows:
            return "Invalid window ID", "Failed"
        content = self.windows[windowID].content
        try:
            UIText(text, content, x, y, fontPath, fontSize, fontColor, renderAllAtOnce=True)
            return "Successfully rendered", "Success"
        except Exception as e:
            return "Failed to render", "Failed"
    
    def UIButton(self, windowID, text, x=None, y=None, w=0, h=0, fontPath="/opt/pygui/assets/defaultFont.ttf", fontSize=20, fontColor=[0,0,0], widgetID=None, eventSocketPath=None):
        if widgetID is None:
            return "Please provide widget ID", "Failed"
        if windowID not in self.windows:
            return "Invalid window ID", "Failed"
        content = self.windows[windowID].content
        def clickCallback():
            self.sendEventToApp(eventSocketPath, widgetID)
        try:
            UIButton(w=w, h=h, x=x, y=y, callback=clickCallback, renderText=text, renderImagePath="", fontSize=fontSize, fontColor=fontColor, renderAllAtOnce=True, targetDest=self.windows[windowID])
            for button in self.windows[windowID].buttons:
                print(button)
        except Exception as e:
            print(e)
    def sendEventToApp(self, windowID:int, widgetID:int):
        payload = {
            "action":"click",
            "args": [
                widgetID
            ]
        }
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(f"/tmp/pyguiEvents-{windowID}.sock")
        s.sendall(json.dumps(payload).encode("utf-8"))

def obtainScreenSize():
    displayInfo = pygame.display.Info()
    w, h = displayInfo.current_w, displayInfo.current_h
    return w, h

class Taskbar:
    def __init__(self, targetSurface:pygame.Surface, color=[212, 208, 200], height=50):
        self.tS = targetSurface
        self.bgColor = color
        self.height = height

        self.screenw, self.screenh = obtainScreenSize()
        self.w = self.screenw
        self.h = height if height else 50

        self.tbSurface = pygame.Surface((self.w, self.h))
        self.tbSurface.fill(self.bgColor)

        self.buttons = []

        self.x = 0
        self.y = self.screenh - self.h

    def drawTaskbar(self):
        self.tS.blit(self.tbSurface, (self.x, self.y))
        drawShadowsonSurface(self.tbSurface, self.w, self.h)
