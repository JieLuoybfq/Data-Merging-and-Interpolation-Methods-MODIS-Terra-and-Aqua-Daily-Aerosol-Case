import glob, os
from shutil import copyfile

path = "/media/lancer/01D124DD7D476BA0/apom/prod/"
os.chdir(path)
folderList = glob.glob("A201*:Aerosol_Optical_Depth_Land_Ocean")

for folder in folderList:
	copyfile(path+folder+"/"+folder+"_EvaluateInfo.csv", path+folder+"_EvaluateInfo.csv")