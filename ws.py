import logging
import time
import os
from ChatbotConfig import WEBSOCKETPORT, jwtKey
import jwt
import json
import asyncio
import websockets
import websockets.handshake
import signal
import concurrent.futures
import traceback
import nest_asyncio
import UserObj
import pickle
nest_asyncio.apply()
#import multiprocessing
#multiprocessing.set_start_method('fork', True)

# TODO：Multi processing websocket werver
###################################
# connectionClient={}
# {(ip,port):{"currentRoot":<tree_node>,"knownInfo":{"ID":"Q36061020",}},}
###################################


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
    import chatcoreV3 as cc
    Chatbot = cc.Chatbot()

    logging.critical("Chatbot Core Initinal Done")


class ClientHelper(object):

    @staticmethod
    async def botHandshake(header, clientInfo, websocket) -> UserObj.User:
        user, NewClient = await ClientHelper.restoreUserStatus(header, clientInfo)
        if NewClient!=None:
            await websocket.send(json.dumps({"Response": "sys_token", "Metadata": user.token}))
            await websocket.send(json.dumps({"Response": "sys_key", "Metadata": NewClient}))
            logging.debug(f"Initinal New Client with Token={user.token}")
            user.userUpdate('{"DataType":"sys","Data":"restart"}')
            await Chatbot.chat(user)
            await websocket.send(user.sendbackMessage)
        else:
            history = user.chatHistory
            await websocket.send(json.dumps({"Response": "sys_history", "Metadata": history}))
            logging.debug(f"Load Saved Client with Token={user.token}")
        return user

    @staticmethod
    async def restoreUserStatus(headers, clientInfo):
        # TODO:Key check and restore
        pass
        # Cookie check and restore
        try:
            token = headers["Cookie"].split("token=")[1]
            try:
                user = ClientHelper.loadStatus(token)
                return user, None
            except:
                raise IOError
        except:
            # token not found or token
            token = ClientHelper.__generateToken__(clientInfo[0])
            user = UserObj.User()
            user.token = token
            restoreKey=ClientHelper.__genetatrKey__()
            return user, restoreKey

    @staticmethod
    def loadStatus(token):
        filename = str(token)
        logging.info(f"Client Restor from cookie token {token}")

        with open("./Cookies/"+filename+".json", "rb") as f:
            user = pickle.load(f, encoding="utf8")
        return user

    @staticmethod
    def saveStatus(userStatus):
        filename = userStatus.token

        with open("./Cookies/"+filename+".json", "wb") as f:
            pickle.dump(userStatus, f)

    @staticmethod
    def __generateToken__(ip):
        payload = {
            "iss": "ncku.chatbot.com",
            "iat": int(time.time()),
            "exp": int(time.time()) + 86400*3,
            "ip": ip
        }

        token = jwt.encode(payload, jwtKey, algorithm='HS256').decode("utf-8")

        return token

    @staticmethod
    def __genetatrKey__():
        #exitKey=os.listdir("")
        return "0000"


async def wsHandler(websocket, path):
    header = websocket.request_headers
    clientInfo = websocket.remote_address
    try:
        # Initinal or Restore client state

        user = await ClientHelper.botHandshake(header, clientInfo, websocket)

        async for message in websocket:
            logging.debug(f"Client:{user.token} Received Message:{message}")
            try:
                user.userUpdate(message)
            except TypeError:
                errormessage = traceback.format_exc()
                logging.error(errormessage)
                continue

            try:
                await Chatbot.chat(user)
            except NotImplementedError:
                errormessage = traceback.format_exc()
                logging.error(errormessage)
                continue
            except TypeError:
                errormessage = traceback.format_exc()
                logging.error(errormessage)
                continue

            await websocket.send(user.sendbackMessage)

        # Client Closed

        logging.debug(f"Client Closed with Token={user.token}")
        ClientHelper.saveStatus(user)
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
