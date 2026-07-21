import pygame
from pathlib import Path
import sys
sys.path.insert(0,"/opt/pygui")
from lib.server import *
from pathlib import Path

class WindowAPI:
	def __init__(self, sysServer:SysServer, targetSurface:pygame.Surface, x, y, width=400, height=300, title="window", close=True, fontPath="/opt/pygui/assets/defaultFont.ttf", tbHeight=25, tbColor=[0,0,128]):
		self.x = x
		self.y = y

		self.title = title
		self.targetSurface = targetSurface

		self.bgColor = [212, 208, 200]
		self.lightMargin = [255, 255, 255]
		self.darkMargin = [0,0,0]

		self.tbColor = tbColor
		self.tbWidth = width - 6
		self.tbHeight = tbHeight
		self.tbStartX = 2
		self.tbStartY = 2
		self.w = width
		self.h = height + self.tbHeight + (6 if self.tbHeight > 0 else 0)

		self.close = close

		self.xOffset = 0
		self.yOffset = 0

		self.titleBar = None

		self.titleFS = 12 if tbHeight > 0 else 0

		self.fontPath = fontPath
		self.ID = None

		self.buttons = [] 

		closeBtnH = self.tbHeight - 6 if tbHeight > 0 else 0
		closeBtnW = closeBtnH + 2
		closeBtnY = (self.tbHeight - closeBtnH) // 2 + self.tbStartY
		closeBtnX = (self.w - self.tbStartX - closeBtnW - closeBtnY)
		self.closeBtn = UIButton(closeBtnW, closeBtnH, closeBtnX, closeBtnY, callback=self.closeWindow, renderText="x", fontSize=24)

		self.sysServer = sysServer
		self.isDragging = False

		self.content = pygame.Surface((self.w - 2, self.h - (6 if self.tbHeight > 0 else 0) - self.tbHeight))
		self.content.fill(self.bgColor)

		self.window = pygame.Surface((self.w, self.h))

	def drawWindow(self):
		self.window.fill(self.bgColor)

		self.titleBar = pygame.Rect(2, 2, self.tbWidth, self.tbHeight)
		pygame.draw.rect(self.window, self.tbColor, self.titleBar)
		
		self.titleObject = UIText(self.title, self.window, self.fontPath, self.titleFS, fontColor=[255, 255, 255], renderAllAtOnce=False)
		titleY = (self.tbHeight - int(self.titleObject.height)) // 2 + self.tbStartY
		self.titleObject.blitText(titleY, titleY)

		if self.close and self.tbHeight > 0:
			self.closeBtn.draw(self, tbButtons=True)
		self.window.blit(self.content, (2, self.tbHeight + 4))

		drawShadowsonSurface(self.window, self.w, self.h)

		self.targetSurface.blit(self.window, (self.x, self.y))
		return self.window, self.titleBar, self.titleObject, self.content
	
	def closeWindow(self):
		self.sysServer.destroyWindow(self.ID)
		print(f"Window closed: {self.title}")

	def handleMouseDown(self, mousePos:tuple):
		windowRect = pygame.Rect(self.x, self.y, self.w, self.h)
		if windowRect.collidepoint(mousePos):
			if self.ID != next(reversed(self.sysServer.windows)):
				try:
					self.sysServer.windows[self.ID] = self.sysServer.windows.pop(self.ID)
				except KeyError:
					print("Window not found.")
			for button in self.buttons:
				if button.checkClick(mousePos, self.x, self.y):
					buttonClicked = True
					break
				buttonClicked = False
			if buttonClicked:
				return True
			absTb = pygame.Rect(self.x + self.tbStartX, self.y + self.tbStartY, self.tbWidth, self.tbHeight)
			if absTb.collidepoint(mousePos):
				self.isDragging = True
				print(f"{self.ID}: grabbed onto handle")
		return False
	
	def handleMouseUp(self, mousePos:tuple):
		if self.isDragging:
			self.isDragging = False
		for button in self.buttons:
			if button.checkRelease(mousePos, self.x, self.y):
				return True
		return False
	
	def moveWindow(self, relx, rely):
		if self.isDragging:
			self.x = relx + self.x
			self.y = rely + self.y
			return
		return

