# import scipy as N
import gdal
import sys
import matplotlib.pyplot as pyplot

# try:
#     tif = gdal.Open("/home/lancer/Documents/Workspace/Res/MYD08_D3.A2015001.006.2015007155956/MYD08_D3.A2015001.006.2015007155956:Aerosol_Optical_Depth_Land_Ocean_Mean.tif")
#     tifArray = tif.ReadAsArray()
# except:
#     print 'The file does not exist.'
#     sys.exit(0)

# band1 = tif.GetRasterBand(1)
# band2 = tif.GetRasterBand(2)
# band3 = tif.GetRasterBand(3)

# band1Array = band1.ReadAsArray()
# band2Array = band2.ReadAsArray()
# band3Array = band3.ReadAsArray()

img=mpimg.imread("/home/lancer/Documents/Workspace/Res/MYD08_D3.A2015001.006.2015007155956/MYD08_D3.A2015001.006.2015007155956:Aerosol_Optical_Depth_Land_Ocean_Mean.tif")
imgplot = plt.imshow(img)
imgplot2 = plt.imshow(band3Array)
plt.show()