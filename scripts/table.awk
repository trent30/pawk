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
		if ( l == header || l == footer ) {
			sep="";
			for (ch=1; ch<=NF; ch++) {
				for (jh=0; jh < max[ch] ; jh++) { 
					sep=sep"-";
				}
				sep=sep"+";
			}
			print sep"\n";
		}
		for (c=1; c<=NF; c++) {
			p=""; 
			for (j=0; j < (max[c] - length(data[d])); j++) { 
				p = p" ";
			}
			if ( r[c] == 1 ) {
				print p data[d];
			} else {
				print data[d] p;
			}
			if (c!=NF) {
				print "|";
			}
			d++;
		}
		print "\n";
	}
}
