import json
import logging


class User(object):
    def __init__(self):
        self.userID = ""
        self.currentNode = {}
        self.chatHistory = []
        self.intentLog = [[]]
        self.botSay = botWant()
        self.userSay = userSay()  # type=[control,raw,checked]
        self.recursive = []
        self.sendbackMessage = None

    def botUpdate(self, feature, response, metadate=None):
        self.botSay.WantedFeature = feature
        self.botSay.Response = response
        self.chatHistory.append([response, "Server"])
        self.botSay.Metadata = metadate
        self.sendbackMessage = json.dumps(
            {"Response": self.botSay.Response, "Metadata": self.botSay.Metadata}, ensure_ascii=False)

    def userUpdate(self, inputData: str):
        try:
            data = json.loads(inputData)
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
