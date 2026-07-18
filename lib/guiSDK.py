import traceback
import socket
import sys
sys.path.insert(0, "/opt/pygui")
from lib.baseuiapi import *
import json
import pygame

class App:
    def __init__(self, title:str="App", x:int=None, y:int=None, w:int=400, h:int=300, close:bool=True, tbHeight:int=25, tbColor:list=[0,0,128]):
        self.socketAddr = "/tmp/pygui.sock"
        print(self.socketAddr)

        self.w, self.h = w, h
        self.title = title

        self.displayInfo = pygame.display.Info()
        self.sw = self.displayInfo.current_w
        self.sh = self.displayInfo.current_h

        self.x = x if x is not None else (self.sw - self.w) // 2
        self.y = y if y is not None else (self.sh - self.h) // 2

        self.tbColor = tbColor

        self.tbHeight = tbHeight
        self.close = close

        self.ID:int = None

    def initWindow(self):
        result, status = self.sendRequest(action="initWindow", useSelf=True, useClass="sysServer", title=self.title, x=self.x, y=self.y, w=self.w, h=self.h, tbHeight=self.tbHeight, close=self.close, tbColor=self.tbColor)
        if status == "Success":
            if result.get("result", None) is not None:
                if isinstance(result.get("result", None), tuple):
                    self.ID = result.get("result")
                    return self.ID
                else:
                    return f"Failed to initialize window: {result.get("status", None)}", 2
            else:
                return f"Failed to initialize window: {result.get("status", None)}", 3
        else:
            return status, 1

    def destroyWindow(self, windowID:int=None):
        if windowID is None:
            windowID = self.ID

        result, status = self.sendRequest(action="destroyWindow", useSelf=True, useClass="sysServer", windowID=windowID)    

    def Text(self, text, x=0, y=0, fontSize=20, fontPath="/opt/pygui/assets/defaultFont.ttf"):
        
        if not fontPath:
            fontPath = "/opt/pygui/assets/defaultFont.ttf"

    def sendRequest(self, action:str, useSelf=True, useClass="sysServer", *args, **kwargs):
        
        payload = {
            "function":action,
            "useSelf":useSelf,
            "useClass":useClass,
            "args":args,
            "kwargs":kwargs
        }

        txSocket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            txSocket.connect(self.socketAddr)
            payload = json.dumps(payload)

            txSocket.sendall(payload.encode("utf-8"))
            
            reply = txSocket.recv(1024)
            if reply:
                reply = json.loads(reply)
                print(f"Reply: {reply}")
                return reply, "Success"
            return None, "Nothing received"
        except Exception as e:
            return None, f"Failed: {e}"
        finally:
            txSocket.close()
