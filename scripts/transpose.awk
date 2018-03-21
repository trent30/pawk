%s
{
	if (l=="") {
		l=0;
	}
	for (i=1; i<=NF; i++) {
		data[l++]=$i;
	}
}

END {
	d = 0;
	for (c=0; c<NF; c++) {
		i = c;
		for (l=0; l<NR; l++) {
			printf data[i];
			if (l<NR-1) {
				printf FS;
			}
			i+=NF;
		}
		if (c!=NF) {
			printf RS;
		}
	}
}
