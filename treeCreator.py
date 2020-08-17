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
StudentWAN = {}
ProfWAN = {}
NckuWAN = {Feature: {"UserIdentifity": {InputParser: [], Key: {
    "學生": StudentWAN, "教授": ProfWAN}}}, BalanceFlag: True}
NoneNckuWAN = {}
WAN = {Feature: {"UserDomain": {InputParser: [],
                                Key: {"校內人士": NckuWAN, "校外人士": NoneNckuWAN}}}}

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
            InputParser: [],
            Key: {
                "校內版本": CASVersion,
                "校外版本": NonCASVersion
            }
        }
    }
}
TimesetCorrect = {Feature: {
    "RunAsAdmin": {
        InputParser: [],
        Key: {
            "以系統管理員身份執行": RunAsAdmin,
            "未以系統管理員身份執行": NotRunAsAdmin
        }
    }
}}
InCampus = {Feature: {
    "ComputerTimeset": {
        InputParser: [],
        Key: {
            "時間設定正確": TimesetCorrect,
            "時間設定錯誤": TimesetFalse
        }
    }
}, BalanceFlag: True}
NotUseVPN = {Answer: {"請使用VPN連線"}}
OutCampus = {Feature: {"UseVPN": {
    InputParser: [],
    Key: {"已使用VPN": InCampus,
          "未使用VPN": NotUseVPN}
}}}
CAS = {Feature: {
    "IPDomain": {
        InputParser: ["IPDomainParser"],
        Key: {
            "校內": InCampus,
            "校外": OutCampus
        }
    }
}}
VPNInstall = {Answer: "請參考網頁說明"}
ISTrue = {Answer: "該帳號目前被資安通報處理中"}
iNCKULoginFail = {Answer: "請確認帳號密碼是否正確"}
iNCKULoginSuccess = {Answer: Call61010}
ISFalse = {Feature: {
    "iNCKULogin": {
        InputParser: [],
        Key: {
            "登入成功": iNCKULoginSuccess,
            "登入失敗": iNCKULoginFail
        }
    }
}}
VPNUse = {Feature: {
    "StudentID": {
        InputParser: ["ISParser"],  # Information Security Parser資安通報
        Key: {"ISTrue": ISTrue,
              "ISFalse": ISFalse,
              }
    }
}, BalanceFlag: True}
VPN = {Feature: {"QuestionDomain": {InputParser: [
    "QDParser"], Key: {"安裝": VPNInstall, "使用": VPNUse}}}}
BackupMailTrue={Answer:"請使用備用信箱進行密碼重設"}
BackupMailFalse={Answer:Call61010+"，或是由現場臨櫃處理"}
iNCKUPassForget={Feature:{
    "BackupMail":{
        InputParser:[],
        Key:{
            "已設定":BackupMailTrue,
            "未設定":BackupMailFalse,
        }
    }
}}
iNCKUDefaultPassFail={Answer:Call61010}
iNCKU = {Feature: {"QuestionDomain": {
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
                "成功入口":iNCKU,
                "防疫系統":{Answer:"請直撥分機50340衛保組"}
            }
        }
    }
}
__PATH__ = os.path.dirname(os.path.abspath(__file__))
with open(__PATH__ + "/tree.json", "w") as f:
    json.dump(root, f)
