library(gstat)
library(base)
library(RPostgreSQL)
library(stringr)
library(raster)
library(gdalUtils)
library(rgdal)
library(automap)

data_set = "Aerosol_Optical_Depth_Land_Ocean"
mean = "Aerosol_Optical_Depth_Land_Ocean_Mean"
standard_deviation = "Aerosol_Optical_Depth_Land_Ocean_Standard_Deviation"
pixel_counts = "Aerosol_Optical_Depth_Land_Ocean_Pixel_Counts"
fillValue = -9999
scale_factor = 0.0010000000474974513
add_offset = 0.0

path_mod = "/media/lancer/01D124DD7D476BA0/apom/res/SatResampMOD08_D3/2015/"
path_myd = "/media/lancer/01D124DD7D476BA0/apom/res/SatResampMYD08_D3/2015/"
path_prod = "/media/lancer/01D124DD7D476BA0/apom/prod/"

# path_mod = "/media/lancer/01D124DD7D476BA0/demo_database/apom/res/SatResampMOD08_D3/2015/"
# path_myd = "/media/lancer/01D124DD7D476BA0/demo_database/apom/res/SatResampMYD08_D3/2015/"
# path_prod = "/media/lancer/01D124DD7D476BA0/demo_database/apom/prod/"
file_test_merged = "/media/lancer/01D124DD7D476BA0/demo_database/apom/prod/A2015001:Aerosol_Optical_Depth_Land_Ocean/A2015001:Aerosol_Optical_Depth_Land_Ocean_SAA.tif"
file_test_unmerged = "/media/lancer/01D124DD7D476BA0/demo_database/apom/res/SatResampMOD08_D3/2015/MOD08_D3.A2015001.006.2015035160108/MOD08_D3.A2015001.006.2015035160108:Aerosol_Optical_Depth_Land_Ocean_Mean.tif"
output_file_unmerged = "/media/lancer/01D124DD7D476BA0/demo_database/apom/prod/A2015001:Aerosol_Optical_Depth_Land_Ocean/test.tif"

# fileLists <- Sys.glob(file.path("/media/lancer/01D124DD7D476BA0/workspace/apom/prod", "A2015*"))
# colnames(name_list)[column] <- "columnName"
# --------------------------------------Universal Kriging-------------------------------------------------
createKrigingImage = function(regressPm_file, output_file){
	regressPm_mask_file = regressPm_file
	cross_result_file = "/home/lancer/Desktop/rs.csv"
	# regressPm_mask_file = str_replace(regressPm_file,".tif","_mask.tif")
	# file.copy(regressPm_file,regressPm_mask_file)
	# gdal_rasterize(shape_file,regressPm_mask_file,b=1,i=TRUE,burn=-9999,l="VNM_adm0")
	
	pmRaster = raster(regressPm_mask_file)
	# print("pmRaster")
	# print(pmRaster)
	if (regressPm_file == output_file) { # multi scale_factor if not yet
		pm = values(pmRaster)
		# print("khong nhan!")
	} else {
		pm = values(pmRaster*scale_factor+add_offset)
		# print("nhan!")
	}

	corxy = coordinates(pmRaster)
	# print("corxy")
	# print(corxy)
	x = corxy[,'x']
	y = corxy[,'y']
	
	totalCell = length(pmRaster)
	cell = c(1:totalCell)
	
	table = data.frame(cell, x, y, pm)
	newTable = table
	#testTable=subset(table,pm<0)
	#trainTable=subset(table,pm>=0)
	trainTable = subset(table, !is.na(pm))
	testTable = subset(table, is.na(pm))
	
	auto_trainTable = trainTable
	coordinates(auto_trainTable) =~x+y
	
	auto_variogram = autofitVariogram(pm~1, auto_trainTable)
	auto_model = auto_variogram$var_model$model[2]
	auto_sill = auto_variogram$var_model$psill[2]
	auto_range = auto_variogram$var_model$range[2]
	
	#caculate variogram
	empiVario = variogram(pm~1,locations=~x+y,data=trainTable)
	
	sphModel = vgm(psill=auto_sill,model=auto_model,nugget=0,range=auto_range)		
	sphFit = fit.variogram(empiVario,sphModel)
	# sph fit
	# sill=min(empiVario$gamma)
	# sphModel=vgm(psill=sill,model="Sph",nugget=0,range=min(empiVario$dist))
	# sphModel=vgm(model="Sph",nugget=0,range=1)		
	# sphFit=fit.variogram(empiVario,sphModel)
	
	universal_result = krige(id = "pm", formula = pm~x+y, data = trainTable, newdata = testTable, model = sphFit, locations =~x+y)
	
	# edit tiff
	newTable$pm[is.na(newTable$pm)] = universal_result[,3]
	universalPMRaster = pmRaster
	universalPMRaster[1:totalCell] = newTable$pm
	#universalPMValue=universal_result[,3]
	#universalPMRaster[1:totalCell]=universalPMValue
	
	# edit error tiff
	# errorPMRaster=pmRaster
	# errorPMValue=universal_result[,4]
	# errorPMRaster[1:totalCell]=errorPMValue
	
	# save uk result to tiff
	# uk_file_tail = paste(options, "_i(m)_uk.tif")
	uk_file = str_replace(output_file, ".tif", "_i_uk.tif")
	# uk_file = str_replace(regressPm_file,".tif","_uk.tif")
	writeRaster(universalPMRaster, filename = uk_file, format = "GTiff", overwrite = TRUE)
	#gdal_rasterize(shape_file,uk_file,b=1,i=TRUE,burn=-9999,l="VNM_adm0")
	
	# set n/a value
	# new_uk_raster = raster(uk_file)
	# new_uk_value = values(new_uk_raster)
	# new_uk_value[new_uk_value==-9999]<-NA
	# new_uk_value[new_uk_value<0]<-0
	# new_uk_raster[1:totalCell] = new_uk_value

	# writeRaster(new_uk_raster,filename=uk_file,format="GTiff",overwrite=TRUE)
	
	# save uk error to tiff
	# error_file = str_replace(regressPm_file,"rg.tif","error.tif")
	# writeRaster(errorPMRaster,filename=error_file,format="GTiff",overwrite=TRUE)
	# gdal_rasterize(shape_file,error_file,b=1,i=TRUE,burn=-9999,l="VNM_adm0")
	
	# cross-validation
	universal_result_3 = krige.cv(pm~x+y, trainTable, sphFit, locations = ~x+y, nfold = 3)
	
	# Universal statis

	universal_cor = cor(universal_result_3$var1.pred,universal_result_3$observed)
	universal_rmse = sqrt(sum((universal_result_3$residual)^2)/nrow(universal_result_3))
	universal_re = sum(abs(universal_result_3$residual)/universal_result_3$observed)/nrow(universal_result_3)
	
	filename = uk_file
	samples = nrow(trainTable)
	r2 = universal_cor*universal_cor
	rmse = universal_rmse
	re = universal_re*100
	r2
	rmse
	re
	# rs = read.csv(cross_result_file, header=T, sep=",")
	# rs = data.frame(filename,sample,r2,rmse,re)
	# write.csv(rs,cross_result_file)
}

