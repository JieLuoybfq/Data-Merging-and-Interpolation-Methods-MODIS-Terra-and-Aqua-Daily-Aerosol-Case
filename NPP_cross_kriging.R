# TODO: Add comment
# 
# Author: broken
###############################################################################
#import library

library(raster)
library(gstat)
library(automap)
library(stringr)
library(gdalUtils)
library(rgdal)



#path
path= "D:/prod/"
shape_file = "D:/BDNEN/VNM_adm0.shp"

year_array=c(2012,2013)
for (j in 1:2) {
	inputPath = paste(path,year_array[j],sep="")
	#pm file
	fileArray = list.files(path = inputPath,pattern="rg.tif$",full.names = FALSE,recursive=TRUE)
	totalFile=length(fileArray)
	uCor=uRMSE=uRE=uMFE=uMFB=numberPixel=c(1:totalFile)
	
	for(i in 1:totalFile){
		fileName=fileArray[i]
		
		#PM values
		pmFile=paste(inputPath,fileName,sep="/")
		
		regressPm_mask_file = str_replace(pmFile,".tif","_mask.tif")
		file.copy(pmFile,regressPm_mask_file)
		gdal_rasterize(shape_file,regressPm_mask_file,b=1,i=TRUE,burn=-9999,l="VNM_adm0")
		
		pmRaster=raster(regressPm_mask_file)
		pm=values(pmRaster)
		corxy=coordinates(pmRaster)
		x=corxy[,'x']
		y=corxy[,'y']
		
		
	
		#cell id
		totalCell=length(pmRaster)
		cell = c(1:totalCell)
		
		#data frame
		table=data.frame(cell,x,y,pm)
		newTable=table
		trainTable=subset(table,!is.na(pm)&pm!=-9999)
		testTable=subset(table,is.na(pm))
		
		auto_trainTable = trainTable
		coordinates(auto_trainTable) =~ x+y
		
		auto_variogram = autofitVariogram(pm~1,auto_trainTable)
		auto_model = auto_variogram$var_model$model[2]
		auto_sill = auto_variogram$var_model$psill[2]
		auto_range = auto_variogram$var_model$range[2]

		#caculate variogram
		empiVario=variogram(pm~1,locations=~x+y,data=trainTable)
		
		sphModel=vgm(psill=auto_sill,model=auto_model,nugget=0,range=auto_range)		
		sphFit=fit.variogram(empiVario,sphModel)
		
		
	
		#-----------------------UNIVERSAL KRIGING-----------------------------------
		
		universal_result=krige(id="pm",formula=pm~x+y,data=trainTable,newdata=testTable,model=sphFit,locations=~x+y)
		
			
		#edit tiff
		newTable$pm[is.na(newTable$pm)] = universal_result[,3]
		newTable$pm[newTable$pm==-9999] = NA
		universalPMRaster=pmRaster
		universalPMRaster[1:totalCell]=newTable$pm
		
		## #edit error tiff
		## errorPMRaster=pmRaster
		## errorPMValue=universal_result[,4]
		## errorPMRaster[1:totalCell]=errorPMValue
		
		#save uk result to tiff
		uk_file = str_replace(pmFile,"_rg.tif","_uk.tif")
		writeRaster(universalPMRaster,filename=uk_file,format="GTiff")
		
		
		#cross-validation
		universal_result_3=krige.cv(pm~x+y,trainTable,sphFit,locations=~x+y,nfold=3)
		
		
		#Universal statis
		universal_cor=cor(universal_result_3$var1.pred,universal_result_3$observed)
		universal_rmse=sqrt(sum((universal_result_3$residual)^2)/nrow(universal_result_3))
		universal_re=sum(abs(universal_result_3$residual)/universal_result_3$observed)/nrow(universal_result_3)
		
		universal_mfb = (2*sum((universal_result_3$var1.pred-universal_result_3$observed)/(universal_result_3$observed+universal_result_3$var1.pred)*100))/nrow(universal_result_3)
		universal_mfe = (2*sum(abs(universal_result_3$var1.pred-universal_result_3$observed)/(universal_result_3$var1.pred+universal_result_3$observed)*100))/nrow(universal_result_3)
		
		numberPixel[i]=nrow(trainTable)
		uCor[i]=universal_cor*universal_cor
		uRMSE[i]=universal_rmse
		uRE[i]=universal_re*100
		uMFB[i]=universal_mfb
		uMFE[i]=universal_mfe
				
		str=paste("Complete",fileArray[i],sep=" ")
		print(str)
	}
	

#export statis result
	result_dataframe=data.frame(fileArray,numberPixel,uCor,uRMSE,uRE,uMFB,uMFE)
	outFile=paste(inputPath,"/",year_array[j],"_cross_result.csv",sep="")
	write.csv(result_dataframe,file=outFile)
	print(paste("Finish",year_array[j]))
	

}






