def fileContents(file):
	f = open(file, "r")
	return(f.read())

def writeToFile(file, text):
	f = open(file, "a")
	f.write(text)
	f.close()