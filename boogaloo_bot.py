#A Discord bot that keeps a scoreboard of points, comes with games, a music function, and some random other stuff.

import discord
import asyncio
import numpy as np
import aiohttp
from discord.ext import commands
import time
import os
import sys
import math
import lxml
from lxml import etree
import urllib
#import strawpoll

#Tokens, fill these in with whatever token you want
#TOKEN = '' #Testing version token
TOKEN = '' #Actual version token

bot = commands.Bot(command_prefix='!')
client = discord.Client()

OPUS_LIBS = [os.path.join(sys.path[0], 'Audio\libopus-0.x86.dll'), os.path.join(sys.path[0], 'Audio\libopus-0.x64.dll'), os.path.join(sys.path[0],'libopus-0.dll'), os.path.join(sys.path[0],'libopus.so.0'), os.path.join(sys.path[0],'libopus.0.dylib')]

#------------------------------Variables and constants-------------------------
losses = 73 #Number of Loss pictures currently available for !loss
beds = 86 # Number of beds available for !bed
VOLUME = 0.25
FILE_CAP = 4096

#---------------------------------------Secret variables and functions-------------------------------

#Generates a new secret word	
def new_secret_word():
	file = open(os.path.join(sys.path[0], 'etc/dictionary.txt'), 'r')
	file_contents = file.read().splitlines()
	file.close()
	the_new_secret_word = file_contents[np.random.randint(len(file_contents))]
	del file_contents	
	return the_new_secret_word

secret_word = new_secret_word() #Generate the secret word

#------------------------------------------Special variables----------------------------------
links420 = [ 'https://www.youtube.com/watch?v=WeYsTmIzjkw', 'https://www.youtube.com/watch?v=KlujizeNNQM']

#Prestige arrays. Possible roles, in order, point costs, and colors for each role
prestiges = ['Crusty Crustacean', 'Brine Shrimp', 'Prawn', 'Stone Shrimp', 'Bronze Shrimp', 'Silver Shrimp', 'Golden Shrimp', 'Perfect Prawn', 'Master of Shrimp', 'God of all Shrimp']
prestige_costs = [100, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 500000]
prestige_color = [0x804000, 0xff7733, 0xffaa80, 0xb8b894, 0x994d00, 0xb8b894, 0xe6ac00, 0xffb3d9, 0xff4d4d, 0xffff80]


#Games that the bot could be playing
game_names = [
	'Super Smash Bros. Ultimate', 'Sonic Forces', 'Project FYQ', 'No More Heroes 3', 'Boogaloo Shrimp', 'Kimulator', 'Lucioball', 
	'Pocket Rumble for Switch', 'Skyrim for MS DOS', 'Overwatch?', 'Puyo Puyo', 'a sick saxophone solo', 'Mother 4', 'Kirby Airride 2', 
	'The Boogaloo Game', 'The Cheeto Game', 'Real Fighting Games', 'Princess Gamecube and the Golden Memory Card', 
	'Undertale 2: Revenge of Sans', 'a bad video game', 'Panel de Pon', 'Action 52', 'Elebits', 'The Wonderful 102',
	'Ghost Trick', 'Pikmin 4 (Switch)', 'The Camping Game', 'Super Boogaloo World', 'Knack 2', 'Super Mario Bros. 2 BABY!', 
	'Paper Mario: The Thousand Year Door', 'Just Dance 2019 (Wii)', 'Super Mario 69', 'Donkey Kong 64 (Wall Edition)', 'The Beautiful Game',
	'Yoshi Commits Tax Fraud', 'Kirby Does His Taxes', 'Waluigi\'s Taco Stand', 'Super Mario Bros. USGay', 'The Nonary Game: Ambidex Edition',
	'Bubsy 3D', 'Death Drive Mark II', 'Scooby Doo 2 on BluRay', 'Slap City', 'Sonic Adventure 3', 'Magical Tetris Challenge', 'Super Dunkingronpa 2',
	'Super Puyo Puyo Tsu Remix', 'Pokemon Crystal Vietnam', 'Hotel Mario', 'the slots', 'Brawl Minus', 'Dr Robotnik\'s Mean Bean Machine'
	]
	
#Rarity of card drops and card names. Should all be through 1-10. 1 Being the most rare and 10 being the most common
card_rarities = [
	3, 5, 8, 4, 5, 5, 3, 4, 4, 7,
	3, 2, 6, 6, 4, 3
]

card_names = [
	'Red Hot Pepper Detector', 'Soggy Burger', 'WELCOME!', 'Scott the Woz', 'Segacamp Gamer', 'Abraham Lincoln', 'King Crismon', 'Toad', 'Elebits', 'Flame Hyenard',
	'Cloud\'s Up-air', 'Ankimo', 'Gutsman\'s Ass', 'Jack Frost', 'Seesaw Effect', 'Shield of Effectively Infinite Size'
]

card_sum = sum(card_rarities)

#Auction item names
auction_names = ['handful of Smarties', 'egg', 'used stereo', 'pair of Yeezys', 'wallet I found in a parking lot', 'barbeque grill', 'antique statue', 'human liver', 'very nice watch', 'old mask', 'brilliant urn', 'handcrafted necklace', 'priceless painting', 'royal crown', 'ancient Egyptian sarcophagus']

#Birthday array
birthdays = ['10.14']

#-----------------------------------------Message and join events---------------------------
@bot.event
async def on_member_join(member):
	await bot.send_message(member, message.author.mention + ' ***Welcome!***')

#@bot.event
#async def on_command_error(ctx, error):
#	print ('Error, invalid command used')
	
@bot.event
async def on_message(message):
	#Variable declarations
	your = False
	youre = False
	weeb = False
	Sam = False
	naruto = False
	contains_secret_word = False
	random_integer = np.random.randint(15000)
	global secret_word
	
	#Make sure the bot doesn't read its own messages
	if message.author == bot.user:
		return
	
	#Open stat tracking file
	try:
		file = open(os.path.join(sys.path[0], 'save/stats_') + str(message.server.id) + '.txt', 'r')
		file_info = file.readlines()
	except: #If stat file does not exist for the current server, create one and then do stat tracking
		try:
			current_time = time.localtime() #year, month, day, hour, minute, second, weekday, year day, is daylight savings time?
			file = open(os.path.join(sys.path[0], 'save/stats_') + str(message.server.id) + '.txt', 'w')
			file.write('all 0\nloss 0\nbed 0\nwinner 0\n' + 'year '+ str(current_time[0]) + '\nmonth ' + str(current_time[1]) + '\nday ' + str(current_time[2]) + '\n')
			file.close()
			file = open(os.path.join(sys.path[0], 'save/stats_') + str(message.server.id) + '.txt', 'r')
			file_info = file.readlines()
		except:
			print('Private message from ' + str(message.author))
		
	content = []
	
	#Make some corrections to the file structure
	try:
		for x in file_info:
			content.append(x.split())
	except:
		return
	
	del file_info
	file.close()

	#Add to total count of 
	author_exists = False
	for x in content:
		if x[0] == 'all':
			x[1] = str(int(x[1]) + 1)
		if x[0] == str(message.author.id):
			x[1] = str(int(x[1]) + 1)
			author_exists = True
	
	if not author_exists:
		content.append([str(message.author.id), '1'])
			
	#Check for any key words
	#Parse any message sent for the word  'you're', or 'your'
	msg_list = message.content.split()
	
	weeb_array = ['anime', 'marth', 'lucina', 'sora', 'goku', 'kirito', 'sasuke', 'hentai', 'tsundere', 'yandere', 'ecchi', 'manga', 'pocky', 'vegeta', 'dakimakura', 'nippon', 'sakura', 'itadakimasu', 'gomen', 'baka', 'yaoi', 'yuri', 'waifu', 'miku', 'boruto', 'kawaii', 'moe', 'senpai', 'sensei', 'onii', '-san', '-chan', 'asuna', '-kun', 'arigatou', 'luffy']
	
	
	if str(message.server.id) == '117937572612669443':
		if 'https://www.youtube.com/watch?v=it8vJ03E8c8' in message.content:
			await bot.send_message(message.channel, 'I am not going to acknowledge the Shingle Jingle.')	
			return
	if ('your' in message.content or 'Your' in message.content) and random_integer % 15 == 0:
		your = True
	if ('you\'re' in message.content or 'You\'re' in message.content) and random_integer % 8 == 0:
		youre = True
	if 'Sam' in message.content or 'sam' in message.content or 'Sam\'s' in message.content or 'sam\'s' in message.content:
		Sam = True
	if 'Naruto' in message.content or 'naruto' in message.content or 'boruto\'s dad' in message.content or 'Boruto\'s dad' in message.content:
		naruto = True
	if 'rain' in message.content or 'raining' in message.content:
		await bot.send_file(message.channel, os.path.join(sys.path[0], 'etc/raining.jpg'))
	if 'where are we' in message.content.lower():
		if random_integer % 2 == 0:
			await bot.send_message(ctx.message.channel, 'Bitch Town (Population Quantae)')
		else:
			await bot.send_message(ctx.message.channel, 'Fuck Town')
	
	for x in message.content.split():
		if x.lower() in weeb_array:
			weeb = True
	
	if secret_word.lower() in message.content.lower():
		contains_secret_word = True
	
	#Set the mood if it's right
	if message.content == 'this is so sad':
		await play_music(message ,'https://www.youtube.com/watch?v=kJQP7kiw5Fk')
	
	if contains_secret_word: #Give some points for guessing the secret word
		add_points(message.author, 2000, message.server)
		await bot.send_message(message.channel, 'Nice! You used the secret word, **' + secret_word + '**\nYou\'ve just won 2000 points! I\'ve generated a new word, now.')
		stock_rates(message.server, 0.4)
		secret_word = new_secret_word()

	elif your or youre:
		add_points(message.author, -2, message.server) #Take away 2 points for bad form
		if your == True:
			msg = '*you\'re \n'
		elif youre == True:
			msg = '*your \n'
		await bot.send_message(message.channel, msg)
	elif weeb or naruto:
		add_points(message.author, -3, message.server) #Take away 2 points for bad form
		msg = 'Weebs should go and stay go'
		await bot.send_message(message.channel, msg)
		if random_integer % 17 == 0:
			stock_rates(message.server, -0.02) #Give stocks with a lower rate if someone mentions anime
		if naruto:
			await bot.send_file(message.channel, os.path.join(sys.path[0], 'naruto.jpg'))
	
	#Secret message
	if random_integer == 69 or random_integer == 690 or random_integer == 6969:
		await bot.send_message(message.channel, 'Congrats, you\'ve unlocked secret message 1! https://youtu.be/_NoDMbXqhPI')
		add_points(message.author, 75, message.server) #Give 75 points for sercet 1
		stock_rates(message.server, 0.04)
	if random_integer == 420 or random_integer == 42069:
		await bot.send_message(message.channel, 'Congrats, you\'ve unlocked secret message 2! https://www.youtube.com/watch?v=G-gqbLUKva0')
		add_points(message.author, 150, message.server) #Give 150 points for sercet 2
	if random_integer == 11037 or random_integer == 1337:
		await bot.send_message(message.channel, 'Congrats, you\'ve unlocked secret message 3! https://www.youtube.com/watch?v=jWJYF0Zdjqo')
		add_points(message.author, 250, message.server) #Give 250 points for sercet 3
		
	if random_integer % 300 == 0: #Randomly update the game the bot is playing once every 300 messages or so.
		change_name = game_names[np.random.randint(len(game_names))]
		await bot.change_presence(game=discord.Game(name = change_name, type = 0))
	
	if random_integer % 161 == 0: #If the bot sends 56.
		if random_integer % 3 == 0: #Rare 56
			await bot.send_file(message.channel, os.path.join(sys.path[0], '562.png'), content = message.author.mention + ' Quick!')
		else:
			await bot.send_file(message.channel, os.path.join(sys.path[0], '56.jpg'), content = message.author.mention + ' Quick!')
		response = await bot.wait_for_message(timeout = 10, author = message.author, content = '56')
		if response == None: #If no correct answer is given in the time limit
			response_message = 'Wow, look at this dummy, everyone! Who can\'t even answer a simple math question?\n'
			add_points(message.author, -25, message.server) #Take away 25 points for not knowing math
		else:
			add_points(message.author, 25, message.server) #Give 25 points to the sharp young gentleman/lady.
			response_message = 'Congrats, you did it!\n'
		await bot.send_message(message.channel, message.author.mention + response_message)
		
	if random_integer % 75 == 0: #Random chance to provide interest to the bank
		interest(0.03, message.server) #Interest rate of 4% to the server
		stock_rates(message.server, 0) #Adjust stock rates
		print('Interest applied to the bank and stocks changed on ' + str(message.server))
					
	#Track command requests in stats file
	try:
		if msg_list[0] == '!loss':
			for x in content:
				if x[0] == 'loss':
					x[1] = str(int(x[1]) + 1)
		elif msg_list[0] == '!bed':
			for x in content:
				if x[0] == 'bed':
					x[1] = str(int(x[1]) + 1)
	except:
		print ('Empty message has been sent in ' + str(message.server) + ' \n')
	
	#Output to stats file
	file = open(os.path.join(sys.path[0], 'save/stats_') + str(message.server.id) + '.txt', 'w')
	for x in content:
		try:
			file.write(x[0] + ' ' + x[1] + '\n')
		except:
			print ('Error, unknown characters detected!')
	file.close()
	

	await bot.process_commands(message) #Now do commands
	
	#Give a point afterwards, but only if it was not a command
	try:
		if not str(message.content)[0] == '!':
			add_points(message.author, 1, message.server)
	except:
		pass

#-------------------------------------COMMAND FUNCTIONS----------------------------------	
	
@bot.command(pass_context = True, description = 'Gives a lengthy message about the commands that I know how to do and how you can use them. I will send you the message via PM.')
async def helpme(ctx):
	await bot.send_typing(ctx.message.channel)
	msg1 = '''**Here\'s a list of what I can currently do:**\n
__General functions__\n
**!help** ***(<command>)***			Displays all the commands I can take, or if you use !help with the command's name, gives you more information and usage.
**!helpme**							Displays all the normal commands that I know how to do.
**!coin**							Flips a coin if you don't have one.
**!bed**							Bestows upon you a bed for sleeping. No refunds (Only available at bed time).
**!lore**							Provides some random lore. Picks from a random wiki.
**!info**							Provides information on what the bot has done and how many items I have.
**!stats**							Provides some stats about the messages that have been sent.
**!loss (<number>)**					Posts a random Loss image. If given a number, sends the loss picture with that number in the collection. (0 to number of losses-1)
**!rand** ***<num1> <num2>***			Picks a random number between num1 and num2
**!owhero** ***(dps, tank, support)***	Picks a random Overwatch hero if you need help deciding (Can also give class, but that\'s optional)
**!pin** ***(<+/-/%\number> <text/link>)***				List of links. To add to the list, use +, to remove, use -. Then, provide what should be added to the pin list. With no arguments, pulls a random pin.
'''
	msg2='''\n__Functions involving points or games__\n
**!points**							Life is a competition; figure out who's winning. Gives a leaderboard and a breakdown of scoring.
**!bomb**							Starts a bomb game. Players try to defuse a bomb to gain (or lose) points.
**!superchance**					Like chance time, but with bigger and crazier effects. Must be Prawn prestige or higher. Costs 40 points to play.
**!ultrachance**					An even more extreme chance time. Only usable by those of Silver Shrimp rank or higher. Costs 100 points.
**!rps**							Play ~~Pokken~~ Rock, Paper, Scissors with the bot. You'll win 8 points if you win and lose 8 points if you lose.
**!buy** ***(bed, chance, card)***	Spend 35 points to reset privileges for the day. Can either be for bed, cards, or chance. Works for whole server.
**!bank** ***(<d,w> <amount>)***	Put money in the bank or take money out. Will earn interest over time.
**!stocks** ***(<b,s> <company> <amount>)***	Buy or sell some stocks. Much like real stocks, the prices can change sporadically.
**!slot** ***<bet>***				Play a slot machine for a chance at points. You have to bet points to play. 
**!chance** ***(help)***			Does a random effect. Can be done only once per day. Use 'help' after to see possible effects
**!prestige**						Allows you to earn ranks that allow you access to more commands.
**!reset**							Anyone at the highest prestige may completely reset the points for the entire server.
**!bet** ***<amount>***				Make a bet with another user. The winner is decided by the honor system, so please be honest!
**!card** 							Provides you a random card from the Boogaloo bot's collection. You may have one card per day. 
**!mycards** ***(number)***			Gives you information about what cards you own. Use a number to see a card you own. Shows foils, too.
**!auction**						Start an auction where users bet over an item. Bid wisely to earn points.
'''	
	msg3 = '''\n__Commands related to music:__ \n
**!pinmusic** ***(<+/-/%> <link>)***		Same as pin, but exclusively for music. Randomly gives music if used with no arguments
**!music** ***(<youtube_link>)***			Without an argument, plays a random link from the music list. With a link, joins your voice channel and plays the link. Has a queue which can be interacted with. The audio player can sometimes be janky, so keep that in mind.
**!add** ***<number_of_songs\link>***		Adds songs to the end of the music queue. Will not make bot join call. Can only take 1 link at a time, but with number, will add that many random songs (Less than 15).
**!remove** ***<link>***					Removes the provided link from the music queue.
**!priority** ***<link>***					Adds the provided link to be the second song to play in the music queue. Costs 7 points.
**!killmusic**								Clears the entire music queue and kicks the bot from the call.
**!volume**	***<number>**					Sets the volume for the music to the number provided. Goes from 0 to 2 (2 is 200%).
**!queue**									Displays the current music queue. Takes around 30 seconds to fetch information.
'''
	msg4= '''\n__General information__\n
Every time I start up, I will generate a secret word from a list of commonly used words. If you use the word in a message, you can get bonus points!
There are a few other words that I will react to. See if you can find out what they are.
There is a random chance whenever you reply that I can send a secret message. Some are rarer than others.
I recommend making a specific channel for the bot, so that there is less text spam.
\nPlease send commands in servers and not private messages. I am unable to process some commands unless they are on a text channel in a server.
\nI also have some secret commands, but I won\'t tell you what they are. You have to find out on your own!
\nIf you would like to report any bugs or make a suggestion, please visit my server at: https://discord.gg/SsCzmPC
I may have missed some bugs here and there, so please let me know if you find any and I will try to fix it, thanks!'''
	await bot.start_private_message(ctx.message.author)
	await bot.send_message(ctx.message.author, msg1)
	await bot.send_message(ctx.message.author, msg2)
	await bot.send_message(ctx.message.author, msg3)
	await bot.send_message(ctx.message.author, msg4)

