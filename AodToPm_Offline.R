# TODO: create PM image from aod and temp (PM regression)
# 
# Author: phamha
###############################################################################

#import library
library(gstat)
library(base)
library(RPostgreSQL)
library(stringr)
library(raster)
library(gdalUtils)
library(rgdal)
library(rPython)


host_name = '172.16.81.252'
database_name = 'apom'
user_name = 'postgres'
password = 'postgres'


mean_aod_mod = 0.366114584
abs_aod_mod = 1.029983261
mean_aod_myd = 0.410938839
abs_aod_myd = 1.098215224

mean_avg_temp_mod = 28.58782188
abs_avg_temp_mod = 12.02451107
mean_avg_temp_myd = 28.63081177
abs_avg_temp_myd = 12.06750096


res_folder_mod = "res/SatResampMOD04"
res_folder_myd = "res/SatResampMYD04"

prod_folder_mod = "prod/ProdMODPM"
prod_folder_myd = "prod/ProdMYDPM"

code_folder = "C:/"
#code_folder = "/var/www/html/MODIS/HaPV/MODIS_Quytrinh/"

met_folder = paste(code_folder,"MetTiff/",sep="")
shape_file = paste(code_folder,"BDNEN/VNM_adm0.shp",sep="")
tif2raster_file = paste(code_folder,"tif2rasref.py",sep="")
create_aqi_file = paste(code_folder,"MODIS_CLIP_PM_AQI.py",sep="")
create_png_file = paste(code_folder,"create_png.py",sep="")
create_aot_file = paste(code_folder,"aot_processing.py",sep="")
modis_log_file = paste(code_folder,"modis.log",sep="")
cross_result_file = paste(code_folder,"cross_kriging.csv",sep="")

get_time_query = "select aqstime from %s where filename like "
mod_query = "SELECT distinct mod04.aqstime, mod04.filename,mod04.filepath,mod07.filename as temp_filename,mod07.filepath as temp_filepath FROM res.satresampmod04 as mod04 inner join res.satresampmod07temperature as mod07 ON (mod04.aqstime = mod07.aqstime) where mod07.filename like'%_T_10km%' and mod04.aqstime <='2013-12-26 00:00:00'"
insert_mod_query = "INSERT INTO prodpm.prodmodispm_vn_collection0(aqstime, rasref, filename, filepath, gridid,pmid,max,min,avg, type,sourceid) VALUES ('"

#Regression function
regress_predict = function(sate_data,aod,avg_temp){
	if(sate_data=="mod"){
		pm25 = 21.44446906 * aod + (-26.98361769)*avg_temp + 25.28728856
	}else{
		pm25 = 27.4005404 * aod + (-18.90869037)*avg_temp + 18.99322277
	}
	
	return(pm25)
}
#get data from DB
getDataFromDB <- function(sql_command) {
	out = tryCatch(
			{
				driver = dbDriver("PostgreSQL")
				connect = dbConnect(driver,dbname = database_name,host = host_name,port=5432,user = user_name,password= password)
				rs = dbSendQuery(connect,sql_command)
				data=fetch(rs,n=-1)
				#cat("connect to DB sucessful",file="C:/test.txt",sep="\n",append=TRUE)
				dbDisconnect(connect)
				dbUnloadDriver(driver)
				return (data)	
			},
			error=function(cond) {
				cat("Error:",cond$message,"\n",file = modis_log_file,sep="",append=TRUE)	
				return(NA)		   
			},
			warning=function(cond) {
				cat("warning:",cond$message,"\n",file = modis_log_file,sep="",append=TRUE)
				return(NA)
			},
			finally={
				#dbDisconnect(connect)
				#dbUnloadDriver(driver)
				#print("done")
			} 
	)    
	return(out)
}
#insert data to DB
insertDataToDB <- function(sql_command) {
	out = tryCatch(
			{
				driver = dbDriver("PostgreSQL")
				connect = dbConnect(driver,dbname = database_name,host = host_name,port=5432,user = user_name,password= password)
				rs = dbSendQuery(connect,sql_command)
				dbDisconnect(connect)
				dbUnloadDriver(driver)
				return (1)	
			},
			error=function(cond) {
				cat("Error:",cond$message,"\n",file = modis_log_file,sep="",append=TRUE)	
				return (NA)
			},
			warning=function(cond) {
				cat("warning:",cond$message,"\n",file = modis_log_file,sep="",append=TRUE)
				return (NA)
			},
			finally={
				#dbDisconnect(connect)
				#dbUnloadDriver(driver)
				#print("done")
			} 
	)  
	return(out)

}

