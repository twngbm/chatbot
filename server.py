from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import logging
import time
import os
import sys
#import chatcore as cc
import chatcoreV2 as cc

###################################
#connectionClient={}
#{(ip,port):{"currentRoot":<tree_node>,"knownInfo":{"ID":"Q36061020",}},}
###################################

WEBSOCKETPORT=8080


class ChatServer(WebSocket):
    
    def handleMessage(self):
        #tS = time.time()        
        
        logging.info("Client {ip}:{port} Send Sentence : {sent}".format(ip=self.clientIP, port=self.clientPort,sent=self.data))

        result,connectedClient[(self.clientIP,self.clientPort)]=Chatbot.chat(self.data,connectedClient[(self.clientIP,self.clientPort)])
        
        self.sendMessage(str(result))
        #self.sendMessage(str(time.time()-tS))

    def handleConnected(self):
        self.clientIP = self.address[0]
        self.clientPort = self.address[1]
        
        connectedClient[(self.clientIP,self.clientPort)]={"currentRoot":None,"knownInfo":{}}
        logging.info("Client {ip}:{port} Connected.".format(
            ip=self.clientIP, port=self.clientPort))
        result,connectedClient[(self.clientIP,self.clientPort)]=Chatbot.chat(None,connectedClient[(self.clientIP,self.clientPort)])
        self.sendMessage(str(result))


    def handleClose(self):
        try:
            connectedClient.pop((self.clientIP,self.clientPort))
        except:
            pass
        
        logging.info("Client {ip}:{port} Closed.".format(
            ip=self.clientIP, port=self.clientPort))


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
    
    Chatbot=cc.chatbot()

    logging.critical("Chatbot Core Initinal Done")



if __name__ == "__main__":
    init()
    server = SimpleWebSocketServer('', WEBSOCKETPORT,ChatServer,None)
    logging.critical("Web Socket Server Start")
    try:
        server.serveforever()
    except KeyboardInterrupt:
        server.close()
        logging.critical("Web Socket Server Stop")
        logging.critical("Chatbot Core Stop")