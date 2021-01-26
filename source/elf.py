# Editor for Large Files

import sys, curses
import elffile, elfscreen, elfkeys


def main(stdscr):
	
	screen = elfscreen.ElfScreen(stdscr, sys.argv[1])
	
	screen.lines = screen.file.getnextrows(0, screen.h, screen.w)
	screen.endbyte = screen.file.file.tell()
	screen.finalbyte = screen.file.size
	
	while(True):
		screen.printscreen()
		key = stdscr.getkey()
		elfkeys.onkeypress(key, screen)



curses.wrapper(main)
