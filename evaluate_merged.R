library(hydroGOF)
library(clusterSim)

evaluate = function(station_value, model_value, result_dataframe){
	R2 = cor(station_value,model_value)^2
	RMSE =sqrt(sum((model_value-station_value)^2)/samples)
	RE =(sum(abs(model_value-station_value)/station_value)/samples)*100

	MFB = (2*sum((model_value-station_value)/(station_value+model_value)*100))/samples
	MFE = (2*sum(abs(model_value-station_value)/(model_value+station_value)*100))/samples
	# rs = data.frame(station,samples,R2,RMSE,RE,MFB,MFE)
	temp_dataframe = data.frame(R2,RMSE,RE,MFB,MFE)
	result_dataframe = rbind(result_dataframe, temp_dataframe)
	return(result_dataframe)
}

# result_dataframe = data.frame()
#station

data_station1 = read.csv("/media/lancer/01D124DD7D476BA0/apom/prod/bac_lieu.csv")
data_station = read.csv("/media/lancer/01D124DD7D476BA0/apom/prod/nghia_do.csv")
# print(data_station)

data_station = data_station[complete.cases(data_station),]
data_station1 = data_station1[complete.cases(data_station1),]
# print(data_station)
data_station = rbind(data_station, data_station1)

samples = nrow(data_station)
station_value = data_station$aod_550
# print(station_value)
# model_value = data_station$ukColumn
dataframe = data.frame()

SAA_value = data_station$SAA
dataframe =  evaluate(station_value, SAA_value, dataframe)
MLE_value = data_station$MLE
dataframe =  evaluate(station_value, MLE_value, dataframe)
WPC_value = data_station$WPC
dataframe =  evaluate(station_value, WPC_value, dataframe)

print(dataframe)
# write.csv(dataframe,"/media/lancer/01D124DD7D476BA0/apom/prod/bac_lieu_validate_merged.csv")
write.csv(dataframe,"/media/lancer/01D124DD7D476BA0/apom/prod/validate_merged.csv")
#year
print("y")
