# library(mgcv)

# list.dirs("/media/lancer/01D124DD7D476BA0/workspace/apom/res/SatResampMOD08_D3/2015/")
# fileLists = list.files("/media/lancer/01D124DD7D476BA0/workspace/apom/res/SatResampMOD08_D3/2015/")
# list.files(file.path("/media/lancer/01D124DD7D476BA0/Workspace/apom/prod/A2015001:Aerosol_Optical_Depth_Land_Ocean","A2015*"), dirmark = FALSE)

# Sys.glob(file.path("/media/lancer/01D124DD7D476BA0/workspace/apom/prod/A2015001:Aerosol_Optical_Depth_Land_Ocean", "A2015*.tif"), dirmark = FALSE)
# b = "asddd"
# a = "asd"
# list.dirs(R.home("save"), full.names = FALSE)
# print(a)
# print(b,a)
# fileLists = Sys.glob(file.path("/media/lancer/01D124DD7D476BA0/workspace/apom/prod", "A2015*"))
# for (file in fileLists)
# 	print(file)


# s1 <- "R-"
# s2 <- "projecttttttt"
# test <- paste(s1, s2, sep = "")
# print(test)

# s1 <- "R-"
# s2 <- "project Dina's"
# stringmerge(s1,s2)
# paste(c('a','b','c'), collapse= ' ')

data_set = "Aerosol_Optical_Depth_Land_Ocean"
mean = "Aerosol_Optical_Depth_Land_Ocean_Mean"
standard_deviation = "Aerosol_Optical_Depth_Land_Ocean_Standard_Deviation"
pixel_counts = "Aerosol_Optical_Depth_Land_Ocean_Pixel_Counts"

# SAA = "_SAA"
# MLE = "_MLE"
# WPC = "_WPC"

# path_mod = "/media/lancer/01D124DD7D476BA0/apom/res/SatResampMOD08_D3/2015/"
# path_myd = "/media/lancer/01D124DD7D476BA0/apom/res/SatResampMYD08_D3/2015/"
# path_prod = "/media/lancer/01D124DD7D476BA0/apom/prod/"

path_mod = "/media/lancer/01D124DD7D476BA0/demo_database/apom/res/SatResampMOD08_D3/2015/"
path_myd = "/media/lancer/01D124DD7D476BA0/demo_database/apom/res/SatResampMYD08_D3/2015/"
path_prod = "/media/lancer/01D124DD7D476BA0/demo_database/apom/prod/"
file_test = "/media/lancer/01D124DD7D476BA0/demo_database/apom/prod/A2015001:Aerosol_Optical_Depth_Land_Ocean/A2015001:Aerosol_Optical_Depth_Land_Ocean_SAA.tif"

options1 = "_i(m)"
options2 = "_m(i)"
options3 = "_mi()"
options4 = "_m(mi)"
options5 = "_i(T)"
options6 = "_i(A)"
options7 = "_mi(T)"
options8 = "_mi(A)"

# fileLists = list.files("/media/lancer/01D124DD7D476BA0/workspace/apom/prod/")
# fileLists = list.files(path_prod)
# fileLists
# for (file in fileLists) {
# 	input_file = paste(c(path_prod, file, "/", file, SAA), collapse = "")
# 	print(input_file) 
# }

fileLists = list.files(path_prod)
# ls.size(fileLists)
listLength = length(fileLists)
print(fileLists)
print(listLength)