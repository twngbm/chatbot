import UserObj
import copy
import random
from fuzzywuzzy import fuzz, process
import json
import csv
from ChatbotConfig import *
import logging
import os
import warnings
import re
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class LoaderUtils():
    def __init__(self):
        __PATH__ = os.path.dirname(os.path.abspath(__file__))+"/"
        logging.critical("Loading Solution Tree")
        with open(__PATH__+SOLUTION, "r", encoding="utf-8") as f:
            self.solutionList = json.load(f)

        logging.critical("Loading Similar Dictionary")
        with open(__PATH__+SIMILAR, "r", encoding="utf-8") as f:
            similarList = json.load(f)
        self.similarDict = {}
        for main, sim in similarList.items():
            self.similarDict[main] = main
            for s in sim:
                self.similarDict[s] = main

        logging.critical("Loading Encouraged Dictionary")
        with open(__PATH__+ENCDICT, "r", encoding="utf-8") as f:
            encouragedList = json.load(f)

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

        self.encouragedDict = {x: 2 for x in encouragedList+ITinfotableKey}

        for ITsys, ITsysItem in ITinfotable.items():
            ans = {"系統概述": ITsysItem["功能簡述"],
                   "業務單位": "業務單位/承辦人:{}<br>業務單位分機:{}".format(ITsysItem["業務單位"], ITsysItem["業務負責人分機"]),
                   "系統負責單位": "系統負責單位/承辦人:{}<br>系統負責單位分機:{}".format(ITsysItem["系統負責人"], ITsysItem["系統負責人分機"])}
            #self.solutionList["Keyword"][ITsys] = {"Checklist": ans}

        logging.critical("Loading Question Table")
        with open(__PATH__+QUESTION, "r", encoding="utf-8-sig") as q:
            temp = json.load(q)
        self.question = {
            list(i.keys())[0]: i[list(i.keys())[0]] for i in temp}


class ServerUtils():

    @staticmethod
    async def createNewUser(clientInfo, data, websocket):
        userIP, userPort = clientInfo[0], clientInfo[1]
        userID = ":".join([str(userIP), str(userPort)])
        user = UserObj.User(data, userID)
        logging.info(f"Initinal New Client on {userIP}:{userPort}")
        await ServerUtils.messageSend(user, websocket)
        return user

    @staticmethod
    async def messageSend(user, websocket):
        logging.info(f'{user.userID} <<<<<< {user.sendbackMessage}')
        await websocket.send(user.sendbackMessage)

    @staticmethod
    def messageReceive(user, rawMessage: str):
        logging.info(f"{user.userID} >>>>>> {rawMessage}")
        user.userUpdate(rawMessage)


class ChatUtils():
    def __init__(self, data: LoaderUtils):
        self.data = data

    def getQuestion(self, featureName,  exception=False) -> str:
        question = self.data.question

        try:
            if exception:
                return random.choice(question[featureName]["Exception"])
            return random.choice(question[featureName]["Question"])
        except:
            return random.choice(question["default"]["Question"])

    @staticmethod
    def isURL(url: str) -> bool:
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            # domain...
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None

    @staticmethod
    def isIMG(path: str) -> bool:
        for i in [".png", ".jpeg", ".jpg", ".gif", ".bmp"]:
            if i in path:
                return True
        return False


