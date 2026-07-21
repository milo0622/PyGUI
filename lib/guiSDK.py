import traceback
import socket
import sys
sys.path.insert(0, "/opt/pygui")
from lib.baseuiapi import *
import json
import pygame
import inspect
from pathlib import *
import os
import threading

class App:
    def __init__(self, title:str="App", x:int=None, y:int=None, w:int=400, h:int=300, close:bool=True, tbHeight:int=25, tbColor:list=[0,0,128]):
        self.socketAddr = "/tmp/pygui.sock"
        print(self.socketAddr)

        self.w, self.h = w, h
        self.title = title

        self.sw, self.sh = self.obtainScreenSize()

        self.x = x if x is not None else (self.sw - self.w) // 2
        self.y = y if y is not None else (self.sh - self.h) // 2

        self.tbColor = tbColor

        self.tbHeight = tbHeight
        self.close = close

        self.ID:int = None

        self.window = None

        self.widgets = {}
        self.nextWID = 0

        self.listenPath = None

    def obtainScreenSize(self) -> tuple | None:
        result, status = self.sendRequest(action="obtainScreenSize", useSelf=False, useClass=None)
        if status == "Success":
            return result.get("result")
        return None

    def initWindow(self):
        result, status = self.sendRequest(action="initWindow", useSelf=True, useClass="sysServer", title=self.title, x=self.x, y=self.y, w=self.w, h=self.h, tbHeight=self.tbHeight, close=self.close, tbColor=self.tbColor)
        if status == "Success":
            if result.get("result", None) is not None:
                if isinstance(result.get("result", None), int):
                    self.ID = result.get("result")
                    threading.Thread(target=self.openListener, daemon=True).start()
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

        self.sendRequest(action="destroyWindow", useSelf=True, useClass="sysServer", windowID=windowID)    

    def Text(self, text, x=0, y=0, fontSize=20, fontPath="/opt/pygui/assets/defaultFont.ttf", fontColor=[0,0,0]):
        if not fontPath:
            fontPath = "/opt/pygui/assets/defaultFont.ttf"
        result = self.sendRequest("UIText", useSelf=True, useClass="sysServer", text=text, x=x, y=y, fontSize=fontSize, fontPath=fontPath, fontColor=fontColor, windowID=self.ID)
        if result[1] == "Success":
            payload = {
                "text":text,
                "x":x,
                "y":y,
                "fontSize":fontSize, 
                "fontColor":fontColor,
                "fontPath":fontPath
            }

            self.widgets[self.nextWID] = payload
            self.nextWID += 1
        return payload

    def Button(self, text=None, x=0, y=0, w:str|int=0, h:str|int=0, fontSize=20, fontPath="/opt/pygui/assets/defaultFont.ttf", fontColor=[0,0,0], callback=None, *args, **kwargs):
        if not fontPath:
            fontPath = inspect.signature(fontPath)
        result = self.sendRequest("UIButton", useSelf=True, useClass="sysServer", text=text, x=x, y=y, w=w, h=h, fontPath=fontPath, fontSize=fontSize, fontColor=fontColor, windowID=self.ID, widgetID=self.nextWID, eventSocketPath=self.listenPath)
        if result == "Success":
            payload = {
                "text":text, 
                "x":x,
                "y":y,
                "fontSize":fontSize, 
                "fontColor":fontColor,
                "fontPath":fontPath,
                "w": w,
                "h":h,
                "callback":callback,
                "args":args,
                "kwargs":kwargs
            }

            self.widgets[self.nextWID] = payload
            self.nextWID += 1

        return

    def sendRequest(self, action:str | list, useSelf=True, useClass:str | None="sysServer", *args, **kwargs):
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

    def openListener(self):
        self.listenPath = f"/tmp/pyguiEvents-{self.ID}.sock"
        if Path(self.listenPath).exists():
            os.unlink(self.listenPath)

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.listenPath)
        self.server.listen(1)
        while True:
            conn, _ = self.server.accept()
            data = conn.recv(1024)
            conn.close()
            if not data:
                continue
            else:
                data = json.loads(data)
            action = data.get("action", None)
            if action:
                args = data.get("args", [])
                kwargs = data.get("kwargs", {})
                run = getattr(self, action)
                try:
                    run(*args, **kwargs)
                    continue
                except Exception as e:
                    print(f"Error executing {action}: {e}")
                    continue
