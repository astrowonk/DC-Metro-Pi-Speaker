#!/usr/local/bin/python

########### Python 2.7 #############
import requests, argparse, subprocess

from datetime import datetime
import ConfigParser

try:
	from gtts import gTTS
except ImportError:
    print "no GTTs, will use espeak"


## added this argument handler so someone could test this without constantly making new mp3 files
parser = argparse.ArgumentParser()
parser.add_argument("--nosound", help="Does not create an MP3", action="store_true")
parser.add_argument("--railtest", help="Loads incident JSON from text file", action="store_true")
parser.add_argument("--espeak", help="Uses espeak through subprocess", action="store_true")


args = parser.parse_args()

config = ConfigParser.SafeConfigParser()
## I used to just save this to the same directory as wherever the script was but that cause a lot of issues
## namely it would fail to load the config when run from a crontab
config.read('/usr/local/etc/wmata.cfg')

busstop = str(config.get('wmata','bus_stop'))
railstop = str(config.get('wmata','rail_stop'))
api = str(config.get('wmata','apikey'))
railgroup = str(config.get('wmata','rail_group'))
line = str(config.get('wmata','rail_line'))
theapi = {'api_key' : api}

## It will attempt to get a mp3 save location from the config, if not, /tmp.
try:
	save_file = str(config.get('wmata','save_file')) 
except ConfigParser.NoOptionError:
	save_file = '/tmp/text.mp3'

#### getjson is mostly borrowed documentary code that uses pycurl to get the json data. 

### I used to use pycurl but it took effort to compile on the pi (though worked fine on the Mac) \
# So I switched to requests. Though I may not be forming the URLs using the parameters syntax
# properly it works fine.

# requests has its own problems on the RPi, namely a lot of insescureplatform ssl warnings.
# It was almost as much of a pain getting requests to work without those errors
# as it was getting pycurl to build in the first place

## Contruct our URLS below. These urls are so nice and simple with requests (and formerly with pycurl)

busurl = 'https://api.wmata.com/NextBusService.svc/json/jPredictions?StopID=' + busstop 
railurl = 'https://api.wmata.com/Incidents.svc/json/Incidents'
railPredicUrl = 'https://api.wmata.com/StationPrediction.svc/json/GetPrediction/' + railstop


def getjson(url):

	r = requests.get(url, headers=theapi)


	return r.json()

class busHandler(object):
# Hey look I'm writing objects. This one has quite a few methods. Wmata's data often comes down as lists of dictionaries 
# which confused me at first the methods here contruct and return lists mostly. the two last two probably aren't needed anymore since it is easy
# to just take the first item of the route and busTime lists

	def __init__(self,thejson):
		self.thejson=thejson
	def PredictionList(self):
		return self.thejson['Predictions']
	def busTimeList(self):
		theList = []
		for item in self.PredictionList():
			theList.append(item['Minutes'])
		return theList
	def routeList(self):
		theList = []
		for item in self.PredictionList():
			theList.append(item['RouteID'])
		return theList			
	def nextBusTime(self):
		item = self.PredictionList()[0]
		return str(item['Minutes'])		
	def nextRoute(self):
		item = self.PredictionList()[0]
		return str(item['RouteID'])
		
		
class railHandler(object):
## methods here get allIncidents on every line
## or one particular line. I try to do some text cleanup (only on line incident for some reason)
## as wmata likes to abbreviate for
## reasons I don't particularly understand
	def __init__(self,thejson):
		self.thejson=thejson
	def incidentList(self):
		return self.thejson['Incidents']
	def allIncidents(self):
		theList = []
		for item in self.incidentList():
			theList.append(item['Description'])
		return theList
	def lineIncidents(self,theLine):
		theList = []
		for item in self.incidentList():
			if (theLine in item['LinesAffected']) :
				cleantext = item['Description'].replace('btwn','between')
				#Wmata has started spelling out the word minutes on these now. one day i'll check for the word minutes first before cleaning
				#cleantext = cleantext.replace('min','minutes')
				cleantext = cleantext.replace('add\'l','additional')
				theList.append(cleantext)
		return theList
	

class railPredictionHandler(object):
#you probably never want PRedictionList since it's pretty raw, but I then call that in the other functions 
#since the entire block of 
#prediction data is under that dictionary keyword Trains


	def __init__(self,thejson):
		self.thejson=thejson
	def PredictionList(self):
		return self.thejson['Trains']
	def trainTimes(self,group,myline):
		theList = []
		for item in self.PredictionList():
