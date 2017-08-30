import os, sys
import shutil
import gdal
import subprocess
import psycopg2
import glob
import shutil
from gdalconst import *
from os.path import basename
from datetime import datetime
from shapely.wkt import dumps, loads
from shapely.geometry import box

#connect DB
#~ dbname='template_postgis' 
#~ user='postgres' 
#~ host='localhost' 
#~ password='123456'
host='112.137.129.222' 
dbname='apom2' 
user='postgres' 
password='postgres'
port="5432"

#log filename
log_file_org="SatOrgMOD04_3K.txt"
log_file_resamp="SatResampMOD04_3K.txt"
log_Day=datetime.strftime(datetime.now(), '%Y-%m-%d')+".txt"
logFolder="/home/phamha/Desktop/apom/log"

#info to insert Org
inputFolder="/home/phamha/Desktop/MOD04_3K/2015" #=============*****************
#apom_data/apom2/MOD04_3K
#tempFolder="/media/Document/sathandle" #path folder before 'apom/org, res'  Folder

org_Folder="/home/phamha/Desktop/apom/org/SatOrgMOD04_3K"
satType="MOD04_3K"
tableName_Org="org.satorgMOD04_3k"

#info to insert resample
mer_Folder="/home/phamha/Desktop/" #combine with filepath get from DB
aod_format_resample = "_DT_3km.tif"
resample_folder= "/home/phamha/Desktop/apom/res/SatResampMOD04_3K"
aod_band_resample = '":mod04:Optical_Depth_Land_And_Ocean'
tableName_Resamp="res.satresampMOD04_3k"

#Other info to insert DB
projection=1
typeid=1 #or sourceid
collection=6 

#res 3km
resx=0.0351877397873154
resy=-0.0351877397873154
vietnam_bounds = box(100.1, 25.6, 111.8, 6.4)

#insert Query if not, else update
insert_satOrg = "UPDATE {0} SET sourceid={1}, aqstime='{2}', filename='{3}', path='{4}', corner='{5}', updatetime='{6}',collection={7} WHERE filename='{3}';  \
INSERT INTO {0}( sourceid, aqstime, filename, path, corner, updatetime,collection) SELECT {1}, '{2}', '{3}', '{4}', '{5}', '{6}',{7} WHERE NOT EXISTS \
(SELECT 1 FROM {0} WHERE filename='{3}')"

SelectFromOrg_query = "SELECT path,aqstime, ST_AsText(corner) as corner FROM {0} WHERE filename='{1}'"

insert_satResamp = "UPDATE {0} SET  aqstime='{1}', rasref3='{2}',filename='{3}', filepath='{4}', projection={5}, type={6}, updatetime='{7}', collection={8} WHERE filename='{3}';\
INSERT INTO {0}( aqstime, rasref3, filename, filepath, projection, type,updatetime,collection) SELECT '{1}', '{2}'::raster, '{3}', '{4}', {5}, {6},'{7}',{8} WHERE NOT EXISTS \
(SELECT 1 FROM {0} WHERE filename='{3}')"

def connect():
	dateNow=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
	conn=None
	try:
		conn = psycopg2.connect("dbname="+dbname+ " user="+user+ " host="+host +" password="+password+" port="+port)
	except psycopg2.DatabaseError, e:
		print e
		if not os.path.exists(logFolder):
			os.makedirs(logFolder)
		logrow= "["+dateNow+"] ERROR %s" % e 	
		logfile_day=logFolder+"/"+log_Day
		writeLog(logfile_day,logrow)
	return conn
	
def index(inputFolder,org_Folder,satType):
	#filePath = inputFolder+"/*/*.hdf"
	filePath = inputFolder+"/*.hdf"
	arrFiles1=glob.iglob(filePath)
	arrFiles=sorted(arrFiles1)
	for file in arrFiles:
		print file
		InsertImageInfo(file)
		resample_Image(file)
		print "=========END==================="
	
def InsertImageInfo(file):
	#file path folder
	folderName=os.path.splitext(os.path.basename(file))[0]
	#get year folder merge with pathOrg
	splitYear=folderName.split('.')
	yearFolder=str(splitYear[1][1:5])
	folderPath = os.path.join(org_Folder,yearFolder, folderName)
	
	#create folderPath
	if not os.path.exists(folderPath):
		os.makedirs(folderPath)
		
	#copy file to new directory
	fileName=os.path.basename(file)
	newPath=os.path.join(folderPath, fileName)
	oldPath=file
	if not os.path.isfile(newPath):
		shutil.copy2(oldPath,newPath) 
		
	#create image thumbnail
	folderFilePath=os.path.join(folderPath, folderName)
	createImageThumbnail(satType,newPath,folderFilePath)

	#get metadata from file _convert.tif
	fileTif=folderFilePath+"_convert.tif"
	#create _metadata.txt from gdalinfo
	os.system("gdalinfo " +fileTif+ " >" +folderFilePath+ "_metadata.txt")

	#write corner file
	fileMetadata=folderFilePath+ "_metadata.txt"
	WriteCornerFile(fileMetadata,folderFilePath)
	
	#delete file temp.tif +.xml
	os.chdir(folderPath)
	files=glob.glob('*temp.tif')
	files.extend(glob.glob('*.xml'))
	for perFile in files:
		os.unlink(perFile)
	
	#Insert to DB
	getAndInsertInfo(folderPath, folderName)
	
        
