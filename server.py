from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from chatbot import get_response
import preprocess, time


class ChatServer(WebSocket):

    def handleMessage(self):
        # echo message back to client
        #message = self.data
        #response = get_response(message)
        #print(type(message))
        tS = time.time()
        message = [self.data]
        ckip = preprocess.ckip(message)
        self.sendMessage("wait")
        temp = ckip.GetKeyword()
        temp = "/".join(temp)
        self.sendMessage(temp)
        self.sendMessage(str(time.time()-tS))

    def handleConnected(self):
        print(self.address, 'connected')

    def handleClose(self):
        print(self.address, 'closed')


server = SimpleWebSocketServer('', 8000, ChatServer)
server.serveforever()
