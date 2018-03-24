%s
{
	data[$f]++;
}

END {
	for (i in data) {
		print i FS data[i];
	}
}
