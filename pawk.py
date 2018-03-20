#!/usr/bin/python
# -*- coding: utf-8 -*-

import curses
import os
import sys
import curses.textpad
import subprocess
import copy
import stat
from time import sleep
import ConfigParser

MAX_Y, MAX_X = 0, 0
CMD_LIST = []
CMD_UNDO = []
DATA_LIST = []
DATA_UNDO = []
cat_lst = []
FS = " "
RS = "\n"
SHOW_LINE_NUMBERS = False
OFFSET_X = 1
OFFSET_Y = 1

SCRIPT_PATH = os.path.join( os.path.dirname(sys.argv[0]), "scripts", "" )
CONFIG = ConfigParser.RawConfigParser()

def read_conf():
	global CONFIG
	path = os.path.join( os.path.expanduser('~'), ".config", "pawk", "" ) + "conf.rc"
	if os.path.isfile( path ):
		CONFIG.read(path)
	else:
		path = os.path.join( os.path.dirname(sys.argv[0]), "conf.rc" )
		CONFIG.read( path )

def print_help():
	global CONFIG
	msg = """
	HELP
	
	Commands:
	
	%s : advanced commands
	%s : cut -c<Start>-<End>
	%s : egrep
	%s : head -n <N>
	%s : sort
	%s : substitute
	%s : tail -n <N>
	%s : table
	%s : insert a custom command
	
	awk:
	
	%s : select several fields
	%s : grep one line by his number
	%s : where (select a field with condition)
	%s : change field separator
	%s : change line separator
	
	Misc:
	
	%s : edit script
	%s : show/hide line numbers 
	%s : redo
	%s : undo
	%s : search
	%s : print this help message
	%s : quit
	""" % ( CONFIG.get('main_shortcuts', 'advanced_commands'), \
		CONFIG.get('main_shortcuts', 'cut'), \
		CONFIG.get('main_shortcuts', 'grep'), \
		CONFIG.get('main_shortcuts', 'head'), \
		CONFIG.get('main_shortcuts', 'sort'), \
		CONFIG.get('main_shortcuts', 'substitute'), \
		CONFIG.get('main_shortcuts', 'tail'), \
		CONFIG.get('main_shortcuts', 'table'), \
		CONFIG.get('main_shortcuts', 'custom_command'), \
		CONFIG.get('awk_shortcuts', 'select_fields'), \
		CONFIG.get('awk_shortcuts', 'grep_one_line'), \
		CONFIG.get('awk_shortcuts', 'where'), \
		CONFIG.get('awk_shortcuts', 'field_separator'), \
		CONFIG.get('awk_shortcuts', 'line_separator'), \
		CONFIG.get('misc_shortcuts', 'edit'), \
		CONFIG.get('misc_shortcuts', 'line_numbers'), \
		CONFIG.get('misc_shortcuts', 'redo'), \
		CONFIG.get('misc_shortcuts', 'undo'), \
		CONFIG.get('misc_shortcuts', 'search'), \
		CONFIG.get('misc_shortcuts', 'help'), \
		CONFIG.get('misc_shortcuts', 'quit')
		)
	fill_screen( msg )
	statusBar("press 'q' to quit")
	wait_for_key('q')
	fill_screen( DATA_LIST[ -1 ])
	
def quit_curses():
	curses.nocbreak()
	stdscr.keypad(0)
	curses.echo()
	curses.endwin()
	stdscr.clear()

def quit_menu():
	global DATA_LIST
	global CONFIG
	msg = """
             Quit ?
	
	%s : abort
	%s : save data in file
	%s : save script in file
	%s : print data to standard output
	%s : quit
	""" % (\
	CONFIG.get('quit_shortcuts', 'abort'), \
	CONFIG.get('quit_shortcuts', 'data'), \
	CONFIG.get('quit_shortcuts', 'script'), \
	CONFIG.get('quit_shortcuts', 'print'), \
	CONFIG.get('quit_shortcuts', 'quit') )
	
	print_win( msg.split("\n") )
	c = ord(" ")
	
	while c != ord(CONFIG.get('quit_shortcuts', 'quit')):
		
		c = stdscr.getch()
		
		if c == ord(CONFIG.get('quit_shortcuts', 'abort')):
			fill_screen( DATA_LIST[ -1 ])
			return
		
		if c == ord(CONFIG.get('quit_shortcuts', 'print')):
			quit_curses()
			print( DATA_LIST[ -1 ])
			exit(0)
		
		if c == ord(CONFIG.get('quit_shortcuts', 'quit')):
			quit_curses()
			exit(0)
		
		if c == ord(CONFIG.get('quit_shortcuts', 'data')):
			filename = TextBoxInput(["Enter filename"])
			if filename != "":
				statusBar( save(filename, DATA_LIST[ -1 ]) ) 
		
		if c == ord(CONFIG.get('quit_shortcuts', 'script')):
			save_script()
		
		print_win( msg.split("\n") )

