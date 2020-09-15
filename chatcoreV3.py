import logging
import json
import os
import csv
import random
import warnings
import asyncio
import time
import copy
import UserObj
from ChatbotConfig import *
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    from ckiptagger import data_utils, construct_dictionary, WS, POS

__PATH__ = os.path.dirname(os.path.abspath(__file__))+"/"

logging.critical("Loading Solution Tree")
with open(__PATH__+SOLUTION, "r", encoding="utf-8") as f:
    solutionList = json.load(f)

logging.critical("Loading Similar Dictionary")
with open(__PATH__+SIMILAR, "r", encoding="utf-8") as f:
    similarList = json.load(f)
similarDict = {}
for main, sim in similarList.items():
    similarDict[main] = main
    for s in sim:
        similarDict[s] = main
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

encouragedDict = {x: 2 for x in encouragedList+ITinfotableKey}


for ITsys, ITsysItem in ITinfotable.items():
    ans = {"該系統功能簡述:<br>"+ITsysItem["功能簡述"]+"<br>業務單位: " +
           ITsysItem["業務單位"]+"<br>業務負責人分機: "+ITsysItem["業務負責人分機"]+"<br>系統負責人: " +
           ITsysItem["系統負責人"]+"<br>系統負責人分機: "+ITsysItem["系統負責人分機"]+"<br>": None}
    solutionList["Keyword"][ITsys] = {"Checklist": ans}


logging.critical("Loading Question Table")
with open(__PATH__+QUESTION, "r", encoding="utf-8-sig") as q:
    temp = json.load(q)
    question = {list(i.keys())[0]: i[list(i.keys())[0]] for i in temp}


logging.critical("Loading CKIP-Word Segmentation(WS)")
ws = WS(__PATH__+CKIPDATA)
logging.critical("Loading CKIP-Part-of-Speech(POS)")
pos = POS(__PATH__+CKIPDATA)


