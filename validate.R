# TODO: Add comment
# 
# Author: forever
###############################################################################
library(hydroGOF)
library(clusterSim)

#station
data_station = read.csv("D:/out/prod_kriging/npp_all_rs.csv")

samples = nrow(data_station)
station_value = data_station$avg_pm
model_value = data_station$ukColumn

R2 = cor(station_value,model_value)^2
RMSE =sqrt(sum((model_value-station_value)^2)/samples)
RE =(sum(abs(model_value-station_value)/station_value)/samples)*100

MFB = (2*sum((model_value-station_value)/(station_value+model_value)*100))/samples
MFE = (2*sum(abs(model_value-station_value)/(model_value+station_value)*100))/samples
rs = data.frame(station,samples,R2,RMSE,RE,MFB,MFE)
			
	

write.csv(rs,"D:/out/prod_kriging/station_validate.csv")
#year