# here I'm just leaving these non numerical values out so I can do math on the list 
			if (item['Group'] == group) and (item['Min'] not in ['ARR','BRD','---']) and item['Line']==myline:
				theList.append(item['Min'])
## make the list ints
		return map(int, theList)		
	def trainDestinations(self,group):
		theList = []
		for item in self.PredictionList():
			if item['Group'] == group:
				theList.append(item['DestinationName'])
		return theList
	def averageHeadways(self,x,myline):
## this returns an integer which .. I think I'm ok with
		return self.trainTimes(x,myline)[-1] / len (theTimes)
			
## No more objects, onto the actual script code				

# Get the rawjson data from wmata based on our constructed URLs we made


railIncidentData = getjson(railurl)
predictionData = getjson(railPredicUrl)


##create objects for bus times, rail incidents, and rail times
## if busstop is left out of the config file, we won't make a bustimes object
## nor even query the bus URL
if len(busstop) > 0:
	theBusData = getjson(busurl)
	myBusTimes = busHandler(theBusData)
	isBus = True
else:
	isBus = False

if args.railtest:
	with open('testdata.txt') as data_file:    
 		railIncidentData = json.load(data_file)
else:
	railIncidentData = getjson(railurl)
			
myIncidents = railHandler(railIncidentData)

myRailTimes = railPredictionHandler(predictionData)
	
## here is where we assemble the text myText to speak. This should probably be a function? IT's a lot of if statements
## recent addition to handle a config file that has no bus stop	
if isBus:
	if len(myBusTimes.busTimeList()) != 0:
		myText = "The next bus arrives in " + str(myBusTimes.busTimeList()[0]) + " minutes. It is route " + str(myBusTimes.routeList()[0]) + '. \n'
	
	else:
		myText = "There are no current bus predictions. \n"
		
	if len(myBusTimes.busTimeList()) > 1:
		myText = myText + "Another bus arrives in " + str(myBusTimes.busTimeList()[1]) + " minutes. \n"
else:
	myText = ' '
	


# Loops through all the incidents on our line and in the direction we care about and assembles them into one string.
# This won't work as well on a station and group that has several lines

railText = ' '
if len(myIncidents.lineIncidents(line)) > 0:

	for item in myIncidents.lineIncidents(line):
		##print item
		x = item.partition(':')
		railText = railText + ' ' + x[2]
	x = myIncidents.lineIncidents(line)[0].partition(':')
	railText = x[0] + ' incident. ' + railText + '. \n'

myText = myText + railText

##debugging text
theTimes = myRailTimes.trainTimes(railgroup,line)
# print "Rail times below"
# print theTimes
# print len(theTimes)

#print myRailTimes.PredictionList()

## This builds the string for the average headways


if len(theTimes) == 0:
	myText = myText + "There are no upcoming trains listed. "

if len(theTimes) == 1:
	myText = myText + "There is only one upcoming train time, in "  + str(myRailTimes.averageHeadways(railgroup,line)) + " minutes."

if len(theTimes) > 1 and (myRailTimes.averageHeadways(railgroup,line) > 5):
	myText = myText + "Rail headway are currently averaging " + str(myRailTimes.averageHeadways(railgroup,line)) + " minutes."

if len(theTimes) > 1 and (myRailTimes.averageHeadways(railgroup,line) <= 5):
	myText = myText + "Rail headway times are normal, currently " + str(myRailTimes.averageHeadways(railgroup,line)) + " minutes."


## prints the text to be spoke to the screen using Gtts
## unless the --nosound option was used, uses the google text to speech service and python library to make an mp3
## for now you'll have to find a way to play this
## I use a 2-line shell script that calls this script and then mpg123 on the pi
## mp3 probably needs an option to set the save location
## with espeak it doesn't make an MP3 it just speaks.
print myText	
if args.nosound:
	print 'No MP3 Made'
elif args.espeak:
	subprocess.Popen(["espeak", "-v", "en", "-w", "/tmp/wmata.wav", myText])
else:
	try:
		tts = gTTS(text= myText, lang='en') 
		tts.save(save_file)
	except requests.exceptions.HTTPError:
		print "Google Text to Speech error. Likely due to throttling/CAPTCHa. Switch to espeak with --espeak"
		