createKrigingImage_mi = function(regressPm_file, output_file){
	regressPm_mask_file = regressPm_file
	cross_result_file = "/home/lancer/Desktop/rs.csv"
	
	#PM values
	pmRaster = raster(regressPm_mask_file) # ??
	pm = values(pmRaster*scale_factor+add_offset) # ??
	corxy = coordinates(pmRaster)
	x = corxy[,'x'] # ??
	y = corxy[,'y'] # ??
	
	totalCell = length(pmRaster)
	cell = c(1:totalCell)
	
	table = data.frame(cell, x, y, pm)
	newTable = table
	trainTable = subset(table, !is.na(pm))
	testTable = table

	auto_trainTable = trainTable
	coordinates(auto_trainTable) =~x+y
	
	auto_variogram = autofitVariogram(pm~1, auto_trainTable)
	auto_model = auto_variogram$var_model$model[2]
	auto_sill = auto_variogram$var_model$psill[2]
	auto_range = auto_variogram$var_model$range[2]
	
	#caculate variogram
	empiVario = variogram(pm~1,locations=~x+y,data=trainTable)
	
	sphModel = vgm(psill=auto_sill,model=auto_model,nugget=0,range=auto_range)		
	sphFit = fit.variogram(empiVario,sphModel)
	
	universal_result = krige(id = "pm", formula = pm~x+y, data = trainTable, newdata = testTable, model = sphFit, locations =~x+y)
	
	#edit tiff
	newTable[["pm"]] = universal_result[,3]
	universalPMRaster = pmRaster
	universalPMRaster[1:totalCell] = newTable$pm
	
	uk_file = str_replace(output_file, ".tif", "_mi_uk.tif")
	# uk_file = str_replace(regressPm_file,".tif","_uk.tif")
	writeRaster(universalPMRaster, filename = uk_file, format = "GTiff", overwrite = TRUE)
	
	# cross-validation
	universal_result_3 = krige.cv(pm~x+y, trainTable, sphFit, locations = ~x+y, nfold = 3)
	
	# Universal statis

	universal_cor = cor(universal_result_3$var1.pred,universal_result_3$observed)
	universal_rmse = sqrt(sum((universal_result_3$residual)^2)/nrow(universal_result_3))
	universal_re = sum(abs(universal_result_3$residual)/universal_result_3$observed)/nrow(universal_result_3)
	
	filename = uk_file
	samples = nrow(trainTable)
	r2 = universal_cor*universal_cor
	rmse = universal_rmse
	re = universal_re*100
	r2
	rmse
	re
	# rs = read.csv(cross_result_file, header=T, sep=",")
	# rs = data.frame(filename,sample,r2,rmse,re)
	# write.csv(rs,cross_result_file)
}

