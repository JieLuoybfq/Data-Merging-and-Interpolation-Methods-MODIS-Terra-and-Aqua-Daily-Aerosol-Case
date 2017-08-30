# TODO: Add comment
# 
# Author: broken
###############################################################################
library(raster)
library(base)
library(gstat)
library(RPostgreSQL)
library(hydroGOF)
library(stringr)
dr=dbDriver("PostgreSQL")

path= "C:/Users/forever/Desktop/NPP01/"

DB = "fimo"
HOST ="192.168.0.4"
PORT = 5432
USER = "rasdaman"
PASS = "rasdaman"


con=dbConnect(dr,dbname=DB,host=HOST,port=5432,user=USER,password=PASS)
timeQuery = "SELECT aqstime FROM apom.satresampviirs where filename like '%"
selectStr="SELECT stationid,name,st_asText(location),avg(pm25) as avg_pm 
		FROM apom.grdpmhiscem_data, public.grdstation 
		WHERE grdpmhiscem_data.stationid = grdstation.id AND grdstation.id ="
andStr="' and '"
betweenStr=" AND aqstime between '"
groupStr="'  group by stationid,name,location having avg(pm25) > 0"

correl_result = data.frame()
for (station in 1:6) {
	inputPath = path
	listPath = list.files(path = inputPath,pattern="_rg.tif$",full.names = FALSE,recursive=TRUE)
	number_char = nchar(listPath[1])
	listFile = substr(listPath,6,number_char - 7)
	listyear = substr(listPath,1,4)
	listSize = length(listFile)
	
	listTime=c(1:listSize)
	result_dataframe=data.frame()
	
	for(i in 1:listSize){
		fileName=listFile[i]
		
		ogFile=paste(inputPath,"/",listyear[i],"/",fileName,"_rg.tif",sep="")
		ukFile=paste(inputPath,"/",listyear[i],"/",fileName,"_uk.tif",sep="")
	
		ogRaster=raster(ogFile)
		ukRaster=raster(ukFile)
	
		qr=paste(timeQuery,fileName,"%'",sep="")
		resultSet=dbSendQuery(con,qr)
		record=fetch(resultSet,n=1)
		asqTime=substr(record[1,1],1,30)
		myTime=strptime(asqTime,format="%Y-%m-%d %H:%M:%S")
		
	
		#add 7h
		myTime=myTime+25200
		
		startTime=myTime-1800
		endTime=myTime+1800
		
		aqsMonth=format.Date(myTime,"%m")
		aqsYear=format.Date(myTime,"%Y")
		
		selectQuery=paste(selectStr,station,betweenStr,startTime,andStr,endTime,groupStr,sep="")
		pmRs=dbSendQuery(con,selectQuery)
		pmRecord=fetch(pmRs,n=-1)
		numberRow=nrow(pmRecord)
		if(numberRow>0){
			locationStr=pmRecord[1,3]
			index=regexpr(" ",locationStr)[1]
			xLocation=substr(locationStr,7,index-1)
			yLocation=substr(locationStr,index+1,nchar(locationStr)-1)
				
			ogValue=extract(ogRaster,cbind(as.numeric(xLocation),as.numeric(yLocation)))
			
			## ukValue=extract(ukRaster,cbind(as.numeric(xLocation),as.numeric(yLocation)))
			ukValue=extract(ukRaster,cbind(as.numeric(xLocation),as.numeric(yLocation)),buffer=24000,fun=mean)
				
			pmRecord$ogColumn=ogValue
			pmRecord$ukColumn=ukValue
			
			pmRecord$aqstime=myTime
			pmRecord$aqsyear=aqsYear
			pmRecord$aqsmonth=aqsMonth
						
			result_dataframe = rbind(result_dataframe,data.frame(pmRecord))
		
		}
		
	}
	attach(result_dataframe)
	number_row = nrow(result_dataframe)
	
	u_cor=cor(avg_pm,ukColumn)
	u_r2=u_cor*u_cor
	u_rmse=sqrt(sum((ukColumn-avg_pm)^2)/number_row)
	u_re=(sum(abs(ukColumn-avg_pm)/avg_pm)/number_row)*100
	
	u_mfb = (2*sum((ukColumn-avg_pm)/(avg_pm+ukColumn)*100))/number_row
	u_mfe = (2*sum(abs(ukColumn-avg_pm)/(ukColumn+avg_pm)*100))/number_row
	
	
	correl_result= rbind(correl_result,data.frame(station,number_row,u_r2,u_rmse,u_re,u_mfb,u_mfe))
	
	outFile=paste(inputPath,"/station",station,".csv",sep="")
	write.csv(result_dataframe,file=outFile)
	print(paste("Finish",station))
	
}

outFile=paste(inputPath,"/corel_time.csv",sep="")
write.csv(correl_result,file=outFile)

print("Finish All")




