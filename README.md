# DC-Metro-Pi-Speaker
Generates location specific audio on bus and rail times using WMATA's api.
I wrote this code for my own use as I wanted my raspberry pi to speak topical Metro information in the morning
at specific times.

This is my first python project, and my first object oriented code. I am sure it could be much more "pythonic" in some places. There is still a widespread lack of exception handling, along with other issues. But it works reliably me for me weekday mornings.

The code queries the WMATA api for one bus stop and one rail stop and group. It then processes that into strings which it sends to Google Text to Speech (via gTTS) service and generates and saves to /tmp the mp3. You can then use your mp3 player of choice on the RPi to play the audio.

It also works reasonably well on Mac OS X, and also supports using the built-in OS X speech synthesizer. I haven't tried it on any other systems.

I think the main dependencies are requests and gTTS. If you want to use espeak, you'll need that as well. You'll need mplayer or something to play the actual mp3 file that gTTS makes. 

You'll want to have [audio set up properly on the Pi](https://www.raspberrypi.org/documentation/configuration/audio-config.md). I use USB *powered* speakers that are connected to the headphone jack. 

## Setup:

The setup script will help you make a config file. Usage:

	./setup_wmatapi.py -api [your api key]
	
Prompts will then lead you through picking a rail line, rail stop code, rail "group" (i.e. direction) and write out a config file (including the api key you enter on the command line.)

I can't figure out any easy way to allow users to find their bus stop on the command line. It's much easier to use [BusETA](http://buseta.wmata.com/) and find it on the web based on your route and direction of choice.

For bus stops with more than one route, the optional bus_route config setting allows you to enter comma delimited routes of interest, or just one route.

## Usage:

Put the script wherever you like, and make it executable. You may need to fiddle with the first line to specify where your python interpreter is located.
Edit and copy the example config file to /usr/local/etc/wmata.cfg. You will need an WMATA api key to make it work, and that has to be put into the file.

I have set up a crontab that runs a two line shell script to run this python script, and then use mpg123 to play the mp3 file. So, something like this:

	#!/bin/bash

	/home/pi/bin/wmata.py
	mpg123 -q /tmp/text.mp3

You can run the python script with --nosound and it will query and print text to the terminal but will not use gTTS or espeak to create an audio file.

You can set a save_file option in the config file and specify where the gTTS audio file should be saved. eSpeak for now is always saved to /tmp (I should probably fix that.)

##requests and urllib3 errors

Ok, so requests worked like a charm on OS X with the latest python 2.7 from homebrew, but on the RPi it lots of SSL errors about an insecure platform. PySSL I think is needed. Eventually I got 

	sudo pip install requests[security]

to work though it requires possibly [adding some packages](http://stackoverflow.com/questions/29099404/ssl-insecureplatform-error-when-using-requests-package) via apt-get to make that work properly. python-dev libffi-dev libssl-dev seem to be needed to compile the security options of requests.

In light of this, I may alter the code to see if I can find an alternative to requests. But requests is just so nice... pycurl had similar problems with compilation issues.

## Google Text to Speech issues

So, the clever folks behind the gtts package [got around the forbidden url issues](https://github.com/pndurette/gTTS/pull/17). So if you upgrade to the latest version with

	sudo pip install gtts --upgrade

then you should be good to go. But anyway, now we have some limited espeak support. Much lower quality but it works. It generates a .wav in /tmp, you can just play that with mplayer or something. You'll need to install espeak

	sudo apt-get install espeak
	
and the sound quality is much worse, but it's something if you encounter gtts trouble.

On OS X, you'd need to use homebrew (or some other package manager, but homebrew seems to be the popular one these days) so 
	brew install espeak
	
I also used homebrew to install the latest python 2.7.11, and for that matter, git.

## MacOS X speech

I have added the ability to use the built-in MacOS X "say" command via subprocess on OS X to speak the text, rather than gTTS. Use the --osx flag on the command line. No MP3 or Wave will be generated.
