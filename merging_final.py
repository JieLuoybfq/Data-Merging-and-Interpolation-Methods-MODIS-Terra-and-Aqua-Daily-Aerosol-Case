import sys
import numpy
import ogr, os, osr, glob
from osgeo import gdal
from osgeo.gdalconst import *
# from shutil import copyfile

# gdal.UseExceptions()
gdal.AllRegister()
# try:
#     copyfile()

data_set = "Aerosol_Optical_Depth_Land_Ocean"
mean = "Aerosol_Optical_Depth_Land_Ocean_Mean"
standard_deviation = "Aerosol_Optical_Depth_Land_Ocean_Standard_Deviation"
pixel_counts = "Aerosol_Optical_Depth_Land_Ocean_Pixel_Counts"

path_mod = "/media/lancer/01D124DD7D476BA0/apom/res/SatResampMOD08_D3/2015/"
path_myd = "/media/lancer/01D124DD7D476BA0/apom/res/SatResampMYD08_D3/2015/"
path_prod = "/media/lancer/01D124DD7D476BA0/apom/prod/"

fillValue = -9999
scale_factor = 0.0010000000474974513
add_offset = 0.0

def convertValue(inputArray):
	outputArray = numpy.zeros((rows,cols), numpy.float32)
	for i in range(0, rows):
		for j in range(0, cols):
			if (inputArray[i][j]!=fillValue):
				outputArray[i][j] = (inputArray[i][j] * scale_factor) + add_offset
			else:
				outputArray[i][j] = fillValue
			# outputArray[i][j] = (inputArray[i][j] * 1) + add_offset
	return outputArray
# ---------------------------------Browse file----------------------------------------------
os.chdir(path_mod)
fileListMOD = glob.glob("*08_D3.A*")
fileListMOD.sort()
# file = fileListMOD[0] 
for file in fileListMOD:
	print file
	os.chdir(path_myd)
	fileMYD = glob.glob("*"+file[2:17]+"*")
	print fileMYD
	# print file[10:]
	path_mod_mean = path_mod+file+"/"+file+":"+mean+".tif"
	path_mod_standard_deviation = path_mod+file+"/"+file+":"+standard_deviation+".tif"
	path_mod_pixel_counts = path_mod+file+"/"+file+":"+pixel_counts+".tif"

	path_myd_mean = path_myd+fileMYD[0]+"/"+fileMYD[0]+":"+mean+".tif"
	path_myd_standard_deviation = path_myd+fileMYD[0]+"/"+fileMYD[0]+":"+standard_deviation+".tif"
	path_myd_pixel_counts = path_myd+fileMYD[0]+"/"+fileMYD[0]+":"+pixel_counts+".tif"
# ---------------------------------Open file------------------------------------------------
	try:
	    input_mod_mean = gdal.Open(path_mod_mean)
	    input_mod_sd = gdal.Open(path_mod_standard_deviation)
	    input_mod_pc = gdal.Open(path_mod_pixel_counts)
	    input_myd_mean = gdal.Open(path_myd_mean)
	    input_myd_sd = gdal.Open(path_myd_standard_deviation)
	    input_myd_pc = gdal.Open(path_myd_pixel_counts)
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
	mod_pc_band = input_mod_pc.GetRasterBand(1)
	myd_pc_band = input_myd_pc.GetRasterBand(1)

	rows = input_mod_mean.RasterYSize
	cols = input_mod_mean.RasterXSize

	mod_mean_Data = mod_mean_band.ReadAsArray(0, 0, cols, rows)
	myd_mean_Data = myd_mean_band.ReadAsArray(0, 0, cols, rows)
	mod_sd_Data = mod_sd_band.ReadAsArray(0, 0, cols, rows)
	myd_sd_Data = myd_sd_band.ReadAsArray(0, 0, cols, rows)
	mod_pc_Data = mod_pc_band.ReadAsArray(0, 0, cols, rows)
	myd_pc_Data = myd_pc_band.ReadAsArray(0, 0, cols, rows)

	mod_mean_cropData = numpy.zeros((rows,cols), numpy.float32)
	mod_mean_cropData = convertValue(mod_mean_Data)
	myd_mean_cropData = numpy.zeros((rows,cols), numpy.float32)
	myd_mean_cropData = convertValue(myd_mean_Data)
	mod_sd_cropData = numpy.zeros((rows,cols), numpy.float32)
	mod_sd_cropData = convertValue(mod_sd_Data)
	myd_sd_cropData = numpy.zeros((rows,cols), numpy.float32)
	myd_sd_cropData = convertValue(myd_sd_Data)
	mod_pc_cropData = numpy.zeros((rows,cols), numpy.float32)
	mod_pc_cropData = convertValue(mod_pc_Data)
	myd_pc_cropData = numpy.zeros((rows,cols), numpy.float32)
	myd_pc_cropData = convertValue(myd_pc_Data)
	

