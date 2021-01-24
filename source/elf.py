# Editor for Large Files

import sys, curses
import elffile, elfscreen, elfkeys


def main(stdscr):
	
	file = elffile.ElfFile(sys.argv[1])
	screen = elfscreen.ElfScreen(stdscr)
	screen.header1 = file.path
	screen.header2 = file.name
	screen.footer1 = str(0)
	screen.footer2 = str(file.size)
	
	screen.lines = file.getnextrows(0, screen.h, screen.w)
	screen.endbyte = file.file.tell()
	
	while(True):
		screen.printscreen()
		key = stdscr.getkey()
		elfkeys.onkeypress(key, screen, file)



curses.wrapper(main)
