#from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import logging
import time
import os
import sys
#import chatcore as cc
import chatcoreV2 as cc
import jwt
import json
import asyncio
import websockets
import websockets.handshake
#import client

###################################
# connectionClient={}
# {(ip,port):{"currentRoot":<tree_node>,"knownInfo":{"ID":"Q36061020",}},}
###################################

WEBSOCKETPORT = 8080
jwtKey = 'rteschatbotsecret'
clientList = {}

"""
class ChatServer(WebSocket):
    def handleMessage(self):

        logging.info("Client {ip}:{port} Send Sentence : {sent}".format(
            ip=self.clientIP, port=self.clientPort, sent=self.data))

        if "sys_" in self.data:  # handle sys_control_message
            if "sys_token_" in self.data:
                self.token = self.data.split("sys_token_")[1]
                tokenMiss = False
                try:
                    self.__loadStatus()
                    logging.info("Token Found")
                except:
                    logging.info("Token Missing. Resend Token.")
                    tokenMiss=True
                self.sendMessage("sys_history_"+str(self.connectionStatus["history"]))
            if "sys_newconversation" in self.data or tokenMiss:
                self.token = self.__generateCookie(self.data)
                self.sendMessage("sys_token_" + str(self.token))
                self.connectionStatus = {
                    "currentList": [], "knownInfo": {}, "history": [], "wantedInfo": ""}
                self.connectionStatus["token"] = self.token
                result, self.connectionStatus = Chatbot.chat(
                    None, self.connectionStatus)
                self.sendMessage(result)
                self.__saveStatus()
        else:
            result, self.connectionStatus = Chatbot.chat(
                self.data, self.connectionStatus)
            self.sendMessage(str(result))
            self.__saveStatus()

    def handleConnected(self):
        self.clientIP = self.address[0]
        self.clientPort = self.address[1]
        logging.info("Client {ip}:{port} Connected.".format(
            ip=self.clientIP, port=self.clientPort))

    def handleClose(self):
        self.__saveStatus()
        logging.info("Client {ip}:{port} Closed.".format(
            ip=self.clientIP, port=self.clientPort))

    def __generateCookie(self, mes):
        payload = {
            "iss": "ncku.chatbot.com",
            "iat": int(time.time()),
            "exp": int(time.time()) + 86400*3,
            "ip": self.clientIP
        }

        token = jwt.encode(payload, jwtKey, algorithm='HS256')
        return token

    def __saveStatus(self):
        #filename=self.__sha(self.token)
        filename=str(self.token)
        logging.info("Client {ip}:{port} Saved.".format(
            ip=self.clientIP, port=self.clientPort))
        with open("./Cookies/"+filename+".json", "w", encoding="utf-8") as f:
            json.dump(self.connectionStatus, f, ensure_ascii=False)

    def __loadStatus(self):
        #filename=self.__sha(self.token)
        filename=str(self.token)
        logging.info("Client {ip}:{port} Restored.".format(
            ip=self.clientIP, port=self.clientPort))
        
        with open("./Cookies/"+filename+".json", "r", encoding="utf-8") as f:
            self.connectionStatus = json.load(f)
    def __sha(self,token):
        s=hashlib.sha256()
        s.update(token)
        return s.hexdigest()
"""

def init():
    global Chatbot
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

    Chatbot = cc.Chatbot()

    logging.critical("Chatbot Core Initinal Done")


async def wsHandler(websocket, path):
    print("**************************************")
    print(websocket.request_headers)
    #print(websocket,path)
    print("**************************************")
    async for message in websocket:
        print(f"< {message}")

        greeting = f"Hello {message}"

        await websocket.send(greeting)
        print(f"> {greeting}")



if __name__ == "__main__":
    #init()
    #server = SimpleWebSocketServer('', WEBSOCKETPORT, ChatServer, None)
    logging.critical("Web Socket Server Start")
    start_server = websockets.serve(wsHandler, "0.0.0.0", WEBSOCKETPORT)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

    try:
        pass
    except KeyboardInterrupt:
        pass