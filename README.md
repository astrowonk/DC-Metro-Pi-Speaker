# DC-Metro-Pi-Speaker
Uses python to generate location specific audio on bus and rail times using WMATA's api.
I wrote this code for my own use as I wanted my raspberry pi to speak topical Metro information in the morning
at specific times.

This is my first python project, and my first object oriented code. I am sure it could be much more "pythonic" in some 
places.  There are no doubt numerous issues, including a lack of exception handling.

The code queries the WMATA api for one bus stop and one rail stop and group. It then processes that into strings which it sends to the gTTS service and generates and mp3. You can then use your mp3 player of choice on the RPi to play the audio.

It also works reasonably well on Mac OS X. I haven't tried it on any other systems.

I think the main dependencies are pycurl, gTTS, argparser and whatever is needed to make those run.
