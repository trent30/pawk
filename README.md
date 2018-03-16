# pawk
Description
-----------

Pawk is a WYSIWYG tool to generate bash script very quickly and without pain.
Usually, we can do all what we want with few commands and pipes, but often we waste a lot of time to figure out how to arrange it and what is the good option for each of them. Especially if you are not familiar with awk.

For instance, if you want to compute the sum of field 10 in access.log, just open the file with pawk and press 'a', 's', 'm', '10' and <ENTER>. That's it. You have the result and the script is automatically generate :
« cat access.log | awk '{ print $10 }' | sed s/^$/0/g | awk 'BEGIN{RS="\n";ORS="+"}{if (RT=="") printf "%s",$0; else print}' | sed "s/+$/\n/g" | bc »

Now you can impress your friends and your coworkers with ugly pipes.

Usage
-----

python pawk.py [FILE...]


Shortcuts
---------

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
	

	 Misc :
		e : edit script
		n : show/hide line numbers 
		r : redo
		u : undo
		/ : search
		? : print this help message
		q : quit


Examples
--------

### Select fields

python pawk.py /etc/passwd

	root:x:0:0:root:/root:/bin/bash 
	daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin 
	bin:x:2:2:bin:/bin:/usr/sbin/nologin 
	sys:x:3:3:sys:/dev:/usr/sbin/nologin


Press 'f' (like field) :
	                            1                             |                     2                     | 
	-------------------------------------------------------------------------------------------------------
	root:x:0:0:root:/root:/bin/bash                           |                    
	daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin           |  
	bin:x:2:2:bin:/bin:/usr/sbin/nologin                      |  
	sys:x:3:3:sys:/dev:/usr/sbin/nologin                      |  
	
	Column : 1 | Actuals fields are : [] | a : append | r : remove last one | m : manually | F : field separator | q : quit


As we can see, all the data are in the first field. Indeed, the field separator is <space> by default. To change it to colon (:), just press 'F' (like Field Separator).

	        1        |2|  3  |  4  |                5                 |          6          |        7        | 
	-----------------------------------------------------------------------------------------------------------
	root             |x|0    |0    |root                              |/root                |/bin/bash        |
	daemon           |x|1    |1    |daemon                            |/usr/sbin            |/usr/sbin/nologin| 
	bin              |x|2    |2    |bin                               |/bin                 |/usr/sbin/nologin| 
	sys              |x|3    |3    |sys                               |/dev                 |/usr/sbin/nologin|
	
	Column : 1 | Actuals fields are : [] | a : append | r : remove last one | m : manually | F : field separator | q : quit


Now we obtain the good headers numbers, and we can append all the fields we want with the left or right arrows.
We can append manually (just press 'm') a huge number of fields even more quickly with range '-' and wildcard character '*' :
	┌───────────────────────────────────────────────────┐
	│                                                   │
	│ Enter the list of fields                          │
	│                                                   │
	│ Examples :                                        │
	│ 2 3       : only the fields 2 and 3               │
	│ 2-6 -3    : the fields 2 to 6 except the 3th      │
	│ * -4 -7   : all fields except the 4th and the 7th │
	└───────────────────────────────────────────────────┘


With '* -2', the status bar indicate the fields 1, 3, 4, 5, 6 and 7 are selected:
	
	Column : 1 | Actuals fields are : [1, 3, 4, 5, 6, 7] | a : append | r : remove last one | m : manually | F : field separator | q : quit


Ok, we have all the fields we want, now we can quit with 'q' to watch the result :
	root:0:0:root:/root:/bin/bash 
	daemon:1:1:daemon:/usr/sbin:/usr/sbin/nologin 
	bin:2:2:bin:/bin:/usr/sbin/nologin 
	sys:3:3:sys:/dev:/usr/sbin/nologin 
	sync:4:65534:sync:/bin:/bin/sync


We can continue to run command on the last result and so on, like a pipe but we can watch each intermediate result, so we don't waste time to try and retry and modify the long command line to fix a little bug ( « oh 'cut -c20-27' was wrong so 'cut -c20-28' should work... Let's try again and rerun all this shitstorm » ).

