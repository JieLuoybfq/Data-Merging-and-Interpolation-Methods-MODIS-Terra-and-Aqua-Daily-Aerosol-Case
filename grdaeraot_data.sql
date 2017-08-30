SELECT date_part('year',aqstime) as a_year,date_part('month',aqstime) as a_month,date_part('day',aqstime) as a_day,avg(aod_550)
  FROM org.grdaeraot_data
  where aqstime >='2015-01-01 00:00:00' and aqstime <= '2016-01-01 00:00:00' and stationid = 70
  group by a_year,a_month,a_day
  order by a_year,a_month,a_day 