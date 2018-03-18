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
	
def print_help():
	msg = """
	HELP
	
	Commands :
	
	a : advanced commands
	c : cut -c<Start>-<End>
	g : egrep
	h : head -n <N>
	o : sort
	s : substitute
	t : tail -n <N>
	i : insert a custom command
	
	awk :
	
	f : select several fields
	l : grep one line by his number
	w : where (select a field with condition)
	F : change field separator
	L : change line separator
	
	Shortcuts :
	
	e : edit script
	n : show/hide line numbers 
	r : redo
	u : undo
	/ : search
	? : print this help message
	q : quit
	"""
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
	msg = """
             Quit ?
	
	a : abort
	d : save data in file
	s : save script in file
	p : print data to standard output
	q : quit
	"""
	
	print_win( msg.split("\n") )
	c = ord(" ")
	
	while c != ord('q'):
		
		c = stdscr.getch()
		
		if c == ord('a'):
			fill_screen( DATA_LIST[ -1 ])
			return
		
		if c == ord('p'):
			quit_curses()
			print( DATA_LIST[ -1 ])
			exit(0)
		
		if c == ord('q'):
			quit_curses()
			exit(0)
		
		if c == ord('d'):
			filename = TextBoxInput(["Enter filename"])
			if filename != "":
				popup( save(filename, DATA_LIST[ -1 ]) )
		
		if c == ord('s'):
			save_script()
		
		print_win( msg.split("\n") )

def save_script():
	global CMD_LIST
	if len(CMD_LIST) < 2:
		popup("No command")
	else:
		filename = TextBoxInput(["Enter filename"])
		if filename != "":
			popup( save(filename, cmd_list_to_pipe(CMD_LIST), True ) )

def save( filename, data, script=False):
	if os.path.exists( filename ):
		m = "File exist"
		return m
	fd = open( filename, "w" )
	fd.write( "#!/bin/bash\n\n" + data )
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
	
	old = OFFSET_Y
	OFFSET_Y = 1
	c = ""
	
	while c != ord('q'):
		if len(CMD_LIST) == 0:
			statusBar("There is no command.")
			return
		msg = "\nCommand list :\n\n"
		n = 1
		for i in CMD_LIST:
			msg += str(n) + " : " + i + "\n"
			n += 1
		
		concat = cmd_list_to_pipe(CMD_LIST)
		if concat != "":
			msg += "\n\n\nOneLiner :\n\n"
		msg += concat
		
		fill_screen( msg, line_numbers=False, full_line=True, no_RS=True)
		statusBar("q : quit | u : undo | r : redo | s : save script")
		
		c = stdscr.getch()
		if c == ord('u'):
			undo()
			
		if c == ord('r'):
			redo()
			
		if c == ord('s'):
			save_script()
			
		if c == ord('e'):
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

def fields(limit=0):
	global SHOW_LINE_NUMBERS
	global FS
	global OFFSET_Y
	global MAX_X
	lst = []
	c = ord('a')
	columns = ""
	actual_column = 1
	data, meta = tab_view(DATA_LIST[ -1 ])
	old = OFFSET_Y
	OFFSET_Y = 1
	shift_x = 0
	
	while c != ord('q'):
		
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
		statusBar("Column : %i | Actuals fields are : %s | a : append | r : remove last one | m : manually | F : field separator | q : quit" % (actual_column, str(lst)) )
		
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
	
	start = 0
	end = 2
	shift_x = 0
	
	c = ord('a')
	while c != ord('q'):
		
		while start > shift_x:
			shift_x += MAX_X
		if start - shift_x < 0:
			shift_x -= MAX_X
			
		fill_screen(DATA_LIST[ -1 ], shift_x=shift_x)
		paint_field(stdscr, start - shift_x, start, end + 1, DATA_LIST[ -1 ], OFFSET_Y - 1)
		statusBar("start : %i | end : %i | q : quit" % ( start, end ) )
		
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
		
		if c == ord('q'):
			fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS)
			return
			
		if c == ord('n'):
			pos += 1
			if pos >= len(history):
				pos = 0
				msg = " | search hit BOTTOM, continuing at TOP"
			
		if c == ord('p'):
			pos -= 1
			if pos < 0 :
				pos = len(history) - 1
				msg = " | search hit TOP, continuing at BOTTOM"
		
		OFFSET_Y = history[pos][0] + 1
		fill_screen(DATA_LIST[ -1 ])
		paint(stdscr, 0, history[pos][1], m)
		msg = "line : %i" % OFFSET_Y + msg
		statusBar(msg, "n : next | p : previous | q : quit")

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
		if r ==  ord("l"):
			before = ""
			after = ",p"
		if r ==  ord("r"):
			before = "p,"
			after = ""
	call_pipe("awk '%s{for (i=1; i<=NF; i++) { if (length($i)>max[i]) {max[i]=length($i);}data[l]=$i;l++;}}END {d = 0;for (l=0; l<NR; l++) {for (c=1; c<=NF; c++) {p=\"\"; for (j=0; j < (max[c]-length(data[d])); j++) { p = p\" \";}printf \"%%s%%s\", %s data[d] %s;if (c!=NF) {printf \"%%s\", FS;}d++;}print \"\";}}'" % (awk_begin("l=0;"), before, after))
	
