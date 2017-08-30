import sys
import numpy
import ogr, os, osr
from osgeo import gdal
from osgeo.gdalconst import *
# from shutil import copyfile

# gdal.UseExceptions()
gdal.AllRegister()
# try:
#     copyfile()

path_mod_mean = "/home/lancer/Documents/Workspace/apom/res/SatResampMOD08_D3/2015/MOD08_D3.A2015001.006.2015035160108/MOD08_D3.A2015001.006.2015035160108:Aerosol_Optical_Depth_Land_Ocean_Mean.tif"
path_mod_standard_deviation = "/home/lancer/Documents/Workspace/apom/res/SatResampMOD08_D3/2015/MOD08_D3.A2015001.006.2015035160108/MOD08_D3.A2015001.006.2015035160108:Aerosol_Optical_Depth_Land_Ocean_Standard_Deviation.tif"
path_mod_pixel_counts = "/home/lancer/Documents/Workspace/apom/res/SatResampMOD08_D3/2015/MOD08_D3.A2015001.006.2015035160108/MOD08_D3.A2015001.006.2015035160108:Aerosol_Optical_Depth_Land_Ocean_Pixel_Counts.tif"

path_myd_mean = "/home/lancer/Documents/Workspace/apom/res/SatResampMYD08_D3/2015/MYD08_D3.A2015001.006.2015007155956/MYD08_D3.A2015001.006.2015007155956:Aerosol_Optical_Depth_Land_Ocean_Mean.tif"
path_myd_standard_deviation = "/home/lancer/Documents/Workspace/apom/res/SatResampMYD08_D3/2015/MYD08_D3.A2015001.006.2015007155956/MYD08_D3.A2015001.006.2015007155956:Aerosol_Optical_Depth_Land_Ocean_Standard_Deviation.tif"
path_myd_pixel_counts = "/home/lancer/Documents/Workspace/apom/res/SatResampMYD08_D3/2015/MYD08_D3.A2015001.006.2015007155956/MYD08_D3.A2015001.006.2015007155956:Aerosol_Optical_Depth_Land_Ocean_Pixel_Counts.tif"
fillValue = -9999
scale_factor = 0.0010000000474974513
add_offset = 0.0

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

# for i in range(0, rows):
# 	for j in range(0, cols):
# 		# print "Hehe %s" % (myd_pc_cropData[i][j])
# 		print float(myd_sd_cropData[i][j])
# ----------------------------Create output image----------------------------------------------
driver = input_mod_mean.GetDriver()
# Print driver
outRaster = driver.Create("/home/lancer/Documents/Workspace/apom/prod/test/testAPC_BF.tif", cols, rows, 1, GDT_Float32)
if outRaster is None:
    print 'Could not create tif file'
    sys.exit(1)

outBand = outRaster.GetRasterBand(1)
prod_value = numpy.zeros((rows,cols), numpy.float32)


# --------------------------Calculation new file---------------------------------------------
# count = 0
# fillCount = 0
# count1 = 0




# -------------------------------SAA method----------------------------------------------------------
# for i in range(0, rows):
# 	for j in range(0, cols):
# 		if (mod_mean_cropData[i][j]!=fillValue and myd_mean_cropData[i][j]!=fillValue):
# 			prod_value[i][j] = (mod_mean_cropData[i][j]+myd_mean_cropData[i][j])/2
# 		elif (mod_mean_cropData[i][j]==fillValue and myd_mean_cropData[i][j]!=fillValue):
# 			prod_value[i][j] = myd_mean_cropData[i][j]
# 		elif (mod_mean_cropData[i][j]!=fillValue and myd_mean_cropData[i][j]==fillValue):
# 			prod_value[i][j] = mod_mean_cropData[i][j]
# 		else:
# 			prod_value[i][j] = fillValue




# -------------------------------MLE method-----------------------------------------------------------
# for i in range(0, rows):
# 	for j in range(0, cols): 

# 		# a =  int(pow(mod_sd_cropData[i][j],2))

