import json
import logging


class User(object):
    def __init__(self):
        self.currentNode = {}
        # TODO:Previous Step
        # self.path=[]
        self.chatHistory = []
        self.intentLog = [[]]
        self.token = None
        self.botSay = botWant()
        self.userSay = userSay()  # type=[control,raw,checked]
        self.recursive = []
        self.sendbackMessage = None
        self.key = None  # Restore Key

    def botUpdate(self, feature, response, metadate=None):
        self.botSay.WantedFeature = feature
        self.botSay.Response = response
        self.chatHistory.append([response, "Server"])
        self.botSay.Metadata = metadate
        self.sendbackMessage = json.dumps(
            {"Response": self.botSay.Response, "Metadata": self.botSay.Metadata})

    def userUpdate(self, inputData: str):
        try:
            data = json.loads(inputData)
            logging.info(data)
        except:
            raise TypeError

        if data["DataType"] not in ["raw", "sys", "clicked"]:
            raise TypeError
        if data["Data"] == "":
            raise TypeError

        self.userSay.Message = data["Data"]
        self.userSay.Type = data["DataType"]
        self.chatHistory.append([self.userSay.Message, "Client"])

    def restart(self, s, m):
        import copy
        self.currentNode = copy.deepcopy(s)
        self.recursive = []
        self.intentLog = [[]]
        self.botSay = botWant()
        self.userSay = userSay()
        self.botUpdate("Keyword", m)
        self.userSay = userSay()


class botWant(object):
    def __init__(self):
        self.WantedFeature = None
        self.Response = None
        self.Metadata = None


class userSay(object):
    def __init__(self):
        self.Type = None
        self.Message = None
