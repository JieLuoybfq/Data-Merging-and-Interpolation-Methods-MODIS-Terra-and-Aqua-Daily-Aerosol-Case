from PIL import Image
import numpy

im = Image.open("/home/lancer/Documents/Workspace/Res/MYD08_D3.A2015001.006.2015007155956/MYD08_D3.A2015001.006.2015007155956:Aerosol_Optical_Depth_Land_Ocean_Mean.tif")
im.show()
im.waitkey()