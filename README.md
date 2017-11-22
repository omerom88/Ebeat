# Ebeat

Abstract
Ebeat is a tool that translates movements (such as dancing and other motions in space) into electronic music.
Two users can produce music with their own bodies, and the more they collaborate and dance freely the
more they produce rich and unique music just for them

Technolegy
Kinect camera captures the user’s body in 3 axis at any given time
Ableton app with ready layers, divides into 3 groups - drums, harmony and melody
Python script to receive an input from the Kinect, connects every body joint into a musical layer to
produce sound, and creates a graphic feedback for the user to understand his position in the space

Libaries
OpenNI2, NiTE2, Primesense, libfreenect - kinect libs to recognize the human body
LiveOSC - script that runs in Abelton and allows to control it using LiveOSC protocole
Pylive - Python lib to control Abelton from outside through LiveOSC protocole
Mido - Python lib that allows to read & write in MIDI ports
Pyglet - Python lib to create graphics
