%s
{
	for (i=2; i<=NF; i++) {
		printf $i;
		if (i<NF) {
			printf FS;
		}
	}
	printf RS;
}
