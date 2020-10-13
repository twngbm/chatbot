from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import logging
import time
import os
import sys
#import chatcore as cc
import chatcoreV3 as cc
import UserObj
import asyncio
###################################
#connectionClient={}
#{(ip,port):{"currentRoot":<tree_node>,"knownInfo":{"ID":"Q36061020",}},}
###################################




def init():
    global connectedClient
    global Chatbot
    
    connectedClient={}
    loglevel = os.getenv('LOG', "INFO")
    if loglevel == "DEBUG":
        LOG_LEVEL = logging.DEBUG
    elif loglevel == "INFO":
        LOG_LEVEL = logging.INFO
    elif loglevel == "WARNING":
        LOG_LEVEL = logging.WARNING
    elif loglevel == "ERROR":
        LOG_LEVEL = logging.ERROR
    elif loglevel == "CRITICAL":
        LOG_LEVEL = logging.CRITICAL
    else:
        LOG_LEVEL = logging.ERROR

    formatter = '| %(levelname)s | %(asctime)s | %(process)d | %(message)s |'
    logging.basicConfig(level=LOG_LEVEL, format=formatter,
                        datefmt="%Y-%m-%d %H:%M:%S")
    logging.critical("Chatbot Core Initinal")
    
    Chatbot=cc.Chatbot()

    logging.critical("Chatbot Core Initinal Done")



if __name__ == "__main__":
    init()
    #server = SimpleWebSocketServer('', WEBSOCKETPORT,ChatServer,None)
    logging.critical("Web Socket Server Start")
    #clientIP=0
    #clientPort=1
    #connectedClient[(clientIP,clientPort)]={"currentList":[],"knownInfo":{},"history":[],"wantedInfo":""}
    #result,connectedClient[(clientIP,clientPort)]=Chatbot.chat(None,connectedClient[(clientIP,clientPort)])
    user=UserObj.User()
    user.userUpdate("raw_restart")
    loop=asyncio.get_event_loop()
    loop.run_until_complete(Chatbot.chat(user))
    print(user.botSay.Response)
    
    while True:
        
        data=str(input(":"))
        if "sys_" not in data:
            data="raw_"+data
        user.userUpdate(data)
        loop.run_until_complete(Chatbot.chat(user))
        print(user.botSay.Response)
        print(user.botSay.Metadata)