class IntentUtils():
    def __init__(self, data: LoaderUtils):
        __PATH__ = os.path.dirname(os.path.abspath(__file__))+"/"
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            from ckiptagger import POS, WS, construct_dictionary, data_utils
        self.data = data
        self.solutionList = self.data.solutionList
        self.question = self.data.question
        self.similarDict = self.data.similarDict
        self.encouragedDict = self.data.encouragedDict
        self.encouragedDict = construct_dictionary(self.encouragedDict)

        self.data = data
        logging.critical("Loading CKIP-Word Segmentation(WS)")
        self.ws = WS(__PATH__+CKIPDATA)
        logging.critical("Loading CKIP-Part-of-Speech(POS)")
        self.pos = POS(__PATH__+CKIPDATA)

    def intentParser(self, message, candidate, noDFS=False) -> list:
        if message in candidate:
            # Phase1: If message 100% match candidate
            return [message]

        # Phase2: POS and fuzzy match throught candidate
        tokenList, token_posList = self.__CKIP__(message)

        fuzzyMatched = self.__fuzzymatcher__(
            tokenList, token_posList, candidate)

        if fuzzyMatched != []:
            return fuzzyMatched
        if noDFS:
            return fuzzyMatched

        # Phase3: Try Sub-root search
        # For example: user input : "密碼", System will try to find out ["成功入口","電子信箱"]
        # since both have a "**密碼**" solution
        subMatch = self.__submatch__(tokenList, token_posList)
        if subMatch != []:
            return subMatch

        # Phase #: Unable to find any user intent
        return []

    def __CKIP__(self, message):
        word_sentence_list = self.ws(
            [message],
            sentence_segmentation=True,
            coerce_dictionary=self.encouragedDict)
        pos_sentence_list = self.pos(word_sentence_list)
        return word_sentence_list[0], pos_sentence_list[0]

    def __fuzzymatcher__(self, tokenList, token_posList, candidate) -> list:

        recommend = {}
        droped_list = CKIP_MARK+CKIP_UNWANTED

        for token, token_pos in zip(tokenList, token_posList):
            if token_pos in droped_list:
                continue

            similarPair = process.extractBests(
                token, [*self.similarDict], scorer=fuzz.UWRatio)
            similarText = similarPair[0][0]
            similarScore = similarPair[0][1]
            fuzzymatch = process.extract(
                token, candidate, limit=2, scorer=fuzz.UWRatio)

            similarFuzzymatch = []
            if similarScore >= CONFIDENCE_ACCEPT_THRESHOLD:
                similarFuzzymatch = process.extract(
                    self.similarDict[similarText], candidate, limit=2, scorer=fuzz.UWRatio)

            for match_str, confidence in fuzzymatch+similarFuzzymatch:
                if confidence < CONFIDENCE_DROP_THRESHOLD:
                    continue
                try:
                    recommend[confidence]
                    recommend[confidence].append(match_str)
                except:
                    recommend[confidence] = [match_str]
        if recommend == {}:
            return []
        logging.debug("Intent Score:"+str(recommend))
        maxFuzzy = max(recommend)
        fuzzyMatch = []
        if maxFuzzy >= CONFIDENCE_ACCEPT_THRESHOLD:
            return list(set(recommend[maxFuzzy]))
        for confidence, item in recommend.items():
            candidateGroup = list(set(item))
            if len(fuzzyMatch+candidateGroup) > MAX_INTEND_AMOUNT and fuzzyMatch != []:
                return list(set(fuzzyMatch))
            elif len(fuzzyMatch+candidateGroup) > MAX_INTEND_AMOUNT and fuzzyMatch == []:
                return list(set(candidateGroup))
            else:
                fuzzyMatch += candidateGroup
        return list(set(fuzzyMatch))

    def __submatch__(self, tokenList, token_posList) -> list:
        def dfs(node, head=None):
            nonlocal submatch
            nonlocal wantedToken
            featureName = [*node][0]
            if featureName == "Checklist" or featureName == "Function":
                return
            for feature in node[featureName]:
                if head == None:
                    dfs(node[featureName][feature], feature)
                    continue
                for token in wantedToken:
                    if token in feature:  # Match Method
                        submatch.append(head)
                dfs(node[featureName][feature], head)
        droped_list = CKIP_MARK+CKIP_UNWANTED
        wantedToken = []
        for token, token_pos in zip(tokenList, token_posList):
            if token_pos in droped_list:
                continue
            wantedToken.append(token)
        submatch = []
        dfs(self.solutionList)

        return list(set(submatch))


class FunctionUtils():
    def __init__(self, data: LoaderUtils):
        self.data = data
        self.ChatUtils = ChatUtils(self.data)

    def getMessage(self, *args):
        feature = args[0][0]
        return self.ChatUtils.getQuestion(feature), None, False

    def systemSearch(self, *args):
        # TODO
        return "0", None, False

    def getWeather(self, *args):
        import requests
        api_key = OPENWEATHER_APIKEY
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        city_name = "Tainan"
        complete_url = base_url + "appid=" + api_key + "&q=" + city_name
        response = requests.get(complete_url)
        x = response.json()
        y = x["main"]
        current_temperature = y["temp"]
        current_pressure = y["pressure"]
        current_humidiy = y["humidity"]
        z = x["weather"]
        weather_description = z[0]["description"]
        output = "攝氏溫度:{temp}°C<br>氣壓:{ap} hpa<br>相對溼度:{humidity} %<br>天氣概況:{wd}".format(
            temp=current_temperature, ap=current_pressure, humidity=current_humidiy, wd=weather_description)
        return output, None, False

    def getLocation(self, *args):
        return "img/nckumap.jpg", None, False
