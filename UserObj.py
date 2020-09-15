class User(object):
    def __init__(self):
        self.currentNode={}
        # TODO:Previous Step
        #self.path=[]
        self.chatHistory=[]
        self.token=None
        self.botSay=botWant()
        self.userSay=userSay()#type=[control,raw,checked]
        self.recursive=[]
        self.otp=None#Restore Key
    def botUpdate(self,feature,response,metadate=None):
        self.botSay.WantedFeature=feature
        self.botSay.Response=response
        self.chatHistory.append(response)
        self.botSay.Metadata=metadate
    def userUpdate(self,message:str):
        for prefix in ["clicked_","raw_","sys_"]:
            if message.find(prefix)==0:
                self.userSay.Message=message.split(prefix)[1]
                self.userSay.Type=prefix[:-1]
                if prefix!="sys_":
                    self.chatHistory.append(self.userSay.Message)
                break
class botWant(object):
    def __init__(self):
        self.WantedFeature=None
        self.Response=None
        self.Metadata=None
class userSay(object):
    def __init__(self):
        self.Type=None
        self.Message=None