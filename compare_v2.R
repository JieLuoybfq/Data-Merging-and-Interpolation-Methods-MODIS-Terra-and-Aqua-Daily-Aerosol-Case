library(base)
library(raster)
library(gstat)
library(RPostgreSQL)
library(hydroGOF)
library(stringr)


# DB = "fimo"
# HOST ="192.168.0.4"
# PORT = 5432
# USER = "rasdaman"
# PASS = "rasdaman"

# DB = "sinhvien"
# HOST ="112.137.129.222"
# PORT = 1188
# USER = "sinhvien"
# PASS = "sinhvien"


DB = "test"
HOST ="localhost"
PORT = 5432
USER = "postgres"
PASS = "postgres"

dr=dbDriver("PostgreSQL")

path = "/media/lancer/01D124DD7D476BA0/apom/prod/"
setwd(path)

path_SAA = "/media/lancer/01D124DD7D476BA0/apom/prod/A2015%s:Aerosol_Optical_Depth_Land_Ocean/A2015%s:Aerosol_Optical_Depth_Land_Ocean_SAA.tif"
path_MLE = "/media/lancer/01D124DD7D476BA0/apom/prod/A2015%s:Aerosol_Optical_Depth_Land_Ocean/A2015%s:Aerosol_Optical_Depth_Land_Ocean_MLE.tif"
path_WPC = "/media/lancer/01D124DD7D476BA0/apom/prod/A2015%s:Aerosol_Optical_Depth_Land_Ocean/A2015%s:Aerosol_Optical_Depth_Land_Ocean_WPC.tif"
path_SAA_uk = "/media/lancer/01D124DD7D476BA0/apom/prod/A2015%s:Aerosol_Optical_Depth_Land_Ocean/A2015%s:Aerosol_Optical_Depth_Land_Ocean_SAA_i_uk.tif"
path_MLE_uk = "/media/lancer/01D124DD7D476BA0/apom/prod/A2015%s:Aerosol_Optical_Depth_Land_Ocean/A2015%s:Aerosol_Optical_Depth_Land_Ocean_MLE_i_uk.tif"
path_WPC_uk = "/media/lancer/01D124DD7D476BA0/apom/prod/A2015%s:Aerosol_Optical_Depth_Land_Ocean/A2015%s:Aerosol_Optical_Depth_Land_Ocean_WPC_i_uk.tif"
path_mi_SAA = "/media/lancer/01D124DD7D476BA0/apom/prod/A2015%s:Aerosol_Optical_Depth_Land_Ocean/A2015%s:Aerosol_Optical_Depth_Land_Ocean_mi_uk_SAA.tif"
path_uk_SAA = "/media/lancer/01D124DD7D476BA0/apom/prod/A2015%s:Aerosol_Optical_Depth_Land_Ocean/A2015%s:Aerosol_Optical_Depth_Land_Ocean_i_uk_SAA.tif"
path_miAs1 = "/media/lancer/01D124DD7D476BA0/apom/prod/A2015%s:Aerosol_Optical_Depth_Land_Ocean/A2015%s:Aerosol_Optical_Depth_Land_Ocean_mi_uk_AsOneDataset.tif"

testpath = "/media/lancer/01D124DD7D476BA0/apom/prod/A2015001:Aerosol_Optical_Depth_Land_Ocean/A2015001:Aerosol_Optical_Depth_Land_Ocean_SAA.tif"

# testQuery1 = "SELECT aqstime
# 			FROM org.grdaeraot_data 
# 			WHERE aqstime >='2015-01-01 00:00:00' AND aqstime <= '2016-01-01 00:00:00' AND stationid = %s"
	
timeQuery = "SELECT DATE(aqstime) AS a_date, avg(aod_550)
			FROM aeronet 
			WHERE aqstime >='2015-01-01 00:00:00' AND aqstime <= '2016-01-01 00:00:00'
			GROUP BY a_date
   			ORDER BY a_date;"

