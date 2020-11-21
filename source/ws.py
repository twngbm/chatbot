import asyncio
import json
import logging
import os
import signal
import traceback
from pathlib import Path

import nest_asyncio
import websockets
import websockets.handshake
from ChatbotConfig import *
import Chatcore

from utils import ServerUtils, LoaderUtils

nest_asyncio.apply()


def init():

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
                        datefmt="%Y-%m-%d %H:%M:%S", handlers=[logging.FileHandler("chatbot.log", "a+", "utf-8")])
    logging.critical("Chatbot Core Initinal")
    global DATA
    global Chatbot
    DATA = LoaderUtils()
    Chatbot = Chatcore.Chatbot(DATA)

    logging.critical("Chatbot Core Initinal Done")
    if OPENWEATHER_APIKEY == None:
        logging.error(
            "Open Weather API key missing. Weather Function will not work.\n\
             Please refer to https://openweathermap.org/ for an API key.\n\
             And setup environment variable:\n\
             \t OPENWEATHER_APIKEY=<api_key>\n")


async def wsHandler(websocket, path):
    clientInfo = websocket.remote_address
    user = await ServerUtils.createNewUser(clientInfo, DATA, websocket)
    try:
        async for message in websocket:

            # Feed raw message into User
            try:
                ServerUtils.messageReceive(user, message)

            except:
                errormessage = traceback.format_exc()
                logging.error(errormessage)
                continue

            # Chat Logic
            try:
                await Chatbot.chat(user)

            except:
                errormessage = traceback.format_exc()
                logging.error(errormessage)
                continue

            # Return Server say to Client
            await ServerUtils.messageSend(user, websocket)

        # Client Closed

        logging.info(f"Client {user.userID} Closed")

    except:
        errormessage = traceback.format_exc()
        logging.error(errormessage)
    finally:
        logging.debug(f"Client {user.userID} Dropped")
        del user
        return  # Delete This While Enable Restore


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
