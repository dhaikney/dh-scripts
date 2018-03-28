#!/bin/bash

echo start
for width in `jot -p1 - 1 1 0.5`
do
for height in `jot -p1 - 50 58 0.4`
do
echo "Doing $width $height"
curl "http://maps.google.com/staticmap?center=$height,$width&size=640x640&maptype=satellite&format=png32&zoom=10" > ~/Desktop/maps/map.$width.$height.png
sleep 3

done
done