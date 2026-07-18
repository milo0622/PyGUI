
import socket
import sys
sys.path.insert(0, "/opt/pygui")
from lib.baseuiapi import *
import json
import pygame

class App:
    def __init__(self, title:str="App", x:int=None, y:int=None, w:int=400, h:int=300, close:bool=True, tbHeight:int=25, tbColor:list=[0,0,128]):
        self.socketAddr = "/tmp/pygui.sock"
        self.client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        print(self.socketAddr)
        self.client.connect(self.socketAddr)

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

        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

    def initWindow(self):
        result, status = self.sendRequest(action="initWindow", useSelf=True, useClass="sysServer", title=self.title, x=self.x, y=self.y, w=self.w, h=self.h, tbHeight=self.tbHeight, close=self.close, tbColor=self.tbColor)
        if status == "Success":
            result = json.loads(result)
            if result.get("result", None) is not None:
                if isinstance(result.get("result", None), tuple):
                    window, ID = result.get("result")
                    return window, ID
                else:
                    return f"Failed to initialize window: {result.get("status", None)}", None
            else:
                return f"Failed to initialize window: {result.get("status", None)}", None
        else:
            return status, None

    def destroyWindow(self, windowID:int):
        result, status = self.sendRequest(action="destroyWindow", useSelf=True, useClass="sysServer", windowID=windowID)    
        result = json.loads(result)
        if result.get("result", None) and isinstance(result.get("result", None), tuple):
            if result.get("result", None)[1] == "Success":
                return "Success"
            else:
                return "Failed"
        else:
            return "Failed"

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

        try:
            self.socket.connect(self.socketAddr)
            payload = json.dumps(payload)

            self.socket.sendall(payload.encode("utf-8"))
            
            reply = self.socket.recv(4096)
            reply = json.loads(reply)
            if reply:
                print(f"Reply: {reply}")
                return reply, "Success"
            return None, "Nothing received"
        except Exception as e:
            return None, f"Failed: {e}"
        finally:
            self.socket.close()