def save_script():
	global CMD_LIST
	if len(CMD_LIST) < 2:
		popup("No command")
	else:
		filename = TextBoxInput(["Enter filename"])
		if filename != "":
			statusBar( save(filename, cmd_list_to_pipe(CMD_LIST), True ) )

def save( filename, data, script=False):
	if os.path.exists( filename ):
		m = "File exist"
		print_win([m + ". Do you want to overwrite ? (y/n)"])
		c = stdscr.getch()
		if c != ord('y'):
			return m
	try:
		fd = open( filename, "w" )
	except:
		popup("can't open file %s" % filename)
		return "nothing saved"
	if script:
		fd.write( "#!/bin/bash\n\n" )
	fd.write( data )
	fd.close()
	if script:
		os.chmod(filename, stat.S_IRWXU|stat.S_IRWXG|stat.S_IROTH|stat.S_IXOTH)
	return "%s saved." % filename

def wait_for_key( k ):
	while 1:
		c = stdscr.getch()
		if c == ord(k):
			return

def redraw():
	stdscr.redrawwin()
	stdscr.refresh()

def destroy_window( w ):
	w.erase()
	w.refresh()
	del(w)
	redraw()

def len_max(lst):
	r = 0
	for i in lst:
		li = len(i)
		if li > r:
			r = li
	return r
		
def print_win(msg):
	global MAX_X
	global MAX_Y
	msg = [ "  " + i.replace('\t', '') for i in msg]
	l = len(msg)
	if l > MAX_Y:
		msg = ["Error : message too large"]
		l = 2
	w = len_max( msg ) + 2
	y = (MAX_Y - l) / 2 - 1
	x = (MAX_X - w) / 2 - 1
	new_window = curses.newwin(l + 2, w, y, x)
	new_window.attron(curses.color_pair(2))
	n = 1
	blank = " " * w
	for i in msg:
		try:
			new_window.addstr(n, 0, blank, curses.color_pair(2))
			new_window.addstr(n, 0, i, curses.color_pair(2))
			n += 1
		except:
			pass
	new_window.border()
	new_window.refresh()
	return new_window

def statusBar( left, right="" ):
	global MAX_X
	global MAX_Y
	cls = str(" "*(MAX_X-1))
	stdscr.addnstr(MAX_Y - 1, 0, cls, MAX_X, curses.color_pair(2))
	stdscr.addnstr(MAX_Y - 1, 0, left[:MAX_X - 1], MAX_X, curses.color_pair(2))
	stdscr.addnstr(MAX_Y - 1, MAX_X - len(right) - 1, right[:MAX_X - 1], MAX_X, curses.color_pair(2))
	stdscr.refresh()

def split_rs(data, no_RS):
	global RS
	if no_RS:
		data = data.split("\n")
	else:
		data = data.split(escape_rs( RS ))
	
	if data[ -1 ] == "":
		data.pop()
	return data
	
def fill_screen(data, line_numbers=False, full_line=False, no_RS=False, shift_x=0):
	global MAX_X
	global MAX_Y
	global OFFSET_Y
	global OFFSET_X
	
	stdscr.clear()
	data = split_rs(copy.deepcopy(data), no_RS)

	limit_X = MAX_X
	n = 0
	s = 0
	ld = len(data)
	data = data[ OFFSET_Y - 1 : ]
	limit_Y = min(MAX_Y - 1, len(data))
	nb_num = ""
	
	for i in xrange(limit_Y):
		if line_numbers:
			nb_num = str(n + OFFSET_Y) + " "
		if full_line:
			limit_X = len(nb_num) + len(data[n])
			
		stdscr.addnstr(n +s ,0, nb_num + data[n][shift_x:], limit_X)
		
		if full_line:
			s += (len(nb_num) + len(data[n])) / MAX_X
		n += 1
		
	statusBar("'?' for help", "Line : %i/%i" % (OFFSET_Y, ld) )

