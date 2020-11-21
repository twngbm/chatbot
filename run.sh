if [ ! -d "./data" ] 
then
    echo "File not found, downloading."
    wget -i "./reference/ckipdata.txt" -o data.zip 2>&1
    unzip data.zip
fi

docker build -t chatbot .
docker stop Chatbot_Demo
docker rm Chatbot_Demo
docker run --name=Chatbot_Demo -p 80:80 -p 8080:8080 --restart=always --detach chatbot:latest
