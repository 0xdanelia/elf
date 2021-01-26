import os, sys, curses
import elffile

class ElfScreen:
	
	def __init__(self, stdscr, filename):
		stdscr.clear()
		
		self.file = elffile.ElfFile(filename)
		self.stdscr = stdscr
		self.h = stdscr.getmaxyx()[0] - 2
		self.w = stdscr.getmaxyx()[1]
		self.colors = definecolors()
		self.pos = [0,0]
		self.lines = []
		self.startbyte = 0
		self.endbyte = 0
		self.finalbyte = 0
		self.cursormemory = 0
		self.alt = False
		self.inserted = {}
		
	def curline(self):
		return self.lines[self.pos[0]]
	
	def curlinenum(self):
		n = 0
		b = self.curbyte()
		for l in self.file.startlines:
			if l > b:
				return n
			n = n + 1
		return n
	
	def numlines(self):
		return len(self.lines)
	
	def onlastline(self):
		return self.curline().endswith(elffile.ElfFile.EOF)
	
	def islastline(self, line):
		return line.endswith(elffile.ElfFile.EOF)
	
	def curbyte(self):
		b = self.startbyte
		for i in range(self.pos[0]):
			b = b + len(self.lines[i].encode('utf-8'))
		b = b + len((self.lines[self.pos[0]][:self.pos[1]]).encode('utf-8'))
		return b
	
	def linelengthcheck(self):
		self.pos[1] = self.cursormemory
		length = len(self.curline())
		if self.pos[1] >= length:
			self.pos[1] = length - 1
	
	def addnextrow(self, row):
		if self.lines[-1].endswith(elffile.ElfFile.EOF):
			return
		self.startbyte = self.startbyte + len(self.lines[0].encode('utf-8'))
		self.endbyte = self.endbyte + len(row.encode('utf-8'))
		self.lines.append(row)
		self.lines = self.lines[1:]
		
	def addprevrow(self, row):
		self.startbyte = self.startbyte - len(row.encode('utf-8'))
		self.endbyte = self.endbyte - len(self.lines[-1].encode('utf-8'))
		self.lines.insert(0, row)
		self.lines = self.lines[:-1]
	
	def printscreen(self):
		self.stdscr.clear()
		self.printheader()
		self.printlines()
		self.printfooter()
		self.stdscr.move(self.pos[0]+1, self.pos[1])
		self.stdscr.refresh()
		
	def printlines(self):
		c1 = self.colors['WHITE_ON_BLACK']
		c2 = self.colors['CYAN_ON_BLACK']
		c3 = self.colors['MAGENTA_ON_BLACK']
		c4 = self.colors['YELLOW_ON_BLACK']
		c5 = self.colors['RED_ON_BLACK']
		self.stdscr.move(1,0)
		
		linenum = 1
		for l in self.lines:
			for b in l:
				if b == '\n':
					self.stdscr.addstr('\u21B2', c2)
				elif b == '\r':
					self.stdscr.addstr('\u204B', c3)
				elif b == '\t':
					self.stdscr.addstr('\u2017', c4)
				elif b == elffile.ElfFile.EOF:
					self.stdscr.addstr('\u2297', c5)
				else:
					self.stdscr.addstr(b, c1)
			linenum = linenum + 1
			self.stdscr.move(linenum, 0)
		
	def printheader(self):
		c1 = self.colors['BLACK_ON_WHITE']
		c2 = self.colors['BLUE_ON_WHITE']
		self.stdscr.addstr(0, 0, self.file.path, c1)
		self.stdscr.addstr(self.file.name.ljust(self.w - len(self.file.path)), c2)

	def printfooter(self):
		c1 = self.colors['BLACK_ON_WHITE']
		c2 = self.colors['BLUE_ON_WHITE']
		c3 = self.colors['GREEN_ON_WHITE']
		c4 = self.colors['YELLOW_ON_WHITE']
		c5 = self.colors['MAGENTA_ON_WHITE']
		x = str(self.pos[1])
		y = str(self.pos[0])
		linenum = str(self.curlinenum())
		pos = str(self.curbyte())
		size = str(self.file.size)
		footerstart = '['.rjust(self.w-20-len(x+y+linenum+pos+size))		
		try:
			self.stdscr.addstr(self.h+1, 0, footerstart, c1)
			self.stdscr.addstr(x, c5)
			self.stdscr.addstr(',', c1)
			self.stdscr.addstr(y, c5)
			self.stdscr.addstr(']', c1)
			self.stdscr.addstr('   LINE:', c1)
			self.stdscr.addstr(linenum, c4)
			self.stdscr.addstr('   BYTE:', c1)
			self.stdscr.addstr(pos, c2)
			self.stdscr.addstr('/', c1)
			self.stdscr.addstr(size, c3)
			self.stdscr.addstr(' ', c1)
		except curses.error:
			pass
	
	def gotobyte(self):
		c1 = self.colors['BLACK_ON_WHITE']
		gotobyte = ''
		while True:
			self.stdscr.addstr(0, 0, 'Go to byte:', c1)				
			self.stdscr.addstr(0, 11, gotobyte.ljust(self.w-11), c1)
			self.stdscr.move(0, 11 + len(gotobyte))
			self.stdscr.refresh()

			key = self.stdscr.getkey()
			if key.isnumeric() and len(gotobyte) < self.w-12:
				gotobyte = gotobyte + key
			elif key == 'KEY_BACKSPACE':
				gotobyte = gotobyte[:-1]
			elif key == '\n':
				if gotobyte != '':
					return int(gotobyte)
				break
	
def definecolors():
	c = {}
		
	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
	c['BLACK_ON_WHITE'] = curses.color_pair(1)
	
	curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_WHITE)
	c['BLUE_ON_WHITE'] = curses.color_pair(2)
	
	curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_WHITE)
	c['GREEN_ON_WHITE'] = curses.color_pair(3)
	
	curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
	c['CYAN_ON_BLACK'] = curses.color_pair(4)
	
	curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
	c['MAGENTA_ON_BLACK'] = curses.color_pair(5)
	
	curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
	c['YELLOW_ON_BLACK'] = curses.color_pair(6)
	
	curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)
	c['RED_ON_BLACK'] = curses.color_pair(7)
	
	curses.init_pair(8, curses.COLOR_RED, curses.COLOR_WHITE)
	c['RED_ON_WHITE'] = curses.color_pair(8)
	
	curses.init_pair(9, curses.COLOR_WHITE, curses.COLOR_BLACK)
	c['WHITE_ON_BLACK'] = curses.color_pair(9)
	
	curses.init_pair(10, curses.COLOR_RED, curses.COLOR_BLACK)
	c['RED_ON_BLACK'] = curses.color_pair(10)
	
	curses.init_pair(11, curses.COLOR_YELLOW, curses.COLOR_WHITE)
	c['YELLOW_ON_WHITE'] = curses.color_pair(11)
							   
	curses.init_pair(12, curses.COLOR_MAGENTA, curses.COLOR_WHITE)
	c['MAGENTA_ON_WHITE'] = curses.color_pair(12)
	
	return c
