import cv2

img = cv2.imread("/home/lancer/Documents/Workspace/Res/MYD08_D3.A2015001.006.2015007155956/MYD08_D3.A2015001.006.2015007155956:Aerosol_Optical_Depth_Land_Ocean_Mean.tif",-1)
cv2.imshow('16bit TIFF', img)
cv2.waitKey()
