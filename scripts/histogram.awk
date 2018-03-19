%s
{
	if (length($1)>max) {
		max=length($1);
	}
	labels[l]=$1;
	values[l]=$2;
	l++;
}

END {
	l = 0;
	d = 0;
	for (l=0; l<NR; l++) {
		star="";
		p="";
		for (j=0; j < (max - length(labels[l])); j++) { 
			p = p" ";
		}
		for (k=0; k < values[l]; k++) { 
			star=star"*";
		}
		print p labels[l], FS, star
	}
}
