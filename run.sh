#!/bin/bash
if [ ! -d "./data" ] 
then
    echo "CKIP DATA File not found, downloading."
    wget -i "./reference/ckipdata.txt" -o data.zip 2>&1
    unzip data.zip
fi
if [ -z $1 ] 
then
    echo "Missing OpenWeather Api Key"
    echo "Pass key by:"
    echo "./run.sh OPENWEATHER_APIKEY=<api key>"
    a="_=_"
else
    a=$1
fi
docker build -t chatbot .
docker stop Chatbot_Demo
docker rm Chatbot_Demo
docker run --name=Chatbot_Demo -p 80:80 -p 8080:8080 --env "$a" --restart=always --detach chatbot:latest
