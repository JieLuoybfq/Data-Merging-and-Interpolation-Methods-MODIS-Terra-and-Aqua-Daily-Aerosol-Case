import glob, os


inputFolder = "//media//lancer//TOSHIBA//MODIS Terra//"
os.chdir(inputFolder)
for file in glob.glob("*.hdf"):
    print(file)