createKrigingImage_mi_1set = function(regressPm_file_t, regressPm_file_a, output_file){
	regressPm_mask_file_t = regressPm_file_t
	regressPm_mask_file_a = regressPm_file_a
	cross_result_file = "/home/lancer/Desktop/rs.csv"
	
	# ---------------------------input file 1 --------------------------------------
	pmRaster_t = raster(regressPm_mask_file_t)
	pm = values(pmRaster_t*scale_factor)
	# print(pm)
	corxy = coordinates(pmRaster_t)
	x = corxy[,'x']
	# print(x)
	y = corxy[,'y']
	totalCell = length(pmRaster_t)
	cell = c(1:totalCell)
	table_t = data.frame(cell, x, y, pm)
	
	#testTable=subset(table,pm<0)
	#trainTable=subset(table,pm>=0)
	trainTable_t = subset(table_t, !is.na(pm))
	# testTable_t = table_t
	# 
	pmRaster_a = raster(regressPm_mask_file_a)
	pm = values(pmRaster_a*scale_factor)
	# corxy_a = coordinates(pmRaster_a)
	# x_a = corxy_a[,'x']
	# y_a = corxy_a[,'y']
	# totalCell = length(pmRaster_a)
	# cell = c(1:totalCell)
	table_a = data.frame(cell, x, y, pm)
	tempTable_a = table_a
	# tempTable_a = table_a
	#testTable=subset(table,pm<0)
	#trainTable=subset(table,pm>=0)
	trainTable_a = subset(table_a, !is.na(pm))
	# print(testTable_a)
	# print(table_a)
	# trainTable <- trainTable_t
	# trainTable <- rbind(trainTable_t, trainTable_a) # input train table
	
	# print(trainTable)
	# testTable = newTable_t

	# count = 0
	for (i in 1:totalCell) {
		if (!is.na(table_t$pm[i]) && !is.na(table_a$pm[i])) {
			# print(c(i, trainTable_t$pm[i], trainTable_a$pm[i], " hihi"), collapse = " ")
			# print(i)
			tempTable_a$pm[i] = NA
			# tempTable_a <- tempTable_a[-c(i-count), ]
			# count = count + 1
			# print(nrow(tempTable_a))
			# print(c(i, trainTable_t$pm[i], trainTable_a$pm[i], "hihi", nrow(tempTable_a)), collapse = "  ")
		}
	}
	trainTable_a = subset(tempTable_a, !is.na(pm))
	trainTable = rbind(trainTable_t, trainTable_a) # input train table
	testTable = table_t # input test table 
	newTable = table_t # output table

	# print(table_t)
	# print(table_a)
	# print(tempTable_a)

	# ---------------------------------------------------------Kriging Core----------------------------------------------
	options(warn=1)
	auto_trainTable = trainTable
	coordinates(auto_trainTable) =~x+y
	
	auto_variogram = autofitVariogram(pm~1, auto_trainTable)

	auto_model = auto_variogram$var_model$model[2]
	auto_sill = auto_variogram$var_model$psill[2]
	auto_range = auto_variogram$var_model$range[2]
	
	#caculate variogram
	empiVario = variogram(pm~1,locations=~x+y,data=trainTable)
	
	sphModel = vgm(psill=auto_sill,model=auto_model,nugget=0,range=auto_range)		
	sphFit = fit.variogram(empiVario,sphModel)
	# sph fit
	# sill=min(empiVario$gamma)
	# sphModel=vgm(psill=sill,model="Sph",nugget=0,range=min(empiVario$dist))
	# sphModel=vgm(model="Sph",nugget=0,range=1)		
	# sphFit=fit.variogram(empiVario,sphModel)
	
	universal_result = krige(id = "pm", formula = pm~x+y, data = trainTable, newdata = testTable, model = sphFit, locations =~x+y)
	# print(trainTable)
	# print(table_t)
	# print(testTable_t)
	newTable[["pm"]] = universal_result[,3]
	
	universalPMRaster = pmRaster_t
	universalPMRaster[1:totalCell] = newTable$pm
	
	uk_file = str_replace(output_file, ".tif", "_mi_uk_AsOneDataset.tif")
	# uk_file = str_replace(regressPm_file,".tif","_uk.tif")
	writeRaster(universalPMRaster, filename = uk_file, format = "GTiff", overwrite = TRUE)
	
	# cross-validation
	universal_result_3 = krige.cv(pm~x+y, trainTable, sphFit, locations = ~x+y, nfold = 3)
	
	# Universal statis
	universal_cor = cor(universal_result_3$var1.pred,universal_result_3$observed)
	universal_rmse = sqrt(sum((universal_result_3$residual)^2)/nrow(universal_result_3))
	universal_re = sum(abs(universal_result_3$residual)/universal_result_3$observed)/nrow(universal_result_3)
	
	filename = uk_file
	samples = nrow(trainTable)
	r2 = universal_cor*universal_cor
	rmse = universal_rmse
	re = universal_re*100
	r2
	rmse
	re
	# rs = read.csv(cross_result_file, header=T, sep=",")
	# rs = data.frame(filename,sample,r2,rmse,re)
	# write.csv(rs,cross_result_file)
}


