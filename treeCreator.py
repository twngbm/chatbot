########################
# Node={Feature:
#           {<FeatureName>:
#               {"InputParser":[<Parser Name>],
#                   Key:{"KeyName":<Next Node>}
#                }},
#       BalanceFlag:True/False #此層以下開始進行亂數詢問
#       "Answer":<Answer Text>}
########################
import json
import os
import logging
import time
Feature = "Feature"
InputParser = "InputParser"
Key = "Key"
Answer = "Answer"
BalanceFlag = "BalanceFlag"
Call61010 = "請聯絡61010由專人為您服務"
DormOveruse = {Answer: "您已超流量(24小時內超過8GB)"}
DormHWDead = {Answer: "您所在宿舍/樓層之網路設備目前異常中"}
isDHCP = {Answer: Call61010}  # 未註冊，註冊裝置MAC改變
noDHCP = {Answer: "請設定為DHCP"}
DormHWAlive = {
    Feature: {
        "isDHCP": {
            InputParser: ["BooleanParser"],
            Key: {
                True: isDHCP,
                False: noDHCP
            }
        }
    }
}
DormNonOveruse = {
    Feature: {
        "DormID": {
            InputParser: ["DormHWChecker"],
            Key: {
                False: DormHWDead,
                True: DormHWAlive
            }
        }
    }
}
Dorm = {
    Feature: {
        "StudentID": {
            InputParser: ["DormIDUsage"],
            Key: {
                False: DormOveruse,
                True: DormNonOveruse
            }
        }
    },
    BalanceFlag: True
}  # 床位已滿，網路孔報修
Lab = {Answer: "請聯絡貴系網管進行處理"}
School = {Answer: "請聯絡貴單位網管進行處理"}
LAN = {
    Feature: {
        "Location": {
            InputParser: ["LanLocationParser"],
            Key: {
                "宿舍": Dorm,
                "系館": Lab,
                "行政單位": School
            }
        }
    }
}
StudentWAN = {Answer: Call61010}
ProfWAN = {Answer: Call61010}
NckuWAN = {Feature: {"UserIdentifity": {InputParser: [], Key: {
    "學生": StudentWAN, "教授": ProfWAN}}}, BalanceFlag: True}
NoneNckuWAN = {Answer: Call61010}
WAN = {Feature: {"UserDomain": {InputParser: ["BooleanParser"],
                                Key: {True: NckuWAN, False: NoneNckuWAN}}}}

Network = {
    Feature: {
        "ConnectionType": {
            InputParser: [],
            Key: {
                "有線": LAN,
                "無線": WAN
            }
        }
    }
}
TimesetFalse = {Answer: "請進行網路對時候重新嘗試"}
NotRunAsAdmin = {Answer: "請以系統管理員身份執行"}
NonCASVersion = {Answer: "請安裝本校所提供之授權軟體"}
CASVersion = {Answer: Call61010}
RunAsAdmin = {
    Feature: {
        "InstalledVersion": {
            InputParser: ["BooleanParser"],
            Key: {
                True: CASVersion,
                False: NonCASVersion
            }
        }
    }
}
TimesetCorrect = {Feature: {
    "RunAsAdmin": {
        InputParser: ["BooleanParser"],
        Key: {
            True: RunAsAdmin,
            False: NotRunAsAdmin
        }
    }
}}
InCampus = {Feature: {
    "ComputerTimeset": {
        InputParser: ["BooleanParser"],
        Key: {
            True: TimesetCorrect,
            False: TimesetFalse
        }
    }
}, BalanceFlag: True}
NotUseVPN = {Answer: "請使用VPN連線"}
OutCampus = {Feature: {"UseVPN": {
    InputParser: ["BooleanParser"],
    Key: {True: InCampus,
          False: NotUseVPN}
}}}
CAS = {Feature: {
    "IPDomain": {
        InputParser: ["BooleanParser"],
        Key: {
            True: InCampus,
            False: OutCampus
        }
    }
}}
VPNInstall = {Answer: "請參考網頁說明"}
ISTrue = {Answer: "該帳號目前被資安通報處理中"}
iNCKULoginFail = {Answer: "請確認帳號密碼是否正確"}
iNCKULoginSuccess = {Answer: Call61010}
ISFalse = {Feature: {
    "iNCKULogin": {
        InputParser: ["BooleanParser"],
        Key: {
            True: iNCKULoginSuccess,
            False: iNCKULoginFail
        }
    }
}}
VPNUse = {Feature: {
    "StudentID": {
        InputParser: ["ISParser"],  # Information Security Parser資安通報
        Key: {True: ISTrue,
              False: ISFalse,
              }
    }
}, BalanceFlag: True}
VPN = {Feature: {"VPNQD": {InputParser: [
    "QDParser"], Key: {"安裝": VPNInstall, "使用": VPNUse}}}}
