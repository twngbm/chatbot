from question_generator import MessageGeneator
import warnings
import logging
import json
import os
import csv
import random
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    from ckiptagger import data_utils, construct_dictionary, WS, POS, NER


# User Input -> CKIP -> Google Fuzzy Search -> Keyword Match
class UndefineInput(Exception):
    pass


class Chatbot(object):
    def __init__(self):
        self.__PATH__ = os.path.dirname(os.path.abspath(__file__))
        logging.critical("Loading Solution List")
        with open(self.__PATH__+"/test.json", "r", encoding="utf-8") as f:
            self.solutionList = json.load(f)
        logging.critical("Solution List Loaded")
        self.transformer = Transformer()
        self.MessageGeneator = MessageGeneator()
        self.solutionAppend()
        
    def solutionAppend(self):
        for ITsys in self.transformer.ITinfotable:
            ITsysItem = self.transformer.ITinfotable[ITsys]
            ans = "該系統功能簡述:\n"+ITsysItem["功能簡述"]+"\n業務單位: " + \
                ITsysItem["業務單位"]+"\n業務負責人分機: "+ITsysItem["業務負責人分機"]+"\n系統負責人: " + \
                ITsysItem["系統負責人"]+"\n系統負責人分機: "+ITsysItem["系統負責人分機"]+"\n"
            self.solutionList.append({"Feature": {"Keyword": {"InputParser": [
                                     "CKIPParser"], "Key": ITsys}}, "Answer": ans,"Stop":True})
    def chat(self, sentence, clientStatus):
        currentSolutionList = clientStatus["currentList"]
        knownInfo = clientStatus["knownInfo"]
        wantedFeature = clientStatus["wantedInfo"]
        history = clientStatus["history"]

        if (history == [] and sentence == None) or sentence=="restart":
            currentSolutionList = self.solutionList[:]
            knownInfo={}
            wantedFeature = self.__findWantedKey__(
                currentSolutionList, knownInfo)
            history.append(self.__GetMessage__(wantedFeature))
            updatedClientStatus = {"currentList": currentSolutionList,
                                   "knownInfo": knownInfo, "history": history, "wantedInfo": wantedFeature}
            return self.__GetMessage__(wantedFeature), updatedClientStatus

        history.append(sentence)

        if wantedFeature == "isSolved":
            nextWantedFeature = self.__findWantedKey__(
                currentSolutionList, knownInfo)
            if self.transformer.BooleanParser([sentence])[0] or nextWantedFeature == None:
                history.append(self.__GetMessage__("EndMessage"))
                updateClientStatus = {
                    "currentList": self.solutionList[:], "knownInfo": {}, "history": history, "wantedInfo": "Keyword"}

                return self.__GetMessage__("EndMessage"), updateClientStatus
            elif not self.transformer.BooleanParser([sentence][0]):
                history.append(self.__GetMessage__(nextWantedFeature))
                updateClientStatus = {"currentList": currentSolutionList,
                                      "knownInfo": knownInfo, "history": history, "wantedInfo": nextWantedFeature}
                return self.__GetMessage__(nextWantedFeature), updateClientStatus

        unMatchSolution = []

        for solution in currentSolutionList:
            try:
                inputParser = solution["Feature"][wantedFeature]["InputParser"]
                key = solution["Feature"][wantedFeature]["Key"]
            except:
                unMatchSolution.append(solution)
                continue

            processedData = [sentence]
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
                    history.append(self.__GetMessage__(wantedFeature, True))
                    updateClientStatus = {"currentList": currentSolutionList,
                                          "knownInfo": knownInfo, "history": history, "wantedInfo": wantedFeature}
                    return self.__GetMessage__(wantedFeature, True)+"，或輸入restart以重新開始", updateClientStatus

            inputFeature = processedData
            if len(inputFeature) == 1:
                if key != inputFeature[0]:
                    unMatchSolution.append(solution)
            else:
                findflag = False
                for i in inputFeature:
                    if i == key:
                        findflag = True
                    if not findflag:
                        unMatchSolution.append(solution)
        knownInfo[wantedFeature] = sentence

        # Update currentSolutionList due to unMatchSolution

        for i in unMatchSolution:
            currentSolutionList.remove(i)

        # No answer match, Asume user have wrong input
        if currentSolutionList == []:
            try:
                errorMessage = self.__GetMessage__(wantedFeature, True)
            except:
                errorMessage = self.MessageGeneator.handleUnable()
            knownInfo.pop(wantedFeature)
            for i in unMatchSolution:
                currentSolutionList.append(i)
            history.append(errorMessage)
            updateClientStatus = {"currentList": currentSolutionList,
                                  "knownInfo": knownInfo, "history": history, "wantedInfo": wantedFeature}
            return errorMessage+"，或輸入restart以重新開始", updateClientStatus

        # Answer Finded
        elif len(currentSolutionList) == 1:
            ans = currentSolutionList[0]["Answer"]
            history.append(ans+"\n"+self.__GetMessage__("isSolved"))
            if "Stop" in currentSolutionList[0]:
                history.append(self.__GetMessage__("EndMessage"))
                updateClientStatus = {
                    "currentList": self.solutionList[:], "knownInfo": {}, "history": history, "wantedInfo": "Keyword"}
                return ans+"\n"+self.__GetMessage__("EndMessage"), updateClientStatus
            else:
                updateClientStatus = {
                    "currentList": unMatchSolution, "knownInfo": knownInfo, "history": history, "wantedInfo": "isSolved"}
                return ans+"\n"+self.__GetMessage__("isSolved"), updateClientStatus

        # Find Next Wanted Feature and Ask Question
        nextWantedFeature = self.__findWantedKey__(
            currentSolutionList, knownInfo)

        history.append(self.__GetMessage__(nextWantedFeature))
        updateClientStatus = {"currentList": currentSolutionList,
                              "knownInfo": knownInfo, "history": history, "wantedInfo": nextWantedFeature}

        return self.__GetMessage__(nextWantedFeature), updateClientStatus

    def __findWantedKey__(self, currentSolutionList, knownInfo):
        keyCount = {}
        # print(currentSolutionList)
        # print(knownInfo)
        for solution in currentSolutionList:
            for key in solution["Feature"]:
                if key in knownInfo:
                    continue
                try:
                    keyCount[key] += 1
                except:
                    keyCount[key] = 1
        if keyCount == {}:
            return None
        maxKeyCount = max(keyCount.values())
        mostWantedKey = [k for k in keyCount if maxKeyCount == keyCount[k]]
        # print(mostWantedKey)
        return random.choice(mostWantedKey)

    def __GetMessage__(self, featureName, exception=False):
        return getattr(self.MessageGeneator, featureName)(exception)


