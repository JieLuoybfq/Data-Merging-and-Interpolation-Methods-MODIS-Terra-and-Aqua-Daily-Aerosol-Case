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
	# print(R2)
	# print(RMSE)
	# print(RE)
	# print(MFB)
	# print(MFE)
	# print(temp_dataframe)
	return(result_dataframe)
}

# result_dataframe = data.frame()
#station

data_station = read.csv("/media/lancer/01D124DD7D476BA0/apom/prod/bac_lieu.csv")
data_station1 = read.csv("/media/lancer/01D124DD7D476BA0/apom/prod/nghia_do.csv")

# station_value = data_station$aod_550
# print(station_value)
# model_value = data_station$ukColumn
dataframe = data.frame()

data_station = rbind(data_station1, data_station)

samples = nrow(data_station)
station_value = data_station$aod_550

# SAA_value = data_station$SAA
# dataframe =  evaluate(station_value, SAA_value, dataframe)
# MLE_value = data_station$MLE
# dataframe =  evaluate(station_value, MLE_value, dataframe)
# WPC_value = data_station$WPC
# dataframe =  evaluate(station_value, WPC_value, dataframe)

SAA_uk_value = data_station$SAA_uk
dataframe = evaluate(station_value, SAA_uk_value, dataframe)
MLE_uk_value = data_station$MLE_uk
dataframe = evaluate(station_value, MLE_uk_value, dataframe)
WPC_uk_value = data_station$WPC_uk
dataframe = evaluate(station_value, WPC_uk_value, dataframe)

MOD_mi_value = data_station$MOD_mi
dataframe = evaluate(station_value, MOD_mi_value, dataframe)
MYD_mi_value = data_station$MYD_mi
dataframe = evaluate(station_value, MYD_mi_value, dataframe)

MOD_uk_value = data_station$MOD_uk
dataframe = evaluate(station_value, MOD_uk_value, dataframe)
MYD_uk_value = data_station$MYD_uk
dataframe = evaluate(station_value, MYD_uk_value, dataframe)

uk_SAA_value = data_station$uk_SAA
dataframe = evaluate(station_value, uk_SAA_value, dataframe)
mi_SAA_value = data_station$mi_SAA
dataframe = evaluate(station_value, mi_SAA_value, dataframe)
miAs1_value = data_station$miAs1
dataframe = evaluate(station_value, miAs1_value, dataframe)

# print(data_station)
print(dataframe)
# write.csv(data_station,"/media/lancer/01D124DD7D476BA0/apom/prod/data_station.csv")
# write.csv(dataframe,"/media/lancer/01D124DD7D476BA0/apom/prod/bac_lieu_validate.csv")
write.csv(dataframe,"/media/lancer/01D124DD7D476BA0/apom/prod/validate_new.csv")
#year
