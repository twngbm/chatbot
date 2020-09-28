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
import copy
Feature = "Feature"
InputParser = "InputParser"
Key = "Key"

Checklist = "Checklist"
BalanceFlag = "BalanceFlag"
Call61010 = "請聯絡61010由專人為您服務"

Dorm = {
    Checklist: {
        "請確認是否已註冊。": "http://dorm.cc.ncku.edu.tw/",
        "請檢察是否超流量。": "http://dorm.cc.ncku.edu.tw/",
        "請檢察是否設定DHCP。": "http://dorm.cc.ncku.edu.tw/",
        "請檢查網路線狀態。": "http://dorm.cc.ncku.edu.tw/"
    }}
Lab = {Checklist: {"請聯絡貴系網管進行處理": "各系網管負責人表格"}}
School = {Checklist: {"請聯絡貴單位網管進行處理": "各單位網管負責人表格"}}
LAN = {

    "Location": {

        "宿舍": Dorm,
        "系館": Lab,
        "行政單位": School

    }
}

NckuWAN = {Checklist: {"選取網路基地臺名稱NCKU-WLAN-802.1X，並以成功入口帳號登入使用。":
                       "http://cc.ncku.edu.tw/var/file/2/1002/img/651695129.pdf"}}
NoneNckuWAN = {Checklist: {"若貴校已加入校際無線網路漫遊，可選取網路基地臺名稱TANetRoaming，並以貴校提供之帳號登入使用。":
                           "https://roamingcenter.tanet.edu.tw/"}}
Alumni = {Checklist: {"校友 wifi 服務即日起停止新申請,預計於2020.08.01全面停用":
                      "http://alumni.ncku.edu.tw/p/406-1004-205468,r47.php?Lang=zh-tw"}}
Public = {Checklist: {"請先至行政院提供免費無線上網iTaiwan服務首頁申請帳號，並於開放地點選取網路基地臺名稱NCKU-iTaiwan登入使用。因臺灣學術網路與iTaiwan無線網路雙向漫遊將於109年7月1日起停止服務，NCKU-iTaiwan亦於109年7月1日起停止服務。": ""}}
WAN = {"UserDomain": {
    "本校師生": NckuWAN,
    "他校師生": NoneNckuWAN,
    "本校校友": Alumni,
    "一般民眾": Public}}
Network = {
    "ConnectionType": {

        "有線": LAN,
        "無線": WAN

    }
}


iNCKUPassForget = {Checklist: {
    "請使用備用信箱進行密碼還原": "https://i.ncku.edu.tw/zh-hant/user/password"}}
iNCKUDefaultPassFail = {Checklist: {Call61010: ""}}
iNCKU = {"inckuQD": {
    "忘記密碼": iNCKUPassForget,
    "預設密碼無法登入": iNCKUDefaultPassFail

}}

VPNwin = {Checklist: {"安裝檔下載連結": "64-bits:https://ncku.twaren.net/dana-na/jam/getComponent.cgi?command=get;component=PulseSecure;platform=x64<br>32-bits:https://ncku.twaren.net/dana-na/jam/getComponent.cgi?command=get;component=PulseSecure;platform=x86",
                      "使用說明": "http://cc.ncku.edu.tw/var/file/2/1002/img/237/582085960.pdf"}}


VPNmac = {Checklist: {"安裝檔下載連結": "https://ncku.twaren.net/dana-na/jam/getComponent.cgi?command=get;component=PulseSecure;platform=Macintosh",
                      "使用說明": "http://cc.ncku.edu.tw/var/file/2/1002/img/237/469467801.pdf"}}
VPNdebian = {Checklist: {"安裝檔下載連結": "64-bits:https://ncku.twaren.net/dana-na/jam/getComponent.cgi?command=get;component=PulseSecure;platform=deb64<br>32-bits:https://ncku.twaren.net/dana-na/jam/getComponent.cgi?command=get;component=PulseSecure;platform=deb",
                         "使用說明": "http://cc.ncku.edu.tw/var/file/2/1002/img/237/585714609.pdf"}}
VPNcent = {Checklist: {"安裝檔下載連結": "64-bits:https://ncku.twaren.net/dana-na/jam/getComponent.cgi?command=get;component=PulseSecure;platform=rpm64<br>32-bits:https://ncku.twaren.net/dana-na/jam/getComponent.cgi?command=get;component=PulseSecure;platform=rpm",
                       "使用說明": "http://cc.ncku.edu.tw/var/file/2/1002/img/237/585714609.pdf"}}
VPNios = {Checklist: {
    "安裝與使用說明": "http://cc.ncku.edu.tw/var/file/2/1002/img/237/390725809.pdf"}}
