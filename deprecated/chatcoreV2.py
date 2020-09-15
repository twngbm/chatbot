from question_generator import MessageGeneator
import logging
import json
import os
import csv
import random
import warnings
import asyncio
import time
from ChatbotConfig import *
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    from ckiptagger import data_utils, construct_dictionary, WS, POS
import nest_asyncio
nest_asyncio.apply()

__PATH__ = os.path.dirname(os.path.abspath(__file__))+"/"

logging.critical("Loading Solution List")
with open(__PATH__+SOLUTION, "r", encoding="utf-8") as f:
    solutionList = json.load(f)

logging.critical("Loading Encouraged Dictionary")
with open(__PATH__+ENCDICT, "r", encoding="utf-8") as f:
    encouragedDictionary = json.load(f)

logging.critical("Loading IT Table")
with open(__PATH__+ITTABLE, "r", encoding="utf-8-sig") as csvfile:
    rows = csv.reader(csvfile)
    header = next(rows)
    header[0] = "代號"
    header[6] = "業務負責人分機"
    header[8] = "系統負責人分機"
    header[9] = "備註"
    header = header[:10]
    ITinfotable = {}
    for row in rows:
        ITinfotable[row[1]] = dict(zip(header, row))
    ITinfotableKey = list(ITinfotable.keys())
encouragedDictionary = {**encouragedDictionary, **
                        dict(zip(ITinfotableKey, [2]*len(ITinfotableKey)))}

for ITsys, ITsysItem in ITinfotable.items():
    ans = "該系統功能簡述:<br>"+ITsysItem["功能簡述"]+"<br>業務單位: " + \
        ITsysItem["業務單位"]+"<br>業務負責人分機: "+ITsysItem["業務負責人分機"]+"<br>系統負責人: " + \
        ITsysItem["系統負責人"]+"<br>系統負責人分機: "+ITsysItem["系統負責人分機"]+"<br>"
    solutionList.append({"Feature": {"Keyword": {"InputParser": [
        "intentParser"], "Key": ITsys}}, "Answer": ans, "Stop": True})


logging.critical("Loading Question Table")
with open(__PATH__+QUESTION, "r", encoding="utf-8-sig") as q:
    temp = json.load(q)
    question = {list(i.keys())[0]: i[list(i.keys())[0]] for i in temp}


logging.critical("Loading CKIP-Word Segmentation(WS)")
ws = WS(__PATH__+CKIPDATA)
logging.critical("Loading CKIP-Part-of-Speech(POS)")
#pos = POS(__PATH__+CKIPDATA)


class UndefineInput(Exception):
    pass