# 		if (mod_mean_cropData[i][j]!=fillValue and mod_sd_cropData[i][j]!=0 and myd_mean_cropData[i][j]!=fillValue and myd_sd_cropData[i][j]!=0):
# 			# prod_value[i][j] = mod_mean_cropData[i][j]+myd_mean_cropData[i][j]
# 			# print prod_value[i][j]
# 			# prod_value[i][j] = 250
# 			# print mod_sd_cropData[i][j]
# 			# print myd_sd_cropData[i][j]
# 			# print pow(mod_sd_cropData[i][j],2)
# 			# a = 5.0/2
# 			# print float(a)
# 			# print float(1)/pow(mod_sd_cropData[i][j],2)
# 			# print float(1/pow(mod_sd_cropData[i][j],2) + 1/pow(myd_sd_cropData[i][j],2))
# 			# prod_value[i][j] = (mod_mean_cropData[i][j]/pow(mod_sd_cropData[i][j],2)+ myd_mean_cropData[i][j]/pow(myd_sd_cropData[i][j],2))/(1/pow(mod_sd_cropData[i][j],2) + 1/pow(myd_sd_cropData[i][j],2))
# 			a = (float(mod_mean_cropData[i][j])/pow(mod_sd_cropData[i][j],2) + float(myd_mean_cropData[i][j])/pow(myd_sd_cropData[i][j],2))
# 			b = (float(1)/pow(mod_sd_cropData[i][j],2) + float(1)/pow(myd_sd_cropData[i][j],2))
# 			c = float(a)/b
# 			prod_value[i][j] = float(mod_mean_cropData[i][j]*pow(myd_sd_cropData[i][j],2) + myd_mean_cropData[i][j]*pow(mod_sd_cropData[i][j],2))/(pow(myd_sd_cropData[i][j],2) + pow(mod_sd_cropData[i][j],2)) 
# 			# print a
# 			# print b
# 			# print c
# 			# print prod_value[i][j]
# 			# print "--------"
# 		elif (mod_mean_cropData[i][j]!=fillValue and mod_sd_cropData[i][j]==0 and myd_mean_cropData[i][j]!=fillValue and myd_sd_cropData[i][j]==0):
# 			prod_value[i][j] = fillValue
# 		elif ((mod_mean_cropData[i][j]==fillValue or mod_sd_cropData[i][j]==0) and myd_mean_cropData[i][j]!=fillValue and myd_sd_cropData[i][j]!=0):
# 			prod_value[i][j] = myd_mean_cropData[i][j] 
# 		elif (mod_mean_cropData[i][j]!=fillValue and mod_sd_cropData[i][j]!=0 and (myd_mean_cropData[i][j]==fillValue or myd_sd_cropData[i][j]==0)):
# 			prod_value[i][j] = mod_mean_cropData[i][j] 
# 		else:	
# 			prod_value[i][j] = fillValue

# ------------------------------Averaging With WPC------------------------------------------------
for i in range(0, rows):
	for j in range(0, cols):
		if (mod_mean_cropData[i][j]!=fillValue and myd_mean_cropData[i][j]!=fillValue):
			# print i, j
			# a = (mod_mean_cropData[i][j]*mod_pc_cropData[i][j] + myd_mean_cropData[i][j]*myd_pc_cropData[i][j])
			# print mod_mean_cropData[i][j]*mod_pc_cropData[i][j]
			# a = myd_mean_cropData[i][j]
			# b = myd_pc_cropData[i][j]
			# print a, b
			# print b
			# print a*b
			# print mod_mean_cropData[i][j], mod_pc_cropData[i][j], myd_mean_cropData[i][j], myd_pc_cropData[i][j]
			# b = (mod_pc_cropData[i][j]+myd_pc_cropData[i][j])
			# print a 
			
			# print b
			# c = float(a)/b
			# print c
			
			prod_value[i][j] = (mod_mean_cropData[i][j]*mod_pc_cropData[i][j]+myd_mean_cropData[i][j]*myd_pc_cropData[i][j])/(mod_pc_cropData[i][j]+myd_pc_cropData[i][j])
			# print prod_value[i][j]
			# print "--------"
		elif (mod_mean_cropData[i][j]!=fillValue and myd_mean_cropData[i][j]==fillValue):
			# print "myd"
			prod_value[i][j] = mod_mean_cropData[i][j] 
		elif (mod_mean_cropData[i][j]==fillValue and myd_mean_cropData[i][j]!=fillValue):
			# print "mod"
			prod_value[i][j] = myd_mean_cropData[i][j] 
		else:
			prod_value[i][j] = fillValue
			# print "fill"


# ---------------------------------Write data------------------------------------------------------
outBand.WriteArray(prod_value, 0, 0)

# Flush data to disk, set the NoData value and calculates stats
outBand.FlushCache()
outBand.SetNoDataValue(fillValue)

# Georeference the image and set the projection
outRaster.SetGeoTransform(input_mod_mean.GetGeoTransform())
outRaster.SetProjection(input_mod_mean.GetProjection())

del prod_value
print "Test Done!"