class Transformer(object):
    def __init__(self):
        self.__PATH__ = os.path.dirname(os.path.abspath(__file__))
        logging.critical("Loading CKIP Data")
        logging.critical("WS Loading")
        self.ws = WS(self.__PATH__+"/data")
        logging.critical("WS Loaded")
        logging.critical("POS Loading")
        # self.pos = POS(self.__PATH__+"/data")
        logging.critical("POS Loaded")
        logging.critical("NER Loading")
        # self.ner = NER(self.__PATH__+"/data")
        logging.critical("NER Loaded")
        with open(self.__PATH__+"/ckip.json", "r", encoding="utf-8") as f:
            self.word_to_weight = json.load(f)

        logging.critical("Information Technical Principal Loading and Parsing")
        self.ITPrincipalParser()
        self.word_to_weight = {**self.word_to_weight, **
                               dict(zip(self.ITinfotableKey, [2]*len(self.ITinfotableKey)))}
        

    def ITPrincipalParser(self):
        ITPrincipal = "ITPrincipal.csv"

        with open(ITPrincipal, "r", encoding="utf-8-sig") as csvfile:
            rows = csv.reader(csvfile)
            header = next(rows)
            header[0] = "代號"
            header[6] = "業務負責人分機"
            header[8] = "系統負責人分機"
            header[9] = "備註"
            header = header[:10]

            self.ITinfotable = {}
            for row in rows:
                self.ITinfotable[row[1]] = dict(zip(header, row))
            self.ITinfotableKey = list(self.ITinfotable.keys())
    
    def intentParser(self):
        pass

    def CKIPParser(self, sentence):
        word_to_weight = self.word_to_weight
        dictionary = construct_dictionary(word_to_weight)

        word_sentence_list = self.ws(
            sentence,
            coerce_dictionary=dictionary,
        )
        # pos_sentence_list = self.pos(word_sentence_list)
        # entity_sentence_list = self.ner(word_sentence_list, pos_sentence_list)

        for i, sentence in enumerate([sentence]):

            keyword = []
            for word in word_sentence_list[i]:
                if word in word_to_weight:
                    keyword.append(word)
        # logging.info("CKIP find TOKEN : {token}".format(token=str(keyword)))
        if keyword == []:
            raise UndefineInput
        print(keyword)
        return keyword

    def LocationParser(self, feature):
        return feature

    def DormIDUsage(self, feature):

        n = feature[0][-1]
        try:
            n = int(n)
        except:
            raise UndefineInput
        if n % 2 == 0:
            return [False]
        else:
            return [True]

    def DormHWChecker(self, feature):

        if "勝" in feature[0]:
            return [True]
        elif "光" in feature[0]:
            return [False]
        else:
            raise UndefineInput

    def Google(self, sentenct, feature):
        return "Google Say this is:"+str(sentenct)

    def LanLocationParser(self, feature):
        return feature

    def BooleanParser(self, feature):
        if feature[0] in ["Yes", "正確", "是", "成功", "有", "校內", "正常"]:
            return [True]
        elif feature[0] in ["No","錯誤","否","非","失敗","沒有","無","異常"]:
            return [False]
        else:
            return None

    def IPDomainParser(self, feature):
        pass

    def ISParser(self, feature):
        n = feature[0][-1]
        try:
            n = int(n)
        except:
            raise UndefineInput
        if n % 2 == 0:
            return [False]
        else:
            return [True]

    def QDParser(self, feature):
        return feature
