from osgeo import gdal
import sys
import numpy as np
import ogr, os, osr
from osgeo.gdalconst import *
# from shutil import copyfile

# gdal.UseExceptions()
gdal.AllRegister()
# try:
#     copyfile()
try:
    input_mod_mean = gdal.Open("/home/lancer/Documents/Workspace/apom/res/SatResampMOD08_D3/2015/MOD08_D3.A2015001.006.2015035160108/MOD08_D3.A2015001.006.2015035160108:Aerosol_Optical_Depth_Land_Ocean_Mean.tif")
    input_mod_sd = gdal.Open("/home/lancer/Documents/Workspace/apom/res/SatResampMOD08_D3/2015/MOD08_D3.A2015001.006.2015035160108/MOD08_D3.A2015001.006.2015035160108:Aerosol_Optical_Depth_Land_Ocean_Standard_Deviation.tif")

    
    input_myd_mean = gdal.Open("/home/lancer/Documents/Workspace/apom/res/SatResampMYD08_D3/2015/MYD08_D3.A2015001.006.2015007155956/MYD08_D3.A2015001.006.2015007155956:Aerosol_Optical_Depth_Land_Ocean_Mean.tif")
    input_myd_sd = gdal.Open("/home/lancer/Documents/Workspace/apom/res/SatResampMYD08_D3/2015/MYD08_D3.A2015001.006.2015007155956/MYD08_D3.A2015001.006.2015007155956:Aerosol_Optical_Depth_Land_Ocean_Standard_Deviation.tif")
    
    print 'Load Done!'
except RuntimeError, e:
	print 'Unable to open tif file'
	print e
	sys.exit(1)

band = input_mod_mean.GetRasterBand(1)
rows = input_mod_mean.RasterYSize
cols = input_mod_mean.RasterXSize

print rows
print cols

# count = 0
# fillCount = 0
# count1 = 0
# prod_array = [[0 for x in range(mod_array.shape[1])] for x in range(mod_array.shape[0])]
# for i in range(0, mod_array.shape[0]):
# 	for j in range(0, mod_array.shape[1]):
# 		if (mod_array[i][j]>0 and myd_array[i][j]>0):
# 			prod_array[i][j] = (mod_array[i][j]+myd_array[i][j])/2
# 		elif (mod_array[i][j]<0 and myd_array[i][j]>0):
# 			prod_array[i][j] = myd_array[i][j] 
# 		elif(mod_array[i][j]>0 and myd_array[i][j]<0):
# 			prod_array[i][j] = mod_array[i][j] 
# 		else:
# 			prod_array[i][j] = myd_array[i][j]



print "[ RASTER BAND COUNT ]: ", src_ds.RasterCount
for band in range( src_ds.RasterCount ):
	band += 1
	print "[ GETTING BAND ]: ", band
	srcband = src_ds.GetRasterBand(band)
	if srcband is None:
		continue

	stats = srcband.GetStatistics( True, True )
	if stats is None:
        continue

	print "[ STATS ] =  Minimum=%.3f, Maximum=%.3f, Mean=%.3f, StdDev=%.3f" % (	stats[0], stats[1], stats[2], stats[3] )


# mod_array = np.array(mod_src_ds.GetRasterBand(1).ReadAsArray())
# print mod_array.shape
# print mod_array.size
# print mod_array[0][3]

# myd_array = np.array(myd_src_ds.GetRasterBand(1).ReadAsArray())
# print myd_array.shape[0]
# print myd_array.size
# print myd_array[7][0]


count = 0
fillCount = 0
count1 = 0
prod_array = [[0 for x in range(mod_array.shape[1])] for x in range(mod_array.shape[0])]
for i in range(0, mod_array.shape[0]):
	for j in range(0, mod_array.shape[1]):
		if (mod_array[i][j]>0 and myd_array[i][j]>0):
			prod_array[i][j] = (mod_array[i][j]+myd_array[i][j])/2
		elif (mod_array[i][j]<0 and myd_array[i][j]>0):
			prod_array[i][j] = myd_array[i][j] 
		elif(mod_array[i][j]>0 and myd_array[i][j]<0):
			prod_array[i][j] = mod_array[i][j] 
		else:
			prod_array[i][j] = myd_array[i][j]
print prod_array
print mod_array.shape[0]
print count
print fillCount
print count1
print count + fillCount + count1


#