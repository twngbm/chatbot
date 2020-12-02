---
tags: Chatbot
title: 交接文件
---
# User Manual
## Use Guide
1. Choose Version.

    a. Web Version
    ![](https://i.imgur.com/jBU1fa8.png)
    
    b. Zenbo Version
    ![](https://i.imgur.com/Ek9vfYR.png)
2. Enter URL in web browser.

   a. Web Version URL: **http://<Chatbot_Server_IP>/web**
   
   b. Zenbo Version URL: **http://<Chatbot_Server_IP>/zenbo**
   
3. Start Use.

## UI Description
1. [Web Version](https://github.com/twngbm/chatbot/blob/master/doc/chatbot%E4%BD%BF%E7%94%A8%E8%AA%AA%E6%98%8E.pdf)

    ![](https://i.imgur.com/8RhuR9x.png)

2. [Zenbo Version](https://github.com/twngbm/chatbot/blob/master/doc/zenbo%E4%BD%BF%E7%94%A8%E8%AA%AA%E6%98%8E.pdf)

   ![](https://i.imgur.com/DJmqmy5.jpg)


# Installation Guide
## Requirement
:::warning
1. Linux OS, which [can install docker engine](https://docs.docker.com/engine/install/). Tested on **Ubuntu 18.04**, other linux distribution may also work.
2. **Docker Installed.** Test on Docker version 19.03.8, other version may also work.
    ```
    $ sudo apt update && sudo apt install docker.io
    ```
4. Allow port 80 and port 8080 on firewall.
5. [Open weather API key](https://openweathermap.org/api).

    
:::
## Installation
Choose one of the method described below.
### 1. Build From Source
1. Get Source From **[Here](https://github.com/twngbm/chatbot)**
    ```
    $ sudo apt install git
    $ git clone https://github.com/twngbm/chatbot
    $ cd chatbot
    ```
2. *(Optional)* Download CKIP data from **[GD](https://drive.google.com/drive/folders/105IKCb88evUyLKlLondvDBoh7Dy_I1tm)** or **[GD2](https://drive.google.com/file/d/12Y3xTzawcYhNXWjgSZYQw7YrNRxS-gAx/view?usp=sharing)**, unzip it and move the /data to source's root.
    ![](https://i.imgur.com/tnfKChf.png)
    ```
    $ sudo apt install wget unzip
    $ wget https://ckip.iis.sinica.edu.tw/data/ckiptagger/data.zip
    $ unzip data.zip
    ```
3. Change file mode **run.sh** to executable.
    ```
    $ chomd +x run.sh
    ```
4. Build and run. ++**Root privilege needed.**++
    ```
    $ sudo ./run.sh OPENWEATHER_APIKEY=<Open weather API key>
    ```

### 2. Run Pre-Build Image
1. Pull docker image.
    ```
    $ docker pull twngbm/chatbot
    ```
    Or download docker image from **[HERE](https://drive.google.com/file/d/17IP4sefZkIF7e1rtxWolht8c7OmAugFi/view?usp=sharing)** and load the image.
    ```
    $ docker load -i twngbm_chatbot_1.0.tar
    ```
2. Run docker image.
    ```
    $ docker run -p 80:80 -p 8080:8080 --env "OPENWEATHER_APIKEY=<Open weather API key>" --detach twngbm/chatbot:1.0
    ```

# Development Guide
## Resource
Python Requirements List:
|Package Name|Version|
|------------|-------|
|numpy|1.19.1|
|ckiptagger|0.1.1|
|tensorflow|1.15.2|
|python-Levenshtein|0.12.0|
|websockets|8.1|
|fuzzywuzzy|0.18.0|
|ckipnlp|0.9.1|
|nest_asyncio|1.4.0|
|requests|2.21.0|
1. [Offline Python Dependence Package](https://drive.google.com/drive/folders/1SJZIwJjKlT-SJJz9PH5hmx3CwGdvU2lI?usp=sharing)
## Archicture
### Repository Organization
- **doc/** : Docoument for this project.
- **html/** : Web Interface, which is the user interface for this project. The web interface only provide input and display.
- **reference/**: Text data,NCKU computer center's data and rule/logic base data for chat logic.
- **source/**: Source code.
    -  **ChatbotConfig.py**: Chatbot configuration and constant variable.
    -  **Chatcore.py**: Main program for handling input of user. Basically, it will depend on user's input,state of user and rule base data in **"reference/solution.json"** then generate next question or final answer, or change the state of user.
    -  **UserObj.py**: Class for handling state of user, storing user information, providing method for changing the user's state, getting current's state information ,etc.
    -  **main.sh**: Entrypoint for the program.
    -  **utils.py**: Helper function class which will be referenced by other file.
        - LoaderUtils Class: For data loading purpose. Initialize once at program start up
        - ServerUtils Class: Class for handling websocket connection,read and send.
        - ChatUtils Class: Class for message processing support.
        - IntentUtils Class: Class to find intent of user, using CKIP for broker. Initialize once at program start up. Class method **intentParser()** take in *Message* which user input, a candidate list that user may pick from, which depend on user's current state. This method will finally return a single candidate, multi candidate or nothing.
        - FunctionUtils Class: Class where you can define your own chat function for more purpose,such as get weather, get current position, get current time ,etc.
    -  **ws.py**:Handle program initialize and websocket loop for websocket connection. This file is the python program entrypoint of all.
- **Dockerfile**: Docker file for building docker image.
- **run.sh**: Helper file to build and run this project.
### Design
#### Archicture
![](https://i.imgur.com/xhtaIn4.png)
#### State
![](https://i.imgur.com/3EkPk7G.png)
#### Workflow
1. Main Flow

![](https://i.imgur.com/UFuGRPc.png)

2. Create Connection

![](https://i.imgur.com/IJCRcZH.png)

3. State Change

![](https://i.imgur.com/ATiJz5y.png)

TODO:json editor, last step unsolved saver