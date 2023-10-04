import csv, json as jn, pandas as pd, os
from flask import Flask, render_template, request

templateDir = str(os.getcwd())
print(templateDir)

app = Flask(__name__, template_folder = templateDir)

@app.route('/')
def data_query():
    return render_template('index.html')

@app.route('/result', methods = ['GET', 'POST'])
def data_result():
    if request.method == 'POST':
        fileName = request.form['file_name']

    def fileType(fileName):
        length = len(fileName)
        fileFormat = fileName[length - 4:]
        return fileFormat

    def readText(fileName):
        with open(fileName) as data:
            content = data.read()
            return content
    
    def readCSV(fileName):
        content = pd.read_csv(fileName)
        content = content.drop(['adult', 'belongs_to_collection', 'budget', 'homepage', 'id', 'imdb_id', 'original_title', 'poster_path', 'production_countries', 'revenue', 'spoken_languages', 'status', 'tagline', 'video'], axis =1)
        return content

    def writeText(dB, exportName):
         exit()
     
    def writeCSV(dB, exportName):
        dB.to_csv(exportName, index = False)

    fileFormat = fileType(fileName)

    if fileFormat == '.txt':
        contents = readText(fileName)
        return render_template('result.html', tables = [contents.to_html()], titles = [''])
    elif fileFormat == '.csv':
        contents = readCSV(fileName)
        print(contents)
        return render_template('result.html', tables = [contents.to_html()], titles = [''])
    elif fileFormat == 'json':
        exit()
    else:
        return "Invalid file type"
    
    #ynExport = input("Would you like to export the data? (Y/N): ")

    #if (ynExport == 'Y') or (ynExport == 'y') or (ynExport == 'yes') or (ynExport == 'Yes'):
    #    exportFormat = input("What format would you like to export to (csv, txt, json): ")
    #    exportName = input("Please enter the file name: ")
    #    if (exportFormat == 'csv'):
    #        writeCSV(contents, exportName)
    #    elif (exportFormat == 'txt'):
    #        writeText(contents, exportName)
    #else:
    #    exit()
            
if __name__ == '__main__':
    app.run() 