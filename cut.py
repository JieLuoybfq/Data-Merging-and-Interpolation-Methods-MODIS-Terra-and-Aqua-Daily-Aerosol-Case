import glob, os

# inputFolder = "/media/lancer/TOSHIBA/MODIS Aqua"
# outputFolder = "/media/lancer/TOSHIBA/MODIS Terra Cut/"
inputFolder = "/home/lancer/Documents/Workspace"

mean = "Aerosol_Optical_Depth_Land_Ocean_Mean"
standard_deviation = "Aerosol_Optical_Depth_Land_Ocean_Standard_Deviation"
pixel_counts = "Aerosol_Optical_Depth_Land_Ocean_Pixel_Counts"

os.chdir(inputFolder)
for file in glob.glob("*.hdf"):
	regrid_command =  "gdalwarp -te 100.1 6.4 111.8 25.6 -srcnodata -9999 -dstnodata -9999 -overwrite -multi HDF4_EOS:EOS_GRID:{0}:mod08:{1} /media/lancer/TOSHIBA/AquaCut/{2}:{1}.tif"
	os.system(regrid_command.format(file, mean, file[:-4]))
	os.system(regrid_command.format(file, standard_deviation, file[:-4]))
	os.system(regrid_command.format(file, pixel_counts, file[:-4]))


	