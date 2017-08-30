import sys
import numpy
import ogr, os, osr, glob
from osgeo import gdal
from osgeo.gdalconst import *
import csv
import psycopg2

# from shutil import copyfile

# gdal.UseExceptions()
gdal.AllRegister()
# try:
#     copyfile()

dataSet = "Aerosol_Optical_Depth_Land_Ocean"
mean = "Aerosol_Optical_Depth_Land_Ocean_Mean"
standard_deviation = "Aerosol_Optical_Depth_Land_Ocean_Standard_Deviation"
pixel_counts = "Aerosol_Optical_Depth_Land_Ocean_Pixel_Counts"

path_mod = "/media/lancer/01D124DD7D476BA0/apom/res/SatResampMOD08_D3/2015/"
path_myd = "/media/lancer/01D124DD7D476BA0/apom/res/SatResampMYD08_D3/2015/"
path_prod = "/media/lancer/01D124DD7D476BA0/apom/prod/"

# path_mod = "/media/lancer/01D124DD7D476BA0/demo_database/apom/res/SatResampMOD08_D3/2015/"
# path_myd = "/media/lancer/01D124DD7D476BA0/demo_database/apom/res/SatResampMYD08_D3/2015/"
# path_prod = "/media/lancer/01D124DD7D476BA0/demo_database/apom/prod/"

standard_deviation_blockValue = 0
fillValue = -9999
scale_factor = 0.0010000000474974513
add_offset = 0.0
# ----------------------------------------------------------------------------------
def diagnosticTool(inputArray, blockValue):
	count = 0
	for i in range(0, rows):
		for j in range(0, cols):
			if (inputArray[i][j]!=fillValue and inputArray[i][j]!=blockValue):
				count = count + 1
			# outputArray[i][j] = (inputArray[i][j] * 1) + add_offset
	return count
# ----------------------------------------------------------------------------------
def convertJDayToGDay(jDay):
	year = 2015
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
# -----------------------------------------------------------------------------------------
def convertValue(inputArray):
	outputArray = numpy.zeros((rows,cols), numpy.float32)
	for i in range(0, rows):
		for j in range(0, cols):
			if (inputArray[i][j]!=fillValue):
				outputArray[i][j] = (inputArray[i][j] * scale_factor) + add_offset
			else:
				outputArray[i][j] = fillValue
	return outputArray
# ---------------------------------------Connect Database---------------------------------------
host = 'localhost'
dbname = 'test'
user = 'postgres'
password = 'postgres'
port = 5432
query = "INSERT INTO evaluate (aqstime, filled_mod_mean, filled_myd_mean, filled_mod_sd, filled_myd_sd, filled_saa, filled_mle, filled_wpc, total_pixels) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}','{7}','{8}')"
query1 = "INSERT INTO evaluate (aqstime, filled_mod_mean, filled_myd_mean, filled_mod_sd, filled_myd_sd, filled_saa, filled_mle, filled_wpc, total_pixels) VALUES ('1','1','1','1','1','1','1','1','1')"

try:
	conn = psycopg2.connect("dbname = "+dbname+" user = "+user+" host = "+host+" password = "+password)
	cur = conn.cursor()
	print "Connect Done!"
except:
	print "I am unable to connect to the database"
# cur.execute(query1)
# conn.commit()
# statement = query.format(aqstime, filled_mod_mean, filled_myd_mean, filled_mod_sd, filled_myd_sd, filled_SAA, filled_MLE, filled_WPC, cols*rows)
# print statement
# try:
# 	cur.execute(query1)
# 	conn.commit()
# 	print "Change Done!"
# except:
# 	print "I can't INSERT to my database"
# ---------------------------------Browse file----------------------------------------------------
os.chdir(path_mod)
fileListMOD = glob.glob("*08_D3.A*")
fileListMOD.sort()
# file = fileListMOD[0] 
for file in fileListMOD:
	print file
	jday = int(file[14:17])
	aqstime = convertJDayToGDay(jday)
	print aqstime
	os.chdir(path_myd)
	fileMYD = glob.glob("*"+file[2:17]+"*")
	# print fileMYD
	path_mod_mean = path_mod+file+"/"+file+":"+mean+".tif"
	path_mod_standard_deviation = path_mod+file+"/"+file+":"+standard_deviation+".tif"
	# path_mod_pixel_counts = path_mod+file+"/"+file+":"+pixel_counts+".tif"

	path_myd_mean = path_myd+fileMYD[0]+"/"+fileMYD[0]+":"+mean+".tif"
	path_myd_standard_deviation = path_myd+fileMYD[0]+"/"+fileMYD[0]+":"+standard_deviation+".tif"
	# path_myd_pixel_counts = path_myd+fileMYD[0]+"/"+fileMYD[0]+":"+pixel_counts+".tif"
# ---------------------------------Open file------------------------------------------------
	try:
	    input_mod_mean = gdal.Open(path_mod_mean)
	    input_mod_sd = gdal.Open(path_mod_standard_deviation)
	    # input_mod_pc = gdal.Open(path_mod_pixel_counts)
	    input_myd_mean = gdal.Open(path_myd_mean)
	    input_myd_sd = gdal.Open(path_myd_standard_deviation)
	    # input_myd_pc = gdal.Open(path_myd_pixel_counts)
	    input_SAA = gdal.Open(path_prod+file[9:17]+":"+dataSet+"/"+file[9:17]+":"+dataSet+"_SAA.tif")
	    input_MLE = gdal.Open(path_prod+file[9:17]+":"+dataSet+"/"+file[9:17]+":"+dataSet+"_MLE.tif")
	    input_WPC = gdal.Open(path_prod+file[9:17]+":"+dataSet+"/"+file[9:17]+":"+dataSet+"_WPC.tif")
	    print 'Load Done!'
	except RuntimeError, e:
		print 'Unable to open tif file'
		print e
		sys.exit(1)
	