VPNandroid = {Checklist: {
    "安裝與使用說明": "http://cc.ncku.edu.tw/var/file/2/1002/img/237/662072256.pdf"}}

VPNInstall = {
    "OSversion": {

        "Windows": VPNwin,
        "MacOS": VPNmac,
        "Ubuntu": VPNdebian,
        "CentOS": VPNcent,
        "iOS": VPNios,
        "Android": VPNandroid

    }}

VPNLogin = {Checklist: {
    "請使用成功入口帳號與密碼登入": "",
    "如忘記成功入口帳密請參考": {"Reference": ["成功入口", "忘記密碼"]}
}}
VPN = {
    "VPNQD": {

        "登入": VPNLogin,
        "安裝與使用": VPNInstall
    }}

CAS = {Checklist: {
    "如您在校外進行認證，請使用VPN連線": {"Reference": ["VPN"]},
    "認證檔案請以系統管理員身分執行": "http://www.cc.ncku.edu.tw/download/qa.php",
    "認證時請確認電腦時間設定正確": "http://www.cc.ncku.edu.tw/download/qa.php",
    "請確認電腦上欲安裝與認證之軟體版本為本校提供，且未認證之校外版本軟體已移除": "http://www.cc.ncku.edu.tw/download/qa.php"
}}

staff_mail_pisa = {"mail_qd": {

    "帳號申請": {Checklist: {"本校已全面使用Gsuit作為本校個人信箱之帳號": "https://www.gs.ncku.edu.tw/%E5%95%9F%E7%94%A8%E6%95%99%E5%AD%B8/%E6%95%99%E8%81%B7%E5%93%A1"}},
    "忘記密碼": {Checklist: {"為保護您本人帳號之安全性<br>請攜帶申請人<br><b>員工識別證</b><br><b>身分證</b><br>至計算機與網路服務中心1F服務台進行更改，或致電61010由專人為您服務。": "http://cc.ncku.edu.tw/p/412-1002-14652.php?Lang=zh-tw"}},
    "忘記帳號": {Checklist: {"請致電#61010為您服務。": ""}},
    "使用期限": {Checklist: {"若您為離職教職員工，則將於離職後半年系統自動刪除該帳號。": "http://cc.ncku.edu.tw/p/412-1002-14652.php?Lang=zh-tw",
                         "若您為退休教職員工，則依現行管理政策該帳號將終身保留。": "http://cc.ncku.edu.tw/p/412-1002-14652.php?Lang=zh-tw"}},
    "Webmail": {Checklist: {"點此進入webmail頁面": "https://mail.ncku.edu.tw/cgi-bin/login?index=1"}},
    "在iphone系統使用": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9Mekl2Y0hSaFh6RTFPVEE0TWw4MU1URTVNamcwWHpBNU5ETTJMbkJrWmc9PQ==&fname=WSGGXWB0YWLKOO1050LKRKHGVWPKWTGGFGB0XSKKA125XWRKMOMKA0EG14OK50XXNOWW00IHVS04EGKKMOFGTS24STB0MKHCCCMPXWTS14ZWMO01SSGCYWFCNPPO44KKDGA041GDVWNKDC3514B0UW10UT35QPVWMOB4NKEG34HGCDUSPO00QPXXIG10XW14XSJGGCGCWS34FHLOMLQLPOA0SSROJGA0QODCTSDCNO10FDZXHCLK54IC50MOFHHCKLB0QL14TXJDMLTWYSA4FCB4OOKKA0QKZTCCYX10VSTWDHDH"}},
    "在Android系統使用": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9Memt2Y0hSaFh6RTFPVEE0T1Y4NU1UTTRNelk0WHpBNU5ETTJMbkJrWmc9PQ==&fname=WSGGXWB0YWLKOO1050LKRKHGVWPKWTGGFGB0XSKKA125XWCCSSECLOUW14OKSWUSLOWWJD05A4NOMOWSIG30A025B0FGXSHCGGVX04B0YSYW50SWSSHG20PKNO40XTZXFGNO50SXVWB4JGWSB0MO04ICA1QLQPEGYSQOYWDGDGA4JGTWRKPOUT25TSPOROWWPK1410YS20MO35LOZTRLB0FCXWMKJG45WWPOYSOKSS10A1YX5010WTHGQO3025LK1434GGGCCCGDWSPKUSUSLOSWB1OK34OKZTCCID10TSZSDHDH"}},
    "在Mac系統使用": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/var/file/2/1002/attach/10/pta_105741_6271936_66737.pdf"}},
    "在Outlook系統使用": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MekV5TDNCMFlWOHhOVGt3T1RKZk1USTNORE15WHpBNU5ETTRMbkJrWmc9PQ==&fname=0054ROB0RKSSVXHHEDXSJGGDZSB4TSB1QOQK4020VX25DC40DCA4YSFGWW54DGOKSSWWCDMP44A054MK34XSMK35YSROWSGC41VXA4FCYSYWVS5050GGRPGHUSPOWWLP50POSWWTZSJCDG35ECNOYSWS01UXIGCCA0DCOPVWQOA4LKQKICKKA5JHFG0435YWMOOKZTMOYSEGFHRLMLIDNOB5UWB0VSPPUSDC0150SS10PP00WWZSWW24KKTWZTKKFGUWSSKKA1NPMLEG34A4FDDGWSHGKLPKZTPOWWXXDGVWLK14MOMOUWWSIGICRKYSUTXTXWB0WSECJG50EC00CDGHDG4415HHEDA0UW34RK30USGCSTQKOKMP00GDVSPO"}},
    "收發郵件轉寄": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MemswTDNCMFlWOHhOamt4TmpWZk9ESTVPRE13Tmw4d09UUXpOaTV3WkdZPQ==&fname=LOGGVWOKYW44A1YX50LKSXHGVW30WTGG34UWGGGCCCQLPO40FCB4QOB400OOKLSSA4POVX15A404FG141430TSGGB0MONOXSLPJDXWA034MK30FCUS54B5PKRK40CDIDDGA0DCXTQOMOCG00WX24ZWYS44UXSSTSFC3030US20GCHHHH"}},
    "信箱頁面語言更改": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MemsxTDNCMFlWOHhOamt4TmpaZk1UQTVPRFExTWw4d09UUXpOaTV3WkdZPQ==&fname=WSGGNKA0RKDCA110EDLKWW24MKPK25RL2034CCYSTXZTOO40DCYWLOPO0054B4SSLOTSTXIHDG04MOHCRKPKTSMOKL34B1NOCCVXXWTSLKA450SW145424DCGCLK0115JCLKSXHGTWFGSWHCUS30A110"}},
    "自動回覆": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MemsyTDNCMFlWOHhOamt4TmpkZk9UZzNPRE01TTE4d09UUXpOaTV3WkdZPQ==&fname=WSGGNKA0KK10OO25EDLKFCMOIGMOCG00USUWQLB1GGVXCCSSNKB4FD54FG54JGWX44POGD152004NK14PKMOA0YSYSRKWSGCJDVXHGB5SWB001UWECGCKLXXRKPO4511DGNO54NKVWKOSSXSPKRK40MPMLGDYXB0NK30YSDGQO10NOPKVWPO21KKJCLKEGZWQOOKA0KK20UWB1NOHD51NLRK"}},
    "通訊錄管理": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MekF2Y0hSaFh6RTJPVEUyT0Y4eU5qUXdORGc1WHpBNU5ETTJMbkJrWmc9PQ==&fname=WSGGXWB0YWLKOO1050LKRKHGVWPKWTGGYSB0XSNKVXGDXW40YSYWA054WWOOKLOKWW54B505A404NKXTKO30TSMOSTIC10LKGGRLNOTSUWZWCDUWFHTS45PKUS00ZT25DGA041GDZSKOWTB150FGWSICXT51LKB0NK30YSDGDGCCB5FCYWQOYTYXDGB0A0CH1430JDGGWSA0CGMK21XT30A514B0JG45SSPOROFCYWKK41IHWW04DHHG"}},
    "誤判信放行": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9Memd5TDNCMFlWOHhOamt4TlROZk1UWTNOalF4TjE4d09UUXpOUzV3WkdZPQ==&fname=LOGGVWOKYW44A1YX50LKSXHGVW3025GGYSB0IC24QPQLDC40A020YWUWLO10USOKDGKKDHXXDG04LOLO14SWTSXWSTB0NKHCZTVXDCA0LKB0B450GG10KLDCPKPOWW25B0NO50SXVWB4USXSWSVW043501QLTTRKNK30ECTWDG54NOQKVWPOA5KKNO10PO34QOOKA0KK20UWB1NOHD51NLRK"}},
    "預設名單": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9Memd6TDNCMFlWOHhOamt4TlRSZk9EQTVOemN5WHpBNU5ETTJMbkJrWmc9PQ==&fname=LOGGVWOKYW44A1YX50LKSXHGVW3025GGYSB0IC24QPQLDC40A020YWUWLO10USOKDGKKDHXXDG04LOLO14SWTSXWSTB0NKHCZTVXDCA0LKB0B450GG10KLDCDGPOXXOOEDNO54XSVWPKWSNPDG3440LKCCGDQPSSNK30YSDGOOKKRK50DGLKUT10IG04FG34OO30GDB1B430A1A1"}},
    "誤刪除": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MemcwTDNCMFlWOHhOamt4TlRWZk16Z3dNVFkwTlY4d09UUXpOaTV3WkdZPQ==&fname=LOGGVWOKYW44A1YX50LKSXHGVW3025GGYSB0IC24QPQLDC40A020YWUWLO10USOKDGKKDHXXDG04LOLO14SWTSXWSTB0NKHCZTVXDCA0LKB0B450GG10KLDCICPO44MP04NO54XSRK30A1KOPKFG40MPCCGDYXQPYSQOYSDGQO10RKPKDGLKUT10IG04FG34OO30GDB1B430A1A1"}},
}}
staff_mail_z = {"mail_qd": {

    "帳號申請": {Checklist: {"帳號即為\"z+您的員工識別證號\"，舉例:若您的員工識別證號為10745678，則您的公務信箱帳號即為z10745678": ""}},
    "忘記密碼": {Checklist: {"公務信箱密碼與成功入口密碼連動，修改成功入口密碼即可修改您的公務信箱密碼。": "http://cc.ncku.edu.tw/p/412-1002-14655.php?Lang=zh-tw"}},
    "使用期限": {Checklist: {"自您於本校人事室報到完成，且人事室完成人事資料建檔後即可使用。至您離職或退休半年後刪除": "http://cc.ncku.edu.tw/p/412-1002-14655.php?Lang=zh-tw"}},
    "Webmail": {Checklist: {"點此進入webmail頁面": "https://mail.ncku.edu.tw/cgi-bin/login?index=1"}},
    "在iphone系統使用": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9Mekl2Y0hSaFh6RTFPVEE0TWw4MU1URTVNamcwWHpBNU5ETTJMbkJrWmc9PQ==&fname=WSGGXWB0YWLKOO1050LKRKHGVWPKWTGGFGB0XSKKA125XWRKMOMKA0EG14OK50XXNOWW00IHVS04EGKKMOFGTS24STB0MKHCCCMPXWTS14ZWMO01SSGCYWFCNPPO44KKDGA041GDVWNKDC3514B0UW10UT35QPVWMOB4NKEG34HGCDUSPO00QPXXIG10XW14XSJGGCGCWS34FHLOMLQLPOA0SSROJGA0QODCTSDCNO10FDZXHCLK54IC50MOFHHCKLB0QL14TXJDMLTWYSA4FCB4OOKKA0QKZTCCYX10VSTWDHDH"}},
    "在Android系統使用": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/var/file/2/1002/attach/36/pta_105742_2580653_66805.pdf"}},
    "在Mac系統使用": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/var/file/2/1002/attach/37/pta_105738_4897746_64477.pdf"}},
    "在Outlook系統使用": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MekV5TDNCMFlWOHhOVGt3T1RKZk1USTNORE15WHpBNU5ETTRMbkJrWmc9PQ==&fname=0054ROB0RKSSVXHHEDXSJGGDZSB4TSB1QOQK4020VX25DC40DCA4YSFGWW54DGOKSSWWCDMP44A054MK34XSMK35YSROWSGC41VXA4FCYSYWVS5050GGRPGHUSPOWWLP50POSWWTZSJCDG35ECNOYSWS01UXIGCCA0DCOPVWQOA4LKQKICKKA5JHFG0435YWMOOKZTMOYSEGFHRLMLIDNOB5UWB0VSPPUSDC0150SS10PP00WWZSWW24KKTWZTKKFGUWSSKKA1NPMLEG34A4FDDGWSHGKLPKZTPOWWXXDGVWLK14MOMOUWWSIGICRKYSUTXTXWB0WSECJG50EC00CDGHDG4415HHEDA0UW34RK30USGCSTQKOKMP00GDVSPO"}},
    "收發郵件轉寄": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MemswTDNCMFlWOHhOamt4TmpWZk9ESTVPRE13Tmw4d09UUXpOaTV3WkdZPQ==&fname=LOGGVWOKYW44A1YX50LKSXHGVW30WTGG34UWGGGCCCQLPO40FCB4QOB400OOKLSSA4POVX15A404FG141430TSGGB0MONOXSLPJDXWA034MK30FCUS54B5PKRK40CDIDDGA0DCXTQOMOCG00WX24ZWYS44UXSSTSFC3030US20GCHHHH"}},
    "信箱頁面語言更改": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MemsxTDNCMFlWOHhOamt4TmpaZk1UQTVPRFExTWw4d09UUXpOaTV3WkdZPQ==&fname=WSGGNKA0RKDCA110EDLKWW24MKPK25RL2034CCYSTXZTOO40DCYWLOPO0054B4SSLOTSTXIHDG04MOHCRKPKTSMOKL34B1NOCCVXXWTSLKA450SW145424DCGCLK0115JCLKSXHGTWFGSWHCUS30A110"}},
    "自動回覆": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MemsyTDNCMFlWOHhOamt4TmpkZk9UZzNPRE01TTE4d09UUXpOaTV3WkdZPQ==&fname=WSGGNKA0KK10OO25EDLKFCMOIGMOCG00USUWQLB1GGVXCCSSNKB4FD54FG54JGWX44POGD152004NK14PKMOA0YSYSRKWSGCJDVXHGB5SWB001UWECGCKLXXRKPO4511DGNO54NKVWKOSSXSPKRK40MPMLGDYXB0NK30YSDGQO10NOPKVWPO21KKJCLKEGZWQOOKA0KK20UWB1NOHD51NLRK"}},
    "通訊錄管理": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MekF2Y0hSaFh6RTJPVEUyT0Y4eU5qUXdORGc1WHpBNU5ETTJMbkJrWmc9PQ==&fname=WSGGXWB0YWLKOO1050LKRKHGVWPKWTGGYSB0XSNKVXGDXW40YSYWA054WWOOKLOKWW54B505A404NKXTKO30TSMOSTIC10LKGGRLNOTSUWZWCDUWFHTS45PKUS00ZT25DGA041GDZSKOWTB150FGWSICXT51LKB0NK30YSDGDGCCB5FCYWQOYTYXDGB0A0CH1430JDGGWSA0CGMK21XT30A514B0JG45SSPOROFCYWKK41IHWW04DHHG"}},
    "誤判信放行": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9Memd5TDNCMFlWOHhOamt4TlROZk1UWTNOalF4TjE4d09UUXpOUzV3WkdZPQ==&fname=LOGGVWOKYW44A1YX50LKSXHGVW3025GGYSB0IC24QPQLDC40A020YWUWLO10USOKDGKKDHXXDG04LOLO14SWTSXWSTB0NKHCZTVXDCA0LKB0B450GG10KLDCPKPOWW25B0NO50SXVWB4USXSWSVW043501QLTTRKNK30ECTWDG54NOQKVWPOA5KKNO10PO34QOOKA0KK20UWB1NOHD51NLRK"}},
    "預設名單": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9Memd6TDNCMFlWOHhOamt4TlRSZk9EQTVOemN5WHpBNU5ETTJMbkJrWmc9PQ==&fname=LOGGVWOKYW44A1YX50LKSXHGVW3025GGYSB0IC24QPQLDC40A020YWUWLO10USOKDGKKDHXXDG04LOLO14SWTSXWSTB0NKHCZTVXDCA0LKB0B450GG10KLDCDGPOXXOOEDNO54XSVWPKWSNPDG3440LKCCGDQPSSNK30YSDGOOKKRK50DGLKUT10IG04FG34OO30GDB1B430A1A1"}},
    "誤刪除": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MemcwTDNCMFlWOHhOamt4TlRWZk16Z3dNVFkwTlY4d09UUXpOaTV3WkdZPQ==&fname=LOGGVWOKYW44A1YX50LKSXHGVW3025GGYSB0IC24QPQLDC40A020YWUWLO10USOKDGKKDHXXDG04LOLO14SWTSXWSTB0NKHCZTVXDCA0LKB0B450GG10KLDCICPO44MP04NO54XSRK30A1KOPKFG40MPCCGDYXQPYSQOYSDGQO10RKPKDGLKUT10IG04FG34OO30GDB1B430A1A1"}},

}}
staff_mail_gs = {"mail_qd": {

    "帳號申請": {Checklist: {"請參考帳號申請文件": "https://www.gs.ncku.edu.tw/%E5%95%9F%E7%94%A8%E6%95%99%E5%AD%B8/%E6%95%99%E8%81%B7%E5%93%A1"}},
    "使用說明": {Checklist: {"請參考使用說明文件": "https://www.gs.ncku.edu.tw/%E5%B8%B3%E8%99%9F%E8%AA%AA%E6%98%8E/%E6%95%99%E8%81%B7%E5%93%A1"}},
    "忘記密碼": {Checklist: {"請參考密碼重設說明文件": "https://www.gs.ncku.edu.tw/faq/%E5%B8%B3%E5%AF%86%E5%95%8F%E9%A1%8C/%E5%BF%98%E4%BA%86%E5%AF%86%E7%A2%BC%E8%A6%81%E5%A6%82%E4%BD%95%E6%9F%A5%E8%A9%A2%E5%91%A2"}},
    "忘記帳號": {Checklist: {"教職員工登入gsuit帳號為\"員工編號\"，請勿輸入個人郵件帳號": "https://www.gs.ncku.edu.tw/faq/%E5%B8%B3%E5%AF%86%E5%95%8F%E9%A1%8C/%E6%89%BE%E4%B8%8D%E5%88%B0%E6%82%A8%E7%9A%84-google-%E5%B8%B3%E6%88%B6#h.p_DWdKahR8Y9Wi"}},
    "修改寄件人別名": {Checklist: {"請參考說明文件": "https://www.gs.ncku.edu.tw/faq/%E5%B8%B3%E8%99%9F%E5%95%9F%E7%94%A8/gmail-%E5%AF%84%E4%BB%B6%E4%BA%BA%E5%88%A5%E5%90%8D%E8%A8%AD%E5%AE%9A"}},
    "修改寄件者顯示名稱": {Checklist: {"請參考說明文件": "https://www.gs.ncku.edu.tw/faq/gmail/%E5%A6%82%E4%BD%95%E4%BF%AE%E6%94%B9%E5%AF%84%E4%BB%B6%E8%80%85%E9%A1%AF%E7%A4%BA%E5%90%8D%E7%A8%B1"}},
    "更改預設寄件人帳號": {Checklist: {"請參考說明文件": "https://www.gs.ncku.edu.tw/faq/gmail/%E5%A6%82%E4%BD%95%E6%9B%B4%E6%94%B9%E9%A0%90%E8%A8%AD%E5%AF%84%E4%BB%B6%E4%BA%BA%E5%B8%B3%E8%99%9F"}}

}}

