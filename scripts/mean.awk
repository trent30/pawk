%s
{
	if (l=="") { sum=0; l=0; field=%s}
	for (i=1; i<=NF; i++) {
		data[l++]=$i;
	}
	sum=sum+$field
}

END {
	m = sum/NR;
	d = 0;
	for (l=0; l<NR; l++) {
		for (c=1; c<=NF; c++) {
			printf data[d++] FS;
		}
		if (c!=NF) {
			print m;
		}
	}
}
