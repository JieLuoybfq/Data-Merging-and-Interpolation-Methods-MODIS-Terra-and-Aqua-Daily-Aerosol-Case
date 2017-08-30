import gdal
from gdalconst import *
dataset = gdal.Open( filename, GA_ReadOnly )
if dataset is None:
    ...
