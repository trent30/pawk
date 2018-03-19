====== pawk ======


===== Description =====

Pawk is a WYSIWYG tool to generate bash scripts very quickly and without pain.
Usually, one can do all that they want with a few commands and pipes, but often waste a lot of time figuring out how to arrange commands, and what the appropriate parameters are for each of them. Especially when not familiar with awk.

For instance, if you want to compute the sum of field 10 in access.log, just open the file with pawk and press 'a', 's', 'm', '10' and <ENTER>. That's it. You have the result and the script is automatically generated: 
« cat access.log | awk '{ print $10 }' | sed s/^$/0/g | awk 'BEGIN{RS="\n";ORS="+"}{if (RT=="") printf "%s",$0; else print}' | sed "s/+$/\n/g" | bc »

Now you can impress your friends and colleagues with ugly pipes.

===== Usage =====

python pawk.py [FILE...]


===== Shortcuts =====

'''
 Commands:
	a : advanced commands
	c : cut -c<Start>-<End>
	g : egrep
	h : head -n <N>
	o : sort
	s : substitute
	t : tail -n <N>
	T : table
	i : insert a custom command
'''
	

'''
 awk:
	f : select several fields
	l : grep one line by its number
	w : where (select a field with a condition)
	F : change field separator
	L : change line separator
'''
	

'''
 Misc:
	e : edit script
	n : show/hide line numbers 
	r : redo
	u : undo
	/ : search
	? : print this help message
	q : quit
'''


===== Examples =====

==== Select fields ====

python pawk.py /etc/passwd

{{{code: lang="html" linenumbers="False"
root:x:0:0:root:/root:/bin/bash 
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin 
bin:x:2:2:bin:/bin:/usr/sbin/nologin 
sys:x:3:3:sys:/dev:/usr/sbin/nologin
}}}


Press 'f' (like field):
{{{code: lang="html" linenumbers="False"
                            1                             |                     2                     | 
-------------------------------------------------------------------------------------------------------
root:x:0:0:root:/root:/bin/bash                           |                    
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin           |  
bin:x:2:2:bin:/bin:/usr/sbin/nologin                      |  
sys:x:3:3:sys:/dev:/usr/sbin/nologin                      |  

Column : 1 | Actuals fields are : [] | a : append | r : remove last one | m : manually | F : field separator | q : quit
}}}


As we can see, all the data is in the first field. Indeed, the field separator is <space> by default. To change it to colon (:), just press 'F' (like Field Separator).

{{{code: lang="html" linenumbers="False"
        1        |2|  3  |  4  |                5                 |          6          |        7        | 
-----------------------------------------------------------------------------------------------------------
root             |x|0    |0    |root                              |/root                |/bin/bash        |
daemon           |x|1    |1    |daemon                            |/usr/sbin            |/usr/sbin/nologin| 
bin              |x|2    |2    |bin                               |/bin                 |/usr/sbin/nologin| 
sys              |x|3    |3    |sys                               |/dev                 |/usr/sbin/nologin|

Column : 1 | Actuals fields are : [] | a : append | r : remove last one | m : manually | F : field separator | q : quit
}}}


Now we obtain correct headers numbers, and we can append all the fields we want with the left and right arrows.
We can append manually (just press 'm') a huge number of fields even more quickly with range '-' and the wildcard character '*':
{{{code: lang="html" linenumbers="False"
┌───────────────────────────────────────────────────┐
│                                                   │
│ Enter the list of fields                          │
│                                                   │
│ Examples :                                        │
│ 2 3       : only the fields 2 and 3               │
│ 2-6 -3    : the fields 2 to 6 except the 3th      │
│ * -4 -7   : all fields except the 4th and the 7th │
└───────────────────────────────────────────────────┘
}}}


With '* -2', the status bar indicates the fields 1, 3, 4, 5, 6 and 7 are selected:
{{{code: lang="html" linenumbers="False"

Column : 1 | Actuals fields are : [1, 3, 4, 5, 6, 7] | a : append | r : remove last one | m : manually | F : field separator | q : quit
}}}


Ok, we have all the fields we want, now we can quit with 'q' to watch the result:
{{{code: lang="html" linenumbers="False"
root:0:0:root:/root:/bin/bash 
daemon:1:1:daemon:/usr/sbin:/usr/sbin/nologin 
bin:2:2:bin:/bin:/usr/sbin/nologin 
sys:3:3:sys:/dev:/usr/sbin/nologin 
sync:4:65534:sync:/bin:/bin/sync
}}}


We can continue to run commands on the last result and so on, like a pipe, but we can watch each intermediate result, so we don't waste time trying and retrying, and modifying a long command line to fix a little bug ( « oh 'cut -c20-27' was wrong so 'cut -c20-28' should work... Let's try again and rerun all this shitstorm » ).

The script to obtain the last result can be viewed with 'e' (like edit):
{{{code: lang="html" linenumbers="False"
Command list:  

1 : cat /etc/passwd
2 : awk 'BEGIN{FS=":";}{ print $1":"$3":"$4":"$5":"$6":"$7 }'
3 : head -n 1

OneLiner:

awk 'BEGIN{FS=":";}{ print $1":"$3":"$4":"$5":"$6":"$7 }' /etc/passwd | head -n 1



q : quit | u : undo | r : redo | s : save script
}}}


Each command can be undone or redone to quickly retry if you miss something. The data is cached so it should be instantaneous.
When you save the script, the shebang is automatically added and the file is automatically executable (because we always forget to 'chmod +x').

When you quit the program, a popup asks what we want to do.
{{{code: lang="html" linenumbers="False"
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
}}}

