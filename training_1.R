
library(base)


path = "/media/lancer/01D124DD7D476BA0/demo_database/apom/"
# path1 = "/media/lancer/01D124DD7D476BA0/demo_database/apom/prod/"

setwd(path)
# filenames <- Sys.glob(file.path("prod/A2015003:Aerosol_Optical_Depth_Land_Ocean", "A20*.tif"))



# print(filenames[1])

test <- data.frame()

for (i in 1:5){
	ab <- i
	cb <- i+1
	temp <- data.frame(ab, cb)
	test <- cbind(test, temp)
}

# outFile=paste(inputPath,"/station",station,".csv",sep="")
write.csv(test,file="/media/lancer/01D124DD7D476BA0/demo_database/apom/haha.csv")
# test <- rbind(test, temp)
# temp = data.frame()
# temp$a = 111
# temp$b = 211
print(test)