#Create Kriging image from regression image
createKrigingImage = function(regressPm_file){
	
	regressPm_mask_file = str_replace(regressPm_file,".tif","_mask.tif")
	file.copy(regressPm_file,regressPm_mask_file)
	gdal_rasterize(shape_file,regressPm_mask_file,b=1,i=TRUE,burn=-9999,l="VNM_adm0")
	
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
	uk_file = str_replace(regressPm_file,"rg.tif","uk.tif")
	writeRaster(universalPMRaster,filename=uk_file,format="GTiff",overwrite=TRUE)
	gdal_rasterize(shape_file,uk_file,b=1,i=TRUE,burn=-9999,l="VNM_adm0")
	
	#set n/a value
	new_uk_raster = raster(uk_file)
	new_uk_value = values(new_uk_raster)
	new_uk_value[new_uk_value==-9999]<-NA
	new_uk_value[new_uk_value<0]<-0
	new_uk_raster[1:totalCell] = new_uk_value

	writeRaster(new_uk_raster,filename=uk_file,format="GTiff",overwrite=TRUE)
	
	
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
#Create regression and kriging images and insert to DB
create_pm_image = function(sate_data,aod_file,source_id){

	if(sate_data=="mod"){
		type = 0
		time_query = sprintf(get_time_query, "res.satresampmod04")
		res_folder = res_folder_mod
		prod_folder = prod_folder_mod
		min_aod = mean_aod_mod
		max_aod = abs_aod_mod
		min_temp = mean_avg_temp_mod
		max_temp = abs_avg_temp_mod
		
	}else{
		type = 1
		time_query = sprintf(get_time_query, "res.satresampmyd04")
		res_folder = res_folder_myd
		prod_folder = prod_folder_myd
		min_aod = mean_aod_myd
		max_aod = abs_aod_myd
		min_temp = mean_avg_temp_myd
		max_temp = abs_avg_temp_myd
	}
	
	# get aqstime base on file name
	file_name = basename(aod_file)
	file_name = str_replace(file_name,".tif","")

	time_query = paste(time_query,"'",file_name,"%'",sep="")
	data = getDataFromDB(time_query)
	if(!is.na(data)){
				
		mod04_aqstime = data$aqstime[1]
		aqstime = strptime(mod04_aqstime,format="%Y-%m-%d %H:%M:%S")
		aqstime = aqstime + 25200	
		
		month = format.Date(aqstime,"%m")
		year = format.Date(aqstime,"%Y")
		
		# crop aod file base on shap file
		aod_mask_file = str_replace(aod_file,".tif","_mask.tif")
		file.copy(aod_file,aod_mask_file)
		
		gdal_rasterize(shape_file,aod_mask_file,b=1,i=TRUE,burn=-9999,l="VNM_adm0")
		aod_dataset = raster(aod_mask_file)
		aod_dataset[aod_dataset[] == -9999] <- NA
		
		if(file.exists(aod_mask_file)){
			file.remove(aod_mask_file)
		} 
		
		#log to file
		mask_str = "[ %s ] Mask image [ %s ] sucessful"
		mask_log = sprintf(mask_str, Sys.time(),aod_file)
		cat(mask_log,"\n",file = modis_log_file,sep="",append=TRUE)
		
	
		aod_data = values(aod_dataset)
		aod_data = aod_data * 0.00100000004749745
		
		corxy = coordinates(aod_dataset)
		x = corxy[,'x']
		y = corxy[,'y']
				
		avg_temp_file  = paste(met_folder,"temp",as.numeric(month),".tif",sep="")
		avg_temp_dataset  =  raster(avg_temp_file)
		avg_temp_data  = values(avg_temp_dataset) 
	
		# chuan hoa aod va temp
		aod_data = (aod_data - min_aod)/max_aod
		avg_temp_data = (avg_temp_data - min_temp)/max_temp
		
		#hoi quy gia tri pm
		pm25 = regress_predict(sate_data,aod_data,avg_temp_data)
		
		total_pixel = sum(!is.na(aod_data))
		ratio = total_pixel/2024*100
		print(paste("Pixel:",total_pixel,"Cloud ratio:",ratio,sep=" "))
		
		############## CREATE REGRESSION IMAGES
		
		# Remove out of range pixel
		table = data.frame(x,y,aod_data,avg_temp_data,pm25)
		table$pm25[table$aod_data<-1|table$aod_data>1|table$avg_temp_data<-1|table$avg_temp_data>1]<-NA
		
		# save regression images
		og_raster = aod_dataset
		totalCell = ncell(og_raster)
		og_raster[1:totalCell] = table$pm25
		
		# edit file name
		#mod04
		pm_file = str_replace(aod_file,".hdf_DT_10km","")
		#myd04
		pm_file = str_replace(aod_file,".hdf_DB_10km","")
		pm_file = str_replace(aod_file,".tif","_rg.tif")
		pm_file = str_replace(pm_file,res_folder,prod_folder)

		#create output path
		out_path = dirname(pm_file)
		dir.create(path=out_path,showWarnings = FALSE,recursive = TRUE,mod="777")
		
		writeRaster(og_raster,filename=pm_file,format="GTiff",overwrite=TRUE)
		#gdal_rasterize(shape_file,pm_file,b=1,i=TRUE,burn=-9999,l="VNM_adm0")
		
		# write to log file
		mask_str = "[ %s ] create regression image [ %s ] sucessful"
		mask_log = sprintf(mask_str, Sys.time(),pm_file)
		cat(mask_log,"\n",file = modis_log_file,sep="",append=TRUE)
		
		#create pm image
		createKrigingImage(pm_file)
		print ("Create Kriging image good!");
		
		uk_file = str_replace(pm_file,"rg.tif","uk.tif")
		
		# write finish to log file
		mask_str = "[ %s ] create kriging image [ %s ] sucessful"
		mask_log = sprintf(mask_str, Sys.time(),uk_file)
		cat(mask_log,"\n",file = modis_log_file,sep="",append=TRUE)
		
		python.assign("raster_file",uk_file)
		python.load(tif2raster_file)
		raster_ref = python.get("raster_ref")
		
		uk_raster = raster(uk_file)
		uk_value = values(uk_raster)
		uk_value = uk_value[uk_value!=-9999]
		max_value = max(uk_value,na.rm = TRUE)
		min_value = min(uk_value,na.rm = TRUE)
		avg_value = mean(uk_value,na.rm = TRUE)
		
		start_index = regexpr("apom/prod",uk_file)
		mid_index = regexpr("M[^M]*$",uk_file)
		end_index = nchar(uk_file)	
		uk_file_path = substr(uk_file,start_index,mid_index-1)
		uk_file_name = substr(uk_file,mid_index,end_index)
		
		aqstime2 = aqstime - 25200
		query = paste(insert_mod_query,aqstime2,"'::timestamp, '",raster_ref,"'::raster, '",uk_file_name,"', '",uk_file_path,"', 1, 1, ",max_value,", ",min_value,", ",avg_value,", ",type,", ",source_id,")",sep="")
		
		#print(query)
		#insert pm images to database
		out = insertDataToDB(query)
		if(!is.na(out)){
			print ("Insert to database good!");
			mask_str = "[ %s ] insert kriging image [ %s ] to DB sucessful"
			mask_log = sprintf(mask_str, Sys.time(),uk_file)
			cat(mask_log,"\n",file = modis_log_file,sep="",append=TRUE)
			
		
		}else{
			print ("Can not insert to database");
		}


		############# END CODE
		
		if(ratio>=30){
			# write ratio to log file
			mask_str = "[ %s ] data ratio is [ %s ]"
			mask_log = sprintf(mask_str, Sys.time(),ratio)
			cat(mask_log,"\n",file = modis_log_file,sep="",append=TRUE)
			# create regression image
	
			# end code
			
			
		}else{
			# write ratio to log file
			mask_str = "[ %s ] data ratio is [ %s ]"
			mask_log = sprintf(mask_str, Sys.time(),ratio)
			cat(mask_log,"\n",file = modis_log_file,sep="",append=TRUE)
			# write finish to log file
			mask_str = "[ %s ] Process file name [ %s ] finish"
			mask_log = sprintf(mask_str, Sys.time(),aod_file)
			cat(mask_log,"\n",file = modis_log_file,sep="",append=TRUE)
		}
	}
	
			
}


# Test example
sat_data = "mod"
source_id = 0

#aod_file = "/apom_data/apom/res/SatResampMOD04/2015/MOD04_L2.A2015107.0310.051.2015107141007/MOD04_L2.A2015107.0310.051.2015107141007.hdf_DT_10km.tif"

# mod/myd , aot file, temp file
# Test command
# create_pm_image("mod","linear","4np",aod_file,temp_file, source_id)


#insertDataToDB(mod_query)
#data = insertDataToDB(mod_query)
#total_record = nrow(data)
#print(total_record)



#for(i in 1:total_record){

#	aod_filename = str_trim(data$filename[i])
#	aod_path = str_trim(data$filepath[i])
#	aod_file = paste(data_folder,aod_path,aod_filename,sep = "")
	
	
#	temp_filename = str_trim(data$temp_filename[i])	
#	temp_path = str_trim(data$temp_filepath[i])
#	temp_file = paste(data_folder,temp_path,temp_filename,sep = "")
	
#	create_pm_image("mod","linear","4np",aod_file,temp_file)
	

#}



