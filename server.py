from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
#from chatbot import get_response
import logging
import time
import os
import struct
import subprocess
import sys
import signal


def create_msg(content):
    return struct.pack("<I", len(content)) + content


def get_message(fifo):
    """Get a message from the named pipe."""
    msg_size_bytes = os.read(fifo, 4)
    msg_size = struct.unpack("<I", msg_size_bytes)[0]
    msg_content = os.read(fifo, msg_size).decode("utf8")
    return msg_content


class ChatServer(WebSocket):

    def handleMessage(self):

        tS = time.time()


        self.sendMessage("Running")

        msg = create_msg(self.data.encode("utf8"))
        logging.info("Client {ip}:{port} Send Sentence : {sent}".format(ip=self.clientIP, port=self.clientPort,sent=self.data))
        writer = os.open(__PATH__+"/input.pipe",
                         os.O_WRONLY | os.O_NONBLOCK)
        os.write(writer, msg)

        reader = os.open(__PATH__+"/output.pipe", os.O_RDONLY)
        result = get_message(reader)

        os.close(writer)
        os.close(reader)
        logging.info("CKIP find TOKEN : {token}".format(token=str(result)))
        self.sendMessage(str(result))
        self.sendMessage(str(time.time()-tS))

    def handleConnected(self):
        self.clientIP = self.address[0]
        self.clientPort = self.address[1]
        logging.info("Client {ip}:{port} Connected.".format(
            ip=self.clientIP, port=self.clientPort))

    def handleClose(self):

        logging.info("Client {ip}:{port} Closed.".format(
            ip=self.clientIP, port=self.clientPort))


def handle_sigterm(*args):
    raise KeyboardInterrupt()


def init():
    loglevel = os.getenv('LOG', "ERROR")
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
    logging.critical("Chatbot Core Start")


if __name__ == "__main__":
    init()
    signal.signal(signal.SIGTERM, handle_sigterm)
    __PATH__ = os.path.dirname(os.path.abspath(__file__))
    pid = os.fork()

    if pid == 0:
        ckip = subprocess.Popen(["python3.6", __PATH__+"/preprocess.py"], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        try:
            ckip.wait()
        except KeyboardInterrupt:
            os.remove(__PATH__+"/input.pipe")
            os.remove(__PATH__+"/output.pipe")
        finally:
            os._exit(0)
    else:
        while True:
            try:
                reader = os.open(__PATH__ +
                                 "/output.pipe", os.O_RDONLY)
                break
            except:
                time.sleep(1)
        result = get_message(reader)
        os.close(reader)
        if result == "ACK":
            server = SimpleWebSocketServer('', 8080, ChatServer)

            try:
                logging.critical("Web Socket Server Start")
                server.serveforever()
            except KeyboardInterrupt:
                server.close()
                logging.critical("Web Socket Server Stop")
                logging.critical("Chatbot Core Stop")

        else:
            raise IOError
