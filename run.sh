if [ ! -d "./data" ] 
then
    wget -i "./reference/ckipdata.txt" -o data.zip
    unzip data.zip
fi

docker build -t chatbot .
docker stop Chatbot_Demo
docker rm Chatbot_Demo
docker run --name=Chatbot_Demo -p 80:80 -p 8080:8080 --restart=always --detach chatbot:latest