class Chatbot(object):

    @staticmethod
    async def chat(sentence, clientStatus):

        currentSolutionList = clientStatus["currentList"]
        knownInfo = clientStatus["knownInfo"]
        wantedFeature = clientStatus["wantedInfo"]
        history = clientStatus["history"]
        if (history == [] and sentence == None) or sentence == "restart":
            currentSolutionList = solutionList[:]
            knownInfo = {}
            wantedFeature = Chatbot.__findWantedKey__(
                currentSolutionList, knownInfo)
            history.append(Chatbot.__GetMessage__(wantedFeature))
            clientStatus["knownInfo"] = knownInfo
            clientStatus["currentList"] = currentSolutionList
            clientStatus["wantedInfo"] = wantedFeature
            clientStatus["history"] = history

            return Chatbot.__GetMessage__(wantedFeature), clientStatus

        history.append(sentence)
        
        if wantedFeature == "isSolved":
            nextWantedFeature = Chatbot.__findWantedKey__(
                currentSolutionList, knownInfo)
            if Transformer.BooleanParser([sentence])[0] or nextWantedFeature == None:
                history.append(Chatbot.__GetMessage__("EndMessage"))
                updateClientStatus = {
                    "currentList": solutionList[:], "knownInfo": {}, "history": history, "wantedInfo": "Keyword"}
                return Chatbot.__GetMessage__("EndMessage"), updateClientStatus

            elif not Transformer.BooleanParser([sentence])[0]:
                history.append(Chatbot.__GetMessage__(nextWantedFeature))
                updateClientStatus = {"currentList": currentSolutionList,
                                      "knownInfo": knownInfo, "history": history, "wantedInfo": nextWantedFeature}
                return Chatbot.__GetMessage__(nextWantedFeature), updateClientStatus

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
                    preprocessor = getattr(Transformer, functionName)
                except:
                    logging.error(
                        "No Function Named{fn}".format(fn=functionName))
                    raise NotImplementedError
                try:
                    #loop=asyncio.get_event_loop()
                    processedData=await preprocessor(processedData)
                    
                    #processedData = preprocessor(processedData)
                except TypeError:
                    raise TypeError
                except UndefineInput:
                    history.append(Chatbot.__GetMessage__(
                        wantedFeature, True)+"，或輸入restart以重新開始")
                    updateClientStatus = {"currentList": currentSolutionList,
                                          "knownInfo": knownInfo, "history": history, "wantedInfo": wantedFeature}

                    return Chatbot.__GetMessage__(wantedFeature, True)+"，或輸入restart以重新開始", updateClientStatus

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
                errorMessage = Chatbot.__GetMessage__(wantedFeature, True)
            except:
                pass
            knownInfo.pop(wantedFeature)
            errorMessage += "，或輸入restart以重新開始"
            for i in unMatchSolution:
                currentSolutionList.append(i)
            history.append(errorMessage)
            updateClientStatus = {"currentList": currentSolutionList,
                                  "knownInfo": knownInfo, "history": history, "wantedInfo": wantedFeature}

            return errorMessage, updateClientStatus
        
        # Answer Finded
        elif len(currentSolutionList) == 1:

            ans = currentSolutionList[0]["Answer"]
            ansText = ans+"<br>"+Chatbot.__GetMessage__("isSolved")
            history.append(ansText)

            if "Stop" in currentSolutionList[0]:
                ansText = ans+"<br>"+Chatbot.__GetMessage__("EndMessage")
                history.append(ansText)
                updateClientStatus = {
                    "currentList": solutionList[:], "knownInfo": {}, "history": history, "wantedInfo": "Keyword"}
                return ansText, updateClientStatus
            else:
                updateClientStatus = {
                    "currentList": unMatchSolution, "knownInfo": knownInfo, "history": history, "wantedInfo": "isSolved"}
                return ansText, updateClientStatus
        
        # Find Next Wanted Feature and Ask Question
        nextWantedFeature = Chatbot.__findWantedKey__(
            currentSolutionList, knownInfo)

        history.append(Chatbot.__GetMessage__(nextWantedFeature))
        updateClientStatus = {"currentList": currentSolutionList,
                              "knownInfo": knownInfo, "history": history, "wantedInfo": nextWantedFeature}

        return Chatbot.__GetMessage__(nextWantedFeature), updateClientStatus

    @staticmethod
    def __findWantedKey__(currentSolutionList, knownInfo):
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

    @staticmethod
    def __GetMessage__(featureName, exception=False):
        try:
            if exception:
                return random.choice(question[featureName]["Exception"])
            return random.choice(question[featureName]["Question"])
            
        except:
            raise NotImplementedError


class Transformer(object):

    @staticmethod
    def intentParser():
        pass

    @staticmethod
    async def CKIPParser(sentence):

        dictionary = construct_dictionary(encouragedDictionary)
        
        word_sentence_list = ws(
            sentence,
            recommend_dictionary=dictionary
        )
        
        #pos_sentence_list = pos(word_sentence_list)

        for i, sentence in enumerate([sentence]):
            keyword = []
            for word in word_sentence_list[i]:
                if word in encouragedDictionary:
                    keyword.append(word)
        if keyword == []:
            raise UndefineInput
        
        return keyword

    @staticmethod
    def LocationParser(feature):
        return feature

    @staticmethod
    def DormIDUsage(feature):

        n = feature[0][-1]
        try:
            n = int(n)
        except:
            raise UndefineInput
        if n % 2 == 0:
            return [False]
        else:
            return [True]

    @staticmethod
    def DormHWChecker(feature):

        if "勝" in feature[0]:
            return [True]
        elif "光" in feature[0]:
            return [False]
        else:
            raise UndefineInput

    @staticmethod
    def LanLocationParser(feature):
        return feature

    @staticmethod
    def BooleanParser(feature):
        if feature[0] in ["Yes", "正確", "是", "成功", "有", "校內", "正常"]:
            return [True]
        elif feature[0] in ["No", "錯誤", "否", "非", "失敗", "沒有", "無", "異常"]:
            return [False]
        else:
            return None
    @staticmethod
    def IPDomainParser(feature):
        pass


    @staticmethod
    def ISParser(feature):
        n = feature[0][-1]
        try:
            n = int(n)
        except:
            raise UndefineInput
        if n % 2 == 0:
            return [False]
        else:
            return [True]

    @staticmethod
    def QDParser(feature):
        return feature
