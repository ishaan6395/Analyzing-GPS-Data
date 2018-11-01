# importing the modules

import math
import simplekml
import pandas as pd

"""
@author Ishaan Thakker
Program to generate a KML file  from GPS data with Left turns and Stop signs after finding the optimal path.
"""

# this dictionary will store the cost function value for each file

time_file = {}
# main function
def main():
	# file names of all the files stored in a list
	file_names = ['ZI8G_ERF_2018_08_16_1428.txt','ZIAC_CO0_2018_10_12_1250.txt','ZIAB_CIU_2018_10_11_1218.txt',
'ZIAA_CTU_2018_10_10_1255.txt','ZI8N_DG8_2018_08_23_1316.txt','ZI8K_EV7_2018_08_20_1500.txt','ZI8J_GKX_2018_08_19_1646.txt',
'ZI8H_HJC_2018_08_17_1745.txt']

	# getting the cost function of all the files and storing it in dictionary
	for name in file_names:
		get_lowest_cost_file(name)	
	
	cost = math.inf
	file_name = ''
	# iterating to find the file with lowest cost function
	for name in file_names:
		
		if cost > time_file[name]:
			cost = time_file[name]
			file_name = name
	# Once the lowest cost function is found performing operations on it to generate the kml file with stop signs and left turns
	perform_op(file_name)


def get_lowest_cost_file(file_name):
	prev_lat = ''
	prev_long = ''
	data = []	
	with open(file_name) as file:
		for line in file:
			elements = line.split(',')
			if elements[0] == '$GPRMC':
				# avoiding the rows which have ID of V instead of A in all $GPRMC rows
				if not(prev_lat == elements[3] and prev_long == elements[5]) and elements[2]=='A':
					data.append([elements[0],elements[1], elements[3], elements[4], elements[5], elements[6], elements[7], elements[8], elements[9]])
					prev_lat = elements[3]
					prev_long = elements[5]
			
	
	# Adding data in data frame
	csv_data = pd.DataFrame(data)
	
	# Splitting data in individual list for further operations	
	speed = csv_data[6]
	time = csv_data[1]
	time = [float(i) for i in time]
	speed = [float(i) for i in speed]

	
	time_file[gettime_diff(str(time[len(time)-1]) , str(time[0]))] = file_name
	max_speed = max(speed)
	cost = gettime_diff(str(time[len(time)-1]) , str(time[0]))/30 + 0.5 * (max_speed)/52.13
	time_file[file_name] = cost
	