# stationQuery = "SELECT id, st_asText(location) 
# 				FROM public.grdstation
# 				WHERE id = %s"

# testQuery2 = "SELECT aqstime FROM org.grdaeraot_data where stationid = 70 limit 10;"


con = dbConnect(dr, dbname=DB, host=HOST, port=PORT, user=USER, password=PASS)

convertGDayToJDay = function(year, month, day){
	dayList = c(1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)
	if (year %% 4 == 0){
		date = dayList[month] + day 
	} else {
		date = dayList[month] + day - 1
	}
	return(date)
}

# testquery = "SELECT aqstime FROM org.grdaeraot_data WHERE (aqstime > '2014-12-31 00:00:00'
#  			AND aqstime < '2016-01-01 00:00:00') limit 10;"

# dbExistsTable(con, c("org","grdaeraot_data"))

# table <- dbGetQuery(con, testquery)
# table <- dbGetQuery(con, timeQuery)

# print(table)
# print(table[1, ])
# a = table[1, ]

# print(table)
# testQuery2 = "SELECT aqstime FROM apom.satresampviirs where filename like '%"
# a = paste(testQuery2, "ahihi", "'%", sep="")

# old <- "abcefg"
# a = gsub('^([a-z]{4})([a-z]{5})$', '\\1j\\2', old)
# b = gsub('^(.{3})(.*)$', '\\1d\\2', old)

# sprintf("aass %s adasda %s  casd %s", "hihi", "1", "1")
# print(a)
# print(b)
# timeQuery = "SELECT aqstime FROM apom.satresampviirs where filename like '%"
# selectStr="SELECT stationid,name,st_asText(location),avg(pm25) as avg_pm FROM apom.grdpmhiscem_data,public.grdstation WHERE grdpmhiscem_data.stationid = grdstation.id AND grdstation.id ="
# andStr="' and '"
# betweenStr=" AND  aqstime between '"
# groupStr="'  group by stationid,name,location having avg(pm25) > 0"


# asqTime4 = substr(record[4,1],1,30)
# print(asqTime4)

# stationList = c(68, 70, 71, 72)
# stationList = c(70)

# correl_result = data.frame()

# for (station in stationList) {
	# print(station)
	# timeQuery = sprintf(timeQuery, station)
resultSet1 = dbSendQuery(con, timeQuery)
record1 = fetch(resultSet1, n=-1)
	# print(record1)
numberRow = nrow(record1)
print(numberRow)
	# aQuery = sprintf(aerosolQuery, station)
	# resultSet2 = dbSendQuery(con, aQuery)
	# record2 = fetch(resultSet2)

	# sQuery = sprintf(stationQuery, station)
	# resultSet3 = dbSendQuery(con, sQuery)
	# record3 = fetch(resultSet3)
	# locationStr = record3[1,2]
	# print(locationStr)
	# index = regexpr(" ",locationStr)[1]
	# print(index)
	# xLocation = substr(locationStr,7,index-1)
	# yLocation = substr(locationStr,index+1,nchar(locationStr)-1)

xLocation = 105.73
yLocation = 9.28

# xLocation = 9.28
# yLocation = 105.73

	# print(record3)
result_dataframe = data.frame()