def drawShadowsonSurface(targetSurface, surfacew, surfaceh, lightMargin=[255, 255, 255], darkMargin=[0,0,0], width=2):
	topleft = (0, 0)
	topright = (surfacew - width, 0)
	bottomleft = (0, surfaceh - width)
	bottomright = (surfacew - width, surfaceh - width)
	pygame.draw.line(targetSurface, lightMargin, topleft, bottomleft, width=width )
	pygame.draw.line(targetSurface, lightMargin, topleft, topright, width=width)
	pygame.draw.line(targetSurface, darkMargin, topright, (bottomright[0], bottomright[1] + width // 2), width=width)
	pygame.draw.line(targetSurface, darkMargin, bottomleft, (bottomright[0] + width // 2, bottomright[1]), width=width)

def drawShadowsonRect(parentSurface, targetRect:pygame.Rect, lightMargin=[255, 255, 255], darkMargin=[0,0,0], grayMargin=[80,80,80], clicked=False):
	"""The clicked parameter inverts the drawing logic vertically and horizontally"""
	topColor = lightMargin if not clicked else darkMargin
	leftColor = lightMargin if not clicked else darkMargin
	rightColor = darkMargin if not clicked else lightMargin
	bottomColor = darkMargin if not clicked else lightMargin
	topleft = targetRect.topleft
	topright = targetRect.topright
	bottomleft = targetRect.bottomleft
	bottomright = targetRect.bottomright	
	rectw = targetRect.width
	recth = targetRect.height
	pygame.draw.line(parentSurface, leftColor, topleft, bottomleft)
	pygame.draw.line(parentSurface, topColor, topleft, topright)
	pygame.draw.line(parentSurface, rightColor, topright, bottomright)
	pygame.draw.line(parentSurface, bottomColor, bottomleft, bottomright)
	if not clicked:
		pygame.draw.line(parentSurface, grayMargin, (topright[0] - 1, topright[1] + 1), (bottomright[0] - 1, bottomright[1]))
		pygame.draw.line(parentSurface, grayMargin, (bottomleft[0] + 1, bottomleft[1] - 1), (bottomright[0] - 1, bottomright[1] - 1))
	else:
		pygame.draw.line(parentSurface, grayMargin, (topleft[0] + 1, topleft[1] + 1), (bottomleft[0] + 1, bottomleft[1] - 1))
		pygame.draw.line(parentSurface, grayMargin, (topleft[0] + 1, topleft[1] + 1), (topright[0] - 1, topright[1] + 1))

class UIButton:
	def __init__(self, w, h, x, y, callback, targetDest=None, renderText="", renderImagePath="", color:pygame.Color=[212, 208, 200], shadows=True, fontSize=20, fontColor=[0,0,0], renderAllAtOnce=True):
		self.w = w
		self.h = h
		self.x = x
		self.y = y

		self.callback = callback
		self.isClicked = False

		self.font = pygame.font.Font(None, fontSize)
		self.text = renderText

		self.color = color

		if not renderImagePath:
			self.imageObject = None
		elif Path(renderImagePath).exists():
			self.imageObject = pygame.image.load(renderImagePath)

		self.appended = False

		self.isClicked = False

		self.shadows = shadows
		self.fontColor = fontColor
		self.targetDest = targetDest

		if renderAllAtOnce and targetDest is not None:
			self.draw(targetDest=self.targetDest)

	def draw(self, targetDest:WindowAPI | SysServer, tbButtons=False):
		self.targetDest = targetDest
		self.tS = self.targetDest.content if isinstance(self.targetDest, WindowAPI) else self.targetDest.tS
		if tbButtons:
			self.tS = self.targetDest.window
		
		self.buttonObject = pygame.Rect((self.x, self.y, self.w, self.h))
		pygame.draw.rect(self.tS, self.color, self.buttonObject)

		additionalOffset = 1 if self.isClicked else 0

		if self.text is not None:
			self.textObject = self.font.render(self.text, True, self.fontColor)
		if self.imageObject is not None:
			imageX = (self.w - self.imageObject.get_width()) // 2 + self.x + additionalOffset
			imageY = (self.h - int(self.imageObject.get_height())) // 2 + self.y + additionalOffset
			self.tS.blit(self.imageObject, (imageX, imageY))
		if self.textObject is not None:
			textX = (self.w - self.textObject.get_width()) // 2 + self.x + additionalOffset
			textY = (self.h - self.textObject.get_height()) // 2 + self.y + additionalOffset
			self.tS.blit(self.textObject, (textX, textY))

		if self.shadows:
			drawShadowsonRect(self.tS, self.buttonObject, clicked=self.isClicked)

		if not self.appended:
			targetDest.buttons.append(self)
			self.appended = True

		return self.buttonObject, self.imageObject, self.textObject

	def checkClick(self, mousePos, windowX, windowY):
		absX, absY = windowX + self.x, windowY + self.y
		buttonRect = pygame.Rect(absX, absY, self.w, self.h)
		if buttonRect.collidepoint(mousePos):
			print("check: click")
			self.isClicked = True
			return True
		self.isClicked = False
		return False

	def checkRelease(self, mousePos, windowX, windowY):
		if self.isClicked:
			self.isClicked = False
			absX, absY = windowX + self.x, windowY + self.y
			buttonRect = pygame.Rect(absX, absY, self.w, self.h)
			if buttonRect.collidepoint(mousePos):
				print("check: release")
				self.click()
		return False

	def click(self, args:tuple):
		if self.callback:
			self.callback(*args)

class UIText:
	def __init__(self, text, targetSurface:pygame.Surface, x=None, y=None, fontPath:str="/opt/pygui/assets/defaultFont.ttf", fontSize:int=12, fontColor=pygame.Color, renderAllAtOnce=True):
		self.font = pygame.font.Font(fontPath, fontSize)
		self.fontSize = fontSize
		self.tS = targetSurface
		self.fontColor = fontColor

		self.x = x
		self.y = y

		self.rendered = self.font.render(text, True, self.fontColor)
		self.height = self.rendered.get_height()
		self.width = self.rendered.get_width()

		self.rendered = self.font.render(text, True, self.fontColor)
		self.height = self.rendered.get_height()
		self.width = self.rendered.get_width()
		if renderAllAtOnce:
			self.blitText()

		self.appended = False
		
	def blitText(self, x=None, y=None):
		"""x or y coordinates are optional if already defined when initializing UIText object"""
		self.x = x if x else self.x
		self.y = y if y else self.y
		if hasattr(self, 'rendered') and self.rendered is not None:
			self.tS.blit(self.rendered, (self.x, self.y))
			return
		else:
			print("BLUD RENDER TS FIRST")
			return

class UIImage:
	def __init__(self, targetSurface:pygame.Surface, imagePath:str, x:int=0, y:int=0, width:int=None, height:int=None):
		self.tS = targetSurface
		self.imagePath = imagePath
		self.w = width
		self.h = height

		if not Path(self.imagePath).exists():
			print(f"{self.imagePath}: No image file found")
			return
		self.loadedImage = pygame.image.load(self.imagePath).convert_alpha()
		self.orgW = loadedImage.get_width()
		self.orgH = loadedImage.get_height()

		if self.w is not None or self.h is not None:
			self.loadedImage = pygame.transform.scale(self.loadedImage, (self.w if self.w is not None else self.orgW, self.h if self.h is not None else self.orgH))
	
	def blitImage(self):
		if hasattr(self, "loadedImage") and self.loadedImage is not None:
			self.tS.blit(self.loadedImage, (self.x, self.y))
