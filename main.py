import discord
import datetime
import time
import aiohttp
import json
from threading import Thread
import asyncio

class MyClient(discord.Client):
	daily_user_list = []
	chatbot_job = False
	chatbot_job_thread = None

	async def on_ready(self):
		print('Logged on as {0}!'.format(self.user))

	async def on_message(self, message):
		#print('Message from {0.author}: {0.content}'.format(message))
		if message.author.bot:
			return None
		#simple_greet(message)
		if message.content.startswith("알파,") and self.chatbot_job == False and len(message.content.strip()) != 3:
			self.chatbot_job = True
			await self.simple_chat(message)
			#self.chatbot_job_thread = Thread(target=self.simple_chat, args=[message])
			#self.chatbot_job_thread.start()
			return
		elif message.content.startswith("알파,") and self.chatbot_job == True:
			await message.channel.send("챗봇이 생각 중입니다. 출력 결과를 기다리세요.")
			return


		await self.daily_greet(message)
		
	def check_daily_user_list(self):
		while True:
			print("Start check_daily_user_list()...")
			need_to_remove = []
			today = datetime.datetime.now()
			#print("Today is :" + str(today))
			for idx, val in enumerate(self.daily_user_list):
				if val[1] + datetime.timedelta(days=1) < today:
					# note to need_to_remove list to delete this user from daily_user_list
					need_to_remove.append(idx)
			if need_to_remove == []:
				print("No need to continue to delete...")
				pass
			else:
				print("Need to delete user from user list : ")
				print(need_to_remove)
				print("")
				for val in reversed(need_to_remove):
					del self.daily_user_list[val]
				print("")
				print("Done, current list is : ")
				print(self.daily_user_list)
			time.sleep(3600)
			#self.check_daily_user_list()
		pass
		
	async def check_user_list(self, author):
		for list in self.daily_user_list:
			if list[0] == author:
				return True
		return False
		
	async def daily_greet(self, message):
		# check message is greeting
		if '안녕' in message.content:
			user_name_discriminator = message.author.name + "#" + message.author.discriminator
			# check user is listed on daily_user_list
			if await self.check_user_list(user_name_discriminator):
				print("already exists in user_list")
				# doing nothing
				pass
			else:
				await message.channel.send('안녕하세요, {0.author.display_name}'.format(message))
				#print(message.author.name + " " + message.author.discriminator)
				# just putting message.author makes Huge formed info into variable...
				self.daily_user_list.append([user_name_discriminator, datetime.datetime.now()])
				print(self.daily_user_list)
		else:
			# doing nothing
			pass
	
	# This function is not using right now...
	async def simple_greet(self, message):
		if '=안녕하살법' in message.content:
			await message.channel.send('=안녕하살법받아치기')
		elif '안녕하살법' in message.content:
			await message.channel.send('안녕하살법받아치기')
		elif '안녕' in message.content:
			await message.channel.send('안녕하세요')

	# This function is not working rigth now...
	async def simple_chat(self, message):
		try:
			#print("simple_chat()")
			#await message.channel.send("챗봇이 응답하지 않습니다, 담당자에게 확인하세요.")
			
			proccessed_message = message.content.replace("알파,", "", 1).strip()
			headers = {"Content-Type" : "application/json; charset=utf-8"}
			my_json = {"str" : proccessed_message}
			timeout1 = aiohttp.ClientTimeout(total=60)
			timeout2 = aiohttp.ClientTimeout(total=40)

			async with aiohttp.ClientSession(timeout=timeout1) as session:
				async with session.post("http://127.0.0.1:5000/chat", headers=headers, json=my_json, timeout=timeout2) as r:
					if r.status == 200:
						js = await r.json()
						await message.channel.send(js['result'].strip().replace("\n", ""))
						self.chatbot_job = False
					else:
						print("post error in simple_chat()")


			#res = requests.post("http://127.0.0.1:5000/chat", headers=headers, data=json.dumps(data), timeout=60)
			#res_json = res.json()
			#print(res_json)

			#await message.channel.send(res_json['result'].strip().replace("\n", ""))
			#message.channel.send(res_json['result'].strip().replace("\n", ""))
			#await message.channel.send("챗봇이 응답합니다. 담당자에게 확인하세요.")

		except Exception as e:
			print(e)
			#await message.channel.send("챗봇이 응답하지 않습니다. 담당자에게 확인하세요.")
			message.channel.send("챗봇이 응답하지 않습니다. 담당자에게 확인하세요.")
			self.chatbot_job = False

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)

th1 = Thread(target=client.check_daily_user_list)
th1.daemon = True
th1.start()

client.run('<PUTYOURTOKENHERE>')
print("main.py is done, exiting...")
