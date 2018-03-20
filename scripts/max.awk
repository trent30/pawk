%s
{
	if (l=="") { 
		sum=0;
		l=0;
		f=%s;
		max=$f;
	}
	for (i=1; i<=NF; i++) {
		data[l++]=$i;
	}
	if ( $f %s max ) {
		max = $f;
	}
}

END {
	d = 0;
	for (l=0; l<NR; l++) {
		for (c=1; c<=NF; c++) {
			printf data[d++] FS;
		}
		if (c!=NF) {
			print max;
		}
	}
}
