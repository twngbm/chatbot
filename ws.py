import logging
import time
import os
from ChatbotConfig import WEBSOCKETPORT, jwtKey, CLIENT_PATH, EXPIRE_TIME
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
from pathlib import Path
nest_asyncio.apply()
#import multiprocessing
#multiprocessing.set_start_method('fork', True)

# TODO：Multi processing websocket werver


def init():
    global Chatbot
    global key_cookie
    global cookie_key

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
    logging.critical("Load Key_Cookie Pair")

    try:
        os.mkdir("./"+CLIENT_PATH)
    except:
        pass
    try:
        os.mkdir("./"+CLIENT_PATH+"/Cookies")
    except:
        pass

    try:
        with open("./"+CLIENT_PATH+"key_cookies.json", "r") as f:
            key_cookie = json.load(f)
        cookie_key = {y: x for x, y in key_cookie.items() if y != None}

    except:
        Path("./"+CLIENT_PATH+"key_cookies.json").touch()
        key_cookie = {1000: None}
        cookie_key = {}


class ClientHelper(object):
    @staticmethod
    async def botHandshake(header, clientInfo, websocket, message, user) -> UserObj.User:

        try:
            message = json.loads(message)
            DataType = message["DataType"]
            Data = message["Data"]
        except:
            raise TypeError

        if DataType == "raw" and Data != "是":
            user = ClientHelper.createNewUser(clientInfo[0], websocket)
            await websocket.send(json.dumps({"Response": "sys_token", "Metadata": user.token}))
            await websocket.send(json.dumps({"Response": Chatbot.__GetMessage__("SysNewKey")+str(user.key), "Metadata": None}))
            await Chatbot.chat(user)
            user.userUpdate(json.dumps(message))
            await Chatbot.chat(user)
            await websocket.send(user.sendbackMessage)
            return user
        elif DataType == "sys_key":
            keyToken = ClientHelper.keyCheck(Data)

            if not keyToken:
                await websocket.send(json.dumps({"Response": Chatbot.__GetMessage__("SysWrongKey"), "Metadata": None}))

            elif keyToken == "Expiry":
                await websocket.send(json.dumps({"Response": Chatbot.__GetMessage__("SysExpiryKey"), "Metadata": None}))

            else:
                try:
                    user = ClientHelper.loadStatus(keyToken)
                    await websocket.send(json.dumps({"Response": "sys_token", "Metadata": user.token}))
                    await websocket.send(json.dumps({"Response": "sys_history", "Metadata": user.chatHistory}))
                    logging.debug(f"Load Saved Client with Token={user.token}")
                except:
                    user = ClientHelper.createNewUser(clientInfo[0], websocket)
                    await websocket.send(json.dumps({"Response": "sys_token", "Metadata": user.token}))
                    await websocket.send(json.dumps({"Response": Chatbot.__GetMessage__("SysNewKey")+str(user.key), "Metadata": None}))
                    await Chatbot.chat(user)
                    await websocket.send(user.sendbackMessage)
                return user

        elif DataType == "sys" and Data == "start":
            # Try to find token
            pass

        elif type(user) == str:
            if Data == "是":
                try:
                    user = ClientHelper.loadStatus(user)
                    await websocket.send(json.dumps({"Response": "sys_history", "Metadata": user.chatHistory}))
                    logging.debug(f"Load Saved Client with Token={user.token}")
                    return user
                except:
                    pass
            user = ClientHelper.createNewUser(clientInfo[0], websocket)
            await websocket.send(json.dumps({"Response": "sys_token", "Metadata": user.token}))
            await websocket.send(json.dumps({"Response": Chatbot.__GetMessage__("SysNewKey")+str(user.key), "Metadata": None}))
            await Chatbot.chat(user)
            await websocket.send(user.sendbackMessage)
            return user

        headerToken = ClientHelper.tokenCheck(header)

        if not headerToken:
            await websocket.send(json.dumps({"Response": Chatbot.__GetMessage__("SysMissToken"), "Metadata": None}))

        elif headerToken == "Expiry":
            await websocket.send(json.dumps({"Response": Chatbot.__GetMessage__("SysExpiryToken"), "Metadata": None}))

        else:
            await websocket.send(json.dumps({"Response": Chatbot.__GetMessage__("SysFindToken"), "Metadata": ["是", "否"]}))
            return str(headerToken)
        user = ClientHelper.createNewUser(clientInfo[0], websocket)
        await websocket.send(json.dumps({"Response": "sys_token", "Metadata": user.token}))
        await websocket.send(json.dumps({"Response": Chatbot.__GetMessage__("SysNewKey")+str(user.key), "Metadata": None}))
        await Chatbot.chat(user)
        await websocket.send(user.sendbackMessage)
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
            restoreKey = ClientHelper.__genetatrKey__(token)
            user = UserObj.User()
            user.token = token
            user.key = restoreKey
            return user

    @staticmethod
    def createNewUser(userIP, websocket) -> UserObj.User:
        user = UserObj.User()

        token = ClientHelper.__generateToken__(userIP)
        restoreKey = ClientHelper.__genetatrKey__(token)

        user.token = token
        user.key = restoreKey
        logging.info(f"Initinal New Client with Key={user.key}")

        user.userUpdate('{"DataType":"sys","Data":"restart"}')

        return user

    @staticmethod
    def loadStatus(token):
        filename = str(token)
        logging.info(f"Client Restor from cookie token {token}")

        with open("./"+CLIENT_PATH+"/Cookies/"+filename+".pkl", "rb") as f:
            user = pickle.load(f, encoding="utf8")
        return user

    @staticmethod
    def saveStatus(userStatus):
        filename = userStatus.token
        key_cookie[userStatus.key]["Expiry"] = int(time.time()+EXPIRE_TIME)
        with open("./"+CLIENT_PATH+"/Cookies/"+filename+".pkl", "wb") as f:
            pickle.dump(userStatus, f)

    @staticmethod
    def keyCheck(key):
        try:
            key = int(key)
            cookieData = key_cookie[key]
        except:
            return None
        if cookieData == None:
            return None
        if time.time() > int(cookieData["Expiry"]):
            return "Expiry"
        return cookieData["Token"]

    @staticmethod
    def tokenCheck(headers):
        try:
            token = headers["Cookie"].split("token=")[1]
            key = cookie_key[token]
            cookieData = key_cookie[key]
        except:
            return None
        if time.time() > int(cookieData["Expiry"]):
            cookie_key.pop(token, None)
            key_cookie.pop(key, None)

            try:
                os.remove("./"+CLIENT_PATH+"Cookies/"+token)
            except:
                pass

            return "Expiry"
        return token

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
    def __genetatrKey__(token):
        for key, value in key_cookie.items():
            if value == None:
                key_cookie[key] = {"Token": token,
                                   "Expiry": int(time.time()+EXPIRE_TIME)}
                cookie_key[token] = key
                return key
            elif time.time() > int(value["Expiry"]):
                try:
                    os.remove("./"+CLIENT_PATH+"Cookies/"+value["Token"])
                except:
                    pass
                cookie_key.pop(value["Token"], None)

                key_cookie[key] = {"Token": token,
                                   "Expiry": int(time.time()+EXPIRE_TIME)}
                cookie_key[token] = key
                return key
        key = key+1
        cookie_key[token] = key
        key_cookie[key] = {"Token": token,
                           "Expiry": int(time.time()+EXPIRE_TIME)}
        return key


