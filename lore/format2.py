file = open('F:\Discord bot\TestBot\kirbyout.txt', 'r')
file_contents = file.readlines()
new_contents = []
file.close()
for x in file_contents:
	if x != '\n':
		new_contents.append(x)
file = open('F:\Discord bot\TestBot\kirbyout2.txt', 'w')
for x in new_contents:
	file.write(x)
file.close()