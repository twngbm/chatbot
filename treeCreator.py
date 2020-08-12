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
DormOveruse = {Answer: "您已超流量(24小時內超過8GB)"}
DormHWDead = {Answer: "您所在宿舍/樓層之網路設備目前異常中"}
isDHCP = {Answer: "請聯絡61010由專人為您服務"}  #未註冊，註冊裝置MAC改變
noDHCP = {Answer: "請設定為DHCP"}
DormHWAlive = {
    Feature: {
        "isDHCP": {
            InputParser: ["BooleanParser"],
            Key: {
                True: isDHCP,
                "False": noDHCP
            }
        }
    }
}
DormNonOveruse = {
    Feature: {
        "DormID": {
            InputParser: ["DormHWChecker"],
            Key: {
                "HWDead": DormHWDead,
                "HWAlive": DormHWAlive
            }
        }
    }
}
Dorm = {
    Feature: {
        "StudentID": {
            InputParser: ["DormIDUsage"],
            Key: {
                "Overuse": DormOveruse,
                "Non-Overuse": DormNonOveruse
            }
        }
    },
    BalanceFlag: True
}  #床位已滿，網路孔報修
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
StudentWAN={}
ProfWAN={}
NckuWAN={Feature:{"UserIdentifity":{InputParser:[],Key:{"學生":StudentWAN,"教授":ProfWAN}}},BalanceFlag:True}
NoneNckuWAN={}
WAN = {Feature:{"UserDomain":{InputParser:[],Key:{"校內人士":NckuWAN,"校外人士":NoneNckuWAN}}}}

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
CAS={}
root = {
    Feature: {
        "Keyword": {
            InputParser: ["CKIPParser"],
            Key: {
                "網路": Network,
                "授權軟體":CAS #Campus Authorized Software
            }
        }
    }
}
__PATH__ = os.path.dirname(os.path.abspath(__file__))
with open(__PATH__ + "/tree.json", "w") as f:
    json.dump(root, f)
