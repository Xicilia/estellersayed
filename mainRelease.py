#this is first version that isnt really useful but in time maybe i fix all problems



import random
import requests
import io
import vk_api
from vk_api import VkApi
from vk_api import upload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.upload import VkUpload
import threading
import time



###########   WORK WTIH TEXT ##################

def find(text,target,withClear = False):
	#function which checking if text have target symbol
	#if withClear is true removes target from text
		for letter in text:

				if letter == target:

					result = text.index(letter)

					if withClear:
						text = text[:result] + text[result+1:]
						return result,text

					return result

		return False

def normalizeText(text):
	#function which delete some html tags from text which arent supported by vk

	while find(text,'>'):

		subStart,text = find(text,'<',True)
		subEnd,text = find(text,'>',True)

		if text[subStart:subEnd] == 'br' or text[subStart:subEnd] == '\n' : #add enter instead <br>
			#idk why its deleting \n from original text needs to fix later
			text = text.replace(text[subStart:subEnd],'\n')

		else:
			text = text.replace(text[subStart:subEnd],'')

	return text

#################################################

def timer(timer):
	i = 0
	for i in range(0,timer):
		i += 1
		time.sleep(1)
		print(i)



class Bot:

	def __init__(self,id,token):

		self.logfile = 'log.txt'

		self.token = token
		self.id = id

		self.timerThread = threading.Thread(target=timer,args=(5,))

		self.session: VkApi = vk_api.VkApi(token=self.token)
		self.longpoll = VkBotLongPoll(self.session, self.id)

		self.api = self.session.get_api()
		self.upload = VkUpload(self.api)

		print('bot initialized')

	def writeToLog(self,event):
		#doesnt work as i want needs to be supplemented
		with open(self.logfile,'a') as f:
			f.write(event)
		

	def sendMsg(self,text,toWho,imageStuff,isAttachment = False):
		#send message
		if isAttachment:

			attachment = f'photo{imageStuff[0]}_{imageStuff[1]}_{imageStuff[2]}'
			self.api.messages.send(random_id=random.randint(0,999999),message=text,peer_id=toWho,attachment=attachment)

		else:
			self.api.messages.send(random_id=random.randint(0,999999),message=text,peer_id=toWho)

	def getImageFromThread(self,url):

		image = requests.get(url).content #image as content from web page

		byteImage = io.BytesIO(image) #image as bytes

		try:
			response = self.upload.photo_messages(byteImage)[0]

			imageStuff = [response['owner_id'], response['id'], response['access_key'],]

			return imageStuff

		except:

			return None


	def getMainPostFromThread(self):
		#gets main thread post with text and image(if has)
		isAttachment = True

		data = requests.get('https://2ch.hk/b/catalog.json') #have a lot of useless info about all page
		dataJson = data.json()

		threads = dataJson['threads'] #have info only about threads, but still a lot of trash

		threadNumber = random.randint(0,len(threads)) #just a temp var for get random thread in list of threads

		sendingText = normalizeText(threads[threadNumber]['comment']) # in this step already have formated text

		picRelated = 'https://2ch.hk' + threads[threadNumber]['files'][0]['path'] #path for post pic

		try:
			imageStuff = self.getImageFromThread(picRelated)

		except:
			isAttachment = False

			imageStuff = None
		
		return isAttachment, sendingText, imageStuff


	def listenEvents(self):	
		for event in self.longpoll.listen():

			if event.type == VkBotEventType.MESSAGE_NEW:
				if event.object.message['text'].lower() == 'бот':

					if not self.timerThread.is_alive():

						self.timerThread = threading.Thread(target=timer,args=(5,))
						self.timerThread.start()
						
						isAttachment,sendingText,imageStuff = self.getMainPostFromThread()
						self.sendMsg(sendingText ,event.object.message['peer_id'],imageStuff,isAttachment)

					else:
						self.sendMsg('куда лезешь подожди дурак' ,event.object.message['peer_id'],None,False)

				elif event.object.message['text'].lower() == 'ролл':

					self.sendMsg(str(random.randint(100,999)),event.object.message['peer_id'])

groupID = 0
token = 0

bot = Bot(groupID,token)

bot.listenEvents()