def perform_op(file_name):
	global time_file
	kml = simplekml.Kml()
	# initializing empty lists
	data = []
	time = []
	latitude = []
	NS = []
	longitude = []
	EW = []
	speed = []
	tracking = []
	date = []
	
	# kml_text is an empty string which is used to generate text for the kml file
	kml_text = ''
	kml_text+='<?xml version="1.0" encoding="UTF-8"?>\n'
	kml_text+='<kml xmlns="http://www.opengis.net/kml/2.2">\n'
	kml_text+='<Document>\n'
	kml_text+='<Style id="yellowPoly">\n'
	kml_text+='<LineStyle>\n'
	kml_text+='<color>Af00ffff</color>\n'
	kml_text+='<width>6</width>\n'
	kml_text+='</LineStyle>\n'
	kml_text+='<PolyStyle>\n'
	kml_text+='<color>7f00ff00</color>\n'
	kml_text+='</PolyStyle>\n'
	kml_text+='</Style>\n'
	kml_text+='<Placemark><styleUrl>#yellowPoly</styleUrl>\n'
	kml_text+='<LineString>\n'
	kml_text+='<Description>Speed in MPH, not altitude.</Description>\n'
	kml_text+='<extrude>1</extrude>\n'
	kml_text+='<tesselate>1</tesselate>\n'
	kml_text+='  <altitudeMode>clamp to ground</altitudeMode>\n'
	kml_text+='<coordinates>\n'
				
	count = 0
	prev_lat = ''
	prev_long = ''
	# reading data from the text file line by line and only performing operation on lines which start with $GPRMC
	with open(file_name) as file:
		for line in file:
			elements = line.split(',')
			if elements[0] == '$GPRMC':
				# avoiding the rows which have ID of V instead of A in all $GPRMC rows
				if not(prev_lat == elements[3] and prev_long == elements[5]) and elements[2]=='A':
					data.append([elements[0],elements[1], elements[3], elements[4], elements[5], elements[6], elements[7], elements[8], elements[9]])
					prev_lat = elements[3]
					prev_long = elements[5]
			

	# Adding data in data frame
	csv_data = pd.DataFrame(data)
	#print(csv_data)
	# Splitting data in individual list for further operations	
	direction_lat = csv_data[3]
	direction_long = csv_data[5]
	speed = csv_data[6]
	tracking = csv_data[7]	
	time = csv_data[1]
	# converting time and speed in float format 
	time = [float(i) for i in time]
	speed = [float(i) for i in speed]
	tracking = [float(i) for i in tracking]
	ls = []

	latitude = csv_data[2]
	longitude = csv_data[4]
	
	# formatting latitude and longitude in degree and minutes
	latitude = [float(format_degree(latitude[i])) for i in range(0,len(latitude)) ]
	longitude = [float(format_degree(longitude[i])) for i in range(0,len(longitude))]
	
	# Adding negative signs for latitude and longitude according to direction(-ve for longitude in west and -ve for latitude in south)	
	latitude = format_lat(latitude, direction_lat)
	longitude = format_long(longitude, direction_long)
	
	x = 20
	pointa = []
	pointb = []
	count = 0
	# Detecting left turns in the GPS data available
	while (x < len(speed)):
		# making the size of the window 20 
		a = tracking[x-20]		
		b = tracking[x]
		diff = abs(a-b)

		"""
		Here we are checking for left turns so we need to check the difference in two points so we need to make sure that 
		point a is greater than point b and their difference is in the range 55 - 110
		if the point is not greater than b then to determine that the turn is left turn or not then we need to see
		that whether the difference lies in the range after adding 360 to point a or not.
		"""

		if a > b:
			if (diff>55 and diff< 110):
				sp = []
				for y in range(x-20, x):
					sp.append(speed[y])
				
				if speed[x-20]>4 or speed[x]>4:
					#print(x-20, a, b)
					pointa.append(longitude[x])
					pointb.append(latitude[x])
					#print('here',x)
					x = x + 20
				else:

					x = x + 1
			else:
				x =  x + 1
		elif ((360 - diff)>60 and (360-diff)<110):
			
			if speed[x-20]>1 and speed[x]>1:
				sp = []
				for y in range(x-20, x):
					sp.append(speed[y])
				count = len([i for i in sp if i < 20])
				if count>0:
					if speed[x-20] > 1 or speed[x]>1:								
						pointa.append(longitude[x])
						pointb.append(latitude[x])
						#print('here',x)
					x = x + 20
				else:
					x = x+1	
			else:
				x =  x + 1
		else:
			x = x + 1


	# appending the points of left turn to the kml_text string
	for x in range(0, len(latitude)):
		kml_text+=(str(longitude[x])+','+str(latitude[x])+'\n')
	


	
	"""
	For Stop sign
	The following code below determines the stop signs using threshold_speed, threshold_distance and threshold_time
	"""	
	#initializing the lists needed for finding stop signs
	stoplong = []
	stoplat = []
	threshold_speed = 15
	threshold_dist = 0.1
	long = longitude
	lat = latitude
	x = 1

	"""
	Here we calculate Haversine distance for every two points and for determining whether it is a stop sign or not
	we calculate the time difference between two points and take the speed of the current point
	1) If the current speed is less than threshold and if the time difference is greater than threshold we need to check for distance
	2) If the distance is less than threshold distance then we can see that it is a stop sign
	"""
	while (x<len(long)):
		x0 = long[x-1]
		x1 = long[x]
		y0 = lat[x-1]
		y1 = lat[x]
		dlon = x1-x0
		dlat = y1-y0
		a = math.sin(dlat/2)**2 + math.cos(y0) * math.cos(y1) * math.sin(dlon/2)**2
		c = 2 * math.asin(math.sqrt(a))
		r = 6371
		dist = c*r
		time_diff = abs(time[x] - time[x-1])
			
		if time_diff > 0.5 and speed[x]>0.1 and speed[x] < threshold_speed:
			if dist>=0.01:
				stoplong.append(long[x-1])
				stoplat.append(lat[x-1])
				#print(x)
				x = x+8
			else:
				x = x+1
		else:
			x = x+1	

	kml_text+='</coordinates>\n'
	kml_text+='</LineString>\n'
	kml_text+='</Placemark>\n'
	for x in range(0, len(pointa)):
		kml_text+='<Placemark><description>Default Pin is Yellow</description><Point><coordinates>'+str(pointa[x])+','+str(pointb[x])+',0.0</coordinates></Point></Placemark>'
	for x in range(0, len(stoplong)):
		if speed[x] >0.01:	
			kml_text+='<Placemark><description>Red PINfor A Stop</description><Style id="normalPlacemark"><IconStyle><color>ff0000ff</color><Icon><href>http://maps.google.com/mapfiles/kml/paddle/1.png</href></Icon></IconStyle></Style><Point><coordinates>'+str(stoplong[x])+','+str(stoplat[x])+',0.0</coordinates></Point></Placemark>'
		
	
	kml_text+='</Document>\n'
	kml_text+='</kml>\n'
	time_file[gettime_diff(str(time[len(time)-1]) , str(time[0]))] = file_name
	max_speed = max(speed)
	cost = gettime_diff(str(time[len(time)-1]) , str(time[0]))/30 + 0.5 * (max_speed)/52.13
	time_file[file_name] = cost
	fname = file_name.split('.')
	f = open(fname[0]+'.kml','w')
	f.write(kml_text)
	#print(len(longitude), len(latitude), len(time))
	#print(len(stoplong), len(stoplat))
	print(file_name+' File Saved which has the optimal Path')

# This function formats the latitude value as negative if the direction is south
def format_lat(lat,  direction):
	return_ls = []
	for x in range(0, len(lat)):
		if direction[x] =='N':
			return_ls.append(lat[x])
		else:
			return_ls.append(-1*lat[x])
	return return_ls

# This function formats the longitude value as negative if the direction is sWest
def format_long(long, direction):
	return_ls = []
	for x in range(0, len(long)):
		if direction[x] == 'E':
			return_ls.append(long[x])
		else:
			return_ls.append(-1*long[x])
	return return_ls

#This function converts the longitude and latitude in degree and minutes
def format_degree(element):
	elements = element.split('.')
	one = float((elements[0][:len(elements[0])-2]))
	two = elements[0][3:]+'.'+elements[1][:]
	return(float(one)+(float(two))/60)

#This function gives the time difference between two points in minutes
def gettime_diff(a,b):

	a1 = float(a[:2])
	a2 = float(a[2:4])
	a3 = float(a[4:])
	b1 = float(b[:2])
	b2 = float(b[2:4])
	b3 = float(b[4:])
	part1 = a1 - b1
	part2 = 60 - b2 + a2
	part3 = 60 - b3 + a3
	ans = 0.0
	for x in range(0,int(part1)-1):
		ans+=60.0
	ans+=part2+part3/60
	return ans

if __name__=='__main__':
	main()
	
	
	