# --------------------------------------Test side-------------------------------------------------------------------

# createKrigingImage(file_test_merged, file_test_merged)
# createKrigingImage(file_test_unmerged, output_file_unmerged)

# --------------------------------------Option Lists----------------------------------------------------------------
option_1 = function() {
	fileLists = list.files(path_prod)
	for (file in fileLists) {
		# file = fileLists[1]
		# paste(c(path_prod, file, "/", file, SAA), collapse = "")
		input_file_SAA = paste(c(path_prod, file, "/", file, "_SAA", ".tif"), collapse = "")
		input_file_MLE = paste(c(path_prod, file, "/", file, "_MLE", ".tif"), collapse = "")
		input_file_WPC = paste(c(path_prod, file, "/", file, "_WPC", ".tif"), collapse = "")

		createKrigingImage(input_file_SAA, input_file_SAA)
		createKrigingImage(input_file_MLE, input_file_MLE)
		createKrigingImage(input_file_WPC, input_file_WPC)
	}	
}

option_2_5_6 = function() {
	fileLists1 = list.files(path_mod)
	fileLists2 = list.files(path_myd)
	for (file in fileLists1) {
		input_file = paste(c(path_mod, file, "/", file, ":", mean, ".tif"), collapse = "")
		output_file = paste(c(path_prod, substr(file, 10, 17), ":", data_set, "/", file, ":", mean, ".tif"), collapse = "")
		createKrigingImage(input_file, output_file)
	}

	for (file in fileLists2) {
		input_file = paste(c(path_myd, file, "/", file, ":", mean, ".tif"), collapse = "")
		output_file = paste(c(path_prod, substr(file, 10, 17), ":", data_set, "/", file, ":", mean, ".tif"), collapse = "")
		createKrigingImage(input_file, output_file)
	}
}

option_4_7_8 = function() {
	fileLists1 = list.files(path_mod)
	fileLists2 = list.files(path_myd)
	for (file in fileLists1) {
		input_file = paste(c(path_mod, file, "/", file, ":", mean, ".tif"), collapse = "")
		output_file = paste(c(path_prod, substr(file, 10, 17), ":", data_set, "/", file, ":", mean, ".tif"), collapse = "")
		createKrigingImage_mi(input_file, output_file)
	}

	for (file in fileLists2) {
		input_file = paste(c(path_myd, file, "/", file, ":", mean, ".tif"), collapse = "")
		output_file = paste(c(path_prod, substr(file, 10, 17), ":", data_set, "/", file, ":", mean, ".tif"), collapse = "")
		createKrigingImage_mi(input_file, output_file)
	}
}

option_3 = function() {
	fileLists1 = list.files(path_mod)
	fileLists2 = list.files(path_myd)
	fileLength = length(fileLists1)
	for (i in 1:fileLength) {
		file_t = fileLists1[i]
		file_a = fileLists2[i]
		input_file_t = paste(c(path_mod, file_t, "/", file_t, ":", mean, ".tif"), collapse = "")
		input_file_a = paste(c(path_myd, file_a, "/", file_a, ":", mean, ".tif"), collapse = "")
		output_file = paste(c(path_prod, substr(file_t, 10, 17), ":", data_set, "/", substr(file_t, 10, 17), ":", data_set, ".tif"), collapse = "")

		createKrigingImage_mi_1set(input_file_t, input_file_a, output_file)
	}
}
# -------------------------------------------main---------------------------------------------------------------
option_1()
option_2_5_6()
option_4_7_8()
option_3()