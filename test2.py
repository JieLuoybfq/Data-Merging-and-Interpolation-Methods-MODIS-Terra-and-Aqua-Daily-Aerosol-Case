import psycopg2
try:
	conn = psycopg2.connect("dbname = 'apom' user = 'postgres' host = 'localhost' password = 'postgres'")
	print "Connect Done!"
except:
	print "I am unable to connect to the database"

cur = conn.cursor()
try:
	cur.execute("INSERT INTO aerosol_d3 (filename) VALUES ('dinafile.txt')")
	# cur.execute("UPDATE aerosol_d3 SET filename = 'tgfdhsfs' WHERE id = 2")
	conn.commit()
	print "Change done!"

except:
	print "I can't INSERT to my database"

# rows = cur.fetchall()
# print "\nShow me the database:\n"for 
