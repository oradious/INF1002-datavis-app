import csv, json

fileName = input("Please enter the name of the file you wish to open: ")

def readText(fileName):
    with open(fileName) as data:
        content = data.read()
        return content
    
contents = readText(fileName)
print(contents)