@bot.command(pass_context = True, description = 'Provides some information regarding my statistics. These are independent of your server. I will send you a private message with the information.')
#!info implementation
async def info(ctx):
	try:
		file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_pinlist.txt'), 'r')
		file_contents = file.readlines()
		file.close()
	except:
		file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_pinlist.txt'), 'w')
		file.close()
		file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_pinlist.txt'), 'r')
		file_contents = file.readlines()
		file.close()
	
	count = len(file_contents)
	del file_contents
	
	try:
		file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_musiclist.txt'), 'r')
		file_contents = file.readlines()
		file.close()
	except:
		file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + 'musiclist.txt'), 'w')
		file.close()
		file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + 'musiclist.txt'), 'r')
		file_contents = file.readlines()
		file.close()
	
	count2 = len(file_contents)
	del file_contents
	
	msg = 'Currently, there are **' + str(losses) + '**  loss pictures I can choose from \nI offer a selection of ***' + str(beds) + '***  beds for your comfort \nThe pin list contains ***' + str(count) + '***  items\nThe music list contains ***' + str(count2) + '*** songs\nI can play one of ***' + str(len(game_names)) + '*** games.\nThere are **' + str(len(card_rarities)) + '** cards to collect.\nUse **!helpme** for a list of commands or **!stats** for even more information\n'
	
	#Send the message
	await bot.start_private_message(ctx.message.author)
	await bot.send_message(ctx.message.author, msg)

@bot.command(pass_context = True, description = 'Provides data that I collected about this specific server. I will send you a private message with the information.')
#!stats impementations
async def stats(ctx):
	file = open(os.path.join(sys.path[0], 'save/stats_') + str(ctx.message.server.id) + '.txt', 'r')
	file_info = file.readlines()
	file_contents = []
	
	#Format to remove the spaces DEBUG This can be optimized
	for x in file_info:
		file_contents.append(x.split())
	
	del file_info
	file.close()
	
	#Now, provide info
	msg = ''
	name = ''
	for x in file_contents:
		if x[0] == 'all':
			msg += 'Here are the stats I have collected for ' + str(ctx.message.server) + '. Please remember that I can only read messages when I am online.\n Since _July 15, 2018_, I have read _' + x[1] + '_ messages.\n'
		elif x[0] == 'loss':
			msg += 'I have posted _' + x[1] + '_ loss memes.\n'
		elif x[0] == 'bed':
			msg += 'I have provided _' + x[1] + '_ beds for your sleeping pleasure.\n'
		elif x[0] == 'winner' or x[0] == 'year' or x[0] == 'month' or x[0] == 'day':
			await asyncio.sleep(1)
		else:
			#Get the user's name before diplaying it
			user_list = []
			for y in ctx.message.server.members:
			
				if str(y.id) == x[0]: #If a match is found
					name = str(y)
					break
			msg = msg + '**' + name + '** has made _' + x[1] + '_ posts.\n'
		
	#Send the message
	try:
		await bot.start_private_message(ctx.message.author)
		await bot.send_message(ctx.message.author, msg)
	except:
		await bot.start_private_message(ctx.message.author)
		await bot.send_message(ctx.message.author, 'The stats information is too large for Discord to receive. Sorry.')
		
#!mystats implementation
@bot.command(pass_context = True, description = 'Provides statistics specifically for you in this server. I will give you information about your post coount and points.')
async def mystats(ctx):
	#Open stats file
	try:
		file = open(os.path.join(sys.path[0], 'save/stats_') + str(ctx.message.server.id) + '.txt', 'r')
		file_info = file.readlines()
	except: #If stats file does not exist for the current server, create one
		file = open(os.path.join(sys.path[0], 'save/stats_') + str(ctx.message.server.id) + '.txt', 'w')
		file.write(str(ctx.message.author.id) + ' 0\n')
		file.close()
		file = open(os.path.join(sys.path[0], 'save/stats_') + str(ctx.message.server.id) + '.txt', 'r')
		file_info = file.readlines()
	
	#Format the file and then do what you need to
	content = []
	
	for x in file_info:
		content.append(x.split())
	
	#Find how many posts they have
	for x in content:
		if x[0] == str(ctx.message.author.id):
			await bot.send_message(ctx.message.channel, ctx.message.author.mention + 'You have made _' + x[1] + '_ posts.\n')
			return	
	
	try: #Try to give them a message about their points
		await bot.send_message(ctx.message.channel, 'You have _' + x[1] + '_ points.\n')
	except: #If there was an error, ssumse it was because theu did not exist.
		await bot.send_message(ctx.message.channel, 'You have not many any posts yet or have no points.')
	
#!update implementation. Used to update game that the bot s playing
@bot.command(pass_context = True, description = 'One of the secret commands. Use this to update the bot\'s nickname and game that it is playing. If you give this command an argument, it will change what the bot is playing to that argument.\n**Example of usage:**\n!update\n!update Undertale 2: Revenge of Sans')
async def update(ctx):
	await bot.change_nickname(ctx.message.server.me, 'Boogaloo Bot (Use !helpme)')
	#See if the user wants to update the name
	msg_list =  ctx.message.content.split()
	change_name = ''
	if len(msg_list) >= 2:
		for x in msg_list[1:len(msg_list)]:
			change_name += x + ' '
	else:
		change_name = game_names[np.random.randint(len(game_names))]
	await bot.change_presence(game=discord.Game(name = change_name, type = 0))
	#Need permission to change roles
	try:
		await bot.create_role(ctx.message.server, name = 'Boogaloo Bot', colour = discord.Colour(0xff8533))
		role = discord.utils.get(ctx.message.server.roles, name = 'Boogaloo Bot')
		await bot.add_roles(ctx.message.server.me, role)
	except:
		pass

@bot.command(pass_context = True, description = 'Provides a random number between the first and second argument, inclusive. (Ex. !rand 1 10 will give you a number between 1 and 10)')
#!rand imlpementation
async def rand(ctx, num1 = None, num2 = None):
	msg_list = ctx.message.content.split()
	if num2 == None or num1 == None:
		msg = '!rand takes 2 arguments. Usage: \n !rand num1 num2'
	else:
		try:
			num1 = int(num1)
			num2 = int(num2)
			rand_int = np.random.randint(num1, num2+1, 1)
			msg = 'Random number is: ' + str(rand_int[0]) + '\n'
		except:
			msg = 'That\'s not a number, ya dumby'
	await bot.send_message(ctx.message.channel, msg)

		
@bot.command(pass_context = True, description = 'Provides you a random image of the eternal meme. If you provide a number after !loss, you can get the image with that number. Also gives you an extra 3 points. Limited to 10 per day to avoid spam.\n**Examples of usage**\n!loss\n!loss 27')
#!loss implementation
async def loss(ctx, loss_number = None):
	if get_loss(ctx.message.author, ctx.message.server) > 10:
		await bot.send_message(ctx.message.channel, 'You have already gotten 10 losses today. Wait until tomorrow for more!.')
		return
		
	await bot.send_typing(ctx.message.channel)
	add_loss(ctx.message.author, ctx.message.server)
	add_points(ctx.message.author, 3, ctx.message.server) #Give the person 3 points for a loss
	msg_list = ctx.message.content.split()
	if loss_number == None:
		rand_int = np.random.randint(losses)
	else:
		try:
			rand_int = int(loss_number)
		except:
			await bot.send_message(ctx.message.channel, 'Error. Please use a number with !loss. To see usage, use ***!help loss***')
			return
	try:
		if rand_int % 10 == rand_int:
			filename_str = '00' + str(rand_int)
		elif rand_int % 100 == rand_int:
			filename_str = '0' + str(rand_int)
		else:
			filename_str = str(rand_int)
		await bot.send_file(ctx.message.channel, os.path.join(sys.path[0], 'loss/' + filename_str + '.png'), content = 'Look at this great meme! \nThis is loss number _' + str(rand_int) + '_')
	except:
		await bot.send_message(ctx.message.channel, 'Error, Did you provide a number or was the number too big?\nUse ***!help loss*** for usage or ***!info*** for loss count')
	
@bot.command(pass_context = True, description = 'Flips a coin and tells you if it is heads or tails.')
#!coin implementation
async def coin(ctx):
	rand_int = np.random.randint(2)
	if rand_int == 0:
		msg = 'Heads! \n'
	else:
		msg = 'Tails! \n'
	await bot.send_message(ctx.message.channel, msg)

#!bed implementation
@bot.command(pass_context = True, description = 'Provides you with one of many beds for your sleeping pleasure. You are only allowed one bed per day and you may only ask for a bed when it is bedtime (5:30PM-5AM PST). Each bed also comes with 5 points. If you are unhappy with the bed you have been given, you can buy a new one with the !buy command.')
async def bed(ctx):
	await bot.send_typing(ctx.message.channel)
	current_time_og = time.localtime() #year, month, day, hour, minute, second, weekday, year day, is daylight savings time?
	
	#Fix a bug with overwriting the current time correctly.
	current_time = []
	current_time.append(current_time_og[0])
	current_time.append(current_time_og[1])
	try:
		if current_time_og[3] <= 5: #If it is before 5AM, count it towards today's bed
			current_time.append(current_time_og[2] - 1)
		else:
			current_time.append(current_time_og[2])
		current_time.append(current_time_og[3]) #Have to add this and the next line to fix the overwrite problem.
		current_time.append(current_time_og[4])
	except:
		print ('Error trying to convert time in !bed function.\n')

	date_string = os.path.join(sys.path[0], 'save/beds/bed.') + str(current_time[0]) + '.' + str(current_time[1]) + '.' + str(current_time[2]) + '.txt'
	try: #See if someone has already asked for a bed and the file exists
		file = open(date_string, 'r')
		file_contents = file.readlines()
		file.close()
	except: #If not, create the file and delete all old beds.
		clear_beds()
		file = open(date_string, 'w')
		file.write('File created at ' + str(current_time[3]) + ':' + str(current_time[4]) + '\n')
		file.close()
		file_contents = ['File created at ' + str(current_time[3]) + ':' + str(current_time[4]) + '\n']
	
	has_bed = False
	for x in file_contents: #Check if the person has already posted a bed today, if so 
		if x == (str(ctx.message.author.id) + '\n'):
			has_bed = True
			
	if has_bed: #If the person has already gotten a bed, discipline them!
		await bot.send_message(ctx.message.channel, ctx.message.author.mention + ' Don\'t be greedy! You\'ve already gotten a bed today. Please wait until tomorrow.\nYou can get a new bed in: **' + str(25 - current_time[3]) + '** _hours_ and **' + str(60 - current_time[4]) + '** _minutes_.')
	
	elif not has_bed:
		rand_int = np.random.randint(beds)
		#Fix the filename
		if rand_int % 10 == rand_int:
			filename_str = '00' + str(rand_int)
		elif rand_int % 100 == rand_int:
			filename_str = '0' + str(rand_int)
		else:
			filename_str = str(rand_int)
		
		if current_time[3] >= 18 or current_time[3] < 5 or (current_time[3] == 4 and current_time[4] >=30) or str(ctx.message.author.id) == '157262048508510208':
			add_points(ctx.message.author, 5, ctx.message.server) #Give 5 points for today's bed
			await bot.send_file(ctx.message.channel, os.path.join(sys.path[0], 'bed/') + filename_str + '.png', content = 'Good night, sleep tight! \n')
			try:
				file_contents.append(str(ctx.message.author.id) + '\n')
				file = open(date_string, 'w')
				for x in file_contents:
					file.write(x)
				file.close()
			except:
				print ('Error writing to today\'s bed file.\n')
		else:
			await bot.send_message(ctx.message.channel, 'Now is no time to be sleeping. Please try again later if you would like a bed.')
	
		
@bot.command(pass_context=True, description = 'Picks a random Overwatch hero. If you specify a class, the character you get will only be from that class.\n**Example of usage:**\n!owhero\n!owhero dps\n!owhero tank\n!owhero support')
#!owhero implementation
async def owhero(ctx, role = None):
	await bot.send_typing(ctx.message.channel)
	#Error checking
	lower_bound = 0
	upper_bound = 27 #Number of Overwatch Heroes
	msg_flag = False
	
	if not role == None:
		if role == 'dps':
			lower_bound = 0
			upper_bound = 15
		elif role == 'tank':
			lower_bound = 15
			upper_bound = 22
		elif role == 'support':
			lower_bound = 22
			upper_bound = 28
		else:
			await bot.send_message(ctx.message.channel, 'Error with usage. Use !help owhero to see how to use this command correctly.')
			return
	#Generate the hero
	msg = 'You should play '
	rand_int = np.random.randint(lower_bound, upper_bound, 1)
	hero_array = ['Doomfist', 'Genji', 'McCree', 'Pharah', 'Reaper', 'Soldier', 'Sombra', 'Tracer', 'Bastion', 'Hanzo', 'Junkrat', 'Mei', 'Symmetra', 'Torbjorn', 'Widowmaker', 'Dva', 'Orisa', 'Reinhardt', 'Roadhog', 'Winston', 'Wrecking Ball', 'Zarya', 'Ana', 'Brigitte', 'Lucio', 'Mercy', 'Moira', 'Zenyatta']
	msg += hero_array[rand_int[0]]
	msg += ' this match. Have fun. \n'
	
	await bot.send_message(ctx.message.channel, msg)
	await bot.send_file(ctx.message.channel, os.path.join(sys.path[0], 'OW/') + hero_array[rand_int[0]] + '.png')
		
#!lore implementation.
@bot.command(pass_context = True, description = 'Provides lore from a randomly selected video game. You will receive points based on what kind of lore you get. If you get bad lore, you will lose points. Currently supports Kirby, Mario, Pikmin, Ace Attorney, Sword Art Online, Jojo, Attack on Titan, and Undertale')
async def lore(ctx):
	rand_number = np.random.random_sample()
	lore_link = ''
	stock_chance = np.random.randint(2)
	
	if rand_number <= 0.25: #If under 20%, do the kirby wiki
		game_title = 'kirby.txt'
		lore_link = 'http://kirby.wikia.com/wiki/'
		add_points(ctx.message.author, 4, ctx.message.server) #Give four points for good lore
		if stock_chance == 1:
			stock_rates(ctx.message.server, 0.02)
	elif rand_number <= 0.42: #If under 42%, do the Mario wiki
		game_title = 'mario.txt'
		lore_link = 'https://www.mariowiki.com/'
		add_points(ctx.message.author, 3, ctx.message.server) #Give three points for lore
	elif rand_number <= 0.51: #Jojo wiki
		game_title = 'jojo.txt'
		lore_link = 'http://jojo.wikia.com/wiki/'
		add_points(ctx.message.author, 6, ctx.message.server) #Take three points for lore
		if stock_chance == 1:
			stock_rates(ctx.message.server, 0.03)
	elif rand_number <= 0.61: #Pimin wiki
		game_title = 'pikmin.txt'
		lore_link = 'https://www.pikminwiki.com/'
		add_points(ctx.message.author, 2, ctx.message.server) #Give two points for lore
	elif rand_number <= 0.7: #Sword Art Online wiki wiki
		game_title = 'sao.txt'
		lore_link = 'http://swordartonline.wikia.com/wiki/'
		add_points(ctx.message.author, -8, ctx.message.server) #Bad lore, lose some points
		if stock_chance == 1:
			stock_rates(ctx.message.server, -0.03)
	elif rand_number <= 0.85: #Ace Attorney wiki
		game_title = 'ace_attorney.txt'
		lore_link = 'http://aceattorney.wikia.com/wiki/'
		if stock_chance == 1:
			stock_rates(ctx.message.server, 0.03)
		add_points(ctx.message.author, 4, ctx.message.server) #Give points for lore
	elif rand_number <= 0.97: #Undertale wiki
		game_title = 'undertale.txt'
		lore_link = 'http://undertale.wikia.com/wiki/'
		add_points(ctx.message.author, -12, ctx.message.server) #Lose points for bad lore
		if stock_chance == 1:
			stock_rates(ctx.message.server, -0.02)
	elif rand_number <= 1.0: #Attack on Titan wiki
		game_title = 'snk.txt'
		lore_link = 'http://attackontitan.wikia.com/wiki/'
		add_points(ctx.message.author, -5, ctx.message.server) #Lose points for bad lore
	
	#Try to open the file, if there is an error, let the user know
	try:
		file = open(os.path.join(sys.path[0], 'lore/' + game_title) , 'r')
		file_contents = file.readlines()
		rand_int = np.random.randint(len(file_contents))
	except:
		print('Error with !lore')
		await bot.send_message(ctx.message.channel, 'I had an issue with the lore. Please try again.')
	
	#Give the user their lore
	try:
		await bot.send_message(ctx.message.channel, 'Here is the lore I have provided for you: ' + lore_link + file_contents[rand_int])
	except:
		await bot.send_message(ctx.message.channel, 'Error acquiring lore!\n')
		print(lore_link)
	file.close()

