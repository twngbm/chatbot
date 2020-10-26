import copy
import json
import logging


from utils import ChatUtils, LoaderUtils, FunctionUtils


class User(object):
    def __init__(self, data: LoaderUtils, userID):
        self.data = data
        self.userID = userID
        #self.rootFeature = [*self.currentNode][0]
        self.ChatUtils = ChatUtils(self.data)
        self.FunctionUtils = FunctionUtils(self.data)
        self.restart()

    def botUpdate(self, response,  metadate, lastChosen, Dtype=None, reference=None):
        self.botSay.Response = response
        if not Dtype:
            if ChatUtils.isURL(self.botSay.Response):
                self.sendbackMessage = json.dumps(
                    {"Response": reference, "Metadata": self.botSay.Metadata, "lastChosen": lastChosen, "Type": 2, "URL": self.botSay.Response}, ensure_ascii=False)
                return
            elif ChatUtils.isIMG(self.botSay.Response):
                Dtype = 1
            else:
                Dtype = 0
        self.botSay.Metadata = metadate
        self.sendbackMessage = json.dumps(
            {"Response": self.botSay.Response, "Metadata": self.botSay.Metadata, "lastChosen": lastChosen, "Type": Dtype}, ensure_ascii=False)
        return

    def userUpdate(self, inputData: str):
        try:
            data = json.loads(inputData)
        except:
            raise TypeError

        if data["DataType"] not in ["raw", "sys", "clicked", 0, 1]:
            raise KeyError

        try:
            self.userSay.relatively = data["Relatively"]
        except:
            self.userSay.relatively = 0

        try:
            self.userSay.Message = data["Data"]
        except:
            raise ValueError

        if data["DataType"] in ["raw", "clicked", 1]:
            self.userSay.Type = "raw"
        else:
            self.userSay.Type = "sys"

    def restart(self):
        self.currentNode = copy.deepcopy(self.data.solutionList)
        self.history = [self.currentNode]
        self.intentLog = []
        self.inFunction = False
        self.functionCounter = -1
        self.lastFunctionOutput = []
        self.botSay = botSay()
        self.userSay = userSay()
        feature = self.currentFeatureName()
        response = self.ChatUtils.getQuestion(feature)
        self.botUpdate(response, None, None)
        logging.info(f"{self.userID} RESTART")

    def updateFunction(self, intent):
        if not self.inFunction:
            self.updateNode(
                self.currentNode[self.currentFeatureName()][intent]["Function"], intent)
        self.inFunction = True
        self.functionCounter += 1
        if self.functionCounter >= len(self.currentNode):
            self.restart()
            return

        currentFunction = copy.deepcopy(self.currentNode[self.functionCounter])
        functionName = currentFunction.pop(0)
        functionArgs = []
        for args in currentFunction:
            if args == "$INPUT":
                args = intent
            elif args == "$LAST":
                # History function output
                args = self.lastFunctionOutput
            functionArgs.append(args)
        try:
            response, checklist, unbound = getattr(
                self.FunctionUtils, functionName)(functionArgs)
        except:
            raise NotImplementedError

        if unbound:
            response = self.ChatUtils.getQuestion(
                "Unbounded").format(INPUT=intent)
            self.botUpdate(response, checklist, intent)
            self.functionCounter -= 1
            return
        self.lastFunctionOutput.append([response, checklist])
        if self.functionCounter == len(self.currentNode)-1:
            # End of function list
            checklist = [self.ChatUtils.getQuestion("SysRestartConfirm")]
        self.botUpdate(response, checklist, intent)
        return

    def updateNode(self, newNode, lastIntent):
        self.history.append(newNode)
        self.intentLog.append(lastIntent)
        logging.info("History PUSH {}".format([[*x][0] for x in self.history]))
        logging.info("intentLog PUSH{}".format(self.intentLog))
        self.currentNode = newNode

    def undoNode(self):
        logging.info(f"{self.userID} UNDO")
        if self.inFunction:
            self.functionCounter -= 1
            if self.functionCounter <= -1:
                self.restart()
                return
            self.lastFunctionOutput.pop()
            lastOutput = self.lastFunctionOutput[-1]
            self.botUpdate(lastOutput[0], lastOutput[1], None)
            return

        if len(self.intentLog) <= 1:
            self.restart()
            return
        previousNode = self.history.pop()
        previousIntent = self.intentLog.pop()
        self.currentNode = self.history[-1]
        response = self.ChatUtils.getQuestion(self.currentFeatureName()).format(
            PATH=self.intentPath(), DESCRIPTION=self.checklistDescription())
        selectList = self.currentFeature()
        self.botUpdate(response, selectList, None, -1)
        logging.info("History POP{}".format([[*x][0] for x in self.history]))
        logging.info("intentLog POP{}".format(self.intentLog))
        return

    def jump(self):
        pass

    def reference(self, path: list):
        tempSolution = copy.deepcopy(self.data.solutionList)
        for pathName in path:
            tempSolution = tempSolution[[*tempSolution][0]][pathName]
        return tempSolution

    def lastIntent(self):
        try:
            return self.intentLog[-1]
        except:
            return None

    def currentFeatureName(self) -> str:
        return [*self.currentNode][0]

    def currentFeature(self) -> list:
        feature = [*self.currentNode[self.currentFeatureName()]]
        if "Description" in feature:
            feature.remove("Description")
            feature.append(self.ChatUtils.getQuestion("SysRestartConfirm"))
        return feature

    def nextNode(self, intent) -> dict:
        try:
            return self.currentNode[self.currentFeatureName()][intent]
        except:
            raise KeyError

    def nextFeature(self, intent) -> str:
        return [*self.nextNode(intent)][0]

    def intentPath(self) -> str:
        return "-".join(self.intentLog)

    def checklistDescription(self) -> str:
        try:
            return self.currentNode["Checklist"]["Description"]
        except:
            return None

    def isRoot(self) -> bool:
        return self.currentFeatureName() is [*self.data.solutionList][0]


class botSay(object):
    def __init__(self):
        self.Response = None
        self.Metadata = None


class userSay(object):
    def __init__(self):
        self.Type = None
        self.Message = None
        self.relatively = None
