import logging

import UserObj


class ClientHelper(object):
    @staticmethod
    async def botHandshake(clientInfo, websocket, Chatbot) -> UserObj.User:
        # Disable all restore and cookies method
        user = ClientHelper.createNewUser(clientInfo[0], clientInfo[1])
        await Chatbot.chat(user)
        await websocket.send(user.sendbackMessage)
        logging.info(f'{user.userID} <<<<<< {user.sendbackMessage}')
        return user

    @staticmethod
    def createNewUser(userIP, userPort) -> UserObj.User:
        user = UserObj.User()
        logging.info(f"Initinal New Client on {userIP}:{userPort}")
        user.userID = ":".join([str(userIP), str(userPort)])
        user.userUpdate('{"DataType":"sys","Data":"restart"}')
        return user
    """
    @staticmethod
    async def restoreUserStatus(headers, clientInfo, key_cookie, cookie_key):
        # TODO:Key check and restore
        pass
        # Cookie check and restore
        try:
            token = headers["Cookie"].split("token=")[1]
            try:
                user = ClientHelper.loadStatus(token)
                return user, None
            except:
                raise IOError
        except:
            # token not found or token
            token = ClientHelper.__generateToken__(clientInfo[0])
            restoreKey = ClientHelper.__genetatrKey__(
                token, key_cookie, cookie_key)
            user = UserObj.User()
            user.token = token
            user.key = restoreKey
            return user
            
    @staticmethod
    def loadStatus(token):
        filename = str(token)
        logging.info(f"Client Restor from cookie token {token}")

        with open("./"+CLIENT_PATH+"/Cookies/"+filename+".pkl", "rb") as f:
            user = pickle.load(f, encoding="utf8")
        return user

    @staticmethod
    def saveStatus(userStatus, key_cookie):
        filename = userStatus.token
        key_cookie[userStatus.key]["Expiry"] = int(time.time()+EXPIRE_TIME)
        with open("./"+CLIENT_PATH+"/Cookies/"+filename+".pkl", "wb") as f:
            pickle.dump(userStatus, f)

    @staticmethod
    def keyCheck(key, key_cookie):
        try:
            key = int(key)
            cookieData = key_cookie[key]
        except:
            return None
        if cookieData == None:
            return None
        if time.time() > int(cookieData["Expiry"]):
            return "Expiry"
        return cookieData["Token"]

    @staticmethod
    def tokenCheck(headers, key_cookie, cookie_key):
        try:
            token = headers["Cookie"].split("token=")[1]
            key = cookie_key[token]
            cookieData = key_cookie[key]
        except:
            return None
        if time.time() > int(cookieData["Expiry"]):
            cookie_key.pop(token, None)
            key_cookie.pop(key, None)

            try:
                os.remove("./"+CLIENT_PATH+"Cookies/"+token)
            except:
                pass

            return "Expiry"
        return token

    @staticmethod
    def __generateToken__(ip):
        payload = {
            "iss": "ncku.chatbot.com",
            "iat": int(time.time()),
            "exp": int(time.time()) + 86400*3,
            "ip": ip
        }

        token = jwt.encode(payload, jwtKey, algorithm='HS256').decode("utf-8")

        return token

    @staticmethod
    def __genetatrKey__(token, key_cookie, cookie_key):
        for key, value in key_cookie.items():
            if value == None:
                key_cookie[key] = {"Token": token,
                                   "Expiry": int(time.time()+EXPIRE_TIME)}
                cookie_key[token] = key
                return key
            elif time.time() > int(value["Expiry"]):
                try:
                    os.remove("./"+CLIENT_PATH+"Cookies/"+value["Token"])
                except:
                    pass
                cookie_key.pop(value["Token"], None)

                key_cookie[key] = {"Token": token,
                                   "Expiry": int(time.time()+EXPIRE_TIME)}
                cookie_key[token] = key
                return key
        key = int(key)+1
        cookie_key[token] = key
        key_cookie[key] = {"Token": token,
                           "Expiry": int(time.time()+EXPIRE_TIME)}
        return key
        """