class Chatbot(object):

    async def chat(self, User: UserObj.User):

        # Restart Chat or Initinal Chat
        if User.chatHistory == [] or User.userSay.Message == "restart":
            User.currentNode = copy.deepcopy(solutionList)
            wantedFeature = "Keyword"
            featureMessage = self.__GetMessage__(wantedFeature)
            User.botUpdate(wantedFeature, featureMessage)
            return

        # Find out User Intent or Feature
        if User.userSay.Type == "sys":
            # Handle System Control Message

            # TODO:Previous Step
            # if User.userSay.Message=="previous":#Back to Pervious Step
            #    User.path.pop()
            #    pass
            if User.userSay.Message == "return":
                # Return to Upper Recursive

                if User.recursive == []:
                    # When we don't have any preserved recursive Ckecklist
                    # We just simply restart chat.
                    User.currentNode = copy.deepcopy(solutionList)
                    wantedFeature = "Keyword"
                    featureMessage = self.__GetMessage__(wantedFeature)
                    User.botUpdate(wantedFeature, featureMessage)
                    return
                else:
                    # When we have preserved recursive Checklist.
                    # We pop the last Checklist from User.recursive
                    # This is the previous Checklist ,the one which before we enter current recursive
                    # We than simply restore it state.
                    outer = User.recursive.pop()
                    User.currentNode = outer
                    User.botUpdate("Checklist", self.__GetMessage__(
                        "Checklist"), [*outer["Checklist"]])
                    return

            elif User.userSay.Message == "restart":
                # Restart Chat(Initinal State)
                User.currentNode = copy.deepcopy(solutionList)
                wantedFeature = "Keyword"
                featureMessage = self.__GetMessage__(wantedFeature)
                User.botUpdate(wantedFeature, featureMessage)
                return

        elif User.userSay.Type == "raw":
            # User Input via Text
            # We create candidateList via current node's all feature.
            # Than we try to find out what user's intent.
            candidateList = [*User.currentNode[User.botSay.WantedFeature]]
            UserIntent = self.__intentParser__(
                User.userSay.Message, candidateList)

            if User.botSay.WantedFeature == "Checklist" and len(UserIntent) >= 1:
                # If it in Checklist state, pick the hightest score one of current candidate list
                # Just for convience.
                UserIntent = [UserIntent[0]]
            elif len(UserIntent) > 1:
                # If it NOT in Checklist state and there is more than one intent, ask user again
                # without changing state
                logging.info(f"Guess Intent: {UserIntent}")
                User.botUpdate(User.botSay.WantedFeature,
                               self.__GetMessage__("Unbounded"), UserIntent)
                return
            elif len(UserIntent) == 0:
                # If we can't find any intent inside our list, just ask the same question again
                # without changing state
                User.botUpdate(User.botSay.WantedFeature,
                               self.__GetMessage__("Keyword", True), None)
                return
        elif User.userSay.Type == "clicked":
            # User Input via Picked One in List
            UserIntent = [User.userSay.Message]

        logging.info(f"Intent Found:{UserIntent}")

        # Goto Next Stage
        # aka Feature State

        # TODO:Previous Step
        # User.path.append(UserIntent[0])

        # newNode=oldnode[WantedFeatureName][Feature]
        # Feature was founded on the above code.
        newNode = User.currentNode[User.botSay.WantedFeature][UserIntent[0]]

        if type(newNode) == str:
            # If and only if we are in checklist state and client pick an item on list will this condition be true
            # cause other node on tree,type(newNode) will be dictionary
            # There are one exception where we need to "Reference" other node in solution tree ,make type(newNode)==dict,
            # where we'll handle with next condition
            # We than return the string object to Client, Client will determind how to display.
            User.botUpdate("Checklist", newNode, None)
            return
        elif (type(newNode) == dict and "Reference" in newNode and User.botSay.WantedFeature == "Checklist"):
            # We reserve "Reference" as a reserved word ,which mean a reference will be made inside checklist
            # We push Current Checklist leaf to User.recursive
            # We now enter new recursive, just after we push our pervious Checklist
            # Than we travel path that define in "Reference"'s value from root
            # We Skip the FeatureName and go to next node by using path
            # We will finally reach the very node we want to reference.
            # No mather we are in feature state or checklist state, we just update the User.botUpdate with
            # current wantedFeature and featureList.
            User.recursive.append(User.currentNode)
            refPath = newNode["Reference"]
            tempSolution = copy.deepcopy(solutionList)
            for pathName in refPath:
                tempSolution = tempSolution[[*tempSolution][0]][pathName]
            User.currentNode = tempSolution
            wantedFeature = [*tempSolution][0]
            User.botUpdate(wantedFeature, self.__GetMessage__(
                wantedFeature), [*tempSolution[wantedFeature]])
            return
        elif "Checklist" in newNode:
            # We Now reach leaf node. Now we are in checklist state
            # Treat it as normal node
            # We'll Show the information that need to be check aka. Checklist
            # Ckecklist state will be last as long as User.botSay.WantedFeature=="Checklist"
            User.botUpdate("Checklist", self.__GetMessage__(
                "Checklist"), [*newNode["Checklist"]])
            User.currentNode = newNode
            return
        else:
            # Feature State
            # We now want to find deeper feature so that we can go to leaf node
            # Just update user.currentNode with newnode and user.botsay.WantedFeature with new wanted feature

            newwantedFeature = [*newNode][0]
            response = self.__GetMessage__(newwantedFeature)
            selectList = [*newNode[newwantedFeature]]
            User.botUpdate(newwantedFeature, response, selectList)
            User.currentNode = newNode
            return

    def __GetMessage__(self, featureName, exception=False):
        try:
            if exception:
                return random.choice(question[featureName]["Exception"])
            return random.choice(question[featureName]["Question"])

        except:
            raise NotImplementedError

    def __intentParser__(self, message, candidate):
        if message in candidate:
            return [message]
        tokenList, token_posList = self.__CKIP__(message)

        matched = self.__fuzzymatcher__(tokenList, token_posList, candidate)

        return matched

    def __CKIP__(self, message):
        dictionary = construct_dictionary(encouragedDict)
        word_sentence_list = ws(
            [message],
            sentence_segmentation=True,
            coerce_dictionary=dictionary)
        pos_sentence_list = pos(word_sentence_list)
        return word_sentence_list[0], pos_sentence_list[0]

    def __fuzzymatcher__(self, tokenList, token_posList, candidate):
        mark = ['COLONCATEGORY', 'COMMACATEGORY', 'DASHCATEGORY', 'DOTCATEGORY', 'ETCCATEGORY',
                'EXCLAMATIONCATEGORY', 'PARENTHESISCATEGORY', 'PAUSECATEGORY', 'PERIODCATEGORY', 'QUESTIONCATEGORY',
                'SEMICOLONCATEGORY', 'SPCHANGECATEGORY', 'WHITESPACE']

        recommend = {}
        #wanted_word = ["FW", "Na", "Nb", "Nc", "Ncd", "Nv"]
        droped_list = ["DE", "D", "Nh", "Cbb", "Caa", "Cab",
                       "Cba", "Da", "Dfa", "Dfb", "Di", "Dk", "DM", "I", "V_2", "Nd", "VE"]+mark

        for token, token_pos in zip(tokenList, token_posList):
            if token_pos in droped_list:
                continue

            similarPair = process.extractBests(
                token, [*similarDict], scorer=fuzz.UWRatio)
            similarText = similarPair[0][0]
            similarScore = similarPair[0][1]
            fuzzymatch = process.extract(
                token, candidate, limit=2, scorer=fuzz.UWRatio)

            similarFuzzymatch = []
            if similarScore >= CONFIDENCE_ACCEPT_THRESHOLD:
                similarFuzzymatch = process.extract(
                    similarDict[similarText], candidate, limit=2, scorer=fuzz.UWRatio)

            for match_str, confidence in fuzzymatch+similarFuzzymatch:
                if confidence < CONFIDENCE_DROP_THRESHOLD:
                    continue
                if confidence >= CONFIDENCE_ACCEPT_THRESHOLD:
                    return [match_str]
                try:
                    recommend[confidence]
                    recommend[confidence].append(match_str)
                except:
                    recommend[confidence] = [match_str]
        order = sorted(recommend)
        finded = []
        for score in order:
            finded += recommend[score]
            if len(finded) > 5:
                return list(set(finded))
        return list(set(finded))
