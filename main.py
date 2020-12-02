
# 3 hrs nov 28
# 3 hrs nov 29



import os
import sys
import subprocess
import time
# import screeninfo
from PIL import ImageTk, Image
from pynput.keyboard import Key, Controller
keyboard = Controller()

try:
	import Tkinter as tk
except ImportError:
	import tkinter as tk

try:
	import ttk
	py3 = False
except ImportError:
	import tkinter.ttk as ttk
	py3 = True


SOURCE_DIR = "source"
class ButtonScript:
	def __init__(self, action: list, image: ImageTk.PhotoImage):
		self.action, self.image = action, image
	
	
	def __repr__(self):
		return f"{self.__class__.__name__}({self.action[0]}, {self.image})"
	
	
	@staticmethod
	def fromString(s, sz):
		action, image = s.split('`')
		action = action.split(' ')
		image = ImageTk.PhotoImage(Image.open(f"{SOURCE_DIR}/{image}").resize(sz, Image.ANTIALIAS))
		return ButtonScript(action, image)
	
	
	def getActionFunction(self, win):
		pre, *tokens = self.action
		
		if pre == "QUIT":
			return sys.exit
		
		if pre == "NEXT":
			return win.nextPage
		
		if pre == "MACRO":
			def macro():
				keyboard.press(Key.alt_l)
				keyboard.press(Key.tab)
				keyboard.release(Key.alt_l)
				keyboard.release(Key.tab)
				time.sleep(0.1)
				for key in tokens:
					k = getattr(Key, key, None)
					keyboard.press(k if k else key)
				for key in tokens:
					k = getattr(Key, key, None)
					keyboard.release(k if k else key)
			return macro
		
		if pre == "RUN":
			def run():
				subprocess.Popen(' '.join(tokens), shell=True)
			return run



SCRIPT_DIR = "scripts"
def getButtons(sz):
	pages = []
	for fn in os.listdir(SCRIPT_DIR):
		scripts = []
		with open(f"{SCRIPT_DIR}/{fn}", "r") as f:
			for line in f:
				scripts.append(ButtonScript.fromString(line[:-1], sz))
		pages.append(scripts)
	return pages


class Window:
	def __init__(self):
		self.root = tk.Tk()
		self.currentPage = 0
		# enter geometry of desired monitor
		# m = screeninfo.get_monitors()[0]
		# self.w = m.width
		# self.h = m.height
		# self.x = m.x
		# self.y = m.y
		self.w = 480
		self.h = 800
		self.x = 0
		self.y = 0

		self.root.geometry(f"{self.w}x{self.h}+{self.x}+{self.y}")
		# self.root.attributes('-fullscreen', True)
		self.root.overrideredirect(True)
		
		# self.root.bind("<Escape>", lambda e: root.destroy())
		self.root.title("On Screen Macros")
		self.root.configure(background="#000000")
		
		# TODO: implement pages (below section will be changed)
		# NOTE: ensure number of lines in file match gw * gh
		self.gw, self.gh = 5, 4
		d = min(self.w // self.gw, self.h // self.gh)
		self.bw = self.bh = d
		self.scl = 0.75
		
		self.createButtons()
		
		self.root.mainloop()
	
	
	def createButtons(self):
		sz = (int(self.bw * self.scl), int(self.bh * self.scl))
		self.pages = getButtons(sz)
		self.numPages = len(self.pages)
		
		self.buttons = []
		for page, scripts in enumerate(self.pages):
			for y in range(self.gh):
				for x in range(self.gw):
					i = x + y * self.gw
					
					b = tk.Button(self.root)
					b.place(relx=x*self.bw/self.w + page, rely=y*self.bh/self.h, height=self.bh, width=self.bw)
					b.configure(activebackground="#677075",
								background="#464e52",
								borderwidth="0",
								relief="sunken",
								image=scripts[i].image,
								command=scripts[i].getActionFunction(self))
					
					self.buttons.append(b)
	
	
	def nextPage(self):
		self.currentPage = (self.currentPage + 1) % self.numPages
		for page in range(self.numPages):
			for y in range(self.gh):
				for x in range(self.gw):
					b = self.buttons[x + y * self.gw + page * self.gw * self.gh]
					b.place(relx=x*self.bw/self.w + (page - self.currentPage))
	


if __name__ == '__main__':
	Window()