for (i in 1:numberRow) {
	aqsTime = substr(record1[i,1],1,10)
	print(aqsTime)
	myTime = strptime(aqsTime,format="%Y-%m-%d")
	aqsYear = format.Date(myTime,"%Y")
	aqsYear = as.numeric(aqsYear)
	aqsMonth = format.Date(myTime,"%m")
	aqsMonth = as.numeric(aqsMonth)
	aqsDay = format.Date(myTime,"%d")
	aqsDay = as.numeric(aqsDay)
	aqsDate = convertGDayToJDay(aqsYear, aqsMonth, aqsDay)
		if (aqsDate>0 && aqsDate<10){
		format_aqsDate = paste("00", aqsDate, sep="")
	} else if (aqsDate>=10 && aqsDate<100) {
		format_aqsDate = paste("0", aqsDate, sep="")
	} else if (aqsDate>=100) {
		format_aqsDate = aqsDate
	}

	fileRaster = raster(sprintf(path_SAA, format_aqsDate, format_aqsDate))
	value1 = extract(fileRaster, cbind(xLocation, yLocation))
	# print(value1)
	fileRaster = raster(sprintf(path_MLE, format_aqsDate, format_aqsDate))
	value2 = extract(fileRaster, cbind(xLocation, yLocation))

	fileRaster = raster(sprintf(path_WPC, format_aqsDate, format_aqsDate))
	value3 = extract(fileRaster, cbind(xLocation, yLocation))

	fileRaster = raster(sprintf(path_SAA_uk, format_aqsDate, format_aqsDate))
	value4 = extract(fileRaster, cbind(xLocation, yLocation))
	# print(value4)
	fileRaster = raster(sprintf(path_MLE_uk, format_aqsDate, format_aqsDate))
	value5 = extract(fileRaster, cbind(xLocation, yLocation))

	fileRaster = raster(sprintf(path_WPC_uk, format_aqsDate, format_aqsDate))
	value6 = extract(fileRaster, cbind(xLocation, yLocation))

	filenames = Sys.glob(file.path(paste0("A2015", format_aqsDate, ":Aerosol_Optical_Depth_Land_Ocean"), paste0("MOD08_D3.A2015", format_aqsDate, "*_mi_uk.tif")))
	fileRaster = raster(filenames[1])
	value7 = extract(fileRaster, cbind(xLocation, yLocation))

	filenames = Sys.glob(file.path(paste0("A2015", format_aqsDate, ":Aerosol_Optical_Depth_Land_Ocean"), paste0("MYD08_D3.A2015", format_aqsDate, "*_mi_uk.tif")))
	fileRaster = raster(filenames[1])
	value8 = extract(fileRaster, cbind(xLocation, yLocation))

	filenames = Sys.glob(file.path(paste0("A2015", format_aqsDate, ":Aerosol_Optical_Depth_Land_Ocean"), paste0("MOD08_D3.A2015", format_aqsDate, "*_i_uk.tif")))
	fileRaster = raster(filenames[1])
	value9 = extract(fileRaster, cbind(xLocation, yLocation))

	filenames = Sys.glob(file.path(paste0("A2015", format_aqsDate, ":Aerosol_Optical_Depth_Land_Ocean"), paste0("MYD08_D3.A2015", format_aqsDate, "*_i_uk.tif")))
	fileRaster = raster(filenames[1])
	value10 = extract(fileRaster, cbind(xLocation, yLocation))

	fileRaster = raster(sprintf(path_uk_SAA, format_aqsDate, format_aqsDate))
	value11 = extract(fileRaster, cbind(xLocation, yLocation))

	fileRaster = raster(sprintf(path_mi_SAA, format_aqsDate, format_aqsDate))
	value12 = extract(fileRaster, cbind(xLocation, yLocation))

	fileRaster = raster(sprintf(path_miAs1, format_aqsDate, format_aqsDate))
	value13 = extract(fileRaster, cbind(xLocation, yLocation))

	time = aqsTime
	SAA = value1
	MLE = value2
	WPC = value3
	SAA_uk = value4
	MLE_uk = value5
	WPC_uk = value6
	MOD_mi = value7
	MYD_mi = value8
	MOD_uk = value9
	MYD_uk = value10
	uk_SAA = value11
	mi_SAA = value12
	miAs1 = value13
	aod_550 = record1[i, 2]
	# print(aod_550)
	temp_dataframe=data.frame(time, SAA, MLE, WPC, SAA_uk, MLE_uk, WPC_uk, MOD_mi, MYD_mi, MOD_uk, MYD_uk, uk_SAA, mi_SAA, miAs1, aod_550)	
	result_dataframe = rbind(result_dataframe,temp_dataframe)
}
# print(result_dataframe)
write.csv(result_dataframe, file="bac_lieu.csv")







	# inputPath = path
	# listPath = list.files(path = inputPath,pattern="_rg.tif$",full.names = FALSE,recursive=TRUE)
	# number_char = nchar(listPath[1])
	# listFile = substr(listPath,6,number_char - 7)
	# listyear = substr(listPath,1,4)
	# listSize = length(listFile)
	
	# listTime=c(1:listSize)
	# result_dataframe=data.frame()
	
	# for(i in 1:listSize){
	# 	fileName=listFile[i]
		
	# 	# ogFile=paste(inputPath,"/",listyear[i],"/",fileName,"_rg.tif",sep="")
	# 	# ukFile=paste(inputPath,"/",listyear[i],"/",fileName,"_uk.tif",sep="")
	
	# 	ogRaster=raster(ogFile)
	# 	ukRaster=raster(ukFile)
	
	# 	qr=paste(timeQuery,fileName,"%'",sep="")
	# 	resultSet=dbSendQuery(con,qr)
	# 	record=fetch(resultSet,n=1)
	# 	asqTime=substr(record[1,1],1,30)
	# 	myTime=strptime(asqTime,format="%Y-%m-%d %H:%M:%S")
		
	# 	#add 7h
	# 	myTime=myTime+25200
		
	# 	startTime=myTime-1800
	# 	endTime=myTime+1800
		
	# 	aqsMonth=format.Date(myTime,"%m")
	# 	aqsYear=format.Date(myTime,"%Y")
		
	# 	selectQuery=paste(selectStr,station,betweenStr,startTime,andStr,endTime,groupStr,sep="")
	# 	pmRs=dbSendQuery(con,selectQuery)
	# 	pmRecord = fetch(pmRs,n=-1)
	# 	numberRow=nrow(pmRecord)
	# 	if(numberRow>0){
		
	# 		locationStr=pmRecord[1,3]
	# 		index=regexpr(" ",locationStr)[1]
	# 		xLocation=substr(locationStr,7,index-1)
	# 		yLocation=substr(locationStr,index+1,nchar(locationStr)-1)
				
	# 		ogValue=extract(ogRaster,cbind(as.numeric(xLocation),as.numeric(yLocation)))
			
	# 		## ukValue=extract(ukRaster,cbind(as.numeric(xLocation),as.numeric(yLocation)))
	# 		ukValue=extract(ukRaster,cbind(as.numeric(xLocation),as.numeric(yLocation)),buffer=24000,fun=mean)
				
	# 		pmRecord$ogColumn=ogValue
	# 		pmRecord$ukColumn=ukValue
			
	# 		pmRecord$aqstime=myTime
	# 		pmRecord$aqsyear=aqsYear
	# 		pmRecord$aqsmonth=aqsMonth
						
	# 		result_dataframe = rbind(result_dataframe,data.frame(pmRecord))
	# 	}	
	# }
	# attach(result_dataframe)
	# number_row = nrow(result_dataframe)
	
	# u_cor=cor(avg_pm,ukColumn)
	# u_r2=u_cor*u_cor
	# u_rmse=sqrt(sum((ukColumn-avg_pm)^2)/number_row)
	# u_re=(sum(abs(ukColumn-avg_pm)/avg_pm)/number_row)*100
	
	# u_mfb = (2*sum((ukColumn-avg_pm)/(avg_pm+ukColumn)*100))/number_row
	# u_mfe = (2*sum(abs(ukColumn-avg_pm)/(ukColumn+avg_pm)*100))/number_row
	
	# correl_result= rbind(correl_result,data.frame(station,number_row,u_r2,u_rmse,u_re,u_mfb,u_mfe))
	
	# outFile=paste(inputPath,"/station",station,".csv",sep="")
	# write.csv(result_dataframe,file=outFile)
	# print(paste("Finish",station))
# }

# outFile=paste(inputPath,"/corel_time.csv",sep="")
# write.csv(correl_result,file=outFile)

# print("Finish All")





