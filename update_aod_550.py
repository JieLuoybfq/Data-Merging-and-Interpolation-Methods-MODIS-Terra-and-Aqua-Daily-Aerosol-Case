import os, glob
import psycopg2

# host = 'localhost'
# dbname = 'apom'
# user = 'postgres'
# password = 'postgres'
# port = '5432'

host = '112.137.129.222'
dbname = 'postgres'
user = 'sinhvien'
password = 'sinhvien'
# port = '1188'

try:
	conn = psycopg2.connect("dbname = "+dbname+" user = "+user+" host = "+host+" password = "+password)
	# conn = psycopg2.connect("dbname = 'apom' user = 'postgres' host = 'localhost' password = 'postgres'")
	print "Connect Done!"
except:
	print "I am unable to connect to the database"