So we shouldn't lose work.


==== Table ====

With table command 'T' we can choose a header separator and the right-aligned fields, the other one will be left-aligned.
{{{code: lang="html" linenumbers="False"
root  |x|0|    0|root  |/root          |/bin/bash         
------+-+-+-----+------+---------------+-----------------
daemon|x|1|    1|daemon|/usr/sbin      |/usr/sbin/nologin
bin   |x|2|    2|bin   |/bin           |/usr/sbin/nologin
sys   |x|3|    3|sys   |/dev           |/usr/sbin/nologin
sync  |x|4|65534|sync  |/bin           |/bin/sync        
games |x|5|   60|games |/usr/games     |/usr/sbin/nologin
man   |x|6|   12|man   |/var/cache/man |/usr/sbin/nologin
lp    |x|7|    7|lp    |/var/spool/lpd |/usr/sbin/nologin
mail  |x|8|    8|mail  |/var/mail      |/usr/sbin/nologin
news  |x|9|    9|news  |/var/spool/news|/usr/sbin/nologin
}}}

Here, only the 4th field is right-aligned and the header is on the first line (even if it doesn't make any sense in the context).
Note: considering field separators are replaced by "|", you should use this command only at the end, just for the final rendering.

==== Sort ====

With 'o' we can sort by fields. After the field selection, we can also add parameters to the sort command. A brief reminder is displayed, because we are always mistaken between '-r' and '-R'.
{{{code: lang="html" linenumbers="False"
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
}}}



==== Select fields with condition ====

python pawk.py /tmp/birth

{{{code: lang="html" linenumbers="False"
1 
2 Bart 
3 23/02
4 
5 Homer
6 18/06
}}}


If we want only the line with name, we can use the « where » command ('w'):
{{{code: lang="html" linenumbers="False"
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

}}}

(n+1)%3==0

{{{code: lang="html" linenumbers="False"
1 Bart   
2 Homer
}}}

Now we only have every third line.


==== Substitute ====

The 's' command uses awk to substitute, to use a regex we can call another command with 'i' (insert a custom command) on:
{{{code: lang="html" linenumbers="False"
libc6
libcairo2
libgcc1
}}}


sed s/^/_/g
{{{code: lang="html" linenumbers="False"
_libc6
_libcairo2
_libgcc1
}}}


sed s/$/_/g
{{{code: lang="html" linenumbers="False"
_libc6_
_libcairo2_
_libgcc1_
}}}


tr '\n' ';'
{{{code: lang="html" linenumbers="False"
_libc6_;_libcairo2_;_libgcc1_;
}}}



==== Advanced commands ====

The 'a' shortcut displays the advanced commands menu:

{{{code: lang="html" linenumbers="False"
ADVANCED COMMANDS 

a : append a field
i : insert the line number on the first field
c : count occurrences on selected field
s : sum values on selected field
p : padding
P : auto padding all fields
t : transpose
m : compute the mean
h : histogram
}}}


=== Append a field ===
{{{code: lang="html" linenumbers="False"
12 2
20 4
50 6
}}}


Like a spreadsheet, we can do arithmetic operations on the new field: $1+$2
{{{code: lang="html" linenumbers="False"
12 2 14
20 4 24
50 6 56
}}}


Or concatenate text: " | "$1" apples and "$2" bananas"
{{{code: lang="html" linenumbers="False"
12 2 14  | 12 apples and 2 bananas
20 4 24  | 20 apples and 4 bananas
50 6 56	 | 50 apples and 6 bananas
}}}


=== Transpose ===
{{{code: lang="html" linenumbers="False"
12 20 50
2 4 6
14 24 56
}}}


=== Padding ===
We can align on the left or on the right with a specific width. Here, $1 on the right with width=6, and $5 on the left with width=10:
{{{code: lang="html" linenumbers="False"
  root:x:0:0:root      :/root:/bin/bash                                  
daemon:x:1:1:daemon    :/usr/sbin:/usr/sbin/nologin
   bin:x:2:2:bin       :/bin:/usr/sbin/nologin
   sys:x:3:3:sys       :/dev:/usr/sbin/nologin
}}}


=== Auto padding ===
With auto padding 'P', no need to figure out the maximum size record for each field, all of them are padded with the minimum size automatically:
{{{code: lang="html" linenumbers="False"
  root:x:0:0:  root:    /root:        /bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
   bin:x:2:2:   bin:     /bin:/usr/sbin/nologin
   sys:x:3:3:   sys:     /dev:/usr/sbin/nologin
}}}


=== Count occurrences ===
It's like a "SELECT field, count(*) FROM file GROUP BY field;"

For instance, if we apply « count command » 'c' with field 7 on /etc/password:
{{{code: lang="html" linenumbers="False"
/bin/bash:5
/bin/false:34
/bin/sh:2
/bin/sync:1
/usr/sbin/nologin:18
}}}


=== Histogram ===

We can also display an histogram 'h'. Field one must contain the labels, and field two the values:
{{{code: lang="html" linenumbers="False"
        /bin/bash : *****
       /bin/false : **********************************
          /bin/sh : **
        /bin/sync : *
/usr/sbin/nologin : ******************
}}}


=== Sum ===
{{{code: lang="html" linenumbers="True"
10
10

10
10
}}}

Just compute the sum of a field, empty lines are automatically replaced by 0.
{{{code: lang="html" linenumbers="False"
40
}}}


=== Mean ===
{{{code: lang="html" linenumbers="False"
8.0000000000
}}}

Why it is not 10? Because line 3 is empty.
