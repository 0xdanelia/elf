import sys, curses

cursorcheck = ['KEY_UP', 'KEY_DOWN', 'KEY_NPAGE', 'KEY_PPAGE']

def onkeypress(key, screen, file):
	
	if key == 'KEY_UP':
		if screen.pos[0] > 0:
			screen.pos[0] = screen.pos[0] - 1
		else:
			prevrow = file.getprevrow(screen.startbyte, screen.w)
			if prevrow == '':
				screen.cursormemory = 0
			else:
				screen.addprevrow(prevrow)
		
	elif key == 'KEY_DOWN':
		if screen.pos[0] < screen.h - 1:
			screen.pos[0] = screen.pos[0] + 1
		else:
			nextrow = file.getnextrow(screen.endbyte, screen.w)
			if nextrow == '':
				screen.cursormemory = len(screen.curline()) - 1
			else:
				screen.addnextrow(nextrow)
	
	elif key == 'KEY_LEFT':
		if screen.pos[1] == 0:
			if screen.pos[0] == 0:
				prevrow = file.getprevrow(screen.startbyte, screen.w)
				if prevrow != '':
					screen.addprevrow(prevrow)
					screen.pos[1] = len(screen.curline()) - 1
			else:
				screen.pos[0] = screen.pos[0] - 1
				screen.pos[1] = len(screen.curline()) - 1
		else:
			screen.pos[1] = screen.pos[1] - 1
	
	elif key == 'KEY_RIGHT':
		if screen.pos[1] == len(screen.curline()) - 1:
			if screen.pos[0] == screen.h - 1:
				nextrow = file.getnextrow(screen.endbyte, screen.w)
				if nextrow != '':
					screen.addnextrow(nextrow)
					screen.pos[1] = 0
			else:
				screen.pos[0] = screen.pos[0] + 1
				screen.pos[1] = 0
		else:
			screen.pos[1] = screen.pos[1] + 1
			
	elif key == 'KEY_NPAGE':
		nextrows = file.getnextrows(screen.endbyte, screen.h, screen.w)
		for row in nextrows:
			screen.addnextrow(row)
			
	elif key == 'KEY_PPAGE':
		prevrows = file.getprevrows(screen.startbyte, screen.h, screen.w)
		for row in reversed(prevrows):
			screen.addprevrow(row)
			
	elif ord(key) == 27:
		screen.alt = True
		
	elif screen.alt:
		screen.alt = False
		if key == 'G':
			gotobyte = screen.alt_g()
			if gotobyte > file.size:
				gotobyte = file.size			
			screen.lines = file.getrowsaround(gotobyte, screen.h, screen.w)
			screen.startbyte = file.file.tell()
			screen.endbyte = screen.startbyte + len(''.join(screen.lines).encode('utf-8'))
		
			p = screen.startbyte
			screen.pos = [0,0]
			for l in screen.lines:
				length = len(l.encode('utf-8'))
				if length + p > gotobyte:
					length = 0
					x = 0
					for c in l:
						length = length + len(c.encode('utf-8'))
						if length > gotobyte - p:
							screen.pos[1] = x
							break
						x = x + 1
					break
				screen.pos[0] = screen.pos[0] + 1
				p = p + length
		
	
	if key in cursorcheck:
		screen.linelengthcheck()
	else:
		screen.cursormemory = screen.pos[1]