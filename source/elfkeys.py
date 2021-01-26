import sys, curses

cursorcheck = ['KEY_UP', 'KEY_DOWN', 'KEY_NPAGE', 'KEY_PPAGE']

def onkeypress(key, screen):
	
	if key == 'KEY_UP':
		if screen.pos[0] > 0:
			screen.pos[0] = screen.pos[0] - 1
		else:
			prevrow = screen.file.getprevrow(screen.startbyte, screen.w)
			if prevrow == '':
				screen.cursormemory = 0
			else:
				screen.addprevrow(prevrow)
		
	elif key == 'KEY_DOWN':
		if screen.pos[0] < screen.numlines() - 1:
			screen.pos[0] = screen.pos[0] + 1
		elif screen.onlastline():
			screen.pos[1] = len(screen.curline()) - 1
			screen.cursormemory = screen.pos[1]
		else:
			nextrow = screen.file.getnextrow(screen.endbyte, screen.w)
			screen.addnextrow(nextrow)
	
	elif key == 'KEY_LEFT':
		if screen.pos[1] == 0:
			if screen.pos[0] == 0:
				prevrow = screen.file.getprevrow(screen.startbyte, screen.w)
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
			if screen.pos[0] == screen.numlines() - 1:
				if not screen.onlastline():
					nextrow = screen.file.getnextrow(screen.endbyte, screen.w)
					screen.addnextrow(nextrow)
					screen.pos[1] = 0
			else:
				screen.pos[0] = screen.pos[0] + 1
				screen.pos[1] = 0
		else:
			screen.pos[1] = screen.pos[1] + 1
			
	elif key == 'KEY_NPAGE':
		if screen.islastline(screen.lines[-1]):
			screen.pos = [screen.numlines()-1, len(screen.lines[-1])-1]
			screen.cursormemory = screen.pos[1]
		else:
			nextrows = screen.file.getnextrows(screen.endbyte, screen.h, screen.w)
			for row in nextrows:
				screen.addnextrow(row)
			
	elif key == 'KEY_PPAGE':
		prevrows = screen.file.getprevrows(screen.startbyte, screen.h, screen.w)
		for row in reversed(prevrows):
			screen.addprevrow(row)
		if len(prevrows) == 0:
			screen.pos = [0,0]
			screen.cursormemory = screen.pos[1]
	
	elif len(key) == 1:
		if ord(key) == 27:
			screen.alt = True

		elif screen.alt:
			screen.alt = False
			if key == 'G':
				alt_shift_g(screen)
				
			
	if key in cursorcheck:
		screen.linelengthcheck()
	else:
		screen.cursormemory = screen.pos[1]

def alt_shift_g(screen):
	gotobyte = screen.gotobyte()
	if gotobyte > screen.file.size:
		gotobyte = screen.file.size			
	screen.lines = screen.file.getrowsaround(gotobyte, screen.h, screen.w)
	screen.startbyte = screen.file.file.tell()
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
	
	
	