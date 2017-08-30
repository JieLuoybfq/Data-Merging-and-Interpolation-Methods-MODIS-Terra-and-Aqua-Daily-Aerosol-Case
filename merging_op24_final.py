import sys
import numpy
import ogr, os, osr, glob
from osgeo import gdal
from osgeo.gdalconst import *
# from shutil import copyfile

# gdal.UseExceptions()
gdal.AllRegister()

data_set = "Aerosol_Optical_Depth_Land_Ocean"
# mean = "Aerosol_Optical_Depth_Land_Ocean_Mean"
# standard_deviation = "Aerosol_Optical_Depth_Land_Ocean_Standard_Deviation"
# pixel_counts = "Aerosol_Optical_Depth_Land_Ocean_Pixel_Counts"

# path_mod = "/media/lancer/01D124DD7D476BA0/apom/res/SatResampMOD08_D3/2015/"
# path_myd = "/media/lancer/01D124DD7D476BA0/apom/res/SatResampMYD08_D3/2015/"
path_prod = "/media/lancer/01D124DD7D476BA0/apom/prod/"

# path_mod = "/media/lancer/01D124DD7D476BA0/demo_database/apom/res/SatResampMOD08_D3/2015/"
# path_myd = "/media/lancer/01D124DD7D476BA0/demo_database/apom/res/SatResampMYD08_D3/2015/"
# path_prod = "/media/lancer/01D124DD7D476BA0/demo_database/apom/prod/"

fillValue = -9999
scale_factor = 0.0010000000474974513
add_offset = 0.0

def merge_interpolationFile(folder, interpolationStyle):
	os.chdir(path_prod+folder)
	fileList = glob.glob("*D08_D3.A*_"+interpolationStyle+"_uk.tif")

	# ---------------------------------Open file------------------------------------------------
	try:
	    input_file_1 = gdal.Open(path_prod+folder+"/"+fileList[0])
	    input_file_2 = gdal.Open(path_prod+folder+"/"+fileList[1])
	    # print 'Load Done!'
	except RuntimeError, e:
		print 'Unable to open tif file'
		print e
		sys.exit(1)

	# ---------------------------------Read data---------------------------------------------------
	file_1_band = input_file_1.GetRasterBand(1)
	file_2_band = input_file_2.GetRasterBand(1)

	rows = input_file_1.RasterYSize
	cols = input_file_2.RasterXSize

	file_1_Data = file_1_band.ReadAsArray(0, 0, cols, rows)
	file_2_Data = file_2_band.ReadAsArray(0, 0, cols, rows)

	# ----------------------------Create output image-----------------------------------------------
	driver = input_file_1.GetDriver()
	outputRaster = driver.Create(path_prod+folder+"/"+fileList[0][9:17]+":"+data_set+"_"+interpolationStyle+"_uk_SAA.tif", cols, rows, 1, GDT_Float32)
	if outputRaster is None:
	    print 'Could not create output tif file'
	    sys.exit(1)
	outputBand = outputRaster.GetRasterBand(1)
	prod_value = numpy.zeros((rows,cols), numpy.float32)

	# ---------------------------------SAA method---------------------------------------------------
	for i in range(0, rows):
		for j in range(0, cols):
			prod_value[i][j] = (file_1_Data[i][j]+file_2_Data[i][j])/2

	# ---------------------------------Write data---------------------------------------------------
	outputBand.WriteArray(prod_value, 0, 0)
	# Flush data to disk, set the NoData value and calculates stats
	outputBand.FlushCache()
	outputBand.SetNoDataValue(fillValue)
	# Georeference the image and set the projection
	outputRaster.SetGeoTransform(input_file_1.GetGeoTransform())
	outputRaster.SetProjection(input_file_1.GetProjection())
	del prod_value

	print "Done!"

# ---------------------------------Browse file------------------------------------------------------
os.chdir(path_prod)
folderList = glob.glob("*"+data_set)
# fileListMOD.sort()
# file = fileListMOD[0] 
for folder in folderList:
	merge_interpolationFile(folder, "i")
	merge_interpolationFile(folder, "mi")
	