async def wsHandler(websocket, path):
    header = websocket.request_headers
    clientInfo = websocket.remote_address
    user = None
    try:
        async for message in websocket:

            # Stop here while user not define
            if not user or type(user) == str:
                try:
                    user = await ClientHelper.botHandshake(header, clientInfo, websocket, message, user)
                    continue
                except TypeError:
                    errormessage = traceback.format_exc()
                    logging.error(errormessage)
                    continue

            logging.debug(f"Client:{user.token} Received Message:{message}")

            # Feed raw message into User
            try:
                user.userUpdate(message)
            except TypeError:
                errormessage = traceback.format_exc()
                logging.error(errormessage)
                continue

            # Chat Logic
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

            # Return Server say to Client
            await websocket.send(user.sendbackMessage)

        # Client Closed

        logging.debug(f"Client Closed")
        if user:
            ClientHelper.saveStatus(user)

    except:
        errormessage = traceback.format_exc()
        logging.error(errormessage)
    finally:
        logging.debug("Client Dropped")
        if user:
            ClientHelper.saveStatus(user)


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
        logging.critical("Save Key Cookie Pair")
        with open("./"+CLIENT_PATH+"key_cookies.json", "w") as f:
            json.dump(key_cookie, f)
        logging.critical("Web Socket Server Stop")
        exit(0)
