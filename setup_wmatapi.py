#!/usr/local/bin/python

########### Python 2.7 #############


## here we will attempt to generate a config file. You need an API key though.
import requests, argparse, ConfigParser

parser = argparse.ArgumentParser()
#get the api key on the command line
parser.add_argument('-api','--api', help='WMATA apikey',required=True)

args = parser.parse_args()

api = args.api

def getjson(url):

	r = requests.get(url, headers=theapi)
	return r.json()


#create the key header for requsests	
theapi = {'api_key' : api}

#get the line code
theLine = str(raw_input('Two Digit Line code? RD, BL, YL, OR, GR, or SV'))

#create URL	
theStationUrl = "https://api.wmata.com/Rail.svc/json/jStations?LineCode=" + theLine

theSetupData = getjson(theStationUrl)

#extract station data and loop through to match names and codes
theStations=theSetupData['Stations']
for item in theStations:
	print item['Name'],item['Code']

#get the station code based on the user picking from above list

theStation = str(raw_input('Station code? '))
theDirectionUrl = 'https://api.wmata.com/StationPrediction.svc/json/GetPrediction/' + theStation 
theRailLineData = getjson(theDirectionUrl)

#loop through trains data and show group numbers
theTrains = theRailLineData['Trains']
for item in theTrains:
	print 'Destination Direction ' + item['DestinationName'] + ' --- Group number = ' + item['Group']

theGroup= str(raw_input('Group Number? '))
print 'You must lookup the bus stop location ID on nextbus or elsewhere on the web'
theBusStop = str(raw_input('Bus Stop Location ID?'))

print 'Create config file with the following settings: \n'
print 'Line = ' + theLine + '\n'
print 'Station = ' + theStation + '\n'
print 'Group = ' + theGroup + '\n'
print 'Bus stop ID = ' + theBusStop + '\n'

theAnswer = str(raw_input("Y/n? "))

if theAnswer == 'y' or theAnswer == 'Y' :
	theLocation = str(raw_input('Config name and location? Default ./wmata.cfg')) or 'wmata.cfg'

	config = ConfigParser.SafeConfigParser()
	config.add_section('wmata')

	config.set('wmata','bus_stop',theBusStop)
	config.set('wmata','rail_stop',theStation)
	config.set('wmata','apikey',api)
	config.set('wmata','rail_group',theGroup)
	config.set('wmata','rail_line',theLine)
	print "file written to " + theLocation + '\n'
	with open(theLocation, 'wb') as configfile:
		config.write(configfile)
   
    
    
    
    