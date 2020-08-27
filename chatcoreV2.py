from question_generator import MessageGeneator
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


class Chatbot(object):
    def __init__(self):
        self.__PATH__ = os.path.dirname(os.path.abspath(__file__))
        logging.critical("Loading Solution List")
        with open(self.__PATH__+"/test.json", "r", encoding="utf-8") as f:
            self.solutionList = json.load(f)
        # print(self.solutionList)
        logging.critical("Solution List Loaded")
        self.transformer = Transformer()
        self.MessageGeneator = MessageGeneator()

    def chat(self, sentence, clientStatus):
        currentSolutionList = clientStatus["currentList"]
        knownInfo = clientStatus["knownInfo"]
        wantedFeature = clientStatus["wantedInfo"]
        history = clientStatus["history"]

        if history == [] and sentence==None:
            currentSolutionList = self.solutionList[:]
            wantedFeature=self.__findWantedKey__(currentSolutionList,knownInfo)
            history.append(self.__GetMessage__(wantedFeature))
            updatedClientStatus={"currentList":currentSolutionList,"knownInfo":knownInfo,"history":history,"wantedInfo":wantedFeature}
            return self.__GetMessage__(wantedFeature),updatedClientStatus
            #wantedFeature = "Keyword"
            #history.append(self.__GetMessage__(wantedFeature))
            #updateClientStatus = {"currentList": currentSolutionList,
            #                      "knownInfo": knownInfo, "history": history, "wantedInfo": wantedFeature}
            #return self.__GetMessage__(wantedFeature), updateClientStatus
        
        #if sentence == None:
        #    return "", clientStatus
        
        history.append(sentence)

        if wantedFeature == "isSolved":
            nextWantedFeature = self.__findWantedKey__(
                currentSolutionList, knownInfo)
            if self.transformer.BooleanParser([sentence])[0] or nextWantedFeature == None:
                history.append(self.__GetMessage__("EndMessage"))
                updateClientStatus = {
                    "currentList": self.solutionList[:], "knownInfo": {}, "history": history, "wantedInfo": "Keyword"}

                return self.__GetMessage__("EndMessage"), updateClientStatus
            else:
                history.append(self.__GetMessage__(nextWantedFeature))
                updateClientStatus = {"currentList": currentSolutionList,
                                      "knownInfo": knownInfo, "history": history, "wantedInfo": nextWantedFeature}
                return self.__GetMessage__(nextWantedFeature), updateClientStatus

        # Find Matched Solution
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
                    return self.__GetMessage__(wantedFeature, True), updateClientStatus

            inputFeature = processedData
            if len(inputFeature) == 1:
                if key != inputFeature[0]:
                    unMatchSolution.append(solution)
            else:
                findflag=False
                for i in inputFeature:
                    if i==key:
                        findflag=True
                    if not findflag:
                        unMatchSolution.append(solution)
        #print(inputFeature,key)
        knownInfo[wantedFeature] = sentence

        # Update currentSolutionList due to unMatchSolution
        
        for i in unMatchSolution:
            # print(i)
            currentSolutionList.remove(i)

        
        for i in currentSolutionList:

            # print(i["Feature"],"\n",i["Answer"])
            pass
        

        # No answer match, Asume user have wrong input
        if currentSolutionList == []:
            try:
                errorMessage = self.__GetMessage__(wantedFeature, True)
            except:
                errorMessage = self.MessageGeneator.handleUnable()
            # print(errorMessage)
            knownInfo.pop(wantedFeature)
            for i in unMatchSolution:
                currentSolutionList.append(i)
            history.append(errorMessage)
            updateClientStatus = {"currentList": currentSolutionList,
                                  "knownInfo": knownInfo, "history": history, "wantedInfo": wantedFeature}
            return errorMessage, updateClientStatus

        # Answer Finded
        elif len(currentSolutionList) == 1:
            ans = currentSolutionList[0]["Answer"]
            history.append(ans+"\n"+self.__GetMessage__("isSolved"))
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
            sentence,
            coerce_dictionary=dictionary,
        )
        #pos_sentence_list = self.pos(word_sentence_list)
        #entity_sentence_list = self.ner(word_sentence_list, pos_sentence_list)

        for i, sentence in enumerate([sentence]):

            keyword = []
            for word in word_sentence_list[i]:
                if word in word_to_weight:
                    keyword.append(word)
        #logging.info("CKIP find TOKEN : {token}".format(token=str(keyword)))
        if keyword==[]:
            raise UndefineInput
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
        if feature[0] in ["Yes", "正確", "是", "成功", "有","校內","正常"]:
            return [True]
        return [False]
    def IPDomainParser(self,feature):
        pass
    def ISParser(self,feature):
        n = feature[0][-1]
        try:
            n = int(n)
        except:
            raise UndefineInput
        if n % 2 == 0:
            return [False]
        else:
            return [True]
    def QDParser(self,feature):
        return feature