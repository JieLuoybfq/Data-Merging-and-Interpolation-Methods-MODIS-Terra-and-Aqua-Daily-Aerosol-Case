import glob, os
from PIL import Image

# inputFolder = "/media/lancer/TOSHIBA/apom/org/SatOrgMYD08_D3/2015/"
inputFolder = "/home/lancer/Documents/Workspace/apom/res/SatResampMOD08_D3/2015/"

mean = "Aerosol_Optical_Depth_Land_Ocean_Mean"
standard_deviation = "Aerosol_Optical_Depth_Land_Ocean_Standard_Deviation"
pixel_counts = "Aerosol_Optical_Depth_Land_Ocean_Pixel_Counts"


def convertToString(number):
	if (number>0 and number<10): 
		string = "00"+str(number) 
	elif (number>=10 and number<100):
		string = "0"+str(number)
	elif number>=100:
		string = str(number)
	return string


# stringCount = str(count)
for i in range(1,6):
	count = i
	os.chdir(inputFolder)
	fileList = glob.glob("*.A2015"+convertToString(count)+".*")
	fileList.sort()
	for file in fileList:
		print file


# MODfilePath = "/home/lancer/Documents/Workspace/Res/{0}/{0}:{1}.tif"
# # print MODfilePath.format(file, mean)
# # im = Image.open(MODfilePath.format(file, mean))
# im = Image.open("/home/lancer/Documents/Workspace/alienware.jpg")
# im.show()