def tab_view(data, no_RS=False):
	global FS
	global RS
	global OFFSET_Y
	global MAX_Y
	global MAX_X
	
	data = split_rs(copy.deepcopy(data), no_RS)
	widths = {}
	begin = OFFSET_Y - 1
	end = begin + MAX_Y
	for j in data[begin: end]:
		cpt = 1
		for i in j.split(escape_rs(FS)):
			l = len(i)
			if widths.get(cpt, None) is None:
				widths[cpt] = 0
			if l > widths[cpt]:
				widths[cpt] = l
			cpt += 1
	r = ""
	for i in xrange(len(widths)):
		r += str(i+1).center(widths[i + 1]) + "|"
		#~ r += str(widths[i + 1]) + "|"
	r += escape_rs(RS) + "-" * MAX_X + escape_rs(RS)
	
	for j in data[begin: end]:
		cpt = 1
		for i in j.split(escape_rs(FS)):
			r += i.ljust(widths[cpt]) + "|"
			cpt += 1
		r += escape_rs(RS)
	return r, widths

def update_maxyx():
	global MAX_X
	global MAX_Y
	MAX_Y, MAX_X = stdscr.getmaxyx()

def call_awk(command, arg, data):
	cmd = [command] 
	if type(arg) == list:
		for i in arg:
			cmd.append(i)
	else:
		cmd.append(arg)
	return call_external_command(cmd, data)

def call_external_command(command, data):
	try:
		p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
		p.stdin.write(data)
	except:
		print_win(["%s fail" % command])
		c = stdscr.getch()
		return None
	else:
		return p.communicate()[0]

def TextBoxInput(m1):
	global MAX_X
	global MAX_Y
	grep_win = print_win( m1 )
	win = curses.newwin(1, MAX_X, MAX_Y - 1, 0)
	tb = curses.textpad.Textbox(win)
	text = tb.edit()
	destroy_window(grep_win)
	destroy_window(win)
	return text[ : -1 ]

def popup( msg ):
	popup = print_win([msg])
	stdscr.getch()
	destroy_window(popup)

def cmd_list_to_pipe( lst ):
	r = ""
	for i in lst:
		r += i + " | "
	return r[ : -3 ]

def print_script():
	global CMD_LIST
	global cat_lst
	global OFFSET_Y
	global SHOW_LINE_NUMBERS
	global CONFIG
	
	old = OFFSET_Y
	OFFSET_Y = 1
	c = ""
	
	while c != ord(CONFIG.get('quit_shortcuts', 'quit')):
		if len(CMD_LIST) == 0:
			statusBar("There is no command.")
			return
		msg = "\nCommand list:\n\n"
		n = 1
		for i in CMD_LIST:
			msg += str(n) + " : " + i + "\n"
			n += 1
		
		concat = cmd_list_to_pipe(CMD_LIST)
		if concat != "":
			msg += "\n\n\nOneLiner:\n\n"
		msg += concat
		
		fill_screen( msg, line_numbers=False, full_line=True, no_RS=True)
		statusBar("q : quit | %s : undo | %s : redo | s : save script" % (\
			CONFIG.get('misc_shortcuts', 'undo'), \
			CONFIG.get('misc_shortcuts', 'redo') ) )
		
		c = stdscr.getch()
		if c == ord(CONFIG.get('misc_shortcuts', 'undo')):
			undo()
			
		if c == ord(CONFIG.get('misc_shortcuts', 'redo')):
			redo()
			
		if c == ord('s'):
			save_script()
			
		if c == ord(CONFIG.get('misc_shortcuts', 'edit')):
			break
	
	OFFSET_Y = old
	fill_screen( DATA_LIST[ -1 ], SHOW_LINE_NUMBERS)

def undo():
	global CMD_LIST
	global CMD_UNDO
	global DATA_LIST
	global DATA_UNDO
	
	if len(CMD_LIST) > 1:
		CMD_UNDO.append(CMD_LIST.pop())
		DATA_UNDO.append(DATA_LIST.pop())
	else:
		statusBar("Nothing to undo.")
		return -1
	return 0
			
def redo():
	global CMD_LIST
	global CMD_UNDO
	global DATA_LIST
	global DATA_UNDO
	
	if len(CMD_UNDO) > 0:
		CMD_LIST.append(CMD_UNDO.pop())
		DATA_LIST.append(DATA_UNDO.pop())
	else:
		statusBar("Nothing to redo.")
		return -1	
		
	return 0

def parse_fields_list( l ):
	add = []
	remove = []
	r = []
	for i in l.split():
		if i[0] == "-":
			remove.append(i[1:])
		elif i == "*":
			cf = count_fields(DATA_LIST[ -1 ])
			for j in xrange(cf):
					add.append(str(j+1))
		else:
			add.append(i)
	
	for i in add:
		if "-" in i:
			start, end = i.split('-')
			for j in range(int(start), int(end) + 1):
				if str(j) not in remove :
					r.append( j )
		else:
			r.append( int(i) )
	for i in remove:
		if int(i) in r:
			r.remove(int(i))
	return r
		
