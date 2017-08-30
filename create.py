import numpy, sys
from osgeo import gdal
from osgeo.gdalconst import *


# register all of the GDAL drivers
gdal.AllRegister()

# open the image
inDs = gdal.Open("/home/lancer/Documents/Workspace/apom/res/SatResampMOD08_D3/2015/MOD08_D3.A2015001.006.2015035160108/MOD08_D3.A2015001.006.2015035160108:Aerosol_Optical_Depth_Land_Ocean_Mean.tif")
if inDs is None:
  print 'Could not open image file'
  sys.exit(1)

# read in the crop data and get info about it
band1 = inDs.GetRasterBand(1)
rows = inDs.RasterYSize
cols = inDs.RasterXSize

cropData = band1.ReadAsArray(0,0,cols,rows)

listAg = [1,5,6,22,23,24,41,42,28,37]
listNotAg = [111,195,141,181,121,122,190,62]

# create the output image
driver = inDs.GetDriver()
#print driver
outDs = driver.Create("/home/lancer/Documents/Workspace/apom/res/SatResampMOD08_D3/2015/MOD08_D3.A2015001.006.2015035160108/MOD08_D3.A2015001.006.2015035160108:Aerosol_Optical_Depth_Land_Ocean_Mean.tif", cols, rows, 1, GDT_Int32)
if outDs is None:
    print 'Could not create reclass_40.tif'
    sys.exit(1)
