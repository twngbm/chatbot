import warnings
import logging
import json
import os
import random
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    from ckiptagger import data_utils, construct_dictionary, WS, POS, NER


class UndefineInput(Exception):
    pass


class chatbot(object):
    def __init__(self):
        self.__PATH__ = os.path.dirname(os.path.abspath(__file__))
        logging.critical("Loading Solution List")
        with open(self.__PATH__+"/solution.json", "r", encoding="utf-8") as f:
            self.solutionList = json.load(f)
        logging.critical("Solution List Loaded")
        self.transformer = Transformer()
        self.MessageGeneator = MessageGeneator()

    def chat(self, sentence, clientStatus):
        currentSolutionList = clientStatus[0]
        knownInfo = clientStatus[1]
        hoshiiFeature = clientStatus[2]
        if currentSolutionList == None and knownInfo == None:
            currentSolutionList = self.solutionList[:]
            knownInfo = {}
            hoshiiFeature = "Keyword"
            return self.__GetMessage__(hoshiiFeature), [currentSolutionList, knownInfo, hoshiiFeature]
        if sentence == None:
            return "", [currentSolutionList, knownInfo]

        # Find Matched Solution
        unMatchSolution = []
        for solution in currentSolutionList:
            inputParser = solution["Feature"][hoshiiFeature]["InputParser"]
            key = solution["Feature"][hoshiiFeature]["Key"]
            processedData = sentence
            for functionName in inputParser:
                try:
                    preprocessor = getattr(self.transformer, functionName)
                except:
                    logging.error(
                        "No Function Named{fn}".format(fn=functionName))
                    raise NotImplementedError
                try:
                    processedData = preprocessor(processedData)
                except UndefineInput:
                    return self.__GetMessage__(hoshiiFeature, True), [currentSolutionList, knownInfo, hoshiiFeature]

            inputFeature = processedData
            if key not in inputFeature:
                unMatchSolution.append(solution)

        knownInfo[hoshiiFeature] = inputFeature
        for i in unMatchSolution:
            currentSolutionList.remove(i)
        for i in currentSolutionList:
            print(i["Answer"])
        if currentSolutionList == []:
            try:
                errorMessage = self.__GetMessage__(hoshiiFeature, True)
            except:
                errorMessage = self.MessageGeneator.handleUnable()
            print(errorMessage)
            knownInfo.pop(hoshiiFeature)
            return self.MessageGeneator.handleUnable(), [unMatchSolution, knownInfo, hoshiiFeature]

        elif len(currentSolutionList) == 1:
            ans = currentSolutionList[0]["Answer"]
            # print(self.solutionList)
            knownInfo.pop("Keyword")
            return ans+"\n"+self.__GetMessage__("Keyword"), [self.solutionList[:], knownInfo, "Keyword"]
        nextHoshiiFeature = self.__findWantedKey__(
            currentSolutionList, knownInfo)
        return self.__GetMessage__(nextHoshiiFeature), [currentSolutionList, knownInfo, nextHoshiiFeature]

    def __findWantedKey__(self, currentSolutionList, knownInfo):
        if "Keyword" not in knownInfo:
            return "Keyword"
        keyCount = {}

        for solution in currentSolutionList:
            for key in solution["Feature"]:
                try:
                    keyCount[key] += 1
                except:
                    keyCount[key] = 1
        priority = sorted(keyCount, key=lambda x: keyCount[x], reverse=True)
        mostWantedKey = []
        mostWantedKeyCount = keyCount[priority[0]]
        for k in priority:
            if keyCount[k] != mostWantedKeyCount:
                break
            if k not in knownInfo:
                mostWantedKey.append(k)
        print(mostWantedKey)
        return random.choice(mostWantedKey)

    def __GetMessage__(self, featureName, exception=False):
        return getattr(self.MessageGeneator, featureName)(exception)


class MessageGeneator(object):
    def __init__(self):
        pass

    def handleUnable(self):
        return "無法處理，可能輸入錯誤?"

    def Keyword(self, exception):
        if exception:
            return "我也想要進來"
        return "我要進來了喔"

    def Location(self, exception):
        if exception:
            return "輸入錯誤"
        return "請輸入地點"

    def StudentID(self, exception):
        if exception:
            return "學號格式錯誤"
        return "請輸入學號"

    def NetConfig(self, exception):
        if exception:
            return "請回答DHCP/PPPOE"
        return "請檢查網路設定"

    def DormRoom(self, exception):
        if exception:
            return "請回答正確宿舍與房號"
        return "請回答宿舍與房號"

    def ChengKungPortal(self, exception):
        if exception:
            return "請回答成功/失敗"
        return "請檢查帳號密碼是否可登入成功入口"

    def JupyterInstalled(self, exception):
        if exception:
            return "請回答成功/失敗"
        return "請檢查安裝VPN軟體Jupyter Notebook成功或失敗"

    def ComputerTimeSet(self, exception):
        if exception:
            return "請回答正常/異常"
        return "請檢查系統時間"

    def RunAsAdmin(self, exception):
        if exception:
            return "請回答是/否"
        return "是否以系統管理者身分執行"


class Transformer(object):
    def __init__(self):
        self.__PATH__ = os.path.dirname(os.path.abspath(__file__))
        logging.critical("Loading CKIP Data")
        logging.critical("WS Loading")
        self.ws = WS(self.__PATH__+"/data")
        logging.critical("WS Loaded")
        logging.critical("POS Loading")
        #self.pos = POS(self.__PATH__+"/data")
        logging.critical("POS Loaded")
        logging.critical("NER Loading")
        #self.ner = NER(self.__PATH__+"/data")
        logging.critical("NER Loaded")

    def CKIPParser(self, sentence):
        word_to_weight = {
            "網路": 1,
            "連線": 1,
            "宿舍": 1,
            "宿網": 2,
            "授權軟體": 1,
            "VPN": 1,
        }
        dictionary = construct_dictionary(word_to_weight)

        word_sentence_list = self.ws(
            [sentence],
            coerce_dictionary=dictionary,
        )
        #pos_sentence_list = self.pos(word_sentence_list)
        #entity_sentence_list = self.ner(word_sentence_list, pos_sentence_list)

        for i, sentence in enumerate([sentence]):

            keyword = []
            for word in word_sentence_list[i]:
                if word in word_to_weight:
                    keyword.append(word)
        logging.info("CKIP find TOKEN : {token}".format(token=str(keyword)))
        return keyword

    def LocationParser(self, feature):
        return feature

    def checkDormNetIDUsage(self, feature):
        n = feature[-1]
        try:
            n = int(n)
        except:
            raise UndefineInput
        if n % 2 == 0:
            return "OverUse"
        else:
            return "NoneOverUse"

    def checkDormNetSwitchHealthy(self, feature):
        if "勝" in feature:
            return "Alive"
        elif "光" in feature:
            return "Dead"
        else:
            raise UndefineInput

    def Google(self, sentenct, feature):
        return "Google Say this is:"+str(sentenct)
