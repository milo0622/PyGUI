import os
import sys
sys.path.insert(0, "/opt/pygui/")
from lib.initialization import *
from lib.server import *
from lib.baseuiapi import *
import pygame
from pathlib import Path
import platform
import socket
import json
from lib.guiSDK import * 
import traceback

class PyGUI:
    def __init__(self):
        fbPreload()
        initialization = init(pygame, mS=2.5)
        self.screen, self.w, self.h = initialization.initPyGame()
        self.curX, self.curY = initialization.initMouse()

    def main(self):
        self.sysServer = SysServer(pygame, self.screen, self.w, self.h, serverAddr="/tmp/pygui.sock")
                
        import threading
        threading.Thread(target=self.autostart, daemon=True).start()
        self.mainloop()

    def mainloop(self, fps=60):
        clock = pygame.time.Clock()
        running = True

        while running:
            try:
                mousePos = pygame.mouse.get_pos()
                clock.tick(fps)

                self.sysServer.drawWallpaper()

                self.recv()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        print("mouse button down detected")
                        if event.button == 1:
                            for winID in list(self.sysServer.windows.keys())[::-1]:
                                if self.sysServer.windows[winID].handleMouseDown(mousePos):
                                    break
                            print(self.sysServer.windows)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        print("mouse button up detected")
                        if event.button == 1:
                            for winID in list(self.sysServer.windows.keys())[::-1]:
                                if self.sysServer.windows[winID].handleMouseUp(mousePos):
                                    break
                    elif event.type == pygame.MOUSEMOTION:
                        if len(self.sysServer.windows) > 0:
                            topWindow = next(reversed(self.sysServer.windows))
                            topWindow = self.sysServer.windows[topWindow]
                            if topWindow.isDragging:
                                topWindow.moveWindow(event.rel[0], event.rel[1])
                        
                for window in self.sysServer.windows.keys():
                    self.sysServer.windows[window].drawWindow()

                self.sysServer.bootFade(0.5)
                pygame.display.flip()
            except (KeyboardInterrupt, EOFError):
                break
    
    def autostart(self):
        app = App(title="PythOS", x=None, y=None, w=300, h=400)
        app.initWindow()
    
    def recv(self):
        incomingMsg = self.sysServer.acceptMessage()
        if incomingMsg:
            try:
                parsed = self.sysServer.decodeMessage(incomingMsg)
                print(parsed)
                if parsed:
                    useSelf = parsed.get("useSelf", False)
                    targFunc = parsed.get("function", "")
                    run = globals().get(targFunc, "")
                    if useSelf:
                        targClass = getattr(self, parsed.get("useClass"), None)
                        if targClass:
                            run = getattr(targClass, targFunc, None)
                    if callable(run):
                        try:
                            result = run(*parsed.get("args", []), **parsed.get("kwargs", {}))
                            replyPayload = {
                                "result": result,
                                "status": "Success"
                            }
                        except Exception as e:
                            print(e)
                            replyPayload = {
                                "result": str(e),
                                "status":"Failure"
                            }
                        reply = json.dumps(replyPayload)

                    else:
                        print("Function not found")
                        replyPayload = {
                            "result": "Function not found",
                            "status":"Failure"
                        }
                        reply = json.dumps(replyPayload)
                    self.sysServer.sendMessage(reply)
            except (ConnectionResetError, BrokenPipeError, socket.error) as e:
                print(f"Client disconnected: {e}")

                return None
            except Exception as e:
                print(f"Error: {e}")
                replyPayload = {
                    "result":str(e),
                    "status": "Failure"
                }
                reply = json.dumps(replyPayload)
                self.sysServer.sendMessage(reply)
        
if __name__ == "__main__":
    gui = PyGUI().main()