BackupMailTrue = {Answer: "請使用備用信箱進行密碼重設"}
BackupMailFalse = {Answer: Call61010+"，或是由現場臨櫃處理"}
iNCKUPassForget = {Feature: {
    "BackupMail": {
        InputParser: ["BooleanParser"],
        Key: {
            True: BackupMailTrue,
            False: BackupMailFalse,
        }
    }
}}
iNCKUDefaultPassFail = {Answer: Call61010}
iNCKU = {Feature: {"inckuQD": {
    InputParser: ["QDParser"],
    Key: {"忘記密碼": iNCKUPassForget,
          "預設密碼無法登入": iNCKUDefaultPassFail}
}}}
root = {
    Feature: {
        "Keyword": {
            InputParser: ["CKIPParser"],
            Key: {
                "網路": Network,
                "授權軟體": CAS,  # Campus Authorized Software
                "VPM": VPN,
                "成功入口": iNCKU,
                "防疫系統": {Answer: "請直撥分機50340衛保組"}
            }
        }
    }
}
__PATH__ = os.path.dirname(os.path.abspath(__file__))
answerList = []
currentList = []
global randomList
global ansList
randomList = []
ansList = []
IP = InputParser


def balanceParser(node):
    for featureKey in node[Feature]:
        for diffFeature in node[Feature][featureKey][Key]:
            if Answer in node[Feature][featureKey][Key][diffFeature]:
                ansList.append([featureKey, diffFeature, node[Feature][featureKey]
                                [IP], node[Feature][featureKey][Key][diffFeature][Answer]])
            else:
                randomList.append(
                    [featureKey, node[Feature][featureKey][InputParser], diffFeature])
                balanceParser(node[Feature][featureKey][Key][diffFeature])


def dfs(node, currentList, balance=False):
    nodeHeader = node.keys()
    global randomList
    global ansList

    if Answer in nodeHeader:
        solution = {Feature: {}, Answer: node[Answer]}
        for f in currentList:
            solution[Feature].update(f)
        answerList.append(solution)

    elif Feature in nodeHeader:
        if BalanceFlag in nodeHeader:
            balanceParser(node)
            for ans in ansList:
                solution = {Feature: {}, Answer: ans[3]}
                for i in currentList:
                    solution[Feature].update(i)
                for f in randomList:
                    if ans[0] != f[0]:
                        solution[Feature].update({f[0]: {IP: f[1], Key: f[2]}})
                solution[Feature].update({ans[0]: {IP: ans[2], Key: ans[1]}})
                answerList.append(solution)
            randomList = []
            ansList = []
        else:
            for featureKey in node[Feature]:
                for diffFeature in node[Feature][featureKey][Key]:
                    temp = {featureKey: {IP: node[Feature][featureKey][InputParser],
                                         Key: diffFeature}}
                    dfs(node[Feature][featureKey][Key]
                        [diffFeature], currentList+[temp])


dfs(root, currentList)


def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


with open("./test.json", "w", encoding='utf-8') as f:
    json.dump(answerList, f, default=set_default, ensure_ascii=False)
# print(answerList)