# ----------------------------Create output image----------------------------------------------
	try:
		os.makedirs(path_prod+file[9:17]+":"+data_set)
		print "Done!"
	except OSError:
		pass

	driver = input_mod_mean.GetDriver()

	# Print driver
	outRaster_SAA = driver.Create(path_prod+file[9:17]+":"+data_set+"/"+file[9:17]+":"+data_set+"_SAA.tif", cols, rows, 1, GDT_Float32)
	if outRaster_SAA is None:
	    print 'Could not create SAA tif file'
	    sys.exit(1)
	outBand_SAA = outRaster_SAA.GetRasterBand(1)
	prod_value_SAA = numpy.zeros((rows,cols), numpy.float32)

	outRaster_MLE = driver.Create(path_prod+file[9:17]+":"+data_set+"/"+file[9:17]+":"+data_set+"_MLE.tif", cols, rows, 1, GDT_Float32)
	if outRaster_MLE is None:
	    print 'Could not create MLE tif file'
	    sys.exit(1)
	outBand_MLE = outRaster_MLE.GetRasterBand(1)
	prod_value_MLE = numpy.zeros((rows,cols), numpy.float32)

	outRaster_WPC = driver.Create(path_prod+file[9:17]+":"+data_set+"/"+file[9:17]+":"+data_set+"_WPC.tif", cols, rows, 1, GDT_Float32)
	if outRaster_WPC is None:
	    print 'Could not create WPC tif file'
	    sys.exit(1)
	outBand_WPC = outRaster_WPC.GetRasterBand(1)
	prod_value_WPC = numpy.zeros((rows,cols), numpy.float32)

# -------------------------------SAA method----------------------------------------------------------
	for i in range(0, rows):
		for j in range(0, cols):
			if (mod_mean_cropData[i][j]!=fillValue and myd_mean_cropData[i][j]!=fillValue):
				prod_value_SAA[i][j] = (mod_mean_cropData[i][j]+myd_mean_cropData[i][j])/2
			elif (mod_mean_cropData[i][j]==fillValue and myd_mean_cropData[i][j]!=fillValue):
				prod_value_SAA[i][j] = myd_mean_cropData[i][j]
			elif (mod_mean_cropData[i][j]!=fillValue and myd_mean_cropData[i][j]==fillValue):
				prod_value_SAA[i][j] = mod_mean_cropData[i][j]
			else:
				prod_value_SAA[i][j] = fillValue

# -------------------------------MLE method-----------------------------------------------------------
	for i in range(0, rows):
		for j in range(0, cols): 
			if (mod_mean_cropData[i][j]!=fillValue and mod_sd_cropData[i][j]!=0 and myd_mean_cropData[i][j]!=fillValue and myd_sd_cropData[i][j]!=0):
				prod_value_MLE[i][j] = float(mod_mean_cropData[i][j]*pow(myd_sd_cropData[i][j],2) + myd_mean_cropData[i][j]*pow(mod_sd_cropData[i][j],2))/(pow(myd_sd_cropData[i][j],2) + pow(mod_sd_cropData[i][j],2)) 
			elif (mod_mean_cropData[i][j]!=fillValue and mod_sd_cropData[i][j]==0 and myd_mean_cropData[i][j]!=fillValue and myd_sd_cropData[i][j]==0):
				prod_value_MLE[i][j] = fillValue
			elif ((mod_mean_cropData[i][j]==fillValue or mod_sd_cropData[i][j]==0) and myd_mean_cropData[i][j]!=fillValue and myd_sd_cropData[i][j]!=0):
				prod_value_MLE[i][j] = myd_mean_cropData[i][j] 
			elif (mod_mean_cropData[i][j]!=fillValue and mod_sd_cropData[i][j]!=0 and (myd_mean_cropData[i][j]==fillValue or myd_sd_cropData[i][j]==0)):
				prod_value_MLE[i][j] = mod_mean_cropData[i][j] 
			else:	
				prod_value_MLE[i][j] = fillValue

# ------------------------------Averaging With WPC----------------------------------------------------
	for i in range(0, rows):
		for j in range(0, cols):
			if (mod_mean_cropData[i][j]!=fillValue and myd_mean_cropData[i][j]!=fillValue):
				prod_value_WPC[i][j] = float(mod_mean_cropData[i][j]*mod_pc_cropData[i][j]+myd_mean_cropData[i][j]*myd_pc_cropData[i][j])/(mod_pc_cropData[i][j]+myd_pc_cropData[i][j])
			elif (mod_mean_cropData[i][j]!=fillValue and myd_mean_cropData[i][j]==fillValue):
				prod_value_WPC[i][j] = mod_mean_cropData[i][j] 
			elif (mod_mean_cropData[i][j]==fillValue and myd_mean_cropData[i][j]!=fillValue):
				prod_value_WPC[i][j] = myd_mean_cropData[i][j] 
			else:
				prod_value_WPC[i][j] = fillValue


# ---------------------------------Write data--------------------------------------------------------
	outBand_SAA.WriteArray(prod_value_SAA, 0, 0)
	# Flush data to disk, set the NoData value and calculates stats
	outBand_SAA.FlushCache()
	outBand_SAA.SetNoDataValue(fillValue)
	# Georeference the image and set the projection
	outRaster_SAA.SetGeoTransform(input_mod_mean.GetGeoTransform())
	outRaster_SAA.SetProjection(input_mod_mean.GetProjection())
	del prod_value_SAA

	outBand_MLE.WriteArray(prod_value_MLE, 0, 0)
	# Flush data to disk, set the NoData value and calculates stats
	outBand_MLE.FlushCache()
	outBand_MLE.SetNoDataValue(fillValue)
	# Georeference the image and set the projection
	outRaster_MLE.SetGeoTransform(input_mod_mean.GetGeoTransform())
	outRaster_MLE.SetProjection(input_mod_mean.GetProjection())
	del prod_value_MLE

	outBand_WPC.WriteArray(prod_value_WPC, 0, 0)
	# Flush data to disk, set the NoData value and calculates stats
	outBand_WPC.FlushCache()
	outBand_WPC.SetNoDataValue(fillValue)
	# Georeference the image and set the projection
	outRaster_WPC.SetGeoTransform(input_mod_mean.GetGeoTransform())
	outRaster_WPC.SetProjection(input_mod_mean.GetProjection())
	del prod_value_WPC

	print "Done!"
