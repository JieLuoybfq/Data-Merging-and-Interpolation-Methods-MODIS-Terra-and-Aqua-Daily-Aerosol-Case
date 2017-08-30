from osgeo import gdal
import ogr, os, osr
import numpy as np


def array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array):

    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Byte)
    outRaster.SetGeoTransform((originX, pixelWidth, 0, originY, 0, pixelHeight))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRasterSRS = osr.SpatialReference()
    outRasterSRS.ImportFromEPSG(4326)
    outRaster.SetProjection(outRasterSRS.ExportToWkt())
    outband.FlushCache()


def main(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array):
    reversed_arr = array[::-1] # reverse array so the tif looks like the array
    array2raster(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,reversed_arr) # convert array to raster



ax = np.array([[ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4],
               [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4],
               [ 1, 6, 6, 6, 6, 1, 6, 6, 6, 6, 1, 6, 6, 6, 1, 6, 1, 1, 1, 4],
               [ 1, 6, 1, 1, 1, 1, 1, 6, 1, 6, 1, 6, 1, 6, 1, 6, 1, 1, 1, 4],
               [ 1, 6, 1, 6, 6, 1, 1, 6, 1, 6, 1, 6, 6, 6, 1, 6, 1, 1, 1, 4],
               [ 1, 6, 1, 1, 6, 1, 1, 6, 1, 6, 1, 6, 1, 6, 1, 6, 1, 1, 1, 4],
               [ 1, 6, 6, 6, 6, 1, 6, 6, 6, 6, 1, 6, 1, 6, 1, 6, 6, 6, 1, 4],
               [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4],
               [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4],
               [ 1, 1, 1, 1, 1, 1, 1, 1, 5, 5, 5, 5, 5, 1, 1, 1, 1, 1, 1, 4]])

if __name__ == "__main__":
    rasterOrigin = (-100,8)
    pixelWidth = 5
    pixelHeight = 5
    newRasterfn = 'test3.tif'
    array = ax


    main(newRasterfn,rasterOrigin,pixelWidth,pixelHeight,array)