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
import threading
import signal
import concurrent.futures
import traceback



###################################
# connectionClient={}
# {(ip,port):{"currentRoot":<tree_node>,"knownInfo":{"ID":"Q36061020",}},}
###################################

WEBSOCKETPORT = 8080
jwtKey = 'rteschatbotsecret'
ITPrincipal = "ITPrincipal.csv"

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


class ClientHelper(object):

    @staticmethod
    def restoreUserStatus(headers, clientInfo):
        # TODO:Key check and restore
        pass
        # Cookie check and restore
        try:
            token = headers["Cookie"].split("token=")[1]
            try:
                userStatus = ClientHelper.loadStatus(token)
                return userStatus, token, False
            except:
                raise IOError
        except:
            # token not found or token
            token = ClientHelper.__generateToken__(clientInfo[0])
            userStatus = {
                "currentList": [], "knownInfo": {}, "history": [], "wantedInfo": "", "token": token}
            return userStatus, token, True

    @staticmethod
    def loadStatus(token):
        filename = str(token)
        logging.info(f"Client Restor from cookie token {token}")

        with open("./Cookies/"+filename+".json", "r", encoding="utf-8") as f:
            connectionStatus = json.load(f)
        return connectionStatus

    @staticmethod
    def saveStatus(userStatus, token):
        filename = str(token)
        with open("./Cookies/"+filename+".json", "w", encoding="utf-8") as f:
            json.dump(userStatus, f, ensure_ascii=False)

    @staticmethod
    def chat(message, userStatus):
        return Chatbot.chat(message, userStatus)

    @staticmethod
    def __generateToken__(ip):
        payload = {
            "iss": "ncku.chatbot.com",
            "iat": int(time.time()),
            "exp": int(time.time()) + 86400*3,
            "ip": ip
        }

        token = jwt.encode(payload, jwtKey, algorithm='HS256')
        return token



async def wsHandler(websocket, path):

    loop = asyncio.get_running_loop()
    header = websocket.request_headers
    clientInfo = websocket.remote_address
    try:
        with concurrent.futures.ProcessPoolExecutor(2) as pool:

            # Initinal or Restore client state
            userStatus, token, NewClient = await loop.run_in_executor(pool, ClientHelper.restoreUserStatus, header, clientInfo)
            if NewClient:
                await websocket.send(f"sys_token_{token}")
                logging.debug(f"Initinal New Client with Token={token}")
                message = None
                result, userStatus = Chatbot.chat(message, userStatus)
                await websocket.send(str(result)+"<br>")

            else:
                history = userStatus["history"]
                await websocket.send(f"sys_history_{history}")
                logging.debug(f"Load Saved Client with Token={token}")

            # Client Chat
            async for message in websocket:
                if message == "":
                    continue
                logging.debug(f"Client:{token} Received Message:{message}")
                if message.find("sys_") == 0:
                    # TODO:Handel command
                    continue
                #TODO:result, userStatus = await loop.run_in_executor(pool, ClientHelper.chat, message, userStatus)
                result, userStatus=Chatbot.chat(message,userStatus)
                await websocket.send(str(result))

            # Client Closed

            logging.debug(f"Client Closed with Token={token}")
            ClientHelper.saveStatus(userStatus, token)

    except:
        errormessage = traceback.format_exc()
        logging.error(errormessage)


if __name__ == "__main__":
    def handle_sigterm(*args):
        raise KeyboardInterrupt()
    signal.signal(signal.SIGTERM, handle_sigterm)

    init()
    logging.critical("Web Socket Server Start")
    wsserver = websockets.serve(wsHandler, "0.0.0.0", WEBSOCKETPORT)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(wsserver)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()
        logging.critical("Web Socket Server Stop")
        exit(0)
