import gdal
import subprocess
import psycopg2
import glob
import shutil

inputFolder = "/media/lancer/TOSHIBA/MODIS Terra/"
cutFolder = "/media/lancer/TOSHIBA/MODIS Terra Cut/"

def re_griding(inputfile, resx, resy, ouputfile):
	regrid_command = "gdalwarp -t_srs '+proj=longlat +datum=WGS84' -tps -ot Float32 -wt Float32 -te 100.1 6.4 111.8 25.6 -tr {0} {1} -r cubic -srcnodata -9999 -dstnodata -9999 -overwrite -multi {2} {3}"
	os.system(regrid_command.format(resx, resy, inputfile, ouputfile))



gdalwarp -t_srs '+proj=longlat +datum=WGS84' -tps -ot Float32 -wt Float32 -te 100.1 6.4 111.8 25.6 -srcnodata -9999 -dstnodata -9999 -overwrite -multi HDF4_EOS:EOS_GRID:"MOD08_D3.A2016032.006.2016034014959.hdf":mod08:Retrieved_Temperature_Profile_Standard_Deviation out.tif


gdalwarp -te 100.1 6.4 111.8 25.6 -srcnodata -9999 -dstnodata -9999 -overwrite -multi HDF4_EOS:EOS_GRID:"MOD08_D3.A2016032.006.2016034014959.hdf":mod08:Aerosol_Optical_Depth_Land_Ocean_Mean out2.tif

gdal_translate -of GTiff HDF4_EOS:EOS_GRID:"MOD08_D3.A2015001.006.2015035160108.hdf":mod08:Aerosol_Optical_Depth_Land_Ocean_Mean modis_ds12.tif

gdal_translate -of GTiff HDF4_EOS:EOS_GRID:"MOD11A1.A2008006.h16v07.005.2008007232041.hdf":MODIS_Grid_Daily_1km_LST:Clear_night_cov modis_ds12.tif

gdal_translate -of GTiff HDF4_EOS:EOS_GRID:"MOD04_L2.A2015333.0254.006.2015333030251.hdf":mod04:Optical_Depth_Land_And_Ocean modis_ds12.tif

gdalinfo MOD04_L2.A2015333.0254.006.2015333030251.hdf

gdal_translate -of GTiff HDF4_EOS:EOS_SWATH:"MOD04_L2.A2015333.0254.006.2015333030251.hdf":Swath00:Optical_Depth_Land_And_Ocean modis_ds12.tif

HDF4_EOS:EOS_SWATH:"MOD04_L2.A2015333.0254.006.2015333030251.hdf":Swath00:Optical_Depth_Land_And_Ocean

gdalwarp -t_srs '+proj=longlat +datum=WGS84' -tps -ot Float32 -wt Float32 -te 100.1 6.4 111.8 25.6 -srcnodata -9999 -dstnodata -9999 -overwrite -multi HDF4_EOS:EOS_SWATH:"MOD04_L2.A2015333.0254.006.2015333030251.hdf":Swath00:Optical_Depth_Land_And_Ocean out123.tif