#!pin implementation
@bot.command(pass_context = True, description = 'Lets you interact with the pin list. Using this command with no arguments will give you a random item from the pin list. If you use +, then you will add an item to the pin list. Using - will take away the item from the pin list if it exists. Using the command with % will send a copy of the current pin list. It is also possible to get a specific pin item if you know its number. You get 3 points for adding something to the list.\n**Examples of usage:**\n!pin\n!pin + <text\link>\n!pin - <text\link>\n!pin %\n!pin <number>')
async def pin(ctx, option = None, link = None):
	await bot.send_typing(ctx.message.channel)
	Errormsg = 'Error, !pin can be used like: \n!pin (Gives random item from pin list)\n!pin + <text/link> (Adds text/link to pin list)\n!pin - <text/link> (Removes text/link from pin list if it exists already)\n!pin % (Sends a copy of the current pin list)\n'
	global FILE_CAP
	
	#Make sure file exists
	try:
		file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_pinlist.txt'), 'r')
		file.close()
	except:
		file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_pinlist.txt'), 'w')
		file.close()
	
	try:
		if option == None and link == None: #If pin is called with no arguments
			file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_pinlist.txt'), 'r')
			file_info = file.readlines()
			if len(file_info) == 0: #Make sure the pin list is populated
				msg = 'There is nothing in the pin list! You can add something to it with:\n!pin + <text/link>\n'
			elif len(file_info) > FILE_CAP:
				msg = 'The pinlist has reached it\'s capacity of _' + str(FILE_CAP) + '_ items. Please delete some items with ***!pin - <link>***\n'
			else:
				rand_int = np.random.randint(len(file_info))
				try:
					rand_int = int(option)
				except:
					pass
				msg = file_info[rand_int] + '\nThis is pin item number ' + str(rand_int)
			await bot.send_message(ctx.message.channel, msg)
			file.close()
			return
	except:
		pass
	
	if option == '%' and link == None: #If pin is called asking for a copy of the list
		await bot.send_file(ctx.message.channel, os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_pinlist.txt'))
		msg = 'Here is the current pin list\n'
		
	
	elif not link == None:
		file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_pinlist.txt'), 'r')	
		file_info = file.readlines()
		
		if option == '+': #Pin list add implementation
			try:
				add_points(ctx.message.author, 3, ctx.message.server) #Give 3 points for a pin item
				add_msg = link + '\n'
				msg = 'Successfully added to pin list!'
				add = True #Boolean to determine whether or not the text should be added
				index = 0 #Place of pin item in the list for letting the person know
				for x in file_info:
					if add_msg == x:
						msg = 'The argument provided is already in the pin list. It is item number ' + str(index) +'. You can use !pin <number> to get a specific item from the pinlist.\n'
						add = False
						break
					index += 1
				if add:
					file.close()
					file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_pinlist.txt'), 'w')
					for x in file_info:
						file.write(x)
					file.write(add_msg)
			except:
				msg = 'Error, please provide a link alongside your +, like this:.\n!pin + <link>'
				
		elif option == '-': #Pin list remove implementation
			del_index = 0
			sub = False
			sub_msg = link + '\n'
			count = 0
			for x in file_info:
				if x == sub_msg:
					del_index = count
					sub = True
					break
				count += 1
				
			if sub: #If remove should be performed. #DEBUG, try to make it more streamlined if possible.
				file.close()
				file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_pinlist.txt'), 'w')
				count = 0
				for x in file_info:
					if not count == del_index:
						file.write(x)
					count += 1
				msg = 'The link has been successfully removed from the pin list! \n'
				
			else:
				msg = 'Argument provided was not found in pin list, and so it cannot be removed\n'
			
		else: #If the correct argument was not specified
			msg = Errormsg
			
		file.close()
	#Make sure add statement checks to make sure the item is not already in the pin list
	else: #If an error has occurred, give a helpful message
		msg = Errormsg
	await bot.send_message(ctx.message.channel, msg)

#!add implementation. Adds a song to the music queue
@bot.command(pass_context = True, description = 'Adds a song or multiple songs to the music queue. Works for the next time the bot plays music, as well. If adding multiple songs, please give a number between 1 and 20, inclusive.\n**Examples of usage:**\n!add <number> (Adds the number of songs randomly to the music queue)\n!add <link>')
async def add(ctx, URL = None):
	try:
		file = open(os.path.join(sys.path[0], 'music/') + str(ctx.message.server.id) + '.txt', 'r')
	except:
		file = open(os.path.join(sys.path[0], 'music/') + str(ctx.message.server.id) + '.txt', 'w')
		file.close()
		file = open(os.path.join(sys.path[0], 'music/') + str(ctx.message.server.id) + '.txt', 'r')
		
	music_queue = file.read().splitlines()
	file.close()
	
	if len(music_queue) > 75: #Set cap of 75 on the music queue
		await bot.send_message(ctx.message.channel, 'Music queue has reached max of 75 entries. Please wait a while before adding more entires.')
		return
	
	if URL == None: #If no argument was provided
		await bot.send_message(ctx.message.channel, 'Please give an argument with add. Either give the number of songs that you would like, or the link to the song you would like added.')
		return
		
	else:	
		try: #Check if the argument is a number, if an exception occurs, it is a link
			if int(URL) <= 0 or int(URL) > 20:
				await bot.send_message(ctx.message.channel, 'Please provide a number between 1 and 20 inclusive.')
				return
				
			file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_musiclist.txt'), 'r')
			file_info = file.read().splitlines()
			if len(file_info) == 0: #Make sure the pin list is populated
				await bot.send_message(ctx.message.channel, 'There is nothing in the music list! You can add something to it with:\n!pinmusic + <link>\n')
				return
		
			file.close()	
				
			for x in range(int(URL)):
				rand_int = np.random.randint(len(file_info))
				new_URL = file_info[rand_int]
				music_queue.append(new_URL)
			
			file = open(os.path.join(sys.path[0], 'music/') + str(ctx.message.server.id) + '.txt', 'w')
			for y in music_queue:
				file.write(y + '\n')
			file.close()
			await bot.send_message(ctx.message.channel, 'I have added _' + str(URL) + '_ songs to the music queue')
			return
			
		except:
			pass
	
	try: #In the event that the argument passed is a link
		if '&list=' in URL or '&t=' in URL:
			try:
				add_msg = URL[0:43] + '\n' #Get rid of &list part of YouTube links.
			except:
				print('Error with trying to convert improper YouTube link')
	
		if not URL in music_queue:
			music_queue.append(URL)
			
			file = open(os.path.join(sys.path[0], 'music/') + str(ctx.message.server.id) + '.txt', 'w')
			for y in music_queue:
				file.write(y + '\n')
			file.close()
			
			await bot.send_message(ctx.message.channel, 'Song added to music queue!')
			return
		await bot.send_message(ctx.message.channel, 'Song is already in the queue.')
		
	except:
		await bot.send_message(ctx.message.channel, 'Error, was the link you provided formatted correctly?')
	
	
#!priority implementation. Adds a song to the music queue
@bot.command(pass_context = True, description = 'Adds a song to the front of the music queue. Works for the next time the bot plays music, as well (makes the song second). Costs 7 points to use.')
async def priority(ctx, URL = None):
	stock_rates(ctx.message.server, 0.01)
	
	try:
		file = open(os.path.join(sys.path[0], 'music/') + str(ctx.message.server.id) + '.txt', 'r')
	except:
		file = open(os.path.join(sys.path[0], 'music/') + str(ctx.message.server.id) + '.txt', 'w')
		file.close()
		file = open(os.path.join(sys.path[0], 'music/') + str(ctx.message.server.id) + '.txt', 'r')
		
	music_queue = file.read().splitlines()
	file.close()

	if URL == None: #If no argument was provided
		await bot.send_message(ctx.message.channel, 'Please provide a link that you would like me to add to the queue.')
		return
	if get_points(ctx.message.author, ctx.message.server) < 7:
		await bot.send_message(ctx.message.channel, 'Priority costs 7 points. You don\'t have enough.')
		return
	if not URL in music_queue:
		music_queue.insert(1, URL)
		
		file = open(os.path.join(sys.path[0], 'music/') + str(ctx.message.server.id) + '.txt', 'w')
		for y in music_queue:
			file.write(y + '\n')
		file.close()
		
		add_points(ctx.message.author, -7, ctx.message.server) #Take 7 points for the priority.
		await bot.send_message(ctx.message.channel, 'Song added to music queue with _priority_!')
		return
	await bot.send_message(ctx.message.channel, 'Song is already in the queue.')
	
#!killmusic implementation. Removes all songs from the music queue
@bot.command(pass_context = True, description = 'Clears the entire music queue and forces the bot out of the call.')
async def killmusic(ctx):
	await bot.send_message(ctx.message.channel, 'Are you sure you would like to kill the music? This will clear the whole music queue and remove the bot from all servers.\n**Type \'yes\' in the next 15 seconds to confirm.**')
	response = await bot.wait_for_message(timeout = 15, content = 'yes')
	if response == None:
		return
		
	try:
		for x in bot.voice_clients:
			await disconnect_from(x)
	except:
		print('Error in trying to kick the bot from a voice channel.')
	
	file = open(os.path.join(sys.path[0], 'music/') + str(ctx.message.server.id) + '.txt', 'w')
	file.close()
	
#!remove implementation. Removes a song to the music queue
@bot.command(pass_context = True, description = 'Adds a song to the music queue. Works for the next time the bot plays music, as well. If no argument is given, adds a random song to the music queue.')
async def remove(ctx, URL = None):
	try:
		file = open(os.path.join(sys.path[0], 'music/') + str(ctx.message.server.id) + '.txt', 'r')
		music_queue = file.read().splitlines()
		file.close()
	except:
		await bot.send_message(ctx.message.channel, 'No music queue exists to remove from.')
		return
		
	if URL == None: #If no argument was provided
		await bot.send_message(ctx.message.channel, 'Please specify a song to remove. Use like !remove <link>')
		return
	try:
		music_queue.remove(URL)
		
		file = open(os.path.join(sys.path[0], 'music/') + str(ctx.message.server.id) + '.txt', 'w')
		for y in music_queue:
			file.write(y + '\n')
		file.close()
		
		await bot.send_message(ctx.message.channel, 'Link was removed from queue.')
	except:
		await bot.send_message(ctx.message.channel, 'Link not found within music queue')

#!queue implementation. Displays music queue
@bot.command(pass_context = True, description = 'Shows the current music queue. Will take roughly 30-45 seconds to complete this request.')
async def queue(ctx):
	await bot.send_message(ctx.message.channel, 'Okay! I will grab the current queue! _Give me a moment to download the information..._')
	
	await bot.send_typing(ctx.message.channel)
	
	msg = '__This is the current music queue:__\n'
	number = 1
	
	try:
		file = open(os.path.join(sys.path[0], 'music/') + str(ctx.message.server.id) + '.txt', 'r')
		music_queue = file.read().splitlines()
		file.close()
	except:
		await bot.start_private_message(ctx.message.author)
		await bot.send_message(ctx.message.author, 'No music queue exists in this server. Use **!music** or **!add** in the server you would like to start music in while in a voice channel.')
		return
	
	for x in music_queue:
		try:
			if number <= 20:
				await asyncio.sleep(1) #don't poll for too many links
				youtube = etree.HTML(urllib.request.urlopen(x).read())
				video_title = youtube.xpath("//span[@id='eow-title']/@title")
				if video_title[0] == None or video_title[0] == '': #Fix error in getting Soundcloud titles
					video_title = 'Unknown Soundcloud link'
				msg += '*' + str(number) + '*. _' + str(video_title[0]) + '_\n'
				number += 1
		except:
			pass
	try:
		await bot.start_private_message(ctx.message.author)
		await bot.send_message(ctx.message.author, msg)
	except:
		await bot.start_private_message(ctx.message.author)
		await bot.send_message(ctx.message.author, 'The music queue is a little too big to send currently. Sorry.')

#!music implementation
@bot.command(pass_context = True, description = 'Plays music in the current voice channel. If you give it no argument, it will randomly select a song from the pin music list. If you would like a song played, please give the bot a link. Please give the bot a few seconds to play YouTube links, as it needs to download the song first. Use \'add\' if a song is playing to add another one to the queue. You can kick the bot with !kickme. The built-in audio player can sometimes be buggy, so keep that in mind.\n**Example of usage:**\n!music\n!music <link>')
async def music(ctx, URL = None):
	await bot.send_typing(ctx.message.channel)
	try:
		if URL == None: #If no argument was provided
			try:
				file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_musiclist.txt'), 'r')
			except: #If there is an error in finding the music list file
				await bot.send_message(ctx.message.channel, 'It doesn\'t seem as though you have a musiclist in this server. Get started by using the **!pinmusic** command.')
				return
			file_info = file.read().splitlines()
			if len(file_info) == 0: #Make sure the pin list is populated
				await bot.send_message(ctx.message.channel,'There is nothing in the music list! You can add something to it with:\n!pinmusic + <link>\n')
				return
			else:
				rand_int = np.random.randint(len(file_info))
				URL = file_info[rand_int]
					
			file.close()
 
		#Before playing music, try to fix the link, prevent playlists
		if '&list=' in URL or '&t=' in URL:
			try:
				URL = URL[0:43] + '\n' #Get rid of &list part of YouTube links.
			except:
				print('Error with trying to convert improper YouTube link')	
			
		await play_music(ctx.message, URL)
		
	except TimeoutError:
		await bot.send_message(ctx.message.channel, 'The music player has timed out')
		print('The bot encountered a TimeoutError while playing music.')
		return
	
	except:
		try:
			for x in bot.voice_clients:
				if x.server == ctx.message.server: #Leave only the voice channel called from
					try:
						await disconnect_from(x)
					except:
						print('Error in trying to kick the bot from a voice channel.')
		except:
			pass
		print ('Error in music command. Bot hopefully kicked from server.')

#!volume implementation. Sets volume for music
@bot.command(pass_context = True, description = 'Sets the volume for the music player. Be patient, it may take until the next song to set the volume.')
async def volume(ctx, level = None):		
	global VOLUME
	if level == None:
		await bot.send_message(ctx.message.channel, 'Error, please use !volume like:\n!volume <number> (Between 0 and 2)')
		return
		
	else:
		try:
			if float(level) >= 0 and float(level) <= 2:
				VOLUME = float(level)
			else:
				await bot.send_message(ctx.message.channel, 'Error, please provide a volume between 0 and 2 inclusive.')
		except:
			await bot.send_message(ctx.message.channel, 'Was that a number that you provided me? Could not set volume to ' + level)
	
#!pinmusic implementation
@bot.command(pass_context = True, description = 'Lets you interact with the music pin list. Same as !pin, but specifically for music. Using this command with no arguments will give you a random item from the music list. If you use +, then you will add an item to the music list. Using - will take away the item from the music list if it exists. Using the command with % will send a copy of the current pin list. Gives you 3 points for adding.\n**Examples of usage:**\n!pinmusic\n!pinmusic + <text\link>\n!pinmusic - <text\link>\n!pinmusic %')
async def pinmusic(ctx, option = None, link = None):
	await bot.send_typing(ctx.message.channel)
	Errormsg = 'Error, !pinmusic can be used like: \n!pinmusic (Gives random item from music list)\n!pinmusic + <link> (Adds link to music list)\n!pinmusic - <link> (Removes link from music list if it exists already)\n!pinmusic % (Sends a copy of the current music list)\n'
	
	#Make sure file exists
	try:
		file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_musiclist.txt'), 'r')
		file.close()
	except:
		file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_musiclist.txt'), 'w')
		file.close()
	
	if option == None and link == None: #If pin is called with no arguments
		file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_musiclist.txt'), 'r')
		file_info = file.readlines()
		if len(file_info) == 0: #Make sure the pin list is populated
			msg = 'There is nothing in the music list! You can add something to it with:\n!pinmusic + <link>\n'
		elif len(file_info) > FILE_CAP:
			await bot.send_message(ctx.message.channel, 'The musiclist has reached it\'s capacity of _' + str(FILE_CAP) + '_ items. Please delete some items with ***!pinmusic - <link>***\n')
			return
		else:
			rand_int = np.random.randint(len(file_info))
			msg = file_info[rand_int]
		file.close()
		
	#If command is called with arguments
	elif option == '%':
		try:
			await bot.send_file(ctx.message.channel, os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_musiclist.txt'))
			msg = 'Here is the current music list\n'
		except:
			msg = Errormsg
		return
		
	elif option == '+': #Pin list add implementation
		file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_musiclist.txt'), 'r')	
		file_info = file.readlines()
		add_msg = link + '\n'
		msg = 'Successfully added to music list!'
		add = True #Boolean to determine whether or not the text should be added
		if '&list=' in link or '&t=' in link:
			await bot.send_message(ctx.message.channel, 'The link provided may not work correctly. Please add without any "&t=" or "&list"')
		
		for x in file_info:
			if x == add_msg:
				msg = 'The argument provided is already in the music list. \n'
				add = False
		if add:
			add_points(ctx.message.author, 3, ctx.message.server) #Give 3 points for a pin item
			file.close()
			file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_musiclist.txt'), 'w')
			for x in file_info:
				file.write(x)
			file.write(add_msg)
			
	elif option == '-': #Pin list remove implementation
		file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_musiclist.txt'), 'r')	
		file_info = file.readlines()
		
		del_index = 0
		sub = False
		sub_msg = link + '\n'
		count = 0
		for x in file_info:
			if x == sub_msg:
				del_index = count
				sub = True
			count += 1
			
		if sub: #If remove should be performed
			file.close()
			file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_musiclist.txt'), 'w')
			count = 0
			for x in file_info:
				if count != del_index:
					file.write(x)
				count += 1
			msg = 'The link has been successfully removed from the music list! \n'
			
		else:
			msg = 'Argument provided was not found in music list, and so it cannot be removed\n'
		
	else: #If the correct argument was not specified
		msg = Errormsg
		
	file.close()
	await bot.send_message(ctx.message.channel, msg)

#!reset implementation. Resets all points, the stocks, and the banks, as well as reverts roles
@bot.command(pass_context = True, description = '')
async def reset(ctx):
	
	for x in range(10): #Get the person's highest role, first
		role_check = discord.utils.get(ctx.message.author.roles, name = prestiges[x])#Get the server's roles
		if not role_check == None:
			role_name = prestiges[x]
	
	role_index = 0
	
	try:
		role_index = prestiges.index(role_name)
	except:
		pass
	
	if role_index < 9:
		await bot.send_message(ctx.message.channel, 'You are not able to reset the points for this server! You need to be at the highest prestige! Use **!prestige** to rank up.')
		return
	else:
		await bot.send_message(ctx.message.channel, '_Are you sure you would like to reset this server for real?_\n\n**This will reset the points, stocks, bank, chance time, and prestige roles for this server.**\n***There is no going back!***\nYou will receive a bonus of 150 points after the reset. All users will get a small bonus based on their prestige. \n\nRespond with **yes** in the next 15 seconds if you are totally sure.')
		response = await bot.wait_for_message(timeout = 15, author = ctx.message.author, channel = ctx.message.channel, content = 'yes')
		if response == None:
			await bot.send_message(ctx.message.channel, '15 seconds have passed. I will not reset the points!')
			return
	
	await bot.send_message(ctx.message.channel, '_Resetting everything..._\n\n**Please do not send me commands while I do this, as it may not work correctly**')
	await bot.send_typing(ctx.message.channel)
		
	os.remove(os.path.join(sys.path[0], 'save/points/points_') + str(ctx.message.server.id) + '.txt') #Remove the points file for this server
	
	try:
		os.remove(os.path.join(sys.path[0], 'save/stocks/stocks_') + str(ctx.message.server.id) + '.txt') #Remove the stocks for this server
	except:
		pass
	
	try:
		os.remove(os.path.join(sys.path[0], 'save/bank/bank_') + str(ctx.message.server.id) + '.txt') #Remove the bank file for this server
	except:
		pass
		
	#Reset all roles
	for y in ctx.message.server.members:
		role_name = None
		for x in range(10):
			role_check = discord.utils.get(y.roles, name = prestiges[x])#Get the server's roles
			if not role_check == None:
				role_name = prestiges[x]
		
		role_index = 0
		
		try:
			role_index = prestiges.index(role_name)
		except:
			pass

		#Give points for prestige before removing		
		if role_index >= 2:
			if role_index < 3:
				add_points(y, 10, ctx.message.server)
			elif role_index < 5:
				add_points(y, 25, ctx.message.server)
			elif role_index < 7:
				add_points(y, 50, ctx.message.server)
			elif role_index <= 9:
				add_points(y, 100, ctx.message.server)
		
		for z in range(5): #Odd bug where it only deletes every other role? To fix, just do it 5 times.		
			try:
				for x in range(role_index + 1):
					try:
						role_to_remove = discord.utils.get(y.roles, name = prestiges[x])
						if not role_to_remove == None:
							await bot.remove_roles(y, role_to_remove) #Attempt to remove previous role if they even have it
					except:
						pass
			except:
				pass
			
	#Save as winner and the date
	file = open(os.path.join(sys.path[0], 'save/stats_') + str(ctx.message.server.id) + '.txt', 'r')
	file_info = file.read().splitlines()
	file.close()
	
	file_contents = []
	for x in file_info:
		file_contents.append(x.split())
	
	del file_info
	
	current_time = time.localtime() #year, month, day, hour, minute, second, weekday, year day, is daylight savings time?
	for x in file_contents:
		if x[0] == 'winner':
			x[1] = str(ctx.message.author.id)
		elif x[0] == 'year':
			x[1] = str(current_time[0])
		elif x[0] == 'month':
			x[1] = str(current_time[1])
		elif x[0] == 'day':
			x[1] = str(current_time[2])
	
	#Write winner to save file
	file = open(os.path.join(sys.path[0], 'save/stats_') + str(ctx.message.server.id) + '.txt', 'w')
	for x in file_contents:
		file.write(x[0] + ' ' + x[1] + '\n')
		
	#Finally, give the previous winner 150 points
	add_points(ctx.message.author, 150, ctx.message.server)
	
	await bot.send_message(ctx.message.channel, 'Server points successfully reset! _Enjoy this new world_')
	
#!prestige implementation. Sets roles based on points
@bot.command(pass_context = True, description = 'Use your points to prestige! With prestiges, you can earn fancy titles to let everyone in the server know how cool you are. Each prestige requires more points to earn. At certain prestiges, you will gain access to new commands. At the highest prestige, you will be given the option to reset the entire server\'s points along with a bonus. Use !reset to do this once you have hit max prestige. There are 10 total prestiges to earn. The Discord API for roles is limited and a bit buggy, so another command called !fixmyroles is also available alongside this one.')
async def prestige(ctx):
	#Try to create all roles if necessary
	color_index = 0
	for x in prestiges:
		if discord.utils.get(ctx.message.server.roles, name = x) == None:
			await bot.create_role(ctx.message.server, name = x, colour = discord.Colour(prestige_color[color_index]))
		color_index += 1
	del color_index

	for x in range(10):
		role_check = discord.utils.get(ctx.message.author.roles, name = prestiges[x])#Get the server's roles
		if not role_check == None:
			role_name = prestiges[x]
			
	try:
		role_index = prestiges.index(role_name)
	except:
		role_index = -1 #If no role was found, it is likely they don't have a role yet.
	
	if role_index >= 9:
		await bot.send_message(ctx.message.channel, 'You have already acheived the highest prestige possible! Congrats! You can reset the points for the entire server with **!reset** with a bonus.')
		return
		
	else:
		await bot.send_message(ctx.message.channel, 'You can prestige to **' + prestiges[role_index + 1] + '** for _' + str(prestige_costs[role_index + 1]) + '_ points.\nType **yes** to confirm or wait 10 seconds to time out.')
		response = await bot.wait_for_message(timeout = 10, author = ctx.message.author, channel = ctx.message.channel, content = 'yes')
		if response == None:
			await bot.send_message(ctx.message.channel, 'Okay, I will not prestige you right now.')
			return
		elif response.content == 'yes':
			if get_points(ctx.message.author, ctx.message.server) < prestige_costs[role_index + 1]:
				await bot.send_message(ctx.message.channel, '_You don\'t have enough points for that prestige right now._ Try again when you have more points.')
				return
			else:
				try: #Attempt to create the role if it even needs done
					if discord.utils.get(ctx.message.server.roles, name = prestiges[role_index + 1]) == None:
						await bot.create_role(ctx.message.server, name = prestiges[role_index + 1], colour = discord.Colour(prestige_color[role_index + 1]))
						
				except:
					pass
					
				new_role = discord.utils.get(ctx.message.server.roles, name = prestiges[role_index + 1])#Get the server's roles
				
				try:
					role_to_remove = discord.utils.get(ctx.message.author.roles, name = role_name)
					await bot.remove_roles(ctx.message.author, role_to_remove) #Attempt to remove previous role if they even have it
				except:
					print('Error with removing role.')
					pass
					
			await bot.add_roles(ctx.message.author, new_role)
			add_points(ctx.message.author, -1*prestige_costs[role_index + 1], ctx.message.server)
			await bot.send_message(ctx.message.channel, 'Congrats, you\'ve prestiged to _' + prestiges[role_index + 1] + '_!\nUse **!fixmyroles** to display your new prestige if it does not work correctly.')
				
#!fixmyroles implementation	
@bot.command(pass_context = True, description = 'Due to a bug in the Discord API that doesn\'t have a proper fix yet, this command is necessary. If you would like to have the highest prestige you have acheived displayed and lower prestiges removed, use this command.')
async def fixmyroles(ctx):
	global prestiges
	await bot.send_message(ctx.message.channel, '_Fixing roles..._\nPlease give me a moment...')
	for x in range(10):
		role_check = discord.utils.get(ctx.message.author.roles, name = prestiges[x])#Get the server's roles
		if not role_check == None:
			role_name = prestiges[x]
	
	try:
		role_index = prestiges.index(role_name)
	except:
		pass

	for x in range(5): #Odd bug where it only deletes every other role? To fix, just do it 5 times.		
		try:
			for x in range(role_index):
				try:
					role_to_remove = discord.utils.get(ctx.message.author.roles, name = prestiges[x])
					if not role_to_remove == None:
						await bot.remove_roles(ctx.message.author, role_to_remove) #Attempt to remove previous role if they even have it
						asyncio.sleep(1)
				except:
					pass
		except:
			pass
		
	await bot.send_message(ctx.message.channel, 'Roles fixed!')
	
#!goodmorning implementation. Wishes everyone in a good morning in a random ways
@bot.command(pass_context = True, description = "Wish everyone a good morning. May only be used once per day. It will \"at\" everyone.")
async def goodmorning(ctx):
	await bot.send_typing(ctx.message.channel)
	current_time = time.localtime() #year, month, day, hour, minute, second, weekday, year day, is daylight savings time?

	date_string = os.path.join(sys.path[0], 'save/goodmorning.') + str(current_time[0]) + '.' + str(current_time[1]) + '.' + str(current_time[2]) + '.txt'
	try: #See if someone has already asked for a good_morning and the file exists
		file = open(date_string, 'r')
		file_contents = file.readlines()
		file.close()
	except: #If not, create the file and delete all old beds.
		clear_good_mornings()
		file = open(date_string, 'w')
		file.write('File created at ' + str(current_time[3]) + ':' + str(current_time[4]) + '\n')
		file.close()
		file_contents = ['File created at ' + str(current_time[3]) + ':' + str(current_time[4]) + '\n']
	
	has_morning = False
	for x in file_contents: #Check if the person has already posted a good_morning today, if so 
		if x == (str(ctx.message.author.id) + '\n'):
			has_morning = True
			
	if has_morning: #If the person has already gotten a bed, discipline them!
		await bot.send_message(ctx.message.channel, ctx.message.author.mention + 'Everyone has already been wished a good morning today. Please wait until tomorrow.')
		return
		
	elif not has_morning: #Wish everyone a good morning
		greeting = ['Good morning', 'Rise and shine', 'Wake up', 'Awaken']
		verb = ['polish', 'grab', 'gain', 'obtain', 'acquire', 'work', 'make', 'earn', 'win', 'hone', 'collect', 'improve', 'bake', 'chop', 'clobber']
		modifier = ['that', 'our', 'the']
		noun = ['bread', 'cheese', 'pickle', 'dough', 'meat', 'cabbage', 'money', 'gold', 'egg', 'ham', 'hard-working spirit', 'pie']
		await bot.send_message(ctx.message.channel, '**' + greeting[np.random.randint(len(greeting))] + ' , gamers!** _Let\'s ' + verb[np.random.randint(len(verb))] + ' ' + modifier[np.random.randint(len(modifier))] + ' ' + noun[np.random.randint(len(noun))] + '!_')
		file_contents.append(str(ctx.message.author.id) + '\n')
		
	#Write to file
	file = open(date_string, 'w')
	for x in file_contents:
		file.write(x)
	file.close()
	
#!secret implementation. Tell the user some secret info
@bot.command(pass_context = True, description = 'Gives you secret information. Tells you what the secret word was, and then changes it.')
async def secret(ctx):
	global secret_word
	msg = 'Here\'s a few secrets:\nI\'ve generated a new secret word. The old secret word was: **' + secret_word + '**'
	secret_word = new_secret_word() #Generate a new secret word now that the old one was spoiled.
	#Maybe add stuff about points or stats?
	await bot.send_message(ctx.message.channel, msg)
	
#!points implementation. Tell the user about points
@bot.command(pass_context = True, description = 'Shows how many points everyone has on the current server. Displays a leaderboard and ways to earn or lose points. You can use !mypoints to see just your points.')
async def points(ctx):
	msg = 'Here is the current leaderboard for points:\n'
	file = open(os.path.join(sys.path[0], 'save/points/points_') + str(ctx.message.server.id) + '.txt', 'r')
	file_original = file.readlines()
	file_contents = []
	user_list = ctx.message.server.members
	
	#Format to remove the spaces
	for x in file_original:
		file_contents.append(x.split())
	
	del file_original
	file.close()
	
	#Sort in descending order
	sort_users(file_contents)
	
	place = 1
	for x in file_contents:
		if place > 20: #Only post the first 25 places to avoid too long of a message.
			break
		#Get the user's name before diplaying it
		for y in user_list:
			if str(y.id) == x[0]: #If a match is found
				name = '***' + str(y) +'***'
				break
		#Correctly format the placing for normal English
		msg += 'In ' + str(place)
		if place%10 == 1 and (place%100 < 10 or place%100 > 19):
			msg += '_st_ '
		elif place%10 == 2 and (place%100 < 10 or place%100 > 19):
			msg += '_nd_ '
		elif place%10 == 3 and (place%100 < 10 or place%100 > 19):
			msg += '_rd_ '
		else:
			msg += '_th_ '
		msg += 'place is : ' +  name + 'with ' + str(x[1]) +' points\n'
		place += 1
	
	#Display the winner if applicable, as well as the starting date
	file = open(os.path.join(sys.path[0], 'save/stats_') + str(ctx.message.server.id) + '.txt', 'r')
	file_info = file.read().splitlines()
	file.close()
	
	file_contents = []
	for x in file_info:
		file_contents.append(x.split())
	
	del file_info
	
	msg += '\nCurrent points were started on _' + file_contents[6][1] + '/' + file_contents[7][1] + '/' + file_contents[5][1] + '_\n'
	winner = 'Nobody'
	
	if file_contents[4][1] == '0':
		msg += 'This is the first points leaderboard.\n'
	else:
		for x in user_list:
			if str(x.id) == file_contents[4][1]: #If a match is found
				winner = str(x)
				break
		msg += 'The points were reset by the previous winner, **' + winner + '**'
	
	#Generic info for the footer. Information about points system is included here
	msg2 = '''\n __Here's how you can gain (or lose points)!:__ \n
	**Send a message**			+1 point
	**Ask for loss**			+2 points
	**Ask for lore**			+1-8 points (May lose points for bad lore)
	**Add to a pin list**		+3 points
	**Get a bed**				+5 points
	**Use the secret word**		+200 points
	**Get a secret message**	+75-250 points (Depends on the message)
	**Correctly answer 7x8**	+25 points
	**Get 7x8 wrong**			-25 points
	**Incorrect your/you're**	-2 point 
	**Use the slot**			(Based on bet)
	**Use chance time**			(Random effect)
	**Play rps**				+8 or -8 (Depends if you win or lose)
	**Save in the bank**
	**Invest in stocks**
	**Play the bomb game**
	**Play the ab game**
	
	Are you winning, son?
	Use !mypoints to see just your points'''
	
	#Send it to the server
	await bot.send_message(ctx.message.channel, msg)
	await bot.start_private_message(ctx.message.author)
	await bot.send_message(ctx.message.author, msg2)

#!mypoints implementation
@bot.command(pass_context = True, description = 'Sends a message telling you how many points you have. If you would like a more comprehensive overview of points, use !points.')
async def mypoints(ctx):
	#Open points file
	try:
		file = open(os.path.join(sys.path[0], 'save/points/points_') + str(ctx.message.server.id) + '.txt', 'r')
		file_info = file.readlines()
	except: #If points file does not exist for the current server, create one
		file = open(os.path.join(sys.path[0], 'save/points/points_') + str(ctx.message.server.id) + '.txt', 'w')
		file.write(str(ctx.message.author.id) + ' 0\n')
		file.close()
		file = open(os.path.join(sys.path[0], 'save/points/points_') + str(ctx.message.server.id) + '.txt', 'r')
		file_info = file.readlines()
	
	#Format the file and then do what you need to
	content = []
	
	for x in file_info:
		content.append(x.split())
	
	#Find how many points they have
	for x in content:
		if x[0] == str(ctx.message.author.id):
			await bot.send_message(ctx.message.channel, 'You have _' + x[1] + '_ points.\n')
			return
			
	#If they don't exist yet
	await bot.send_message(ctx.message.channel, 'You haven\'t gotten any points, yet.')
	
#!slot implementation. Rolls a random number and gives a prize accordingly
@bot.command(pass_context = True, description = 'Play a slot machine for a chance to win points. Requires a bet to use and you must have positive points. Gives anywhere from 1-5 times points, but can also take more points than you bet if you are unlucky. Only takes bets from 1 to 1000 points.\n**Example of usage:**\n!slot 20\n!slot 5')
async def slot(ctx, bet = None):
	
	if bet == None: #If usage is wrong, don't let them play.
		await bot.send_message(ctx.message.channel, 'Error starting slot. Did you use it correctly?\n Usage: **!slot** ***<bet>***\n (Bet is the number of points you want to bet. Max is 50.)\n')
		return	
		
	else: 
		try:
			bet = int(bet)
			if bet > 1000 or bet < 1:
				await bot.send_message(ctx.message.channel, 'Please provide a bet that is between 1 and 1000 points.\n')
				return
		except:
			await bot.send_message(ctx.message.channel, 'Did you try to bet something that wasn\'t a number? You can\'t put _' + str(bet) + '_ into a slot machine.')
			return

	try:
		if not check_points(ctx.message.author, ctx.message.server): #Check if the person has points to spend
			await bot.send_message(ctx.message.channel, 'You need to have positive points in order to play. Get some points first, buddy.\n')
			return
			
		await bot.send_message(ctx.message.channel, 'You paid _' + str(bet) + '_ points to play. Rolling slot...\n')
		await bot.send_typing(ctx.message.channel)
		rand_number = np.random.random_sample()
		rand_bonus = np.random.random_sample()
		if rand_number <= 0.11: #11% Chance of winning 2 times points
			add_points(ctx.message.author, math.floor((2 + rand_bonus)*bet), ctx.message.server) #Give 2*points
			msg = 'Lucky you; you\'ve just won _' + str(math.floor((2 + rand_bonus)*bet)) + '_ points. Go again?\n'
		elif rand_number <= 0.31: #20% Chance of winning 1.25 times points
			add_points(ctx.message.author, math.floor((1.05 + rand_bonus)*bet), ctx.message.server) #Give 1.05*points
			msg = 'Nice! You\'re the proud owner of _' + str(math.floor((1.05 + rand_bonus)*bet)) + '_ points. Go again?\n'
		elif rand_number <= 0.82: #51% Chance of winning nothing
			add_points(ctx.message.author, math.floor(-1*bet), ctx.message.server) #Take away the points required to play if they don't win anything
			msg = 'Too bad, you didn\'t win anything. Maybe next time?\n'
		elif rand_number <= 0.95: #13% Chance of losing 1.5 times points
			add_points(ctx.message.author, math.floor(-1.5*bet), ctx.message.server)
			msg = 'Wow, the slot just stole an extra _' + str(math.floor(0.5*bet))+ '_ points. Life is simply unfair.\n'
		elif rand_number <= 0.985: #3.5% Chance of winning 5*points
			add_points(ctx.message.author, math.floor(4*bet), ctx.message.server) #Give 5*points.
			msg = '**JACKPOT!** Take these _' + str(math.floor(5*bet)) + '_ points.\n'
		elif rand_number <= 1.0: #1.5% Chance of hitting loser's jackpot
			add_points(ctx.message.author, math.floor(-4*bet), ctx.message.server)
			msg = 'You just hit the ***LOSER\'S JACKPOT***! What are the odds?\n _1 in 100, actually_. Looks like you just lost _' + str(math.floor(5*bet))+ '_ points.\n'
		await bot.send_message(ctx.message.channel, msg)
	except:
		await bot.send_message(ctx.message.channel, 'Error playing slot. Your points will stay the same.\n')

#!chance implementation. Performs some wacky chance time shenanigans
@bot.command(pass_context = True, description = 'Activates chance time. Does a random effect to people on the current server. To see a breakdown of the effects and percentages, use !chance help. Chance time can only be used once per day per user, but you can buy another shot at chance with the !buy command.\n**Example of usage:**\n!chance\n!chance help')
async def chance(ctx):
	#Variables
	user_list = []
	for x in ctx.message.server.members: #List of all the users in the server
		user_list.append(x)
	current_time = time.localtime() #year, month, day, hour, minute, second, weekday, year day, is daylight savings time?
	date_string = str(current_time[0]) + '.' + str(current_time[1]) + '.' + str(current_time[2])
	info_msg = '''__Here is what might happen with chance time (Random points are between 1-25):__

You will be given a random number of points ***20%***
A random user will be given a random number of points ***18%***
You will lose a random number of points ***13***
A random user will lose a random number of points ***12%***
One random user will give another random user a random number of points ***14%***
Two random users will swap points ***14%***
The bank will receive a 5% interest bonus and stocks will change ***7%***
'''
	
	#Check whether they want chance time or help
	msg_list = ctx.message.content.split()
	if len(msg_list) > 2: #If the user did not use the command correctly
		await bot.send_message(ctx.message.channel, 'Error. Please use chance time like this:\n!chance\n***or***\n!chance help')
		return
		
	elif len(msg_list) == 2: #If the user might want help
		if msg_list[1] == 'help':
			await bot.send_message(ctx.message.channel, info_msg)
		else:
			await bot.send_message(ctx.message.channel, 'Error. Please use chance time like this:\n!chance\n***or***\n!chance help')
		return
	
	#Try to open the file
	try:
		file = open(os.path.join(sys.path[0], 'save/chance/') + str(ctx.message.server.id) + '_' + date_string + '.txt', 'r')
	except: #If chance file does not exist for the current day, create one
		clear_chance(ctx) #Clear chance function requires context in order to find the server id
		file = open(os.path.join(sys.path[0], 'save/chance/') + str(ctx.message.server.id) + '_' + date_string + '.txt', 'w')
		file.write('Created at ' + str(current_time[3]) + ':' + str(current_time[4]) + '\n')
		file.close()
		file = open(os.path.join(sys.path[0], 'save/chance/') + str(ctx.message.server.id) + '_' + date_string + '.txt', 'r')
	
	try:
		content = file.readlines()
		file.close()
	except:
		print('Error in handling chance file.')
	
	#Find out if the user is allowed to play chance time
	if (str(ctx.message.author.id) + '\n') in content: #If the user has been found to have already used chance time
		await bot.send_message(ctx.message.channel, 'You have already used chance time today.\nYou can use chance time again in _' + str(23 - current_time[3]) + '_ hours and _' + str(60 - current_time[4]) + '_ minutes.')
		return
	
	#Generate the random number for the effect and then do the effect
	await bot.send_message(ctx.message.channel, '_Starting chance time..._\n')
	await bot.send_typing(ctx.message.channel)
	rand_num = np.random.random_sample()
	exchange = np.random.randint(24) + 1 #Between 1 and 25.
	if rand_num <= 0.20: #Give points to the user that asked
		add_points(ctx.message.author, exchange, ctx.message.server)
		await bot.send_message(ctx.message.channel, 'Lucky! You got _' + str(exchange) + '_ points.\n')
	elif rand_num <= 0.35: #Take points from the user that asked
		add_points(ctx.message.author, -1*exchange, ctx.message.server)
		await bot.send_message(ctx.message.channel, 'Unlucky! You lost _' + str(exchange) + '_ points.\n')
	elif rand_num <= 0.42: #Give interest of 5% to the bank
		interest(0.05, ctx.message.server)
		stock_rates(ctx.message.server, 0.02) #Adjust stock rates
		await bot.send_message(ctx.message.channel, 'I\'ve applied a 5% interest to all amounts in the bank.\n')
	elif rand_num <= 0.6: #Give points to a random user
		user = user_list[np.random.randint(len(user_list))]
		add_points(user, exchange, ctx.message.server)
		await bot.send_message(ctx.message.channel, 'I\'ve randomly chosen **' + str(user) + '** to receive _' + str(exchange) + '_ points. Good for you.\n')
	elif rand_num <= 0.72: #Take points from a random user
		user = user_list[np.random.randint(len(user_list))]
		add_points(user, -1*exchange, ctx.message.server)
		await bot.send_message(ctx.message.channel, 'I\'ve randomly chosen **' + str(user) + '** to lose _' + str(exchange) + '_ points. That\'s unfortunate.\n')
	elif rand_num <= 0.86: #Randomly exchange some points
		user1 = user_list[np.random.randint(len(user_list))]
		user2 = user_list[np.random.randint(len(user_list))]
		while user1 == user2: #Fix the case where both users are the same
			user2 = user_list[np.random.randint(len(user_list))]
		add_points(user1, -1*exchange, ctx.message.server)
		add_points(user2, exchange, ctx.message.server)
		await bot.send_message(ctx.message.channel, '***' + str(user1) +'*** has given ***' + str(user2) + '*** _' + str(exchange) + '_ points. How nice of them.\n')
	elif rand_num <= 1.0: #Swap points
		user1 = user_list[np.random.randint(len(user_list))]
		user2 = user_list[np.random.randint(len(user_list))]
		while user1 == user2: #Fix the case where both users are the same
			user2 = user_list[np.random.randint(len(user_list))]
		user1_points = get_points(user1, ctx.message.server)
		user2_points = get_points(user2, ctx.message.server)
		add_points(user1, -1*(user1_points - user2_points), ctx.message.server)
		add_points(user2, user1_points - user2_points, ctx.message.server)
		await bot.send_message(ctx.message.channel, '***' + str(user1) + '*** and ***' + str(user2) + '*** have swapped points. See you next time.\n')
	
	#Write back to the file, now
	try:
		file = open(os.path.join(sys.path[0], 'save/chance/') + str(ctx.message.server.id) + '_' + date_string + '.txt', 'w')
		for x in content:
			file.write(x)
		file.write(ctx.message.author.id + '\n')
	except:
		print('Error writing to chance time file.')

#!superchance implementation. Performs some wacky chance time shenanigans
@bot.command(pass_context = True, description = 'Activates super chance time. Does a random effect to people on the current server, but to a much more extreme extent than normal chance time. Costs 40 points to use.')
async def superchance(ctx):
	#Check for privilieges first
	for x in range(10):
		role_check = discord.utils.get(ctx.message.author.roles, name = prestiges[x])#Get the server's roles
		if not role_check == None:
			role_name = prestiges[x]
		
	role_index = 0	
	try:
		role_index = prestiges.index(role_name)
	except:
		pass
		
	if role_index < 2:
		await bot.send_message(ctx.message.channel, 'Sorry, you must be at least a **Prawn** rank to be able to use this command. Use ***!prestige*** if you\'d like to rank up.')
		return
	
	#Variables
	user_list = []
	for x in ctx.message.server.members: #List of all the users in the server
		user_list.append(x)
	current_time = time.localtime() #year, month, day, hour, minute, second, weekday, year day, is daylight savings time?
	date_string = str(current_time[0]) + '.' + str(current_time[1]) + '.' + str(current_time[2])
	
	#Make sure they have enough points to use it.
	try:
		if get_points(ctx.message.author, ctx.message.server) < 40:
			await bot.send_message(ctx.message.channel, 'You have to have 40 points to play. Try again when you get more points, buddy.')
			return
	except:
		print('Error in get_points function. Called from superchance command.')
	
	add_points(ctx.message.author, -40, ctx.message.server) #take points for activating super chance time
	
	#Generate the random number for the effect and then do the effect
	await bot.send_message(ctx.message.channel, '_Starting_ **super chance time**_..._\n')
	await bot.send_typing(ctx.message.channel)
	rand_num = np.random.random_sample()
	exchange = np.random.randint(60) + 40 #Between 40 and 100.
	if rand_num <= 0.30: #Give points to the user that asked
		add_points(ctx.message.author, exchange, ctx.message.server)
		await bot.send_message(ctx.message.channel, 'Nice! You got _' + str(exchange) + '_ points.\n')
	elif rand_num <= 0.35: #Give super interest
		interest(0.1, ctx.message.server)
		stock_rates(ctx.message.server, 0.02)
		await bot.send_message(ctx.message.channel, 'The bank has just received 10% interest! Stocks have changed.')
	elif rand_num <= 0.42: #Take points from the user that asked
		add_points(ctx.message.author, -1*exchange, ctx.message.server)
		await bot.send_message(ctx.message.channel, 'Unlucky! You lost _' + str(exchange) + '_ points.\n')
	elif rand_num <= 0.65: #Give points to a random user
		user = user_list[np.random.randint(len(user_list))]
		add_points(user, exchange, ctx.message.server)
		await bot.send_message(ctx.message.channel, 'I\'ve randomly chosen **' + str(user) + '** to receive _' + str(exchange) + '_ points. Congrats.\n')
	elif rand_num <= 0.8: #Randomly exchange some points
		user1 = user_list[np.random.randint(len(user_list))]
		user2 = user_list[np.random.randint(len(user_list))]
		while user1 == user2: #Fix the case where both users are the same
			user2 = user_list[np.random.randint(len(user_list))]
		add_points(user1, -1*exchange, ctx.message.server)
		add_points(user2, exchange, ctx.message.server)
		await bot.send_message(ctx.message.channel, '***' + str(user1) +'*** has given ***' + str(user2) + '*** _' + str(exchange) + '_ points. How nice of them.\n')
	elif rand_num <= 0.83: #Everyone in the server gets 20 points
		for x in user_list:
			add_points(x, 20, ctx.message.server)
		await bot.send_message(ctx.message.channel, 'I\'m feeling charitable. Everyone on the server gets 20 points!')
	elif rand_num <= 0.85: #Give bankruptcy
		interest(-0.4, ctx.message.server)
		stock_rates(ctx.message.server, -0.04)
		await bot.send_message(ctx.message.channel, 'The economy is in ruin! The bank was hit pretty hard and the stock market is looking worse!')
	elif rand_num <= 1.0: #Swap points
		user1 = user_list[np.random.randint(len(user_list))]
		user2 = user_list[np.random.randint(len(user_list))]
		while user1 == user2: #Fix the case where both users are the same
			user2 = user_list[np.random.randint(len(user_list))]
		user1_points = get_points(user1, ctx.message.server)
		user2_points = get_points(user2, ctx.message.server)
		add_points(user1, -1*(user1_points - user2_points), ctx.message.server)
		add_points(user2, user1_points - user2_points, ctx.message.server)
		await bot.send_message(ctx.message.channel, '***' + str(user1) + '*** and ***' + str(user2) + '*** have swapped points. See you next time.\n')

#!ultrachance implementation. Performs some wacky chance time shenanigans, but even more so
@bot.command(pass_context = True, description = 'Activates ultra chance time. Does a random effect to people on the current server, but to the highest effect possible. Costs 100 points to use. Only available for those of rank Stone Shrimp or higher.')
async def ultrachance(ctx):
	#Check for privilieges first
	for x in range(10):
		role_check = discord.utils.get(ctx.message.author.roles, name = prestiges[x])#Get the server's roles
		if not role_check == None:
			role_name = prestiges[x]
		
	role_index = 0	
	try:
		role_index = prestiges.index(role_name)
	except:
		pass
		
	if role_index < 5:
		await bot.send_message(ctx.message.channel, 'Sorry, you must be at least a **Silver Shrimp** rank to be able to use this command. Use ***!prestige*** if you\'d like to rank up.')
		return
	
	#Variables
	user_list = []
	for x in ctx.message.server.members: #List of all the users in the server
		user_list.append(x)
	
	#Make sure they have enough points to use it.
	try:
		if get_points(ctx.message.author, ctx.message.server) < 100:
			await bot.send_message(ctx.message.channel, 'You have to have 100 points to play. Try again when you get more points, buddy.')
			return
	except:
		print('Error in get_points function. Called from ultrachance command.')
	
	add_points(ctx.message.author, -100, ctx.message.server) #take points for activating super chance time
	
	#Generate the random number for the effect and then do the effect
	await bot.send_message(ctx.message.channel, '_Starting_ **ultra chance time**_..._\n')
	await bot.send_typing(ctx.message.channel)
	rand_num = np.random.random_sample()
	exchange = np.random.randint(450) + 50 #Between 50 and 500.
	if rand_num <= 0.2: #Give points to the user that asked
		add_points(ctx.message.author, exchange, ctx.message.server)
		await bot.send_message(ctx.message.channel, 'Nice! You got _' + str(exchange) + '_ points.\n')
	elif rand_num <= 0.35: #Give ultra interest
		interest(0.2, ctx.message.server)
		await bot.send_message(ctx.message.channel, 'The bank has just received 20% interest!')
	elif rand_num <= 0.45: #Take points from the user that asked
		add_points(ctx.message.author, -1*exchange, ctx.message.server)
		await bot.send_message(ctx.message.channel, 'Unlucky! You lost _' + str(exchange) + '_ points.\n')
	elif rand_num <= 0.55: #Give points to a random user
		user = user_list[np.random.randint(len(user_list))]
		add_points(user, exchange, ctx.message.server)
		await bot.send_message(ctx.message.channel, 'I\'ve randomly chosen **' + str(user) + '** to receive _' + str(exchange) + '_ points. Congrats.\n')
	elif rand_num <= 0.65: #Randomly exchange some points
		user1 = user_list[np.random.randint(len(user_list))]
		user2 = user_list[np.random.randint(len(user_list))]
		while user1 == user2: #Fix the case where both users are the same
			user2 = user_list[np.random.randint(len(user_list))]
		add_points(user1, -1*exchange, ctx.message.server)
		add_points(user2, exchange, ctx.message.server)
		await bot.send_message(ctx.message.channel, '***' + str(user1) +'*** has given ***' + str(user2) + '*** _' + str(exchange) + '_ points. How nice of them.\n')
	elif rand_num <= 0.8: #Everyone in the server gets 50 points
		for x in user_list:
			add_points(x, 50, ctx.message.server)
		await bot.send_message(ctx.message.channel, 'I\'m feeling charitable. Everyone on the server gets 50 points!')
	elif rand_num <= 0.815: #Give bankruptcy
		interest(-0.6, ctx.message.server)
		stock_rates(ctx.message.server, -0.07)
		await bot.send_message(ctx.message.channel, 'The economy is in _ultra_ ruin! Most of the money in the bank was lost! The stock market is not looking so good...!')
	elif rand_num <= 0.9: #Everyone in the server loses 30 points
		for x in user_list:
			add_points(x, -30, ctx.message.server)
		await bot.send_message(ctx.message.channel, '_Something went wrong..._\nEveryone on the server will have to pay 30 points to fix this.')
	elif rand_num <= 1.0: #Swap points
		user1 = user_list[np.random.randint(len(user_list))]
		user2 = user_list[np.random.randint(len(user_list))]
		while user1 == user2: #Fix the case where both users are the same
			user2 = user_list[np.random.randint(len(user_list))]
		user1_points = get_points(user1, ctx.message.server)
		user2_points = get_points(user2, ctx.message.server)
		add_points(user1, -1*(user1_points - user2_points), ctx.message.server)
		add_points(user2, user1_points - user2_points, ctx.message.server)
		await bot.send_message(ctx.message.channel, '***' + str(user1) + '*** and ***' + str(user2) + '*** have swapped points. See you next time.\n')				
		
#!bomb implementation. Allows users play a game where they attempt to defuse a bomb	
@bot.command(pass_context = True, description = 'Play the bomb game. A random countdown number is generated, and then players will give numbers to make the countdown go down by that number. The player who makes the countdown hit 0 will lose 20 points, while all the winners will gain 10 points. Please consider that the bot will send you a message when it notices that you have joined. Sending many messages may be hard for the bot to process.')
async def bomb(ctx):
	player_list = []
	player_list.append(ctx.message.author)
	og_channel = ctx.message.channel
	await bot.send_message(ctx.message.channel, '__**It\'s time to play the bomb game!**__\nA _bomb_ has been given a random countdown number before it explodes. Players will take turns giving numbers (between 1-10) to tick down the _countdown_. If you set the _bomb_ off, you will lose 20 points. Every player that doesn\'t lose will gain 10 points. I\'ll give you feedback as the _bomb_ ticks down.\n _Type \'play\' in order to join the game._\n\n**GAME BEGINNING IN 45 SECONDS**')
	
	#Wait to see who wants to play
	waiting = 45
	while waiting >= 0:
		try:
			response = await bot.wait_for_message(timeout = 1,  channel = og_channel, content = 'play')
			if response.content == 'play':
				if not response.author in player_list:
					player_list.append(response.author)
					await bot.send_message(ctx.message.channel, str(response.author) + ' has joined.\n')
				elif response.author in player_list:
					await bot.send_message(ctx.message.channel, 'You have already joined.\n')
			waiting -= 1
			if waiting == 15:
				await bot.send_message(ctx.message.channel, '***15 seconds left to enter***\n')
		except:
			if waiting % 20 == 0:
				print('Bomb game starting in ' + str(waiting) + ' seconds.')
			if waiting == 15:
				await bot.send_message(ctx.message.channel, '***15 seconds left to enter***\n')
			waiting -=1
	
	#Make sure at least two players are playing
	if len(player_list) < 2:
		await bot.send_message(ctx.message.channel, 'Only one person entered, so the game will be cancelled.\n')
		return
	
	#Otherwise, let them know who is playing
	msg = '__Here are the players that I have:__\n'
	for x in player_list:
		msg += str(x) + ', '
	await bot.send_message(og_channel, msg)
	
	#Set everything up
	await bot.send_message(og_channel, 'It\'s time to play the bomb game. Generating bomb...\n')
	timer = np.random.randint(80) + 20 #Timer can be between 20 and 100
	turn = 0 #Whose turn it is
	
	#Play the game, now.
	while timer > 0:
	
		#Handle timer messages. May want to add more messages and a message randomizer.
		if timer >= 75:
			msgs = ['The bomb seems to have a lot of time left...', 'It doesn\'t seem that the bomb will explode any time soon...'] 
			warning_message = msgs[np.random.randint(2)]
		elif timer >= 45:
			msgs = ['The bomb still has a ways to go.', 'I don\'t think the bomb will be exploding soon.']
			warning_message = msgs[np.random.randint(2)]
		elif timer >= 25:
			msgs = ['The bomb is getting a bit closer to exploding.', 'I sense that the bomb is getting close to exploding.']
			warning_message = msgs[np.random.randint(2)]
		elif timer >= 13:
			msgs = ['The bomb is getting ready to explode.', 'It\'s going to blow soon!', 'Be careful, the bomb will detonate really soon!']
			warning_message = msgs[np.random.randint(3)]
		await bot.send_message(og_channel, player_list[turn].mention + ', it is your turn. Please give a countdown between 1-10, or 56.\n' + warning_message)
		
		#Wait for a response
		response = await bot.wait_for_message(timeout = 12, author = player_list[turn], channel = og_channel, check = bomb_check)
		
		if response == None: #If no good response was given, default countdown to 10
			countdown = 10
			await bot.send_message(og_channel, 'You ran out of time. Defaulting to 10 ticks...\n')
			
		if response == '56':
			await bot.send_message(ctx.message.channel, '***Okay***, I am ticking the bomb down by _56_ ticks...')
		#Drop the timer by the countdown
		try:
			countdown = int(response.content)
			timer -= countdown
		except:
			print('Error with bomb countdown')
			
		if timer <= 0: #Check if the game is over
			loser = player_list[turn]
		
		turn += 1
		if turn >= len(player_list): #Reset the turn back to the first person if the index exceeds the length
			turn = 0
	
	await bot.send_message(og_channel, str(loser) + ' has lost. They will lose 20 points. Congrats to _everyone else_, though.\n')
		
	#Give the points out
	for x in player_list:
		if x == loser:
			add_points(loser, -20 , ctx.message.server)
		else:
			add_points(x, 10, ctx.message.server)

#!auction implementation. Allows users to bet on random objects to buy them
@bot.command(pass_context = True, description = 'Hold an auction for a random item. Users will bid on the item, whose price is unknown. After a user has won the auction, the item will be sold and points will be gained or lost depending on how the winner\'s bid compares to the actual price. If only one person bids, the auction will be cancelled. Each item has a price range depending on it\'s likely value.')
async def auction(ctx):
	first_bid = True
	bidder = ctx.message.author
	item = np.random.randint(15)
	price = math.ceil((20*item+1)+(np.random.randint(5)-2)*np.random.random_sample()*50)
	if price <= 0:
		price += 100
	current_bid = math.ceil(price*0.5*(np.random.random_sample()+0.12))
	await bot.send_message(ctx.message.channel, 'An auction is starting! Right now, I have a _' + auction_names[item] + '_. Let\'s start the bidding at **' + str(current_bid) + '** points. Type a point amount to make a bid.')
	await bot.send_file(ctx.message.channel, os.path.join(sys.path[0], 'auction/') + str(item + 1) + '.png')
	
	#Wait to see if anyone wants to bid
	waiting = 25
	while waiting >= 0:
		response = await bot.wait_for_message(timeout = 1, channel = ctx.message.channel, check = auction_check)
		try:
			if not response == None:
				if int(response.content) <= current_bid:
					await bot.send_message(ctx.message.channel, response.author.mention + 'That amount is too low. Please bid higher than the current bid.')
				elif int(response.content) >= 500:
					await bot.send_message(ctx.message.channel, 'The maximum bid is 500 points. Please bet a lower amount.')
				elif int(response.content) > get_points(response.author, ctx.message.server):
					await bot.send_message(ctx.message.channel, 'You don\'t have enough points to bid that much...')
				else:
					await bot.send_message(ctx.message.channel, '**' + str(response.author) + '** has bid _' + response.content + '_ points. Would anyone like to outbid him/her?')
					waiting = 15
					current_bid = int(response.content)
					bidder = response.author
					if (not response.author == ctx.message.author) and first_bid: #Make sure at least one other person participates
						first_bid = False
		except:
			pass
		
		if waiting == 12:
			await bot.send_message(ctx.message.channel, '***Going once!***')
		elif waiting == 5:
			await bot.send_message(ctx.message.channel, '***Going twice!***')
		waiting -=1
	
	#If the item was sold
	if first_bid:
		await bot.send_message(ctx.message.channel, 'Only the person who started the auction bid, so it will be cancelled.')
		return
	else:
		await bot.send_message(ctx.message.channel, 'The _' + auction_names[item] + '_ has sold for **' + str(current_bid) + '** points. It\'s actual cost was **' + str(price) + '** points.')
		add_points(bidder, price - current_bid, ctx.message.server)
		if price - current_bid <= 0:
			await bot.send_message(ctx.message.channel, bidder.mention + 'Oof. Better luck next time. You just lost **' + str(current_bid - price) + '** points on that sale.')
		else:
			await bot.send_message(ctx.message.channel, bidder.mention + 'Nice. With that purchase you gained **' + str(price - current_bid) + '** points! Thanks for a successful auction!')
		
#!stop_bot implementation. Makes the bot disconnect from Discord	
@bot.command(pass_context = True, description = 'Logs the bot out of Discord. Please do not use unless you absolutely have to. Use is restricted to certian users.')
async def stop_bot(ctx):
	if not str(ctx.message.author.id) == '122856551848476676':
		await bot.send_message(ctx.message.channel, 'You are not allowed to stop the bot. Only the creator of the bot may do this.')
		return
	
	#Kick the bot from all connected voice clients before logging out
	try:
		for x in bot.voice_clients: 
			try:
				await disconnect_from(x)
			except:
				pass
	except:
		print('Error in trying to kick the bot from a voice channel. In stop_bot')	
	
	try:
		await bot.logout()
		await client.logout()
		print('User ' + str(ctx.message.author) + ' from server ' + str(ctx.message.server) + ' has asked the bot to logout.\n')
	except:
		print('Error trying to disconnect the bot via command. It is possible that someone tried to disconnect over a private message channel.\n')
		print('Disconnect attemtped by user ' + str(ctx.message.author))
		
#!server_message implementation. 
@bot.command(pass_context = True, description = 'Sends a message to all Discord servers that the bot is in. Use is restricted to certain users.')
async def server_message(ctx, message = None):
	if not str(ctx.message.author.id) == '122856551848476676':
		await bot.send_message(ctx.message.channel, 'You are not allowed to send server messages. Only the creator of the bot may do this.')
		return
		
	print(message)
	try:
		for y in bot.servers:
			print('Trying to send message to' + str(y))
			general = find(lambda x: 'general' in x.name,  y.text_channels)
			if general and general.permissions_for(y.me).send_messages:
				await bot.send_message(general, message)
	except:
		print('Disconnect attemtped by user ' + str(ctx.message.author))

#!kickme implementation. Makes the bot leave the calling server's voice channels
@bot.command(pass_context = True)
async def kickme(ctx, description = 'Kicks the bot from any joined voice channels. [Does not currently work]'):
	try:
		for x in bot.voice_clients: #DEBUG Make disconnect from only server called from
			try:
				await disconnect_from(x)
			except:
				pass
	except:
		print('Error in trying to kick the bot from a voice channel.')
	
	print('!kickme used.')

#!buy implementation. Allows user to reset file in exchange for points
@bot.command(pass_context = True, description = 'Allows you to pay 35 points to reset the chance time or bed permissions for the day. When you buy the reset, permissions will be restarted for everyone in the server. \nExample of usage:\n!buy bed\n!buy chance\n!buy card')
async def buy(ctx, option = None):
	#Variables
	msg_list = ctx.message.content.split() #User message
	error_msg = 'Error using buy. You will not lose any points. Did you use the command correctly? !buy can be used like:\n!buy bed\n***OR***\n!buy chance\n***OR***\n!buy card'
	current_time_og = time.localtime() #year, month, day, hour, minute, second, weekday, year day, is daylight savings time?
	
	if option == None: #If the wrong number of arguments were given, set the msg to be the error message
		await bot.send_message(ctx.message.channel, error_msg)
		return
		
	else:
		if option == 'bed': #If they want the beds reset
			
			#Fix a bug with overwriting the current time correctly.
			current_time = []
			current_time.append(current_time_og[0])
			current_time.append(current_time_og[1])
			try:
				if current_time_og[3] <= 2: #If it is before 2AM, count it towards today's bed
					current_time.append(current_time_og[2] - 1)
				else:
					current_time.append(current_time_og[2])
				current_time.append(current_time_og[3]) #Have to add this and the next line to fix the overwrite problem.
				current_time.append(current_time_og[4])
			except:
				print ('Error trying to convert time in !bed section of !buy function.\n')
				
			date_string = os.path.join(sys.path[0], 'save/beds/bed.') + str(current_time[0]) + '.' + str(current_time[1]) + '.' + str(current_time[2]) + '.txt'
			try: #See if someone has already asked for a bed and the file exists, if so, overwrite it
				if get_points(ctx.message.author, ctx.message.server) >= 35:
					file = open(date_string, 'r')
					file.close()
					file = open(date_string, 'w')
				else:
					await bot.send_message(ctx.message.channel, 'You don\'t have enough points do that right now.')
					return
			except: #If not, return and don't charge them
				await bot.send_message(ctx.message.channel, 'No one has asked for a bed yet, today. No need to reset it, then.')
				return
					
			file.write('File reset at ' + str(current_time[3]) + ':' + str(current_time[4]) + ' by ' + str(ctx.message.author) + '\n')
			file.close()
			add_points(ctx.message.author, -35, ctx.message.server)
			await bot.send_message(ctx.message.channel, 'The beds have been reset for the day. I have taken 35 points as a gratuity.\n')
			
		elif option == 'chance': #If they want chance reset
			date_string = str(current_time_og[0]) + '.' + str(current_time_og[1]) + '.' + str(current_time_og[2])
			try: #Try to open the file, if it exists
				if get_points(ctx.message.author, ctx.message.server) >= 35:
					file = open(os.path.join(sys.path[0], 'save/chance/') + str(ctx.message.server.id) + '_' + date_string + '.txt', 'r')
					file.close()
					file = open(os.path.join(sys.path[0], 'save/chance/') + str(ctx.message.server.id) + '_' + date_string + '.txt', 'w')
				else:
					await bot.send_message(ctx.message.channel, 'You don\'t have enough points do that right now.')
					return
			except: #If chance file does not exist for the current day, don't charge the user and return
				await bot.send_message(ctx.message.channel, 'No one has asked for chance time yet, today. No need to reset it, then.')
				return
				
			file.write('File reset at ' + str(current_time_og[3]) + ':' + str(current_time_og[4]) + ' by ' + str(ctx.message.author) + '\n')
			file.close()
			add_points(ctx.message.author, -35, ctx.message.server)
			await bot.send_message(ctx.message.channel, 'Chance time been reset for the day. I have taken 35 points as a gratuity.\n')
		
		elif option == 'card':
			date_string = str(current_time_og[0]) + '.' + str(current_time_og[1]) + '.' + str(current_time_og[2])
			try: #Try to open the file, if it exists
				if get_points(ctx.message.author, ctx.message.server) >= 35:
					file = open(os.path.join(sys.path[0], 'save/card/card_') + str(ctx.message.server.id) + '_' + date_string + '.txt', 'r')
					file.close()
					file = open(os.path.join(sys.path[0], 'save/card/card_') + str(ctx.message.server.id) + '_' + date_string + '.txt', 'w')
				else:
					await bot.send_message(ctx.message.channel, 'You don\'t have enough points do that right now.')
					return
			except: #If card file does not exist for the current day, don't charge the user and return
				await bot.send_message(ctx.message.channel, 'No one has asked for cards yet, today. No need to reset it, then.')
				return
				
			file.write('File reset at ' + str(current_time_og[3]) + ':' + str(current_time_og[4]) + ' by ' + str(ctx.message.author) + '\n')
			file.close()
			add_points(ctx.message.author, -35, ctx.message.server)
			await bot.send_message(ctx.message.channel, 'Cards have been reset for the day. I have taken 35 points as a gratuity.\n')
		
		else: #If bed, card, or chance was not given as the argument
			await bot.send_message(ctx.message.channel, error_msg)
			return
			
	stock_rates(ctx.message.server, 0.03)

@bot.command(pass_context = True, description = 'Get a card. Everything has to be a gacha nowadays. You can get one card per day. There are many cards to collect. There are also foil variations of each time which are rarer. After you collect a certain number of cards, you will be given points as a reward. Getting duplicates now rewards you with 5 points for a normal and 10 for a foil. You can use the !buy command to pay for another chance to get cards. Use !mycards to see your cards.')
#!card implementation. Give the user a random card once per day
async def card(ctx):
	current_time = time.localtime()
	date_string = os.path.join(sys.path[0], 'save/card/card_') + str(ctx.message.server.id) + '_' + str(current_time[0]) + '.' + str(current_time[1]) + '.' + str(current_time[2]) + '.txt'
	
	#check if file exists, first
	try:
		file = open(date_string, 'r')
	except:
		clear_cards(ctx)
		file = open(date_string, 'w')
		file.write('File created at ' + str(current_time[3]) + ':' + str(current_time[4]))
		file.close()
		file = open(date_string, 'r')
	
	#Check if they've gotten a card already today
	file_contents = file.read().splitlines()
	file.close()
	if str(ctx.message.author.id) in file_contents: #If they've gotten a card, send a message and return
		await bot.send_message(ctx.message.channel, ctx.message.author.mention + 'You have already gotten a card today. You can either get a new one by using ***!buy card*** or waiting for another _' + str(23 - current_time[3]) + '_ hours and _' + str(60 - current_time[4]) + '_ minutes.')
		return
		
	#If not, add them to the card save file
	file_contents.append(str(ctx.message.author.id))
	
	#Write back to the file
	file = open(date_string, 'w')
	for x in file_contents:
		file.write(x + '\n')
	file.close()
	
	#Generate what card they should get
	rand_num = np.random.random_sample()
	card_index = 0
	partial_card_sum_low = 0
	partial_card_sum_high = 0
	for x in range(len(card_names)+1):
		if rand_num < partial_card_sum_high/card_sum and rand_num >= partial_card_sum_low/card_sum:
			card_index = x - 1
			break
		
		partial_card_sum_low = partial_card_sum_high
		partial_card_sum_high += card_rarities[x]
		
	#Check if they already have this card. If not, add it to their card file
	try: #Make a file if it doesn't exist
		file = open(os.path.join(sys.path[0], 'save/card/card_') + str(ctx.message.server.id) + '_' + str(ctx.message.author.id) + '.txt', 'r')
	except:
		file = open(os.path.join(sys.path[0], 'save/card/card_') + str(ctx.message.server.id) + '_' + str(ctx.message.author.id) + '.txt', 'w')
		file.write('0 0\n')
		file.close()
		file = open(os.path.join(sys.path[0], 'save/card/card_') + str(ctx.message.server.id) + '_' + str(ctx.message.author.id) + '.txt', 'r')
		
	new_file_contents = file.read().splitlines()
	file_contents = []
	for x in new_file_contents:
		file_contents.append(x.split())
	del new_file_contents
	
	new_card = False
	new_foil = False
	foil = False
	rand_num = np.random.random_sample()
	
	try:
		if card_rarities[card_index] < 4: #If rarity is low, make foil chance higher to help with collection
			rand_num *= 0.5
	except:
		print('Error with trying to increse rate on rare foil.')
		
	if rand_num >= .2 and rand_num <= .4:
		foil = True
	
	#Adjust the file if new card have been added
	for x in range(len(card_rarities)):
		try:
			file_contents[x] = file_contents[x]
		except:
			file_contents.append(['0', '0'])
	
	if foil:
		if file_contents[card_index][1] == '0':
			new_foil = True
			new_card = True
		file_contents[card_index][1] = '1'
	else:
		if file_contents[card_index][0] == '0':
			new_card = True
		file_contents[card_index][0] = '1'
		
	#Save the file
	file = open(os.path.join(sys.path[0], 'save/card/card_') + str(ctx.message.server.id) + '_' + str(ctx.message.author.id) + '.txt', 'w')
	for x in file_contents:
		file.write(x[0] + ' ' + x[1] + '\n')
	file.close()
	
	if new_card: #If they got a new card, count their cards and possibly give them a reward
		card_count = 0
		foil_count = 0
		for x in file_contents:
			if x[0] == '1':
				card_count += 1
			if x[1] == '1':
				card_count += 1
				foil_count += 1
		if card_count == 5:
			await bot.send_message(ctx.message.channel, 'Congrats, you have 5 unique cards. Take 50 points as a bonus.')
			add_points(ctx.message.author, 50, ctx.message.server)
		elif card_count == 10:
			await bot.send_message(ctx.message.channel, 'Congrats, you have 10 unique cards. Take 150 points as a bonus.')
			add_points(ctx.message.author, 150, ctx.message.server)
		elif card_count == 25:
			await bot.send_message(ctx.message.channel, 'Congrats, you have 25 unique cards. Take 300 points as a bonus.')
			add_points(ctx.message.author, 300, ctx.message.server)
		elif card_count == 50:
			await bot.send_message(ctx.message.channel, 'Congrats, you have 50 unique cards. Take 750 points as a bonus.')
			add_points(ctx.message.author, 750, ctx.message.server)
		
		if new_foil:
			if foil_count == 5:
				await bot.send_message(ctx.message.channel, 'Congrats, you have 5 unique foil cards. Take 75 points as a bonus.')
				add_points(ctx.message.author, 75, ctx.message.server)
			elif foil_count == 10:
				await bot.send_message(ctx.message.channel, 'Congrats, you have 10 unique foil cards. Take 200 points as a bonus.')
				add_points(ctx.message.author, 200, ctx.message.server)
			elif foil_count == 25:
				await bot.send_message(ctx.message.channel, 'Congrats, you have 25 unique foil cards. Take 500 points as a bonus.')
				add_points(ctx.message.author, 500, ctx.message.server)
			elif foil_count == 50:
				await bot.send_message(ctx.message.channel, 'Congrats, you have 50 unique foil cards. Take 1500 points as a bonus.')
				add_points(ctx.message.author, 1500, ctx.message.server)
	else:
		if foil:
			add_points(ctx.message.author, 10, ctx.message.server)
		else:
			add_points(ctx.message.author, 5, ctx.message.server)
		await bot.send_message(ctx.message.channel, 'You got a duplicate. I went ahead and bought the card off of you.')
	
	#Display the card, now
	card_string = os.path.join(sys.path[0], 'cards/') + str(card_index + 1)
	if foil:
		card_string += 'f'
	card_string += '.png'
	
	await bot.send_file(ctx.message.channel, card_string)
	await bot.send_message(ctx.message.channel, 'This is card number _' + str(card_index + 1) + '_ of _' + str(len(card_rarities)) + '_, **' + card_names[card_index] + '**!')
	
@bot.command(pass_context = True, description = '')
#!mycards implementation. Display cards the user has
async def mycards(ctx, number = None):

	#Check if they already have this card. If not, add it to their card file
	try: #Make a file if it doesn't exist
		file = open(os.path.join(sys.path[0], 'save/card/card_') + str(ctx.message.server.id) + '_' + str(ctx.message.author.id) + '.txt', 'r')
	except:
		file = open(os.path.join(sys.path[0], 'save/card/card_') + str(ctx.message.server.id) + '_' + str(ctx.message.author.id) + '.txt', 'w')
		file.write('0 0\n')
		file.close()
		file = open(os.path.join(sys.path[0], 'save/card/card_') + str(ctx.message.server.id) + '_' + str(ctx.message.author.id) + '.txt', 'r')

	new_file_contents = file.read().splitlines()
	file_contents = []
	for x in new_file_contents:
		file_contents.append(x.split())
	del new_file_contents	
	
	try:
		if int(number) <= 0 or int(number) > len(card_rarities):
			await bot.send_message(ctx.message.channel, 'Error. The number provided is not a number of card that currently exists. There are ' + str(len(card_rarities)) + ' cards.')
			return
	except:
		pass
	
	normal_count = 0
	card_count = 0
	foil_count = 0
	card_index = 0
	has_card = False
	has_foil = False
	msg = '__Here are the cards you currently own on __***' + str(ctx.message.server) + '***\n'
	for x in file_contents:
		if x[0] == '1':
			card_count += 1
			normal_count += 1
			msg += str(card_index + 1) + ' - _' + card_names[card_index] +'_\n'
			if not number == None:
				try:
					if card_index + 1 == int(number):
						has_card = True
				except:
					await bot.send_message(ctx.message.channel, 'That\'s not a number you provided me!')
					return
		
		if x[1] == '1':
			card_count += 1 
			foil_count += 1
			msg += str(card_index + 1) + ' - _' + card_names[card_index] +' (FOIL)_ \n'
			if not number == None:
				try:
					if card_index + 1 == int(number):
						has_foil = True
				except:
					await bot.send_message(ctx.message.channel, 'That\'s not a number you provided me!')
					return
		
		card_index += 1
					
	if number == None:
		try:
			await bot.start_private_message(ctx.message.author)
			await bot.send_message(ctx.message.author, msg + '\n' + 'You have _' + str(card_count) + '_ out of _' + str(2*len(card_rarities)) + '_ cards. _' + str(normal_count) + '_ are normal cards and _' + str(foil_count) + '_ are foil(s).')
		except:
			await bot.send_message(ctx.message.channel, 'I tried to private message you, but an error occurred. Do you have private messaging blocked?')
		return
	
	else:
		try:
			if has_card or has_foil:
				await bot.send_message(ctx.message.channel, 'Here is card number _' + number + '_!')
				if has_card:
					await bot.send_file(ctx.message.channel, os.path.join(sys.path[0], 'cards/') + number + '.png')
				if has_foil:
					await bot.send_file(ctx.message.channel, os.path.join(sys.path[0], 'cards/') + number + 'f.png')
			else:
				await bot.send_message(ctx.message.channel, 'You do not own that card number.')
				
		except:
			await bot.send_message(ctx.message.channel, 'Error. Did you provide me a correct number?')
		
				
@bot.command(pass_context = True, description = 'Play a game of the Prisoner\'s Dilemma with one other user. You each get a chance to either ally or betray. If you ally together, you will both get points, but if one person betrays an ally, then they receive even more points! If you both betray, though, you\'ll both be penalized.')
#!ab implementation. Play the Prisoner's Dilemma
async def ab(ctx):
	await bot.send_message(ctx.message.channel, '__Let\'s do an AB game!__\nIt\'s time to partake in the Prisoner\'s Dilemma! I will PM both players and wait for a choice of **ally** or **betray**. If you both ally, you\'ll both win, but you can choose to _betray_ the other player for even more points. If you both betray, you\'ll both lose points.\n__Here\'s a run down of the scoring:__\n_Both ally_\t**+12 for both players**\n_One ally and betray_\t**Betray gets +20 and Ally gets -8**\n_Both betray_\t**-3 for both players**\n\nType ***play*** to join.\nWho would like to play against _' + str(ctx.message.author) + '_?\n***Game will begin in 60 seconds.***' )
	player1 = ctx.message.author
	response = await bot.wait_for_message(timeout = 60, content = 'play')
	
	if response == None:
		await bot.send_message(ctx.message.channel, 'Sorry, it looks like nobody else wanted to play.')
		return
	
	if response.author == player1:
		await bot.send_message(ctx.message.channel, 'You cannot play against yourself. Cancelling game.')
		return
	
	player2 = response.author
	
	#Open 2 private message and send them each a message
	await bot.start_private_message(player1)
	await bot.send_message(player1, 'Would you like to ally or betray? Type *ally* or *betray* to make your choice. You have 25 seconds...')
	response1 = await bot.wait_for_message(timeout = 25,  author = player1, check = ab_check)
	if response1 == None:
		await bot.send_message(player1, 'You\'ve run out of time... I will default you to ally.')
		response1 = 'ally'
	else:
		response1 = response1.content
		await bot.send_message(player1, 'You\'ve chosen to ' + response1)
		
	await bot.start_private_message(player2)
	await bot.send_message(player2, 'Would you like to ally or betray? Type *ally* or *betray* to make your choice. You have 25 seconds...')
	response2 = await bot.wait_for_message(timeout = 25,  author = player2,  check = ab_check)	
	if response2 == None:
		await bot.send_message(player2, 'You\'ve run out of time... I will default you to ally.')
		response2 = 'ally'
	else:
		response2 = response2.content
		await bot.send_message(player2, 'You\'ve chosen to ' + response2)
		
	#Determine results and post message
	await bot.send_message(ctx.message.channel, '**' + str(player1) + '** has chosen to _' + response1 + '_\n**' + str(player2) + '** has chosen to _' + response2 + '_\n')
	if response1 == 'ally' and response2 == 'ally':
		await bot.send_message(ctx.message.channel, 'Good choice. You both chose ally. You both get 12 points.')
		add_points(player1, 12, ctx.message.server)
		add_points(player2, 12, ctx.message.server)
	elif response1 == 'ally' and response2 == 'betray':
		await bot.send_message(ctx.message.channel, 'Congrats, _' + str(player2) + '_, you sold out the other player for a cool 20 points.\n_' + str(player1) + '_, looks like you lose 8 points.')
		add_points(player1, -8, ctx.message.server)
		add_points(player2, 20, ctx.message.server)
	elif response1 == 'betray' and response2 == 'ally':
		await bot.send_message(ctx.message.channel, 'Congrats, _' + str(player1) + '_, you sold out the other player for a cool 20 points.\n_' + str(player2) + '_, looks like you lose 8 points.')
		add_points(player1, 20, ctx.message.server)
		add_points(player2, -8, ctx.message.server)
	elif response1 == 'betray' and response2 == 'betray':
		await bot.send_message(ctx.message.channel, 'Wow, can\'t trust anybody these days, huh? I\'m taking 3 points from each of you for your lack of trust.')
		add_points(player1, -3, ctx.message.server)
		add_points(player2, -3, ctx.message.server)
		stock_rates(ctx.message.server, -0.02)
	
@bot.command(pass_context = True, description = 'Play Rock, Paper, Scissors with the bot. If you win, you\'ll be given 8 points, but if you lose, the bot will take 8 points from you. Reply with rock, paper, or scissors to play a specific choice.')
#!rps impementation. For rock, paper, scissors.
async def rps(ctx):
	choice =  np.random.randint(3) #Randomly generate what the bot should choose
	rps_choice = ['rock', 'paper', 'scissors'] #0 for rock, 1 for paper, 2 for scissors
	await bot.send_message(ctx.message.channel, 'Let\'s play rock, paper, scissors. Choose one of the three by typing your option out.') #Tell the user about rps
	response = await bot.wait_for_message(timeout = 30, author = ctx.message.author, check = rps_check)

	#Tell the user what the bot got.
	await bot.send_message(ctx.message.channel, 'I chose ' + rps_choice[choice])	
	
	#Determine the outcome and give points if needed
	if response.content == 'rock' or response.content == 'Rock':
		if choice == 0: #Bot got rock
			msg = 'We tied. Would you like to play again?' #Tie, add no points
		elif choice == 1: #Bot got paper
			msg = 'Nice. I win. Gimme those 8 points.'
			add_points(ctx.message.author, -8, ctx.message.server)
		elif choice == 2: #Bot got scissors
			msg = 'Dang! I guess you won. _Here\'s 8 points_.'
			add_points(ctx.message.author, 8, ctx.message.server)
	elif response.content == 'paper' or response.content == 'Paper':
		if choice == 0: #Bot got rock
			msg = 'Dang! I guess you won. _Here\'s 8 points_.'
			add_points(ctx.message.author, 8, ctx.message.server)
		elif choice == 1: #Bot got paper
			msg = 'We tied. Would you like to play again?' #Tie, add no points
		elif choice == 2: #Bot got scissors
			msg = 'Nice. I win. Gimme those 8 points.'
			add_points(ctx.message.author, -8, ctx.message.server)
	elif response.content == 'scissors' or response.content == 'Scissors':
		if choice == 0: #Bot got rock
			msg = 'Nice. I win. Gimme those 8 points.'
			add_points(ctx.message.author, -8, ctx.message.server)
		elif choice == 1: #Bot got paper
			msg = 'Dang! I guess you won. _Here\'s 8 points_.'
			add_points(ctx.message.author, 8, ctx.message.server)
		elif choice == 2: #Bot got scissors
			msg = 'We tied. Would you like to play again?' #Tie, add no points
	elif response == None:
		msg = '_I couldn\'t wait all day._ I\'m done playing rock, paper, scissors.'
	
	await bot.send_message(ctx.message.channel, msg)
	
@bot.command(pass_context = True, description = 'Allows you to put money in the bank, where it will earn interest. Use \'d\' for deposits and \'w\' for withdrawls. Be careful though, there is a very small probability that superchance will cause a bankruptcy and you will lose some of your money. Interest is decided by random events, so you may get more or less points than expected.\n**Examples of usage:**\n!bank\t(Gives you your balanace)\n!bank d 30\t(Deposit 30 points)\n!bank w 25 (Withdraws 25 points)')
#!bank impementation. Can deposit points for later. Will earn interest.
async def bank(ctx, option = None, amount = None): #option is what the person wants to do, deposit or withdraw, amount is the amount they want to do that with
	#Try to open the file first
	try:
		file = open(os.path.join(sys.path[0], 'save/bank/bank_') + str(ctx.message.server.id) + '.txt', 'r')
	except: #If the file does not exist
		file = open(os.path.join(sys.path[0], 'save/bank/bank_') + str(ctx.message.server.id) + '.txt', 'w')
		file.write(str(ctx.message.author.id) + ' ' + '0\n')
		file.close()
		file = open(os.path.join(sys.path[0], 'save/bank/bank_') + str(ctx.message.server.id) + '.txt', 'r')
		
	#Read the file information
	file_contents = file.read().splitlines() #Gets rid of any line feeds. Make sure to put them back later.
	file.close()
	contents = []
	for x in file_contents:
		contents.append(x.split())
	del file_contents
	
	#Process what option they want
	if option == None and amount == None: #If no arguments are provided, give them their balance
		for x in contents:
			if x[0] == str(ctx.message.author.id):
				await bot.send_message(ctx.message.channel, 'You have _' + str(x[1]) + '_ points in the bank.')
				return
		await bot.send_message(ctx.message.channel, 'You have not yet used the bank. Use ***!help bank*** to see how to make a deposit.') #If id is not found in the file
		return
	else:
		try:
			found_user = False #Whether the user exists or not
			if int(amount) <= 0: #If the user tries to make a negative or zero deposit
				await bot.send_message(ctx.message.channel, 'You can\'t unload a non-positive amount onto the bank! What are you trying to pull?')
				return
				
			if option == 'd': #Make a deposit
				if get_points(ctx.message.author, ctx.message.server) >= int(amount): #Make sure they have enough points to deposit
					for x in contents:
						if x[0] == str(ctx.message.author.id):
							x[1] = str(int(x[1]) + int(amount))
							found_user = True
					if not found_user:
						contents.append([str(ctx.message.author.id), str(amount)])
					add_points(ctx.message.author, -1*int(amount), ctx.message.server) #Now take away the points from their actual point amount
					await bot.send_message(ctx.message.channel, 'I have taken _' + amount + '_ points and put them into the bank.')
				
				else: #If the user did not have enough points for the deposit
					await bot.send_message(ctx.message.channel, 'You don\'t have enough points to make that deposit. Check how many points you have with **!mypoints**')
					return
					
			elif option == 'w': #Make a withdrawl
					for x in contents:
						if x[0] == str(ctx.message.author.id):
							found_user = True
							if int(x[1]) >= int(amount): #Make sure their balance is big enough to withdraw from
								x[1] = str(int(x[1]) - int(amount))
								add_points(ctx.message.author, int(amount), ctx.message.server)
								await bot.send_message(ctx.message.channel, 'I have given you _' + amount + '_ points from your bank account.')
							else: #If the balance is less than they asked for
								await bot.send_message(ctx.message.channel, 'You don\'t have enough points to make that withdrawl. Check how many points you have in the bank with **!bank**')
								return	
					if not found_user: #If the user didn't exist
						await bot.send_message(ctx.message.channel, 'I did not find any deposits that you have made. Use ***!bank d <amount>*** to deposit points into the bank.')
						return
			else:
				await bot.send_message(ctx.message.channel, 'Error. Use w or d for withdrawl or deposit. To see how to use !bank, use ***!help bank.***')
				return
				
		except:
			await bot.send_message(ctx.message.channel, 'There was a problem with your bank command. Did you use the command properly? Use ***!help bank*** to see how to use !bank correctly.')
			return
		
	#Write back to the file when done.
	file = open(os.path.join(sys.path[0], 'save/bank/bank_') + str(ctx.message.server.id) + '.txt', 'w')
	for x in contents:
		file.write(x[0] + ' ' + x[1] + '\n')
	file.close()
	
@bot.command(pass_context = True, description = 'Buy stocks and become a wise investor. You can buy or sell stocks in one of three companies, each with differing chances to increase or decrease in price. Stock price changes are decided by random factors. You can buy stocks from (A)verage School Supplies Comapny, (B)etter Offerings For Americans, or (C)heap Chimp Suppliers.\n**Examples of usage:**\n!stocks (Tells you how many of each stock you have purchased, and the current price of each stock)\n!stocks b A 5 (Buys 5 stocks from company A)\n!stocks s B 6 (Sells 6 stocks from company B\n!stocks b C 10 (Buys 10 stocks from company C)')
#!stocks impementation. Can buy or sell stocks that randomly go up or down
async def stocks(ctx, option = None, type = None, amount = None): #option is what the person wants to do, buy or sell, type is which stock they want, amount is the amount they want to do that with
	#Try to open the file first
	try:
		file = open(os.path.join(sys.path[0], 'save/stocks/stocks_') + str(ctx.message.server.id) + '.txt', 'r')
	except: #If the file does not exist
		file = open(os.path.join(sys.path[0], 'save/stocks/stocks_') + str(ctx.message.server.id) + '.txt', 'w')
		file.write('stocks 15 25 10\n')
		file.close()
		file = open(os.path.join(sys.path[0], 'save/stocks/stocks_') + str(ctx.message.server.id) + '.txt', 'r')
		
	#Read the file information
	file_contents = file.read().splitlines() #Gets rid of any line feeds. Make sure to put them back later.
	file.close()
	contents = []
	for x in file_contents:
		contents.append(x.split()) #Each member will contain 4 members, being id, amount of a, amount of b, amount of c, respeectively
	del file_contents
	
	#Process what option they want
	if option == None and type == None and amount == None: #If no arguments are provided, give them the stocks they own
		await bot.start_private_message(ctx.message.author)
		await bot.send_message(ctx.message.author, 'Here are the current prices of stocks:\n***(A)verage School Supplies Company*** is selling for _' + str(contents[0][1]) + '_ points\n***(B)etter Offerings For Americans*** is going for _' + str(contents[0][2]) + '_ points\n***(C)heap Chimp Suppliers*** stocks are currently _' + str(contents[0][3]) + '_ points.')
		for x in contents:
			if x[0] == str(ctx.message.author.id):
				await bot.send_message(ctx.message.author, 'In **' + str(ctx.message.server) + '**, you have:\n_' + x[1] + '_ stocks in A.\n_' + x[2] + '_ stocks in B.\n_' + x[3] + '_ stocks in C.\nIf you would like to sell stocks, use ***!stocks s <company> <amount>***')
				return
		await bot.send_message(ctx.message.author, 'You have not yet used !stocks. Use ***!help stocks*** to see how the command works.') #If id is not found in the file
		return
	else:
		try:
			#Specify what index to use for later
			index = 1
			if type == 'a' or type =='A':
				index = 1
			elif type == 'b' or type =='B':
				index = 2
			elif type == 'c' or type =='C':
				index = 3
			else:
				await bot.send_message(ctx.message.channel, 'Error, you can only buy from company A, B, or C. Use ***!help stocks*** if you need to see usage.')
				return
			
			found_user = False #Whether the user exists or not
			if int(amount) <= 0: #If the user tries to make a negative or zero deposit
				await bot.send_message(ctx.message.channel, 'You can\'t buy or sell a negative number of stocks. Do you understand how stocks work?')
				return
			
			#Take care of the requested option
			if option == 'b': #Buy stocks
				if get_points(ctx.message.author, ctx.message.server) >= int(amount)*int(contents[0][index]): #Make sure they have enough points to deposit
					for x in contents:
						if x[0] == str(ctx.message.author.id):
							x[index] = str(int(x[index]) + int(amount)) #give the person the amount of stocks that they asked for.
							found_user = True
					if not found_user:
						new_entry = [str(ctx.message.author.id), '0', '0', '0']
						new_entry[index] = amount
						contents.append(new_entry)
					stock_rates(ctx.message.server, 0.02)
					add_points(ctx.message.author, -1*int(amount)*int(contents[0][index]), ctx.message.server) #Now take away the points from their actual point amount
					await bot.send_message(ctx.message.channel, 'You have purchased _' + amount + '_ stocks for *' + str(int(amount)*int(contents[0][index])) + '* points.')
				
				else: #If the user did not have enough points for the purchase
					await bot.send_message(ctx.message.channel, 'You don\'t have enough points to buy that amount of stocks. Check how many points you have with **!mypoints** and the price of stocks with **!stocks**')
					return
					
			elif option == 's': #Sell stocks
					for x in contents:
						if x[0] == str(ctx.message.author.id):
							found_user = True
							if int(x[index]) >= int(amount): #Make sure there are enough stocks to sell
								x[index] = str(int(x[index]) - int(amount))
								stock_rates(ctx.message.server, -0.02)
								add_points(ctx.message.author, int(amount)*int(contents[0][index]), ctx.message.server)
								await bot.send_message(ctx.message.channel, 'I sold _' + amount + '_ of your stocks for _' + str(int(amount)*int(contents[0][index])) + '_ points.')
							else: #If the amount of stocks is less than they asked for
								await bot.send_message(ctx.message.channel, 'You don\'t have the amount of stocks you wanted to sell. Check how many stocks you have bought with **!stocks**')
								return	
					if not found_user: #If the user didn't exist
						await bot.send_message(ctx.message.channel, 'I did not find any record of stocks for you. Use ***!stocks b <company> <amount>*** to buy stocks.')
						return
			else:
				await bot.send_message(ctx.message.channel, 'Error. Use b or s for buy or sell. To see how to use !stocks, use ***!help stocks***')
				return
				
		except:
			await bot.send_message(ctx.message.channel, 'There was a problem with your stocks command. Did you use the command properly? Use ***!help stocks*** to see how to use !stocks correctly.')
			return
		
	#Write back to the file when done.
	file = open(os.path.join(sys.path[0], 'save/stocks/stocks_') + str(ctx.message.server.id) + '.txt', 'w')
	for x in contents:
		file.write(x[0] + ' ' + x[1] + ' ' + x[2] + ' ' + x[3] + '\n')
	file.close()

@bot.command(pass_context = True, description = 'Bet another user points. Winner is decided on the honesty system. Both users must bet the same amount of points.\n**Examples of usage:\n!bet 20\n!bet 50')
#!bet implementation. Allows 2 users to bet each other
async def bet(ctx, amount = None):
	if amount == None:
		await bot.send_message(ctx.message.channel, 'Please provide an amount to bet. Usage:\n***!bet <number>***')
		return
	
	try:
		if int(amount) <=0:
			await bot.send_message(ctx.message.channel, 'You can\'t bet a negative amount! Gambling does not work like that.')
			return
			
		if int(amount) > 5000:
			await bot.send_message(ctx.message.channel, 'Please make a bet less than 5000 points.')
			return
			
		if int(amount) > get_points(ctx.message.author, ctx.message.server):
			await bot.send_message(ctx.message.channel, '_You don\'t have enough points to bet that much!_ Either get more points or bet less.')
			return
		
		await bot.send_message(ctx.message.channel, '_' + str(ctx.message.author) + '_ has bet **' + amount + '** points. Type ***raise*** in the next 20 seconds to take up on this bet. The loser will have to give the winner all of the points.' )
		response = await bot.wait_for_message(timeout = 20, channel = ctx.message.channel, content = 'raise')
		if response == None:
			await bot.send_message(ctx.message.channel, 'Nobody took the offer. The bet is off.')
			return
		elif response.author == ctx.message.author:
			await bot.send_message(ctx.message.channel, '_You can\'t bet against yourself! Cancelling bet._')
			return
		else:
			await bot.send_message(ctx.message.channel, '_' + str(ctx.message.author) + '_ has bet _' + str(response.author) + '_ **' + amount + '** points.\n' + str(ctx.message.author) + ', please type **win** if you won, **lose** if you lost, or **cancel** if you would like to cancel. _Please be honest!_')
			new_response = await bot.wait_for_message(channel = ctx.message.channel, author = ctx.message.author, check = bet_check)
			if new_response == None:
				await bot.send_message(ctx.message.channel, 'Error. Cancelling bet.')
				return
			elif new_response.content == 'win':
				await bot.send_message(ctx.message.channel, 'Congrats on your victory, **' + str(ctx.message.author) + '**!')
				add_points(ctx.message.author, int(amount), ctx.message.server)
				add_points(response.author, -1*int(amount), ctx.message.server)
			elif new_response.content == 'lose':
				await bot.send_message(ctx.message.channel, 'Congrats on your victory, **' + str(response.author) + '**!')
				add_points(ctx.message.author, -1*int(amount), ctx.message.server)
				add_points(response.author, int(amount), ctx.message.server)
			elif new_response.content == 'cancel':
				await bot.send_message(ctx.message.channel, 'The bet will be cancelled. Better luck next time.')
				return
		
	except:
		await bot.send_message(ctx.message.channel, 'Did you correctly provide a number? Use ***!bet <number***')
	
#-----------------------------------BOT EVENTS and GENERAL FUNCTIONS-------------------------------	
	
@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	rand_int = np.random.randint(len(game_names))
	await bot.change_presence(game=discord.Game(name = game_names[rand_int], type = 0))
	print ('The bot is playing ' + game_names[rand_int])
	print('------\n')
	
	#Special events and days
	#Bot will post a random message on 4/20
	current_time = time.localtime() #year, month, day, hour, minute, second, weekday, year day, is daylight savings time?
	if current_time[1] == 4 and current_time[3] == 20:
		rand_int = np.random.randint(len(links420))
		msg420 = 'Happy 4/20 ' + links420[rand_int]
		for server in bot.servers: 
			# Spin through every server
			for channel in server.channels: 
				# Channels on the server
				if channel.permissions_for(server.me).send_messages:
					await bot.send_message(channel, msg420)
					# So that we don't send to every channel:
					break

	
@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await bot.send_message(general, 'Hey there! I\'m the Boogaloo bot! If you would like to see what I can do, use **!helpme**')

def load_opus_lib(opus_libs=OPUS_LIBS):
	if discord.opus.is_loaded():
		return True

	for opus_lib in opus_libs:
		try:
			discord.opus.load_opus(opus_lib)
			return
		except OSError:
			pass

	raise RuntimeError('Could not load an opus lib. Tried %s' % (', '.join(opus_libs)))	

#Add points implementation. Meaty. Adds points many points to the user given on the server given
def add_points(username, points, server): #Adds points via the points file
	#Open points file
	try:
		file = open(os.path.join(sys.path[0], 'save/points/points_') + str(server.id) + '.txt', 'r')
		file_info = file.readlines()
	except: #If stat file does not exist for the current server, create one
		file = open(os.path.join(sys.path[0], 'save/points/points_') + str(server.id) + '.txt', 'w')
		file.write(str(username.id) + ' 0\n')
		file.close()
		file = open(os.path.join(sys.path[0], 'save/points/points_') + str(server.id) + '.txt', 'r')
		file_info = file.readlines()
	
	#Format the file and then do what you need to
	content = []
	
	for x in file_info:
		content.append(x.split())
	
	del file_info
	file.close()

	#Add the points to the current score
	author_exists = False
	for x in content:
		try:
			if x[0] == str(username.id):
				x[1] = str(int(x[1]) + points)
				author_exists = True
				break
		except:
			print(content)
			return
	
	if not author_exists:
		content.append([str(username.id), str(points)])
		
	#Last, sort it
	sort_users(content)
	
	#Finish by writing back to the points file
	file = open(os.path.join(sys.path[0], 'save/points/points_') + str(server.id) + '.txt', 'w')
	for x in content:
		try:
			file.write(x[0] + ' ' + x[1] + '\n')
		except:
			print ('Error, unknown characters detected!')
	file.close()

#Sorts a list of users in descending order based on points. Uses Bubble sort, but shouldn't matter for only 20 or so items, and few re-sorts.
def sort_users(list):
	sorted = False
	temp_store = None
	while not sorted:
		sorted = True
		for x in range(len(list) - 1):
			if int(list[x][1]) < int(list[x+1][1]): #If out of order, just swap
				temp_store = list[x]
				list[x] = list[x+1]
				list[x+1] = temp_store
				sorted = False


#Returns a boolean determining whether or not the user has a positive score or not. True for positive, False for negative
def check_points(username, server):
	if get_points(username, server) <= 0:
		return False
	else:
		return True
	
#Returns how many points the user has
def get_points(username, server):
	#Open points file
	try:
		file = open(os.path.join(sys.path[0], 'save/points/points_') + str(server.id) + '.txt', 'r')
		file_info = file.readlines()
	except: #If stat file does not exist for the current server, create one
		file = open(os.path.join(sys.path[0], 'save/points/points_') + str(server.id) + '.txt', 'w')
		file.write(str(username.id) + ' 0\n')
		file.close()
		file = open(os.path.join(sys.path[0], 'save/points/points_') + str(server.id) + '.txt', 'r')
		file_info = file.readlines()
	
	#Format the file and then do what you need to
	content = []
	
	for x in file_info:
		content.append(x.split())
	
	#found how many points they have
	for x in content:
		if x[0] == str(username.id):
			return int(x[1])
	
	return 0

#Open a loss file and coundt how mnay losses the person has used
def add_loss(username, server): #Adds points via the points file
	#Open loss file
	current_time = time.localtime()
	date_string = os.path.join(sys.path[0], 'save/loss/loss.') + str(current_time[0]) + '.' + str(current_time[1]) + '.' + str(current_time[2]) + '.txt'
	
	try:
		file = open(date_string, 'r')
		file_info = file.readlines()
	except: #If loss file for day does not exist for the current server, create one
		clear_loss()
		file = open(date_string, 'w')
		file.write(str(username.id) + ' 0\n')
		file.close()
		file = open(date_string, 'r')
		file_info = file.readlines()
	
	#Format the file and then do what you need to
	content = []
	
	for x in file_info:
		content.append(x.split())
	
	del file_info
	file.close()

	#Add the points to the current score
	author_exists = False
	for x in content:
		try:
			if x[0] == str(username.id):
				x[1] = str(int(x[1]) + 1)
				author_exists = True
				break
		except:
			return
	
	if not author_exists:
		content.append([str(username.id), '1'])
	
	#Finish by writing back to the loss file
	file = open(date_string, 'w')
	for x in content:
		try:
			file.write(x[0] + ' ' + x[1] + '\n')
		except:
			print ('Error writing to today\'s loss file.')
			print(content)
	file.close()	
	
#Returns a how many losses the person has used today
def get_loss(username, server):
	current_time = time.localtime()
	date_string = os.path.join(sys.path[0], 'save/loss/loss.') + str(current_time[0]) + '.' + str(current_time[1]) + '.' + str(current_time[2]) + '.txt'

	#Open loss file
	try:
		file = open(date_string, 'r')
		file_info = file.readlines()
	except: #If today's loss file does not exist for the current server, create one
		file = open(date_string, 'w')
		file.write(str(username.id) + ' 0\n')
		file.close()
		file = open(date_string, 'r')
		file_info = file.readlines()
	
	#Format the file and then do what you need to
	content = []
	
	for x in file_info:
		content.append(x.split())
	
	#Found how many losses they have
	for x in content:
		if x[0] == str(username.id):
			return int(x[1])
	
	return 0	

#Returns a boolean based for the bomb game on whether the input was good or not
def bomb_check(msg):
	try:
		countdown = int(msg.content)
		if (countdown <= 0 or countdown > 10) and not countdown == 56:
			return False
		else:
			return True
	except:
		#await bot.send_message(msg.channel, 'Error. Was that a number you gave me?')
		return False

#Returns a boolean based for the auction on whether the input is fine
def auction_check(msg):
	try:
		bet = int(msg.content)
		if bet <= 0:
			return False
		else:
			return True
	except:
		return False		
		
#Returns a boolean for the rock, paper, scissors game for whether a valid choice was given.	
def rps_check(msg):
	try:
		if msg.content == 'rock' or msg.content == 'paper' or msg.content == 'scissors' or msg.content == 'Rock' or msg.content == 'Paper' or msg.content == 'Scissors':
			return True
		return False
	except:
		return False

#Returns a boolean to determine a valid message for the ab game.
def ab_check(msg):
	try:
		if msg.content == 'ally' or msg.content == 'betray':
			return True
		else:
			return False
	except:
		return False

#Returns a boolean for valid music commands		
def player_check(msg):
	if msg.content == '#pause' or msg.content == '#skip':
		return True
	else:
		return False

#Check for the !bet command
def bet_check(msg):
	if msg.content == 'win' or msg.content == 'lose' or msg.content == 'cancel':
		return True
	else:
		return False
		
#Interest function for bank. Gives each amount in the bank the interest rate of the argument, and the server to do it to
def interest(rate, server):
	#Try to open the file first
	try:
		file = open(os.path.join(sys.path[0], 'save/bank/bank_') + str(server.id) + '.txt', 'r')
	except: #If the file does not exist
		return
		
	#Read the file information
	file_contents = file.read().splitlines() #Gets rid of any line feeds. Make sure to put them back later.
	file.close()
	contents = []
	for x in file_contents:
		contents.append(x.split())
	del file_contents
	
	#Go through all of the accounts and adjust the amounts
	file = open(os.path.join(sys.path[0], 'save/bank/bank_') + str(server.id) + '.txt', 'w')
	for x in contents:
		x[1] = str(math.ceil(int(x[1])*(1+rate)))
		file.write(x[0] + ' ' + x[1] + '\n')
	file.close()

#Function to adjust stock rates
def stock_rates(server, seed):
	#Try to open the file first
	try:
		file = open(os.path.join(sys.path[0], 'save/stocks/stocks_') + str(server.id) + '.txt', 'r')
	except: #If the file does not exist
		file = open(os.path.join(sys.path[0], 'save/stocks/stocks_') + str(server.id) + '.txt', 'w')
		file.write('stocks 15 25 10\n')
		file.close()
		file = open(os.path.join(sys.path[0], 'save/stocks/stocks_') + str(server.id) + '.txt', 'r')
		
	#Read the file information
	file_contents = file.read().splitlines() #Gets rid of any line feeds. Make sure to put them back later.
	file.close()
	contents = []
	for x in file_contents:
		contents.append(x.split()) #Each member will contain 4 members, being id, amount of a, amount of b, amount of c, respeectively
	del file_contents
	
	#Adjust the stock rates, randomly decide what rate to go with
	rate = (0.8434**int(contents[0][1])+np.random.random_sample()*(int(contents[0][1])/400))*np.sin(2*np.pi*np.random.random_sample()) + seed
	if int(contents[0][1]) < 10:
		rate += 0.02
	elif int(contents[0][1]) > 125:
		rate -= 0.02
	contents[0][1] = str(int(round((1 + rate)*int(contents[0][1]), 0))) #Adjust the rate of stock A
	if int(contents[0][1]) < 3:
		contents[0][1] = '3'
	elif int(contents[0][1]) > 200:
		contents[0][1] = '200'
		
	rate = (0.8736**int(contents[0][2])+np.random.random_sample()*(int(contents[0][2])/375))*np.sin(2*np.pi*np.random.random_sample()) + seed
	if int(contents[0][1]) < 15:
		rate += 0.05
	elif int(contents[0][1]) > 100:
		rate -= 0.04
	contents[0][2] = str(int(round((1 + rate)*int(contents[0][2]), 0))) #Adjust the rate of stock B
	if int(contents[0][2]) < 3:
		contents[0][2] = '3'
	elif int(contents[0][2]) > 200:
		contents[0][2] = '200'
		
	rate = (0.8193**int(contents[0][3])+np.random.random_sample()*(int(contents[0][3])/425))*np.sin(2*np.pi*np.random.random_sample()) + seed
	if int(contents[0][1]) < 6:
		rate += 0.03
	elif int(contents[0][1]) > 150:
		rate -= 0.04
	contents[0][3] = str(int(round((1 + rate)*int(contents[0][3]), 0))) #Adjust the rate of stock C
	if int(contents[0][3]) < 3:
		contents[0][3] = '3'
	elif int(contents[0][3]) > 200:
		contents[0][3] = '200'
	
	#Write back to the file
	file = open(os.path.join(sys.path[0], 'save/stocks/stocks_') + str(server.id) + '.txt', 'w')
	for x in contents:
		file.write(x[0] + ' ' + x[1] + ' ' + x[2] + ' ' + x[3] + '\n')

async def play_music(message, link, URL = True):
	if link == None:
		return
		
	first_play = True	
	
	await bot.send_message(message.channel, '_Starting music..._\nType ***#pause*** to pause at any point _or_ ***#skip*** to skip a song.\nSometimes the bot may not read the command the first time, so try again if it doesn\'t work.')
	
	try:
		file = open(os.path.join(sys.path[0], 'music/') + str(message.server.id) + '.txt', 'r')
	except:
		file = open(os.path.join(sys.path[0], 'music/') + str(message.server.id) + '.txt', 'w')
		file.close()
		file = open(os.path.join(sys.path[0], 'music/') + str(message.server.id) + '.txt', 'r')
		
	music_queue = file.read().splitlines()
	file.close()
	
	load_opus_lib()
	voice_channel = message.author.voice.voice_channel
	try:
		connected = await bot.join_voice_channel(voice_channel)
	except:
		await bot.send_message(message.channel, 'The bot should already be playing music, or you are not in a voice channel. Please use **!add** while in a voice channel to add music.')
		return
		
	if URL:
		player = await connected.create_ytdl_player(link)
	else:
		player = connected.create_ffmpeg_player(os.path.join(sys.path[0], 'audio/') + link, after = await do_nothing(connected))
	try:
		while connected.is_connected():
			if 'Fire Emblem' in str(player.title) or 'anime' in str(player.title) or 'Naruto' in str(player.title):
				await bot.send_message(message.channel, 'Oh. Some weeb added _' + str(player.title) + '_\n')
			else:
				await bot.send_message(message.channel, '**Now playing:** _' + str(player.title) + '_\n')
			player.start()
			player.volume = VOLUME
			while not player.is_done():
				response = await bot.wait_for_message(timeout = 1, check = player_check)
				try:
					if response.content == '#pause':
						player.pause()
						await bot.send_message(message.channel, 'Music paused. Type **#resume** to resume the music.')
						response2 = await bot.wait_for_message(content = '#resume')
						try:
							if response2.content =='#resume':
								player.resume()
						except:
							pass
					elif response.content == '#skip':
						await bot.send_message(message.channel, '_Skipping song..._')
						player.stop()
				except:
					pass
				
			#Update the music queue now that the player is done.
			try:
				file = open(os.path.join(sys.path[0], 'music/') + str(message.server.id) + '.txt', 'r')
				music_queue = file.read().splitlines()
				file.close()
			except:
				pass
			
			if not first_play:
				try:				
					del music_queue[0]
					#Update the music_queue file after it has been changed
					file = open(os.path.join(sys.path[0], 'music/') + str(message.server.id) + '.txt', 'w')
					for y in music_queue:
						file.write(y + '\n')
					file.close()
				
				except:
					pass
			
			else:
				first_play = False
				
			if music_queue:
				del player
			try:
				player = await connected.create_ytdl_player(music_queue[0])
			except TimeoutError:
				await bot.send_message(message.channel, 'The music player has timed out')
				return
			except:
				file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_musiclist.txt'), 'r')	
				file_info = file.readlines()
				
				del_index = 0
				sub = False
				sub_msg = music_queue[0] + '\n'
				count = 0
				for x in file_info:
					if x == sub_msg:
						del_index = count
						sub = True
					count += 1
					
				if sub: #If remove should be performed
					file.close()
					file = open(os.path.join(sys.path[0], 'save/pinlists/' + str(ctx.message.server.id) + '_musiclist.txt'), 'w')
					count = 0
					for x in file_info:
						if count != del_index:
							file.write(x)
						count += 1
						
				await bot.send_message(ctx.message.channel, 'Error with link: ' + sub_msg + '_Deleting from music list..._')

				del music_queue[0]
				
				#Update the music_queue file after it has been changed
				file = open(os.path.join(sys.path[0], 'music/') + str(message.server.id) + '.txt', 'w')
				for y in music_queue:
					file.write(y + '\n')
				file.close()
				
				print('Music queue is empty')
				if music_queue:
					del player
				print('Music player trying: ' + music_queue[0])
				try:
					player = await connected.create_ytdl_player(music_queue[0])
				except:
					await bot.send_message(message.channel, 'The music player has player has encountered 2 consecutive errors. Leaving voice channel...')
					await disconnect_from(connected)
					return
			
	except:
		print('Error in playing music.')
		print('Link is ' + str(link))
		print('URL is ' + str(URL))
		try:
			await disconnect_from(connected)
			print('The link provided is ' + str(link))
		except:
			print('Could not figure out the link. Or possible trouble with disconnecting')
	
	await disconnect_from(connected)

	
#Disconnect from the voice channel
async def disconnect_from(voice_channel):
	await voice_channel.disconnect()
		
#Do nothing. Not currently used. 
async def do_nothing(voice_channel):
	while player.is_playing():
			await asyncio.sleep(1)
			if player.is_done():	
				break
	disconnect_from(connected)

#Removes old loss files.
def clear_loss():
	current_time = time.localtime()
	
	#Now, try to remove all beds from this month up to today
	for y in range(current_time[1]+1): #Deletes all loss files created within this year up to today.
		for x in range(current_time[2]+1):
			try:
				date_string = os.path.join(sys.path[0], 'save/loss/loss') + str(current_time[0]) + '.' + str(y) + '.' + str(x) + '.txt'
				os.remove(date_string)
			except:
				pass
	
#Removes old bed files.
def clear_beds():
	current_time_og = time.localtime()
	#Fix a bug with overwriting the current time correctly.
	current_time = []
	current_time.append(current_time_og[0])
	current_time.append(current_time_og[1])
	try:
		if current_time_og[3] <= 2: #If it is before 2AM, count it towards today's bed
			current_time.append(current_time_og[2] - 1)
		else:
			current_time.append(current_time_og[2])
	except:
		print ('Error trying to convert time in clear_beds function.\n')
	
	#Now, try to remove all beds from this month up to today
	for y in range(current_time[1]+1): #Deletes all bed files created within this year.
		for x in range(current_time[2]):
			try:
				date_string = os.path.join(sys.path[0], 'save/beds/bed.') + str(current_time[0]) + '.' + str(y) + '.' + str(x) + '.txt'
				os.remove(date_string)
			except:
				pass

#Removes old bed files.
def clear_good_mornings():
	current_time = time.localtime()
	
	#Now, try to remove all good_mornings from this month up to today
	for y in range(current_time[1]+1): #Deletes all bed files created within this year.
		for x in range(current_time[2]):
			try:
				date_string = os.path.join(sys.path[0], 'save/goodmorning.') + str(current_time[0]) + '.' + str(y) + '.' + str(x) + '.txt'
				os.remove(date_string)
			except:
				pass				
				
#Removes old card files.
def clear_cards(ctx):
	current_time = time.localtime()
	
	#Now, try to remove all beds from this month up to today
	for y in range(current_time[1]+1): #Deletes all card files created within this year.
		for x in range(current_time[2]):
			try:
				date_string = os.path.join(sys.path[0], 'save/card/card_') + str(ctx.message.server.id) + '_' + str(current_time[0]) + '.' + str(y) + '.' + str(x) + '.txt'
				os.remove(date_string)
			except:
				pass
				
def get_prestige(author):
	global prestiges
	role_name = None
	for x in prestiges:
		if x in author.roles:
			role_name = x
			return role_name
				
#Removes old chance files				
def clear_chance(ctx):
	current_time = time.localtime() #year, month, day, hour, minute, second, weekday, year day, is daylight savings time?
	
	for y in range(current_time[1]+1): #Deletes all bed files created within this year.
		for x in range(current_time[2]):
			try:
				del_file = os.path.join(sys.path[0], 'save/chance/') + str(ctx.message.server.id) + '_' + str(current_time[0]) + '.' + str(y) + '.' + str(x) + '.txt'
				if os.path.isfile(del_file):
					os.remove(del_file)
			except:
				print(del_file)
				pass
	
bot.run(TOKEN)
