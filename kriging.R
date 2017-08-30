library(gstat)
library(base)
library(RPostgreSQL)
library(stringr)
library(raster)
library(gdalUtils)
library(rgdal)

# library(rPython)
# install.packages('rPython')


createKrigingImage = function(regressPm_file){
	regressPm_mask_file = regressPm_file
	cross_result_file = "/home/lancer/Desktop/rs.csv"
	#regressPm_mask_file = str_replace(regressPm_file,".tif","_mask.tif")
	#file.copy(regressPm_file,regressPm_mask_file)
	#gdal_rasterize(shape_file,regressPm_mask_file,b=1,i=TRUE,burn=-9999,l="VNM_adm0")
	
	#PM values
	pmRaster=raster(regressPm_mask_file)
	pm=values(pmRaster)
	corxy=coordinates(pmRaster)
	x=corxy[,'x']
	y=corxy[,'y']
	
	
	totalCell=length(pmRaster)
	cell = c(1:totalCell)
	
	table=data.frame(cell,x,y,pm)
	newTable=table
	#testTable=subset(table,pm<0)
	#trainTable=subset(table,pm>=0)
	trainTable=subset(table,!is.na(pm))
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
	#sph fit
	#sill=min(empiVario$gamma)
	#sphModel=vgm(psill=sill,model="Sph",nugget=0,range=min(empiVario$dist))
	#sphModel=vgm(model="Sph",nugget=0,range=1)		
	#sphFit=fit.variogram(empiVario,sphModel)
	
	universal_result=krige(id="pm",formula=pm~x+y,data=trainTable,newdata=testTable,model=sphFit,locations=~x+y)
	
	#edit tiff
	newTable$pm[is.na(newTable$pm)] = universal_result[,3]
	universalPMRaster=pmRaster
	universalPMRaster[1:totalCell]=newTable$pm
	#universalPMValue=universal_result[,3]
	#universalPMRaster[1:totalCell]=universalPMValue
	
	
	#edit error tiff
	#errorPMRaster=pmRaster
	#errorPMValue=universal_result[,4]
	#errorPMRaster[1:totalCell]=errorPMValue
	
	#save uk result to tiff
	uk_file = str_replace(regressPm_file,".tif","_uk.tif")
	writeRaster(universalPMRaster,filename=uk_file,format="GTiff",overwrite=TRUE)
	#gdal_rasterize(shape_file,uk_file,b=1,i=TRUE,burn=-9999,l="VNM_adm0")
	
	#set n/a value
	#new_uk_raster = raster(uk_file)
	#new_uk_value = values(new_uk_raster)
	#new_uk_value[new_uk_value==-9999]<-NA
	#new_uk_value[new_uk_value<0]<-0
	#new_uk_raster[1:totalCell] = new_uk_value

	#writeRaster(new_uk_raster,filename=uk_file,format="GTiff",overwrite=TRUE)
	
	
	# save uk error to tiff
	# error_file = str_replace(regressPm_file,"rg.tif","error.tif")
	# writeRaster(errorPMRaster,filename=error_file,format="GTiff",overwrite=TRUE)
	# gdal_rasterize(shape_file,error_file,b=1,i=TRUE,burn=-9999,l="VNM_adm0")
	
	# cross-validation
	universal_result_3=krige.cv(pm~x+y,trainTable,sphFit,locations=~x+y,nfold=3)
	
	
	# Universal statis

	universal_cor=cor(universal_result_3$var1.pred,universal_result_3$observed)
	universal_rmse=sqrt(sum((universal_result_3$residual)^2)/nrow(universal_result_3))
	universal_re=sum(abs(universal_result_3$residual)/universal_result_3$observed)/nrow(universal_result_3)
	
	filename = uk_file
	samples = nrow(trainTable)
	r2 = universal_cor*universal_cor
	rmse = universal_rmse
	re = universal_re*100
	
	rs = read.csv(cross_result_file, header=T, sep=",")
	rs = rbind(rs,data.frame(filename,sample,r2,rmse,re))
	write.csv(rs,cross_result_file)
}

createKrigingImage("/home/lancer/Desktop/a.tif")