import requests
import json
import datetime
import time
import yaml
from configparser import ConfigParser




from datetime import datetime
print('Asteroid processing service')

# Initiating and reading config values
print('Loading configuration from file')
#Reading API
try:
                config = ConfigParser()
                config.read('config.ini')

                nasa_api_key = config.get('nasa', 'api_key')
                nasa_api_url = config.get('nasa', 'api_url')
              
except:
                logger.exception('')
print('DONE')

# Getting todays date
dt = datetime.now()
request_date = str(dt.year) + "-" + str(dt.month).zfill(2) + "-" + str(dt.day).zfill(2)  
print("Generated today's date: " + str(request_date))

#PRINTS NASAS URL THAT IT GETS 
print("Request url: " + str(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key))
r = requests.get(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key)

#PRINTS  all the things it shows (status code, headers,content) when it reads the api 
print("Response status code: " + str(r.status_code))
print("Response headers: " + str(r.headers))
print("Response content: " + str(r.text))

#If status code was 200 then  if starts
if r.status_code == 200:
#Getting data as json format
	json_data = json.loads(r.text)
#Creates arrays for asteroids that are safe and  those which are not
	ast_safe = []
	ast_hazardous = []
#Reads the json data and gets the total count of asteroids today
	if 'element_count' in json_data:
#Parses count to int and stores it in ast_count and then just prints it
		ast_count = int(json_data['element_count'])
		print("Asteroid count today: " + str(ast_count))
#If asteroid count was more than 0  then this if will start
		if ast_count > 0:
			for val in json_data['near_earth_objects'][request_date]:
				if 'name' and 'nasa_jpl_url' and 'estimated_diameter' and 'is_potentially_hazardous_asteroid' and 'close_approach_data' in val:
#Getting asteorids  name
					tmp_ast_name = val['name']
#Getting asteroids description url
					tmp_ast_nasa_jpl_url = val['nasa_jpl_url']
					if 'kilometers' in val['estimated_diameter']:
#Getting diameter values  for ast
						if 'estimated_diameter_min' and 'estimated_diameter_max' in val['estimated_diameter']['kilometers']:
							tmp_ast_diam_min = round(val['estimated_diameter']['kilometers']['estimated_diameter_min'], 3)
							tmp_ast_diam_max = round(val['estimated_diameter']['kilometers']['estimated_diameter_max'], 3)
						else:
							tmp_ast_diam_min = -2
							tmp_ast_diam_max = -2
#If the if failed reading the estimated diameter then these will be the values
					else:
						tmp_ast_diam_min = -1
						tmp_ast_diam_max = -1
#Sets the variable for hazardous asteroids
					tmp_ast_hazardous = val['is_potentially_hazardous_asteroid']
#Reading close approach data  and if its lenght is higher than 0 then this if will start
					if len(val['close_approach_data']) > 0:
#Sets the values for the  approaching ast
						if 'epoch_date_close_approach' and 'relative_velocity' and 'miss_distance' in val['close_approach_data'][0]:
							tmp_ast_close_appr_ts = int(val['close_approach_data'][0]['epoch_date_close_approach']/1000)
							tmp_ast_close_appr_dt_utc = datetime.utcfromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')
							tmp_ast_close_appr_dt = datetime.fromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')
#Adding speed values
							if 'kilometers_per_hour' in val['close_approach_data'][0]['relative_velocity']:
								tmp_ast_speed = int(float(val['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']))
							else:
								tmp_ast_speed = -1
#Data for miss distance
							if 'kilometers' in val['close_approach_data'][0]['miss_distance']:
								tmp_ast_miss_dist = round(float(val['close_approach_data'][0]['miss_distance']['kilometers']), 3)
							else:
								tmp_ast_miss_dist = -1
#Sets the values if  the "if" failed
						else:
							tmp_ast_close_appr_ts = -1
							tmp_ast_close_appr_dt_utc = "1969-12-31 23:59:59"
							tmp_ast_close_appr_dt = "1969-12-31 23:59:59"
#Sets the data if there isn't close approach data
					else:
						print("No close approach data in message")
						tmp_ast_close_appr_ts = 0
						tmp_ast_close_appr_dt_utc = "1970-01-01 00:00:00"
						tmp_ast_close_appr_dt = "1970-01-01 00:00:00"
						tmp_ast_speed = -1
						tmp_ast_miss_dist = -1
#Prints the data abaout the asteroid like its name, close aproach time, speed etc.
					print("------------------------------------------------------- >>")
					print("Asteroid name: " + str(tmp_ast_name) + " | INFO: " + str(tmp_ast_nasa_jpl_url) + " | Diameter: " + str(tmp_ast_diam_min) + " - " + str(tmp_ast_diam_max) + " km | Hazardous: " + str(tmp_ast_hazardous))
					print("Close approach TS: " + str(tmp_ast_close_appr_ts) + " | Date/time UTC TZ: " + str(tmp_ast_close_appr_dt_utc) + " | Local TZ: " + str(tmp_ast_close_appr_dt))
					print("Speed: " + str(tmp_ast_speed) + " km/h" + " | MISS distance: " + str(tmp_ast_miss_dist) + " km")
					
					# Adding asteroid data to the corresponding array
					if tmp_ast_hazardous == True:
						ast_hazardous.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])
					else:
						ast_safe.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])
#If there are no asteroids then prints this statement
		else:
			print("No asteroids are going to hit earth today")
#Prints info about safe and hazardous asteroids
	print("Hazardous asteorids: " + str(len(ast_hazardous)) + " | Safe asteroids: " + str(len(ast_safe)))
#If the hazardous asteroid count is not 0 then this if starts 
	if len(ast_hazardous) > 0:
#Sorts the array by time
		ast_hazardous.sort(key = lambda x: x[4], reverse=False)
#Prints possibility of asteroid impact and the asteroid info like  the time and more info 
		print("Today's possible apocalypse (asteroid impact on earth) times:")
		for asteroid in ast_hazardous:
			print(str(asteroid[6]) + " " + str(asteroid[0]) + " " + " | more info: " + str(asteroid[1]))
#Prints the closest distance and more info 
		ast_hazardous.sort(key = lambda x: x[8], reverse=False)
		print("Closest passing distance is for: " + str(ast_hazardous[0][0]) + " at: " + str(int(ast_hazardous[0][8])) + " km | more info: " + str(ast_hazardous[0][1]))
#If there were not any asteroids close then it just prints this statement
	else:
		print("No asteroids close passing earth today")
#If there were no response from API  because of some issues then it will print the  that there were problems connecting
else:
	print("Unable to get response from API. Response code: " + str(r.status_code) + " | content: " + str(r.text))
