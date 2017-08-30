import glob, os

inputFolder = "/home/lancer/Documents/Workspace/"
movedFolder = "/home/lancer/Documents/Workspace/"

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
			date=str(year)+"-"+str((i+1))+"-"+str((jDay+1-day[i]));
			break
	return date	

os.chdir(inputFolder)
fileList = glob.glob("*.hdf")
fileList.sort()
print fileList
for file in fileList:
	year = int(file[10:14])
	jday = int(file[14:17])
	gday = convertJDayToGDay(year, jday)
	collection = int(file[18:21])
	# print test
	a = movedFolder+file[:-4]
	print a
	print file
	try:
	    os.makedirs(movedFolder+file[:-4])
	    print "Done!"
	except OSError:
	    pass

	# os.rename(movedFolder+file, movedFolder+file[:-4]+"/"+file)