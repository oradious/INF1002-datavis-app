import csv, json

fileName = input("Please enter the name of the file you wish to open: ")

def fileType(fileName):
    length = len(fileName)
    fileFormat = fileName[length - 4:]
    return fileFormat

def readText(fileName):
    with open(fileName) as data:
        content = data.read()
        return content
    
def readCSV(fileName):
    with open(fileName, newline = '') as data:
        content = csv.reader(data)
        for row in content:
            print(', '.join(row))

fileFormat = fileType(fileName)

if fileFormat == '.txt':
    contents = readText(fileName)
    contents += "\n I have edited this file"
    print(contents)
elif fileFormat == '.csv':
    readCSV(fileName)
elif fileFormat == 'json':
    exit()
else:
    exit(print("Invalid file type"))