def lst2colums(lst):
	global FS		
	columns = ""
	l = len(lst)
	n = 0
	for i in lst:
		columns += "$%i" %i
		n += 1
		if n < l:
			columns += '"%s"' % FS
	return columns

def paint_field(win, offset_x, start, end, data, shift_y=0 ):
	global FS
	global MAX_Y
	y = 0
	for i in data.split( RS )[shift_y :]:
		paint(win, y, offset_x, i[start:end] )
		y += 1
		if y > MAX_Y:
			return

def width_field(n , dico):
	if len(dico) == 0:
		return 1, 1
	begin = 0
	for i in dico:
		if i == n:
			return begin + n - 1, begin + dico[i] + n - 1
		begin += dico[i]

def fields(limit=0, msg=[]):
	global SHOW_LINE_NUMBERS
	global FS
	global OFFSET_Y
	global MAX_X
	global CONFIG
	lst = []
	c = ord('a')
	columns = ""
	actual_column = 1
	data, meta = tab_view(DATA_LIST[ -1 ])
	old = OFFSET_Y
	OFFSET_Y = 1
	shift_x = 0
	cpt = 0
	
	while c != ord(CONFIG.get('misc_shortcuts', 'quit')):
		
		if limit != 0:
			if len(lst) == limit:
				return lst
		
		d, f = width_field(actual_column , meta)
		while d > shift_x:
			shift_x += MAX_X
		if d - shift_x < 0:
			shift_x -= MAX_X
			
		fill_screen(data, shift_x=shift_x)
		paint_field(stdscr, d - shift_x, d, f, data )
		statusBar("Column : %i | Actuals fields are : %s | a : append | r : remove last one | m : manually | %s : field separator | %s : quit" % ( \
			actual_column, str(lst), \
			CONFIG.get('misc_shortcuts', 'quit'), \
			CONFIG.get('awk_shortcuts', 'field_separator')) )
		
		if cpt == 0 and len(msg) > 0:
			print_win(msg)
		
		c = stdscr.getch()
		
		if c == ord('a') or c == curses.KEY_ENTER:
			lst.append( actual_column )
			actual_column += 1
		
		if c == ord('F'):
			new_field_separator()
			data, meta = tab_view(DATA_LIST[ -1 ])
			
		if c == ord('r'):
			if len(lst) > 0:
				lst.pop()
		
		if c == ord('m'):
			msg = ['', 'Enter the list of fields', '', \
				'Examples :', '' \
				'2 3       : only the fields 2 and 3',\
				'2-6 -3    : the fields 2 to 6 except the 3th',\
				'* -4 -7   : all fields except the 4th and the 7th']
			r = TextBoxInput(msg)
			if isDigitStarMinus(r):
				lst = parse_fields_list( r )
			else:
				popup("Syntax error")
		
		if c == curses.KEY_LEFT:
			actual_column -= 1
		
		if c == curses.KEY_RIGHT:
			actual_column += 1
			
		if actual_column > len(meta):
			actual_column = 1
			shift_x = 0
			
		if actual_column < 1:
			actual_column = len(meta)
		
		cpt += 1
		
	fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS)
	OFFSET_Y = old
	return lst

def cut():
	global SHOW_LINE_NUMBERS
	global RS
	global FS
	global OFFSET_Y
	global MAX_Y
	global MAX_X
	global CONFIG
	
	start = 0
	end = 2
	shift_x = 0
	
	c = ord('a')
	while c != ord(CONFIG.get('misc_shortcuts', 'quit')):
		
		while start > shift_x:
			shift_x += MAX_X
		if start - shift_x < 0:
			shift_x -= MAX_X
			
		fill_screen(DATA_LIST[ -1 ], shift_x=shift_x)
		paint_field(stdscr, start - shift_x, start, end + 1, DATA_LIST[ -1 ], OFFSET_Y - 1)
		statusBar("start : %i | end : %i | %s : quit" % ( start, end, CONFIG.get('misc_shortcuts', 'quit') ) )
		
		c = stdscr.getch()
		
		if c == curses.KEY_LEFT:
			if start > 0:
				start -= 1
				end   -= 1
		
		if c == curses.KEY_RIGHT:
			start += 1
			end   += 1
		
		if c == curses.KEY_UP:
			end += 1
		
		if c == curses.KEY_DOWN:
			end   -= 1
			if end < start:
				end = start
			
	call_pipe("cut -c%i-%i" % (start + 1, end + 1))

