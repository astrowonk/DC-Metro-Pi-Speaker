# DC-Metro-Pi-Speaker
Uses python to generate location specific audio on bus and rail times using WMATA's api.
I wrote this code for my own use as I wanted my raspberry pi to speak topical Metro information in the morning
at specific times.

This is my first python project, and my first object oriented code. I am sure it could be much more "pythonic" in some 
places.  There are no doubt numerous issues, including a lack of exception handling.

The code queries the WMATA api for one bus stop and one rail stop and group. It then processes that into strings which it sends to the gTTS service and generates and saves to /tmp the mp3. You can then use your mp3 player of choice on the RPi to play the audio.

It also works reasonably well on Mac OS X. I haven't tried it on any other systems.

I think the main dependencies are requests, gTTS, argparser and whatever is needed to make those run. espeak if you can't get gTTS to work.

## Usage:

Put the script wherever you like, and make it executable. You may need to fiddle with the first line to specify where your python interpreter is located.
Edit and copy the example config file to /usr/local/etc/wmata.cfg. You will need an WMATA api key to make it work, and that has to be put into the file.

I have set up a crontab that runs a two line shell script to run this python script, and then use mpg123 to play the mp3 file. So, something like this:

	#!/bin/bash

	/home/pi/bin/wmata.py
	mpg123 -q /tmp/text.mp3

You can run the python script with --nosound and it will query and print text to the terminal but will not use gTTS to create the mp3 file.

##requests and urllib3 errors

Ok, so requests worked like a charm on OS X with the latest python, but on the RPi it spat out all kinds of SSL errors about an insecure platform. PySSL I think is needed. Eventually I got 

	sudo pip install requests[security]

to work though it requires possibly [adding some packages](http://stackoverflow.com/questions/29099404/ssl-insecureplatform-error-when-using-requests-package) via apt-get to make that work properly. python-dev libffi-dev libssl-dev seem to be needed to compile the security options of requests.

In light of this, I may alter the code to check for requests and if it's not there, fall back to pycurl.

## Google Text to Speech issues

So, the clever folks behind the gtts package [got around the forbidden url issues](https://github.com/pndurette/gTTS/pull/17). So if you upgrade to the latest version with

	sudo pip install gtts --upgrade

then you should be good to go. But anyway, now we have some limited espeak support. Much lower quality but it works. It generates a .wav in /tmp, you can just play that with mplayer or something. You'll need to install espeak

	sudo apt-get install espeak
	
and the sound quality is much worse, but it's something if you encounter gtts trouble.