mail_staff = {"staff_mail_type": {
    "個人信箱": staff_mail_pisa,
    "公務信箱": staff_mail_z,
    "GSuit": staff_mail_gs
}}

student_mail_pisa = {"mail_qd": {

    "帳號申請": {Checklist: {"帳號即為\"您的學生證號\"": "http://cc.ncku.edu.tw/p/412-1002-14652.php?Lang=zh-tw"}},
    "忘記密碼": {Checklist: {"個人信箱密碼與成功入口密碼連動，修改成功入口密碼即可修改您的個人信箱密碼。": "http://cc.ncku.edu.tw/p/412-1002-14655.php?Lang=zh-tw"}},
    "使用期限": {Checklist: {"將於畢業後半年系統自動刪除該帳號。": "http://cc.ncku.edu.tw/p/412-1002-14652.php?Lang=zh-tw"}},
    "Webmail": {Checklist: {"點此進入webmail頁面": "https://mail.ncku.edu.tw/cgi-bin/login?index=1"}},
    "在iphone系統使用": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9Mekl2Y0hSaFh6RTFPVEE0TWw4MU1URTVNamcwWHpBNU5ETTJMbkJrWmc9PQ==&fname=WSGGXWB0YWLKOO1050LKRKHGVWPKWTGGFGB0XSKKA125XWRKMOMKA0EG14OK50XXNOWW00IHVS04EGKKMOFGTS24STB0MKHCCCMPXWTS14ZWMO01SSGCYWFCNPPO44KKDGA041GDVWNKDC3514B0UW10UT35QPVWMOB4NKEG34HGCDUSPO00QPXXIG10XW14XSJGGCGCWS34FHLOMLQLPOA0SSROJGA0QODCTSDCNO10FDZXHCLK54IC50MOFHHCKLB0QL14TXJDMLTWYSA4FCB4OOKKA0QKZTCCYX10VSTWDHDH"}},
    "在Android系統使用": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9Memt2Y0hSaFh6RTFPVEE0T1Y4NU1UTTRNelk0WHpBNU5ETTJMbkJrWmc9PQ==&fname=WSGGXWB0YWLKOO1050LKRKHGVWPKWTGGFGB0XSKKA125XWCCSSECLOUW14OKSWUSLOWWJD05A4NOMOWSIG30A025B0FGXSHCGGVX04B0YSYW50SWSSHG20PKNO40XTZXFGNO50SXVWB4JGWSB0MO04ICA1QLQPEGYSQOYWDGDGA4JGTWRKPOUT25TSPOROWWPK1410YS20MO35LOZTRLB0FCXWMKJG45WWPOYSOKSS10A1YX5010WTHGQO3025LK1434GGGCCCGDWSPKUSUSLOSWB1OK34OKZTCCID10TSZSDHDH"}},
    "在Mac系統使用": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/var/file/2/1002/attach/10/pta_105741_6271936_66737.pdf"}},
    "在Outlook系統使用": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MekV5TDNCMFlWOHhOVGt3T1RKZk1USTNORE15WHpBNU5ETTRMbkJrWmc9PQ==&fname=0054ROB0RKSSVXHHEDXSJGGDZSB4TSB1QOQK4020VX25DC40DCA4YSFGWW54DGOKSSWWCDMP44A054MK34XSMK35YSROWSGC41VXA4FCYSYWVS5050GGRPGHUSPOWWLP50POSWWTZSJCDG35ECNOYSWS01UXIGCCA0DCOPVWQOA4LKQKICKKA5JHFG0435YWMOOKZTMOYSEGFHRLMLIDNOB5UWB0VSPPUSDC0150SS10PP00WWZSWW24KKTWZTKKFGUWSSKKA1NPMLEG34A4FDDGWSHGKLPKZTPOWWXXDGVWLK14MOMOUWWSIGICRKYSUTXTXWB0WSECJG50EC00CDGHDG4415HHEDA0UW34RK30USGCSTQKOKMP00GDVSPO"}},
    "收發郵件轉寄": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MemswTDNCMFlWOHhOamt4TmpWZk9ESTVPRE13Tmw4d09UUXpOaTV3WkdZPQ==&fname=LOGGVWOKYW44A1YX50LKSXHGVW30WTGG34UWGGGCCCQLPO40FCB4QOB400OOKLSSA4POVX15A404FG141430TSGGB0MONOXSLPJDXWA034MK30FCUS54B5PKRK40CDIDDGA0DCXTQOMOCG00WX24ZWYS44UXSSTSFC3030US20GCHHHH"}},
    "信箱頁面語言更改": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MemsxTDNCMFlWOHhOamt4TmpaZk1UQTVPRFExTWw4d09UUXpOaTV3WkdZPQ==&fname=WSGGNKA0RKDCA110EDLKWW24MKPK25RL2034CCYSTXZTOO40DCYWLOPO0054B4SSLOTSTXIHDG04MOHCRKPKTSMOKL34B1NOCCVXXWTSLKA450SW145424DCGCLK0115JCLKSXHGTWFGSWHCUS30A110"}},
    "自動回覆": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MemsyTDNCMFlWOHhOamt4TmpkZk9UZzNPRE01TTE4d09UUXpOaTV3WkdZPQ==&fname=WSGGNKA0KK10OO25EDLKFCMOIGMOCG00USUWQLB1GGVXCCSSNKB4FD54FG54JGWX44POGD152004NK14PKMOA0YSYSRKWSGCJDVXHGB5SWB001UWECGCKLXXRKPO4511DGNO54NKVWKOSSXSPKRK40MPMLGDYXB0NK30YSDGQO10NOPKVWPO21KKJCLKEGZWQOOKA0KK20UWB1NOHD51NLRK"}},
    "通訊錄管理": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MekF2Y0hSaFh6RTJPVEUyT0Y4eU5qUXdORGc1WHpBNU5ETTJMbkJrWmc9PQ==&fname=WSGGXWB0YWLKOO1050LKRKHGVWPKWTGGYSB0XSNKVXGDXW40YSYWA054WWOOKLOKWW54B505A404NKXTKO30TSMOSTIC10LKGGRLNOTSUWZWCDUWFHTS45PKUS00ZT25DGA041GDZSKOWTB150FGWSICXT51LKB0NK30YSDGDGCCB5FCYWQOYTYXDGB0A0CH1430JDGGWSA0CGMK21XT30A514B0JG45SSPOROFCYWKK41IHWW04DHHG"}},
    "誤判信放行": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9Memd5TDNCMFlWOHhOamt4TlROZk1UWTNOalF4TjE4d09UUXpOUzV3WkdZPQ==&fname=LOGGVWOKYW44A1YX50LKSXHGVW3025GGYSB0IC24QPQLDC40A020YWUWLO10USOKDGKKDHXXDG04LOLO14SWTSXWSTB0NKHCZTVXDCA0LKB0B450GG10KLDCPKPOWW25B0NO50SXVWB4USXSWSVW043501QLTTRKNK30ECTWDG54NOQKVWPOA5KKNO10PO34QOOKA0KK20UWB1NOHD51NLRK"}},
    "預設名單": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9Memd6TDNCMFlWOHhOamt4TlRSZk9EQTVOemN5WHpBNU5ETTJMbkJrWmc9PQ==&fname=LOGGVWOKYW44A1YX50LKSXHGVW3025GGYSB0IC24QPQLDC40A020YWUWLO10USOKDGKKDHXXDG04LOLO14SWTSXWSTB0NKHCZTVXDCA0LKB0B450GG10KLDCDGPOXXOOEDNO54XSVWPKWSNPDG3440LKCCGDQPSSNK30YSDGOOKKRK50DGLKUT10IG04FG34OO30GDB1B430A1A1"}},
    "誤刪除": {Checklist: {"點此下載說明文件": "http://cc.ncku.edu.tw/app/index.php?Action=downloadfile&file=WVhSMFlXTm9MemcwTDNCMFlWOHhOamt4TlRWZk16Z3dNVFkwTlY4d09UUXpOaTV3WkdZPQ==&fname=LOGGVWOKYW44A1YX50LKSXHGVW3025GGYSB0IC24QPQLDC40A020YWUWLO10USOKDGKKDHXXDG04LOLO14SWTSXWSTB0NKHCZTVXDCA0LKB0B450GG10KLDCICPO44MP04NO54XSRK30A1KOPKFG40MPCCGDYXQPYSQOYSDGQO10RKPKDGLKUT10IG04FG34OO30GDB1B430A1A1"}},

}}
student_mail_gs = {"mail_qd": {
    "帳號申請": {Checklist: {"請參考帳號申請文件。": "https://www.gs.ncku.edu.tw/%E5%B8%B3%E8%99%9F%E8%AA%AA%E6%98%8E/%E5%AD%B8%E7%94%9F#h.p_H-oHrYSwcVXY"}},
    "使用說明": {Checklist: {"請參考使用說明文件。": "https://www.gs.ncku.edu.tw/%E5%B8%B3%E8%99%9F%E8%AA%AA%E6%98%8E/%E5%AD%B8%E7%94%9F"}},
    "使用期限": {Checklist: {"畢業後可繼續使用。": "https://www.gs.ncku.edu.tw/%E5%B8%B3%E8%99%9F%E8%AA%AA%E6%98%8E/%E5%AD%B8%E7%94%9F#h.p_SVFUGCL7cV0m"}},
    "忘記密碼": {Checklist: {"請參考密碼重設說明文件。": "https://www.gs.ncku.edu.tw/faq/%E5%B8%B3%E5%AF%86%E5%95%8F%E9%A1%8C/%E5%BF%98%E4%BA%86%E5%AF%86%E7%A2%BC%E8%A6%81%E5%A6%82%E4%BD%95%E6%9F%A5%E8%A9%A2%E5%91%A2"}},
    "修改寄件人別名": {Checklist: {"請參考說明文件。": "https://www.gs.ncku.edu.tw/faq/%E5%B8%B3%E8%99%9F%E5%95%9F%E7%94%A8/gmail-%E5%AF%84%E4%BB%B6%E4%BA%BA%E5%88%A5%E5%90%8D%E8%A8%AD%E5%AE%9A"}},
    "修改寄件者顯示名稱": {Checklist: {"請參考說明文件。": "https://www.gs.ncku.edu.tw/faq/gmail/%E5%A6%82%E4%BD%95%E4%BF%AE%E6%94%B9%E5%AF%84%E4%BB%B6%E8%80%85%E9%A1%AF%E7%A4%BA%E5%90%8D%E7%A8%B1"}},
    "更改預設寄件人帳號": {Checklist: {"請參考說明文件。": "https://www.gs.ncku.edu.tw/faq/gmail/%E5%A6%82%E4%BD%95%E6%9B%B4%E6%94%B9%E9%A0%90%E8%A8%AD%E5%AF%84%E4%BB%B6%E4%BA%BA%E5%B8%B3%E8%99%9F"}}
}}

mail_student = {"student_mail_type": {

    "個人信箱(僅108學年度(含)前擁有)": student_mail_pisa,
    "GSuit": student_mail_gs

}}

Mail = {"MailUserID": {

        "教職員": mail_staff,
        "學生": mail_student,
        "校友": {Checklist: {"請依照以下步驟申請Gsuit信箱": "https://www.gs.ncku.edu.tw/%E5%95%9F%E7%94%A8%E6%95%99%E5%AD%B8/%E7%95%A2%E6%A5%AD%E6%A0%A1%E5%8F%8B"}}

        }}


root = {
    "Keyword": {
        "網路": Network,
        "授權軟體": CAS,  # Campus Authorized Software
        "VPN": VPN,
        "成功入口": iNCKU,
        "電子信箱": Mail,
        "防疫系統": {Checklist: {"請直撥分機50340衛保組": ""}}

    }
}
__PATH__ = os.path.dirname(os.path.abspath(__file__))
global ansList
global tempList
tempDict = {}
ansList = {}
IP = InputParser

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError


print(ansList)
with open("./reference/solution.json", "w", encoding='utf-8') as f:
    json.dump(root, f, default=set_default, ensure_ascii=False)