def debug( m ):
	fd = open("/tmp/debug", "a")
	fd.write(str(m) + '\n')
	fd.close()

def isDigit ( n ):
	for i in n:
		if i not in "0123456789":
			return False
	return True

def isDigitStarMinus(n):
	for i in n:
		if i not in "0123456789-* ":
			return False
	return True

def list2str( l ):
	r = ""
	for i in l:
		r += i + " "
	return r[ : -1 ]

def count_fields( data):
	global RS
	global FS
	r = 0
	for i in data.split(escape_rs( RS )):
		l = len( i.split(escape_rs( FS ) ) )
		if l > r:
			r = l
	return r

def RS_text():
	global RS
	if escape_rs( RS ) != "\n":
		return 'RS="%s";' % RS
	else:
		return ""
		
def FS_text():
	global FS
	if FS != " ":
		return 'FS="%s";' % FS
	else:
		return ""

def awk_begin( m="" ):
	m += RS_text()
	m += FS_text()
	if m == "":
		return ""
	return "BEGIN{%s}" % m

def where():
	msg = ['', '                      "where" condition.', '', \
		'Example : ', '', \
		'$1 ~ /foo/      : select lines where first field contain "foo"', \
		'$7 !~ /^$/      : select lines where 7th field is not empty', \
		'(n>10 && n<15)  : select only the lines 11 to 14.', '']
	r = TextBoxInput(msg)
	if r == "":
		return
	call_pipe("awk '%s{if (%s) {print $0; }; n++}'" % (awk_begin("n=1;"), r))

def escape_rs( t, reverse=False):
	d = { 	"\\n" : "\n", \
			"\\r" : "\r", \
			"\\t" : "\t"  }
	for k, v in d.iteritems():
		if reverse:
			t = t.replace(v, k)
		else:
			t = t.replace(k, v)
	return t

def search_line(m, line_number, line):
	r = []
	pos = -1
	for i in xrange(line.count(m)):
		pos = line.find(m, pos + 1)
		r.append( (line_number, pos) )
	return r

def paint(win, y, x, text):
	cpt = 0
	for i in text:
		try:
			win.addch(y, x + cpt, i, curses.color_pair(2) )
			cpt += 1
		except:
			pass
	
def search( m ):
	global DATA_LIST
	global OFFSET_Y
	global OFFSET_X
	global SHOW_LINE_NUMBERS
	global CONFIG
	
	history = []
	cpt = 0
	d = DATA_LIST[ -1 ].split(escape_rs( RS ))
	for i in d:
		for j in search_line(m, cpt, i):
			history.append(j)
		cpt += 1
	if len(history) == 0 :
		statusBar("No pattern found")
		return
	
	pos = 0
	c = 0
	OFFSET_Y = history[pos][0] + 1
	fill_screen(DATA_LIST[ -1 ])
	paint(stdscr, 0, history[pos][1], m)
	statusBar("%i occurrence(s) found | line : %i" % (len(history), OFFSET_Y), "n : next | p : previous | 'q' : quit")
	
	while True:
		c = stdscr.getch()
		OFFSET_Y = history[pos][0] + 1
		msg = ""
		
		if c == ord(CONFIG.get('misc_shortcuts', 'quit')):
			fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS)
			return
			
		if c == ord(CONFIG.get('misc_shortcuts', 'search_next')):
			pos += 1
			if pos >= len(history):
				pos = 0
				msg = " | search hit BOTTOM, continuing at TOP"
			
		if c == ord(CONFIG.get('misc_shortcuts', 'search_previous')):
			pos -= 1
			if pos < 0 :
				pos = len(history) - 1
				msg = " | search hit TOP, continuing at BOTTOM"
		
		OFFSET_Y = history[pos][0] + 1
		fill_screen(DATA_LIST[ -1 ])
		paint(stdscr, 0, history[pos][1], m)
		msg = "line : %i" % OFFSET_Y + msg
		statusBar(msg, "%s : next | %s : previous | %s : quit" % ( \
			CONFIG.get('misc_shortcuts', 'search_next'), \
			CONFIG.get('misc_shortcuts', 'search_previous'), \
			CONFIG.get('misc_shortcuts', 'quit') ) )

def new_line_separator():
	global RS
	r = TextBoxInput(["Define a new line separator"])
	if r != '':
		RS = r
	fill_screen(DATA_LIST[ -1 ])

def new_field_separator():
	global FS
	r = TextBoxInput(["Define a new field separator"])
	if r != '':
		FS = r

