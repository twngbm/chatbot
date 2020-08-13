class MessageGeneator(object):
    def __init__(self):
        pass

    def handleUnable(self):
        return "無法處理，可能輸入錯誤?"

    def Keyword(self, exception):
        if exception:
            return "我也想要進來"
        return "我要進來了喔"

    def Location(self, exception):
        if exception:
            return "輸入錯誤"
        return "請輸入地點"

    def StudentID(self, exception):
        if exception:
            return "學號格式錯誤"
        return "請輸入學號"

    def NetConfig(self, exception):
        if exception:
            return "請回答DHCP/PPPOE"
        return "請檢查網路設定"

    def DormRoom(self, exception):
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

    def ComputerTimeSet(self, exception):
        if exception:
            return "請回答正常/異常"
        return "請檢查系統時間"

    def RunAsAdmin(self, exception):
        if exception:
            return "請回答是/否"
        return "是否以系統管理者身分執行"
