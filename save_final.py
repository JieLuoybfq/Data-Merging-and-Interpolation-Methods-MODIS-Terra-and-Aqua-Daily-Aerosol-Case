import glob, os
import psycopg2

# inputFolder = "/media/lancer/TOSHIBA/apom/org/SatOrgMOD08"
# outputFolder = "/media/lancer/TOSHIBA/MODIS Terra Cut/"
# movedFolder = "/home/lancer/Documents/Workspace/"
inputFolder = "/home/lancer/Documents/Workspace/"
outputFolder = "/home/lancer/Documents/Workspace/Res/"

# inputFolder = "/media/lancer/TOSHIBA/apom/org/SatOrgMYD08_D3/2015/"
movedFolder = "/media/lancer/TOSHIBA/apom/org/SatOrgMYD08_D3/2015/"
# outputFolder = "/media/lancer/TOSHIBA/apom/res/SatResampMYD08_D3/2015/"
path = "/apom/org/SatOrgMYD08_D3/2015/"

mean = "Aerosol_Optical_Depth_Land_Ocean_Mean"
standard_deviation = "Aerosol_Optical_Depth_Land_Ocean_Standard_Deviation"
pixel_counts = "Aerosol_Optical_Depth_Land_Ocean_Pixel_Counts"

host = 'localhost'
dbname = 'apom'
user = 'postgres'
password = 'postgres'
port = '5432'
query = "INSERT INTO orgmyd08_d3 (sourceid, aqstime, filename, path, id, collection) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}')"
	

def convertJDayToGDay(year, jDay):
	date="1-1" #date and month
	day=()
	#if is_leap_year(year):
	if year % 4 == 0 and year %100 != 0 or year % 400 == 0:
		day=(1, 32, 61, 92, 122, 153, 183, 214, 245, 275, 306, 336)
	else:
		day=(1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)
	for i in range(11,-1,-1):
		if (jDay-day[i]>=0):
			date=str(year)+"-"+str((i+1))+"-"+str((jDay+1-day[i]))
			break
	return date	

try:
	conn = psycopg2.connect("dbname = "+dbname+" user = "+user+" host = "+host+" password = "+password)
	# conn = psycopg2.connect("dbname = 'apom' user = 'postgres' host = 'localhost' password = 'postgres'")
	cur = conn.cursor()
	print "Connect Done!"
except:
	print "I am unable to connect to the database"



count = 0
sourceCount = 0

os.chdir(inputFolder)
fileList = glob.glob("*.hdf")
fileList.sort()
for file in fileList:
	year = int(file[10:14])
	jday = int(file[14:17])
	gday = convertJDayToGDay(year, jday)
	collection = int(file[18:21])
	
	# print file
	# print inputFolder
	# print count

	# ------------------------------------Insert to Database---------------------------------------------
	# statement = query.format(sourceCount, gday, file, path+file[:-4], count, collection)
	# print statement
	# try:
	# 	cur.execute(statement)
	# 	conn.commit()
	# 	print "Change Done!"
	# 	count = count + 1
	# 	sourceCount = sourceCount + 1
	# except:
	# 	print "I can't INSERT to my database"
	
	# ------------------------------------Cut and Convert------------------------------------------------
	try:
		os.makedirs(outputFolder+file[:-4])
		print "Done!"
	except OSError:
		pass

	regrid_command =  "gdalwarp -te 100.1 6.4 111.8 25.6 -srcnodata -9999 -dstnodata -9999 -overwrite -multi HDF4_EOS:EOS_GRID:{0}:mod08:{1} {3}{2}/{2}:{1}.tif"
	print regrid_command
	os.system(regrid_command.format(file, mean, file[:-4], outputFolder))
	os.system(regrid_command.format(file, standard_deviation, file[:-4], outputFolder))
	os.system(regrid_command.format(file, pixel_counts, file[:-4], outputFolder))

	# ------------------------------------Move------------------------------------------------------------
	# try:
	# 	os.makedirs(movedFolder+file[:-4])
	# 	print "Done!"
	# except OSError:
	# 	pass

	# os.rename(movedFolder+file, movedFolder+file[:-4]+"/"+file)