def append_field():
	msg = ['', '                      append a field', '', \
		'Example : ', '', \
		'$1*$2      : just multiply the field 1 and two', \
		'n          : the current line number', '']
	r = TextBoxInput(msg)
	if r == "":
		return
	call_pipe("awk '%s{print $0,%s; n++}'" % (awk_begin("n=1;"), r) )	

def insert_line_number():
	call_pipe("awk '%s{print n\"%s\"$0; n++}'" % (awk_begin("n=1;"), FS) )

def transpose():
	global CMD_LIST
	pre_list = cmd_list_to_pipe(CMD_LIST)
	cmd = "head -n 1 | awk 'BEGIN{RS=\"%s\";ORS=\"%s\"}{if (RT==\"\") printf \"%%s\",$0; else print}' | wc -l | for n in $(seq $( xargs )); do %s | cut --delimiter=\"%s\" -f$n | awk 'BEGIN{RS=\"%s\";ORS=\"%s\"}{if (RT==\"\") printf \"%%s\",$0; else print}'; echo ""; done" % \
		( escape_rs(FS, True), \
		escape_rs(RS, True), \
		pre_list, \
		escape_rs(FS, True), \
		escape_rs(RS, True), \
		escape_rs(FS, True))
	call_pipe(cmd)

def padding(l):
	l2 = lst2colums( [i + 1 for i in xrange(count_fields(DATA_LIST[ -1 ]) ) ] )
	r = ""
	print_win( ["align ?", "l : left", "r : right"] )
	while r != ord("l") and r != ord("r"):
		r = stdscr.getch()
		if r ==  ord("l"):
			l2 = l2.replace('$%i' % l, '$%ip' % l)
		if r ==  ord("r"):
			l2 = l2.replace('$%i' % l, 'p$%i' % l)
	msg = ["length ?"]
	r = TextBoxInput(["length ?"])
	call_pipe("awk '%s{ p=\"\"; for (i = 1; i <= %s - length($%i); i++) { p = p\" \" }; print %s}'" % (awk_begin(), r, l, l2) )

def auto_padding():
	r = ""
	print_win( ["align ?", "l : left", "r : right"] )
	while r != ord("l") and r != ord("r"):
		r = stdscr.getch()
		padding = ""
		if r ==  ord("r"):
			padding = "right=1;"
	call_pipe("awk '%s'" % ( get_script("padding.awk") % awk_begin("l=0;ORS = \"\";" + padding) ) )
	
def advanced_commands():
	global CONFIG
	msg = """
	ADVANCED COMMANDS
	
	%s : append a field
	%s : count occurrences on selected field
	%s : histogram
	%s : insert the line number on the first field
	%s : compute the mean
	%s : maximum value
	%s : minimum value
	%s : padding
	%s : auto padding all fields
	%s : sum values on selected field
	%s : transpose
	
	""" % ( \
	CONFIG.get('ac', 'append_field'), \
	CONFIG.get('ac', 'count'), \
	CONFIG.get('ac', 'histogram'), \
	CONFIG.get('ac', 'insert'), \
	CONFIG.get('ac', 'mean'), \
	CONFIG.get('ac', 'max'), \
	CONFIG.get('ac', 'min'), \
	CONFIG.get('ac', 'padding'), \
	CONFIG.get('ac', 'auto_padding'), \
	CONFIG.get('ac', 'sum'), \
	CONFIG.get('ac', 'transpose') )
	fill_screen( msg )
	statusBar("press '%s' to quit" % CONFIG.get('misc_shortcuts', 'quit'))
	
	while 1:
		c = stdscr.getch()
		
		if c == ord(CONFIG.get('ac', 'count')):
			f = fields(1)
			if len( f ) == 0:
				return
			count( f[0] )
			return
		
		if c == ord(CONFIG.get('ac', 'append_field')):
			append_field()
			return
		
		if c == ord(CONFIG.get('ac', 'insert')):
			insert_line_number()
			return
		
		if c == ord(CONFIG.get('ac', 'transpose')):
			transpose()
			return
		
		if c == ord(CONFIG.get('ac', 'sum')):
			f = fields(1)
			if len( f ) == 0:
				return
			sum_( f[0] )
			return
		
		if c == ord(CONFIG.get('ac', 'mean')):
			f = fields(1)
			if len( f ) == 0:
				return
			mean( f[0] )
			return
		
		if c == ord(CONFIG.get('ac', 'max')):
			f = fields(1)
			if len( f ) == 0:
				return
			max_( f[0] )
			return
		
		if c == ord(CONFIG.get('ac', 'min')):
			f = fields(1)
			if len( f ) == 0:
				return
			min_( f[0] )
			return
		
		if c == ord(CONFIG.get('ac', 'padding')):
			f = fields(1)
			if len( f ) == 0:
				return
			padding( f[0] )
			return
		
		if c == ord(CONFIG.get('ac', 'auto_padding')):
			auto_padding()
			return
		
		if c == ord(CONFIG.get('ac', 'histogram')):
			histogram()
			return
		
		if c == ord(CONFIG.get('misc_shortcuts', 'quit')):
			return

