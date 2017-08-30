import csv
with open('test.csv', 'a') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
	for row in spamreader:
		print ', '.join(row)
		