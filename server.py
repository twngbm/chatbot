from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import logging
import time
import os
import sys
#import chatcore as cc
import chatcoreV2 as cc
import jwt

###################################
#connectionClient={}
#{(ip,port):{"currentRoot":<tree_node>,"knownInfo":{"ID":"Q36061020",}},}
###################################

WEBSOCKETPORT=8080
jwtKey = 'rteschatbotsecret'


class ChatServer(WebSocket):
    
    def handleMessage(self):
        #tS = time.time()        
        
        logging.info("Client {ip}:{port} Send Sentence : {sent}".format(ip=self.clientIP, port=self.clientPort,sent=self.data))

        if(mes.find("sys_") >= 0): #handle the hand shaking
            isFirst, token = setCookie(self,slef.data)
            if(isFirst):
                self.sendMessage("sys_token_" + str(token))
                return
            else:
                return

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

    def setCookie(self, mes):
        if(mes.find("token_") < 0):
            payload = {
                "iss": "ncku.chatbot.com",
                "iat": int(time.time()),
                "exp": int(time.time()) + 86400*3,
                "ip": self.clientIP
            }
            token = jwt.encode(payload, 'rteschatbotsecret', algorithm='HS256')
            return true, token
        else:
            return false,mes.split("token_")[1]



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