def remove_tabs( t ):
	return t.replace("\t", "").replace("\n", "")

def histogram():
	call_pipe("awk '%s'" % (get_script("histogram.awk") % awk_begin("l=0;") ) )
	
def sum_( f ):
	call_pipe("awk '%s'" % (get_script("sum.awk") % ( awk_begin(), f) ) )
	
def mean( f ):
	call_pipe("awk '%s'" % (get_script("mean.awk") % ( awk_begin(), f) ) )
	
def max_( f ):
	call_pipe("awk '%s'" % (get_script("max.awk") % ( awk_begin(), f, ">") ) )
	
def min_( f ):
	call_pipe("awk '%s'" % (get_script("max.awk") % ( awk_begin(), f, "<") ) )
	
def call_pipe(cmd):
	global SHOW_LINE_NUMBERS
	d = call_external_command(["bash", "-c", cmd], DATA_LIST[ -1 ])
	CMD_LIST.append(cmd)
	DATA_LIST.append(d)
	fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS)

def count(lst):
	global CMD_LIST
	pre_list = cmd_list_to_pipe(CMD_LIST) + " | awk '%s{ print $%s }'" % (awk_begin(), lst )
	cmd = "awk '%s{ print $%s }' | sort | uniq | for i in $(xargs -0); do echo -n $i\"%s\" ; %s | grep $i | wc -l; done" \
		% (awk_begin(), lst, escape_rs(FS, True), pre_list)
	call_pipe(cmd)

def sort():
	global FS
	split = "e3e5f8d6e6fd4fb79"
	while split in DATA_LIST[ -1 ]:
		split += split
	columns = ""
	lst = fields()
	msg = """
sort options :

	-d, --dictionary-order
	-f, --ignore-case
	-M, --month-sort
	-h, --human-numeric-sort
	-n, --numeric-sort
	-R, --random-sort
	-r, --reverse
	""".split('\n')
	if len(lst) > 0:
		for i in lst:
			columns += '$%i" "' % i
		columns += '"%s"$0' % split
		cmd = "awk '%s{ print %s }'" % (awk_begin(), columns)
		cmd += "|sort %s" % TextBoxInput(msg)
		cmd += '|sed "s/^.*%s//g"' % split
		call_pipe(cmd)
	fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS)

def get_script( name ):
	return remove_tabs( open( SCRIPT_PATH + name ).read() )

def table( f ):
	columns_align_right = ""
	for i in f:
		columns_align_right += "r[%i]=1;" % i
	msg = """
	Header ?
	
	0 : no header
	N : the Nth line will be a separator
	""".split("\n")
	r = TextBoxInput(msg)
	if r.isdigit():
		if r == "0":
			r = -1
		columns_align_right += "header=%s;" % r
	else:
		columns_align_right += "header=%i;" % -1
	columns_align_right += "footer=-1;"
	call_pipe( "awk '%s'" % ( get_script( "table.awk") % awk_begin("l=0;OFS = \"|\";ORS = \"\";" + columns_align_right ) ) )
	