def getAndInsertInfo(folderPath,folderName):
	log_Org=""
	fileCorner=os.path.join(folderPath, folderName)+ "_corner.txt"
	corner = open(fileCorner, 'r').read()
	arrayC=corner.split(' ')
	polygon="POLYGON((" + arrayC[0] +" "+ arrayC[1]+"," +arrayC[2] +" "+ arrayC[3]+"," +arrayC[6] +" "+ arrayC[7]+"," +arrayC[4] +" "+ arrayC[5]+"," +arrayC[0] +" "+ arrayC[1] + "))"
	corner=  loads(polygon)
	
	#check intersects with VN
	if corner.within(vietnam_bounds) or corner.intersects(vietnam_bounds):
		aqstime = "2011-01-01" #default aqstime 
		strName=folderName.split('.')
		year=int(strName[1][1:5])
		jDay=int(strName[1][5:])
		hour=int(strName[2][0:2])
		minute=int(strName[2][2:])	
		strYear=strName[1][1:5]
		aqstime=convertJDayToDate(year, jDay)+" "+ strName[2][0:2]+":"+strName[2][2:]+":00"
		#===insert info image==
		filename=folderName+".hdf"
		pathtemp=folderPath.split('/apom')
		path= 'apom'+pathtemp[1]
		#path=folderPath
		corner=polygon
		dateNow=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
		try:
			statement= insert_satOrg.format(tableName_Org,typeid,aqstime,filename,path,corner,dateNow,collection)
			conn=connect()
			cursor=conn.cursor()
			cursor.execute(statement)
			conn.commit()
			conn.close()
			log_Org="["+dateNow+"] Insert File "+filename+" to "+tableName_Org +" Successful \n"
		except psycopg2.DatabaseError, e:
			print 'Error %s' % e 
			log_Org="["+dateNow+"] Insert File "+filename+" to "+tableName_Org +" Error: %s " % e 
		
		if not os.path.exists(logFolder):
			os.makedirs(logFolder)
		logfile_org=logFolder+"/"+log_file_org
		writeLog(logfile_org,log_Org)
		logfile_day=logFolder+"/"+log_Day
		writeLog(logfile_day,log_Org)
		
	else:
		#remove folder
		shutil.rmtree(folderPath)

def writeLog(logfile,row):
	if not os.path.exists(logfile):
		with open(logfile,'ab') as f:
			f.write(row)
			f.close()
	else:
		with open(logfile,'ab') as f:
			f.write(row)
			f.close()
	
def WriteCornerFile(fileMetadata,folderFilePath):
	f = open(fileMetadata,"r")
	temp=""
	for line in f:
		if "Upper Left" in line:
			strt = line.replace(' ', '')	
			a=strt.index('(')
			b=strt.index(')')
			c=strt.index(',')
			num1= strt[a+1:c]
			num2=strt[c+1:b]
			ul=num1 + " "+num2
		elif "Lower Left" in line:
			strt = line.replace(' ', '')	
			a=strt.index('(')
			b=strt.index(')')
			c=strt.index(',')
			num1= strt[a+1:c]
			num2=strt[c+1:b]
			ll=num1 + " "+num2
		elif "Upper Right" in line:
			strt = line.replace(' ', '')	
			a=strt.index('(')
			b=strt.index(')')
			c=strt.index(',')
			num1= strt[a+1:c]
			num2=strt[c+1:b]
			ur=num1 + " "+num2
		elif "Lower Right" in line:
			strt = line.replace(' ', '')	
			a=strt.index('(')
			b=strt.index(')')
			c=strt.index(',')
			num1= strt[a+1:c]
			num2=strt[c+1:b]
			lr=num1 + " "+num2
			
	temp=ul+" "+ll+" "+ur+" "+lr
	#create _corner.txt file
	corner_file = open(folderFilePath+ "_corner.txt", "w")
	corner_file.write(temp)
	corner_file.close()

	
