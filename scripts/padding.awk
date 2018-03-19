%s
{
	for (i=1; i<=NF; i++) {
		if (length($i)>max[i]) {
			max[i]=length($i);
		}
		data[l]=$i;
		l++;
	}
}
END {
	d = 0;
	for (l=0; l<NR; l++) {
		for (c=1; c<=NF; c++) {
			p="";
			for (j=0; j < (max[c]-length(data[d])); j++) {
				p = p" ";
			}
			if (right == 1) {
				print p, data[d];
			} else {
				print data[d], p;
			}
			if (c!=NF) {
				print FS;
			}
			d++;
		}
		print "\n";
	}
}