def main_function(arg):
	global FS
	global RS
	global MAX_Y
	global MAX_X
	global CMD_LIST
	global CMD_UNDO
	global DATA_LIST
	global DATA_UNDO
	global SHOW_LINE_NUMBERS
	global OFFSET_Y
	global OFFSET_X
	global CONFIG
	
	read_conf()
	update_maxyx()
	fill_screen(DATA_LIST[0])
	
	while 1:
		c = stdscr.getch()
		
		if c == ord(CONFIG.get('main_shortcuts', 'advanced_commands')):
			advanced_commands()
			fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS)
		
		if c == ord(CONFIG.get('main_shortcuts', 'cut')):
			cut()
		
		if c == ord(CONFIG.get('misc_shortcuts', 'quit')):
			quit_menu()
			
		if c == ord(CONFIG.get('misc_shortcuts', 'undo')):
			undo()
			fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS )
			
		if c == ord(CONFIG.get('misc_shortcuts', 'redo')):
			redo()
			fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS )
			
		if c == ord(CONFIG.get('misc_shortcuts', 'edit')):
			print_script()
			
		if c == ord(CONFIG.get('misc_shortcuts', 'help')):
			print_help()
			
		if c == ord(CONFIG.get('main_shortcuts', 'custom_command')):
			r = TextBoxInput(["External command"])
			if r != "":
				call_pipe(r)
			
		if c == ord(CONFIG.get('main_shortcuts', 'grep')):
			call_pipe("egrep %s" % TextBoxInput(["Enter regex to egrep"]))
		
		if c == ord(CONFIG.get('awk_shortcuts', 'field_separator')):
			new_field_separator()
			fill_screen(DATA_LIST[ -1 ])
			
		if c == ord(CONFIG.get('awk_shortcuts', 'line_separator')):
			new_line_separator()
			fill_screen(DATA_LIST[ -1 ])
			
		if c == ord(CONFIG.get('misc_shortcuts', 'line_numbers')):
			if SHOW_LINE_NUMBERS:
				SHOW_LINE_NUMBERS = False
			else:
				SHOW_LINE_NUMBERS = True
			fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS)
			
		if c == ord( CONFIG.get('awk_shortcuts', 'select_fields') ):
			lst = fields()			
			if len(lst) > 0:
				call_pipe("awk '%s{ print %s }'" % (awk_begin(), lst2colums(lst)) )
			
		if c == ord(CONFIG.get('awk_shortcuts', 'grep_one_line')):
			r = TextBoxInput(["Enter the line number"])
			if isDigit(r):
				call_pipe("awk '%s{if (n==%s) {print $0; exit}; n++}'" % (awk_begin("n=1;"), r))
			else:
				statusBar("You have to enter a valid number")
		
		if c == curses.KEY_RESIZE:
			update_maxyx()
			redraw()
		
		if c == ord(CONFIG.get('main_shortcuts', 'substitute')):
			old = TextBoxInput(["Enter old pattern"])
			new = TextBoxInput(["Enter new pattern"])
			call_pipe("awk 'BEGIN{RS=\"%s\";ORS=\"%s\"}{if (RT==\"\") printf \"%%s\",$0; else print}'" % (old, new))
			
		if c == ord(CONFIG.get('main_shortcuts', 'tail')):
			call_pipe("tail -n " + TextBoxInput(["tail -n <N>"]))
			
		if c == ord(CONFIG.get('main_shortcuts', 'table')):
			table( fields( msg=["Select all fields to align right"] ) )
			
		if c == ord(CONFIG.get('main_shortcuts', 'head')):
			call_pipe("head -n " + TextBoxInput(["head -n <N>"]))
			
		if c == ord(CONFIG.get('main_shortcuts', 'sort')):
			sort()
			
		if c == ord(CONFIG.get('awk_shortcuts', 'where')):
			where()
		
		if c == curses.KEY_NPAGE:
			n = OFFSET_Y + MAX_Y - 1
			if n < len(DATA_LIST[ -1 ].split(escape_rs( RS ) ) ):
				OFFSET_Y = n
				fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS)
				
		if c == curses.KEY_PPAGE:
			n = OFFSET_Y - MAX_Y
			if n < 1:
				OFFSET_Y = 1
			else:
				OFFSET_Y = n
			fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS)
			
		if c == ord(CONFIG.get('misc_shortcuts', 'search')):
			search(TextBoxInput(["Enter pattern to search"]))
		
		sleep(0.01)


if __name__ == "__main__":
	DATA_LIST = []
	cat_lst = []
	arg = sys.argv[1:]
	raw_data = ""
	cat = "cat "
	
	for i in arg:
		if not os.path.exists(i):
			sys.stderr.write("File %s not found." % i)
		else:
			try:
				fd = open(i)
				raw_data += fd.read()
				cat_lst.append(i)
				cat += i
			except:
				sys.stderr.write("Can't read %s." % i)
			else:
				fd.close()
	
	if len(sys.argv) < 2:
		raw_data = ""
		try:
			raw_data = sys.stdin.read()
			# Don't work
		except:
			sys.stderr.write("pipe fail")
	
	else:
		CMD_LIST.append(cat)
	
	DATA_LIST.append(raw_data)
	
	stdscr = curses.initscr()
	curses.start_color()
	curses.noecho()
	curses.cbreak()
	stdscr.keypad(1)
	curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
	curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
	curses.init_pair(3, curses.COLOR_RED, curses.COLOR_WHITE)
	curses.wrapper(main_function)
