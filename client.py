class client(object):
    
	self.IP = ""
	self.token = ""
	self.history = []
	self.knowninfo = {}
	self.currentAns = []

	def getHistory(self):
		return self.history[-10:]
	
	def getknowninfo(self, info):
		try:
			return self.knowninfo[info]
		except:
			return None
	
	def createToken(self, IP):
		import jwt, time
		payload = {
			"iss": "ncku.chatbot.com",
			"iat": int(time.time()),
			"exp": int(time.time()) + 86400*3,
			"ip": ip
		}
		token = jwt.encode(payload, jwtKey, algorithm='HS256')
		return token
