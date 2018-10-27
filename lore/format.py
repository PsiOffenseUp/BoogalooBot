file = open('F:\Discord bot\TestBot\lore\\snk.txt', 'r')
file_contents = file.readlines()
new_contents = []
file.close()
for x in file_contents:
	new_name = ''
	for y in x:
		if y!= '\t':
			new_name += y
		else:
			new_name += '\n'
	new_contents.append(new_name)

file = open('F:\Discord bot\TestBot\kirbyout.txt', 'w')
for x in new_contents:
	file.write(x)