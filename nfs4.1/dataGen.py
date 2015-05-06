f = open("data.txt",'w')

for i in range(0,100000000):
	if(i%2):
		f.write("abcdefghij")
	else:
		f.write("klmnopqrst")