# ---------------------------------Read data------------------------------------------------
	mod_mean_band = input_mod_mean.GetRasterBand(1)
	myd_mean_band = input_myd_mean.GetRasterBand(1)
	mod_sd_band = input_mod_sd.GetRasterBand(1)
	myd_sd_band = input_myd_sd.GetRasterBand(1)
	# mod_pc_band = input_mod_pc.GetRasterBand(1)
	# myd_pc_band = input_myd_pc.GetRasterBand(1)
	SAA_band = input_SAA.GetRasterBand(1)
	MLE_band = input_MLE.GetRasterBand(1)
	WPC_band = input_WPC.GetRasterBand(1)

	rows = input_mod_mean.RasterYSize
	cols = input_mod_mean.RasterXSize

	mod_mean_Data = mod_mean_band.ReadAsArray(0, 0, cols, rows)
	myd_mean_Data = myd_mean_band.ReadAsArray(0, 0, cols, rows)
	mod_sd_Data = mod_sd_band.ReadAsArray(0, 0, cols, rows)
	myd_sd_Data = myd_sd_band.ReadAsArray(0, 0, cols, rows)
	# mod_pc_Data = mod_pc_band.ReadAsArray(0, 0, cols, rows)
	# myd_pc_Data = myd_pc_band.ReadAsArray(0, 0, cols, rows)
	SAA_Data = SAA_band.ReadAsArray(0, 0, cols, rows)
	MLE_Data = MLE_band.ReadAsArray(0, 0, cols, rows)
	WPC_Data = WPC_band.ReadAsArray(0, 0, cols, rows)

	mod_mean_cropData = numpy.zeros((rows,cols), numpy.float32)
	mod_mean_cropData = convertValue(mod_mean_Data)
	myd_mean_cropData = numpy.zeros((rows,cols), numpy.float32)
	myd_mean_cropData = convertValue(myd_mean_Data)
	mod_sd_cropData = numpy.zeros((rows,cols), numpy.float32)
	mod_sd_cropData = convertValue(mod_sd_Data)
	myd_sd_cropData = numpy.zeros((rows,cols), numpy.float32)
	myd_sd_cropData = convertValue(myd_sd_Data)
	# mod_pc_cropData = numpy.zeros((rows,cols), numpy.float32)
	# mod_pc_cropData = convertValue(mod_pc_Data)
	# myd_pc_cropData = numpy.zeros((rows,cols), numpy.float32)
	# myd_pc_cropData = convertValue(myd_pc_Data)

	# print rows
	# print cols
	filled_mod_mean = diagnosticTool(mod_mean_cropData, fillValue)
	filled_myd_mean = diagnosticTool(myd_mean_cropData, fillValue)
	filled_mod_sd = diagnosticTool(mod_sd_cropData, standard_deviation_blockValue)
	filled_myd_sd = diagnosticTool(myd_sd_cropData, standard_deviation_blockValue)
	# filled_mod_pc = diagnosticTool(mod_pc_cropData, fillValue)
	# filled_myd_pc = diagnosticTool(myd_pc_cropData, fillValue)
	filled_SAA = diagnosticTool(SAA_Data, fillValue)
	filled_MLE = diagnosticTool(MLE_Data, fillValue)
	filled_WPC = diagnosticTool(WPC_Data, fillValue)

	print aqstime
	print filled_mod_mean
	print filled_myd_mean
	print filled_mod_sd
	print filled_myd_sd
	print filled_SAA
	print filled_MLE
	print filled_WPC
	print cols*rows
	# print float(filled_mod_mean/(cols*rows))
	
	statement = query.format(aqstime, filled_mod_mean, filled_myd_mean, filled_mod_sd, filled_myd_sd, filled_SAA, filled_MLE, filled_WPC, cols*rows)
	try:
		cur.execute(statement)
		conn.commit()
		print "Change Done!"
	except:
		print "I can't INSERT to my database"


	# myfile = open(path_prod+file[9:17]+":"+dataSet+"/"+file[9:17]+":"+dataSet+"_EvaluateInfo.csv",'wb')
	# wr = csv.writer(myfile, delimiter = ',', quotechar = ' ', quoting = csv.QUOTE_ALL)
	# wr.writerow(["mod_mean"]+["myd_mean"]+["mod_sd"]+["myd_sd"]+["mod_pc"]+["myd_pc"]+["SAA"]+["MLE"]+["WPC"])
	# wr.writerow([filled_mod_mean]+[filled_myd_mean]+[filled_mod_sd]+[filled_myd_sd]+[filled_SAA]+[filled_MLE]+[filled_WPC])
	# wr.writerow([cols*rows]+[cols*rows]+[cols*rows]+[cols*rows]+[cols*rows]+[cols*rows]+[cols*rows])
	# wr.writerow([float(filled_mod_mean)/(cols*rows)]+[float(filled_myd_mean)/(cols*rows)]+[float(filled_mod_sd)/(cols*rows)]+[float(filled_myd_sd)/(cols*rows)]+[float(filled_SAA)/(cols*rows)]+[float(filled_MLE)/(cols*rows)]+[float(filled_WPC)/(cols*rows)])


	