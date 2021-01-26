import os, sys

class ElfFile:
	
	EOF = '\u0004'
	
	def __init__(self, path):
		self.file = open(path, 'r', newline='\n')
		self.name = os.path.basename(path)
		self.path = os.path.abspath(path[:-1*len(self.name)]) + '/'
		self.size = 0
		
		ls = [0]
		self.file.seek(0)
		while True:
			char = self.file.read(1)
			if not char:
				break
			if char == '\n':
				ls.append(self.file.tell())
		self.size = self.file.tell()
		self.file.seek(0)
		self.startlines = ls
		
	def getnextrows(self, startpos, numrows, screenwidth):
		rows = []
		for i in range(numrows):
			row = self.getnextrow(startpos, screenwidth)
			if row == '':
				break
			rows.append(row)
			startpos = startpos + len(row.encode('utf-8'))
			if row.endswith(ElfFile.EOF):
				break
		return rows
	
	def getnextrow(self, startpos, screenwidth):
		if startpos == self.size + 1:
			return ''
		self.file.seek(startpos)
		row = ''
		while len(row) < screenwidth:
			char = self.file.read(1)
			if not char:
				char = ElfFile.EOF
			row = row + char
			if char == '\n' or char == ElfFile.EOF:
				break
		return row
	
	def getprevrows(self, startpos, numrows, screenwidth):
		rows = []
		for i in range(numrows):
			row = self.getprevrow(startpos, screenwidth)
			if row == '':
				return rows
			rows.insert(0, row)
			startpos = startpos - len(row.encode('utf-8'))
		return rows

	def getprevrow(self, startpos, screenwidth):
		if startpos == 0:
			return ''
		prevlinestart = self.getprevlinestart(startpos)
		row = ''
		self.file.seek(prevlinestart)
		while True:
			if len(row) == screenwidth:
				row = ''
			char = self.file.read(1)
			row = row + char
			if char == '\n' or self.file.tell() == startpos:
				break
		return row

	def getprevlinestart(self, pos):
		start = 0
		for ls in self.startlines:
			if ls >= pos:
				return start
			start = ls
		return start

	def getrowsaround(self, pos, numrows, screenwidth):
		rows = []
		pos = self.getprevlinestart(pos)
		prevpos = pos
		nextpos = pos
		while len(rows) < numrows:
			prevrow = self.getprevrow(prevpos, screenwidth)
			if prevrow != '':
				rows.insert(0, prevrow)
				prevpos = prevpos - len(prevrow.encode('utf-8'))
				if len(rows) == numrows:
					break
			nextrow = self.getnextrow(nextpos, screenwidth)
			if nextrow != '':
				rows.append(nextrow)
				nextpos = nextpos + len(nextrow.encode('utf-8'))
			if nextrow == '' and prevrow == '':
				break
		self.file.seek(prevpos)
		return rows
		
		
