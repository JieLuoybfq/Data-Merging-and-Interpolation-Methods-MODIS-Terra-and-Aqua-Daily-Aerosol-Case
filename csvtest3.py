import csv

mylist = [1, 2, 3, 4, 5, 7, 8, 9, 'aasdasdsadsdsad', 'adfsdfd']
myfile = open("haha.csv", 'wb')
wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
wr.writerow(mylist)
print "Done!"