def advanced_commands():
	msg = """
	ADVANCED COMMANDS
	
	a : append a field
	c : count occurrences on selected field
	h : histogram
	i : insert the line number on the first field
	m : compute the mean
	p : padding
	P : auto padding all fields
	s : sum values on selected field
	t : transpose
	
	"""
	fill_screen( msg )
	statusBar("press 'q' to quit")
	while 1:
		c = stdscr.getch()
		
		if c == ord('c'):
			f = fields(1)
			if len( f ) == 0:
				return
			count( f[0] )
			return
		
		if c == ord('a'):
			append_field()
			return
		
		if c == ord('i'):
			insert_line_number()
			return
		
		if c == ord('t'):
			transpose()
			return
		
		if c == ord('s'):
			f = fields(1)
			if len( f ) == 0:
				return
			sum_( f[0] )
			return
		
		if c == ord('m'):
			f = fields(1)
			if len( f ) == 0:
				return
			mean( f[0] )
			return
		
		if c == ord('p'):
			f = fields(1)
			if len( f ) == 0:
				return
			padding( f[0] )
			return
		
		if c == ord('P'):
			auto_padding()
			return
		
		if c == ord('h'):
			f = fields(1)
			if len( f ) == 0:
				return
			histogram( f[0] )
			return
		
		if c == ord('q'):
			return

def histogram(f):
	call_pipe("awk '%s{ print $%s }'" % (awk_begin(), f) )
	r = TextBoxInput(["scale to ?"])
	pre_list = cmd_list_to_pipe(CMD_LIST)
	if r != "":
		if isDigit(r):
			limit = r
			cmd = 'pawk_max=0; for i in $(%s); do if [[ "$i" -gt "$pawk_max" ]]; then pawk_max=$i; fi done; r=$(echo "scale=10;$pawk_max/%s"|bc); for i in $(%s); do echo "scale=0;$i/$r" | bc ; done | for l in $(xargs); do for i in $(seq 0 $l); do echo -n "*"; done ; echo ;done' % (pre_list, limit, pre_list)
	else:
		cmd = 'for l in $(xargs); do for i in $(seq 0 $l); do echo -n "*"; done ; echo ; done'
	
	call_pipe(cmd)
	
def sum_( f ):
	call_pipe("awk '%s{ print $%s }' | sed 's/^$/0/g' | awk 'BEGIN{RS=\"%s\";ORS=\"%s\"}{if (RT==\"\") printf \"%%s\",$0; else print}' | sed \"s/+$/\\n/g\" | bc" % (awk_begin(), f, "\\n", "+") )
	
def mean( f ):
	global CMD_LIST
	pre_list = cmd_list_to_pipe(CMD_LIST)
	sum_( f )
	cmd = "tr '\\n' '/' |  xargs -I'{}' echo \"scale=10;\"{}$(%s) | bc " % ( pre_list + " | wc -l")
	call_pipe(cmd)
	
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
	
	update_maxyx()
	fill_screen(DATA_LIST[0])
	
	while 1:
		c = stdscr.getch()
		
		if c == ord('a'):
			advanced_commands()
			fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS)
		
		if c == ord('c'):
			cut()
		
		if c == ord('q'):
			quit_menu()
			
		if c == ord('u'):
			undo()
			fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS )
			
		if c == ord('r'):
			redo()
			fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS )
			
		if c == ord('e'):
			print_script()
			
		if c == ord('?'):
			print_help()
			
		if c == ord('i'):
			r = TextBoxInput(["External command"])
			if r != "":
				call_pipe(r)
			
		if c == ord('g'):
			call_pipe("egrep %s" % TextBoxInput(["Enter regex to egrep"]))
		
		if c == ord('F'):
			new_field_separator()
			fill_screen(DATA_LIST[ -1 ])
			
		if c == ord('L'):
			new_line_separator()
			fill_screen(DATA_LIST[ -1 ])
			
		if c == ord('n'):
			if SHOW_LINE_NUMBERS:
				SHOW_LINE_NUMBERS = False
			else:
				SHOW_LINE_NUMBERS = True
			fill_screen(DATA_LIST[ -1 ], SHOW_LINE_NUMBERS)
			
		if c == ord('f'):
			lst = fields()			
			if len(lst) > 0:
				call_pipe("awk '%s{ print %s }'" % (awk_begin(), lst2colums(lst)) )
			
		if c == ord('l'):
			r = TextBoxInput(["Enter the line number"])
			if isDigit(r):
				call_pipe("awk '%s{if (n==%s) {print $0; exit}; n++}'" % (awk_begin("n=1;"), r))
			else:
				statusBar("You have to enter a valid number")
		
		if c == curses.KEY_RESIZE:
			update_maxyx()
			redraw()
		
		if c == ord('s'):
			old = TextBoxInput(["Enter old pattern"])
			new = TextBoxInput(["Enter new pattern"])
			call_pipe("awk 'BEGIN{RS=\"%s\";ORS=\"%s\"}{if (RT==\"\") printf \"%%s\",$0; else print}'" % (old, new))
			
		if c == ord('t'):
			call_pipe("tail -n " + TextBoxInput(["tail -n <N>"]))
			
		if c == ord('h'):
			call_pipe("head -n " + TextBoxInput(["head -n <N>"]))
			
		if c == ord('o'):
			sort()
			
		if c == ord('w'):
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
			
		if c == ord('/'):
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