def createImageThumbnail(satType,newPath,folderFilePath):
	#create temp.tif
	if not os.path.isfile(folderFilePath+ "temp.tif"):
		cm="gdal_translate HDF4_EOS:EOS_SWATH:\"" +newPath + "\":mod04:Optical_Depth_Land_And_Ocean " + folderFilePath+ "temp.tif"
		os.system(cm)
	#create _convert.tif from temp.tif
	if satType != "LANDCOVER" and satType != "NPP":
		if not os.path.isfile(folderFilePath+ "_convert.tif"):
			cm1="gdalwarp -t_srs '+proj=longlat +datum=WGS84 + no_defs' -ot Float32 -tps -srcnodata '0' -dstnodata '0' -dstalpha " + folderFilePath + "temp.tif " +folderFilePath+ "_convert.tif"
			os.system(cm1)
	#convert .tif to .png
	os.system("gdal_translate -of PNG -a_nodata '0' " + folderFilePath + "_convert.tif" + " " + folderFilePath + "_convert.png");

	# create thumbnail from _convert.png
	os.system("gdal_translate -of PNG -outsize 500 450 -a_nodata '0' " + folderFilePath + "_convert.png" + " " + folderFilePath + "_thumbnail.png");

def resample_Image(file):
	fileN=os.path.basename(file)
	folderName=os.path.splitext(os.path.basename(file))[0]
	splitYear=folderName.split('.')
	yearFolder=str(splitYear[1][1:5])
	folderPath = os.path.join(resample_folder,yearFolder, folderName)
	
	sta=SelectFromOrg_query.format(tableName_Org,fileN)
	conn=connect()
	cursor=conn.cursor()
	cursor.execute(sta)
	
	rows = cursor.fetchall()
	for row in rows:
		filename=fileN.strip()
		path=row[0].strip()
		aqstime=row[1]
		corner=loads(row[2])
		if corner.within(vietnam_bounds) or corner.intersects(vietnam_bounds):
			#full path file hdf
			inputfilename = mer_Folder +"/"+ path +"/"+filename
			
			aod_input_file = 'HDF4_EOS:EOS_SWATH:"'+ inputfilename + aod_band_resample
			aod_output_file=os.path.join(folderPath,filename + aod_format_resample)
			if not os.path.exists(os.path.dirname(aod_output_file)):
				os.makedirs(os.path.dirname(aod_output_file))
			re_griding(aod_input_file, resx, resy, aod_output_file)
			# run raster2psql and insert to DB
			insert_image_Resamp(filename,folderPath,aqstime,corner,yearFolder)
	
def insert_image_Resamp(filename,folderPath,aqstime,corner,yearFolder):
	pathtemp1=folderPath.split('/apom')
	filepath= 'apom'+pathtemp1[1]
	
	temp_command = "/usr/lib/postgresql/9.1/bin/raster2pgsql -a -f rasref -F {1} "+ tableName_Resamp
	subFolder=os.path.splitext(filename)[0]
	temp3_file = os.path.join(folderPath, filename + aod_format_resample)
	 
	if os.path.isfile(temp3_file):
		temp3_script=os.popen(temp_command.format("rasref3",temp3_file, filename)).read()
		first_index = temp3_script.find("('")
		last_index = temp3_script.find("':")
		temp3_ref=temp3_script[first_index+2:last_index]
		dateNow=datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
		
		statement= insert_satResamp.format(tableName_Resamp,aqstime,temp3_ref,filename,filepath,projection,typeid,dateNow,collection)
		try:
			conn=connect()
			cursor=conn.cursor()
			cursor.execute(statement)
			conn.commit()
			conn.close()
			log_Res="["+dateNow+"] Resample File "+filename+" to "+tableName_Resamp +" Successful \n"
		except psycopg2.DatabaseError, e:
			print 'Error %s' % e 
			log_Res="["+dateNow+"] Insert File "+filename+" to "+tableName_Resamp +" Error %s " % e +" \n"
		
		if not os.path.exists(logFolder):
			os.makedirs(logFolder)
		logfile_res=logFolder+"/"+log_file_resamp
		writeLog(logfile_res,log_Res)
		logfile_day=logFolder+"/"+log_Day
		writeLog(logfile_day,log_Res)
		
		   
def re_griding(inputfile, resx, resy, ouputfile):
	regrid_command = "gdalwarp -t_srs '+proj=longlat +datum=WGS84' -tps -ot Float32 -wt Float32 -te 100.1 6.4 111.8 25.6 -tr {0} {1} -r cubic -srcnodata -9999 -dstnodata -9999 -overwrite -multi {2} {3}"
	os.system(regrid_command.format(resx, resy, inputfile, ouputfile))
	
def convertJDayToDate(year, jDay):
	date="1-1" #date and month;
	day=()
	#if is_leap_year(year):
	if year % 4 == 0 and year %100 != 0 or year % 400 == 0:
		day=(1, 32, 61, 92, 122, 153, 183, 214, 245, 275, 306, 336)
	else:
		day=(1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)
	for i in range(11,-1,-1):
		if (jDay-day[i]>=0):
			date=str(year)+"-"+str((i+1))+"-"+str((jDay+1-day[i]));
			break;
	return date	
		

if __name__ == '__main__':
    index(inputFolder,org_Folder,satType)