The script to obtain the last result can be viewed with 'e' (like edit):
	Commands list :  
	
	1 : cat /etc/passwd
	2 : awk 'BEGIN{FS=":";}{ print $1":"$3":"$4":"$5":"$6":"$7 }'
	3 : head -n 1
	
	OneLiner :
	
	awk 'BEGIN{FS=":";}{ print $1":"$3":"$4":"$5":"$6":"$7 }' /etc/passwd | head -n 1
	
	
	
	q : quit | u : undo | r : redo | s : save script


Each commands can be undo or redo to quickly retry if you miss something. The data are in cache so it should be instantaneous.
When you save the script, the shebang is automatically added and the file is automatically executable (because we always forget to 'chmod +x').

When you quit the program, a popup ask what we want to do.
	┌───────────────────────────────────┐                                                                              
	│                                   │                                                                              
	│              Quit ?               │                                                                              
	│                                   │                                                                              
	│ a : abort                         │                                                                              
	│ d : save data in file             │                                                                              
	│ s : save script in file           │                                                                              
	│ p : print data to standard output │                                                                              
	│ q : quit                          │                                                                               
	│                                   │                                                                              
	└───────────────────────────────────┘

So we shouldn't lost work.

### Sort

With 'o' we can sort by fields. After the fields selection, we can also add parameters to the sort command. A brief reminder is display, because we are always mistaken between '-r' and '-R'.
	┌───────────────────────────────────┐                                                                              
	│                                   │                                                                              
	│ sort options :                    │                                                                              
	│                                   │                                                                              
	│ -d, --dictionary-order            │                                                                              
	│ -f, --ignore-case                 │                                                                              
	│ -M, --month-sort                  │                                                                              
	│ -h, --human-numeric-sort          │                                                                              
	│ -n, --numeric-sort                │  
	│ -R, --random-sort                 │   
	│ -r, --reverse                     │                                                                           
	│                                   │                                                                              
	└───────────────────────────────────┘


### Select fields with condition

python pawk.py /tmp/birth

	1 
	2 Bart 
	3 23/02
	4 
	5 Homer
	6 18/06


If we want only the line with name, we can use the « where » command ('w') :
	 ┌────────────────────────────────────────────────────────────────┐
	 │                                                                │
	 │                       "where" condition.                       │
	 │                                                                │
	 │ Example :                                                      │
	 │                                                                │
	 │ $1 ~ /foo/      : select lines where first field contain "foo" │
	 │ $7 !~ /^$/      : select lines where 7th field is not empty    │
	 │ (n>10 && n<15)  : select only the lines 11 to 14.              │
	 │                                                                │
	 └────────────────────────────────────────────────────────────────┘
	

(n+1)%3==0

	1 Bart   
	2 Homer

Now we have only one line on three.


### Substitute

The 's' command use awk to substitute, to use regex we can call another command with 'i' (insert a custom command) on :
	libc6
	libcairo2
	libgcc1


sed s/^/_/g
	_libc6
	_libcairo2
	_libgcc1


sed s/$/_/g
	_libc6_
	_libcairo2_
	_libgcc1_


tr '\n' ';'
	_libc6_;_libcairo2_;_libgcc1_;


### Advanced commands

The 'a' shortcut display the advanced commands menu :

	ADVANCED COMMANDS 
	
	a : append a field
	i : insert the line number on the first field
	c : count occurrences on selected field
	s : sum values on selected field
	t : transpose
	m : compute the mean
	h : histogram


#### Append a field
	12 2
	20 4
	50 6

Like a spreadsheet, we can do some operation on the new field : $1+$2
	12 2 14
	20 4 24
	50 6 56


#### Transpose
	12 20 50
	2 4 6
	14 24 56


#### Count occurrences
It's like a "SELECT field, count(*) FROM file GROUP BY field;"

For instance, if we apply « count command » 'c' with field 7 on /etc/password :
	/bin/bash:5
	/bin/false:34
	/bin/sh:2
	/bin/sync:1
	/usr/sbin/nologin:18


#### Histogram

We can also display a histogram 'h' of field 2 :
	*****
	**********************************
	**
	*
	******************


The histogram can be scale to a boundary. In this case all the values are increase or decrease by the same ratio, thus the maximum value will touch the boundary.
Here the same histogram with a boundary at 80:
	************
	*********************************************************************************
	*****
	***
	*******************************************


#### Sum
	10
	10
	
	10
	10

Just compute the sum on a field, empty line are automatically replaced by 0.
	40


#### Mean
	8.0000000000

Why it is not 10 ? Because the line 3 is empty.

