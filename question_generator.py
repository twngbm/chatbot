class MessageGeneator(object):
    def __init__(self):
        pass

    def handleUnable(self):
        return "無法處理，可能輸入錯誤?"
    def ConnectionType(self,exception):
        if exception:
            return "請輸入有線/無線"
        return "請問您目前使用的網路類型?"
    def Keyword(self, exception):
        if exception:
            return "無法判斷問題"
        return "請問有什麼問題?"

    def Location(self, exception):
        if exception:
            return "無法辨識，可輸入宿舍/系館/行政單位"
        return "請輸入地點"

    def StudentID(self, exception):
        if exception:
            return "學號格式錯誤"
        return "請輸入學號"

    def NetConfig(self, exception):
        if exception:
            return "請回答DHCP/PPPOE"
        return "請檢查網路設定"

    def DormID(self, exception):
        if exception:
            return "請回答正確宿舍與房號"
        return "請回答宿舍與房號"

    def ChengKungPortal(self, exception):
        if exception:
            return "請回答成功/失敗"
        return "請檢查帳號密碼是否可登入成功入口"

    def JupyterInstalled(self, exception):
        if exception:
            return "請回答成功/失敗"
        return "請檢查安裝VPN軟體Jupyter Notebook成功或失敗"

    def ComputerTimeset(self, exception):
        if exception:
            return "請回答正常/異常"
        return "請問系統時間是否正常"

    def RunAsAdmin(self, exception):
        if exception:
            return "請回答是/否"
        return "是否以系統管理者身分執行"

    def isDHCP(self,exception):
        if exception:
            return "請回答是/否"
        return "是否使用DHCP"
    def UserDomain(self,exception):
        if exception:
            return "請輸入是/否"
        return "請問是否為本校師生?"
    def isSolved(self,exception):
        if exception:
            return "請回答是/否"
        return "<br>請問問題是否有解決?"
    def EndMessage(self,exception):
        if exception:
            return ""
        return "感謝使用，如問題尚無解決請聯絡計網中心61010<br>請問有其他問題嗎?"
    def IPDomain(self,exception):
        if exception:
            return "請輸入是/否"
        return "請問您是否在校內使用"
    def UseVPN(self,exception):
        if exception:
            return "請輸入是/否"
        return "請問是否使用VPN"
    def InstalledVersion(self,exception):
        if exception:
            return "請輸入是/否"
        return "是否使用校內授權網站下載及安裝之版本?"
    def iNCKULogin(self,exception):
        if exception:
            return "請輸入是/否"
        return "請問成功入口是否可登入?"
    def VPNQD(self,exception):
        if exception:
            return "請輸入安裝/使用"
        return "請問在VPN[安裝|使用]上哪一個部分的問題?"
    def BackupMail(self,exception):
        if exception:
            return "請輸入是/否"
        return "請問是否有設定備用信箱?"
    def inckuQD(self, exception):
        if exception:
            return "請輸入<br>忘記密碼<br>預設密碼無法登入"
        return "請問在成功入口使用上有什麼問題?"