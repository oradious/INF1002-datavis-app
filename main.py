import csv, json as jn, pandas as pd, os, matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, url_for, jsonify

templateDir = str(os.getcwd())

app = Flask(__name__, template_folder = templateDir)

def json_to_table(data, columns_to_display=None, sort_column=None):
    if not data:
        return "<p>No data to display</p>"

    if not columns_to_display:
        return "<p>No columns specified for display</p>"

    # Check if a sort column is specified
    if sort_column:
        # Sort the data based on the specified column
        data.sort(key=lambda entry: float(entry['data'].get(sort_column, '0')), reverse = True)

    # Create the HTML table
    table_html = '<table class="table table-bordered table-striped">'
    table_html += '<thead><tr>'

    for col in columns_to_display:
        table_html += f'<th>{col}</th>'

    table_html += '</tr></thead><tbody>'

    for entry in data:
        table_html += '<tr>'
        for col in columns_to_display:
            value = entry['data'].get(col, "")
            # Check if value is a list with a single element, and extract it
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            table_html += f'<td>{value}</td>'
        table_html += '</tr>'

    table_html += '</tbody></table>'
    return table_html


def generate_bar_graph(data, sort_column=None):
    if not data:
        return None

    if sort_column:
        data.sort(key=lambda entry: float(entry['data'].get(sort_column, '0')), reverse = True)
        
    # Retrieving only the top 20 data
    df20 = data[:20]
    
    # Extract data from the column 'rating' for the y-axis
    y_column = []
    for entry in df20:
        rating = entry['data'].get('rating', '0')
        # Convert rating to float if it's numeric
        try:
            rating = float(rating)
        except ValueError:
            rating = 0.0  # Default value for non-numeric ratings
        y_column.append(rating)

    # Extract data from the column 'title' for the x-axis
    x_column = [entry['data'].get('title', 'Unknown') for entry in df20]

    # Create the bar graph
    plt.figure(figsize=(12, 10))
    plt.bar(x_column, y_column)
    plt.xlabel('Titles')
    plt.ylabel('Rating')
    plt.title('Top 20 Movie Titles')
    plt.xticks(rotation=90)  # Rotate x-axis labels for better visibility
    plt.subplots_adjust(bottom = 0.5)  # Adjust the bottom margin

    # Save the graph
    img_path = os.path.join('static', 'top20movies.png')
    plt.savefig(img_path)
    return img_path

@app.route('/')
def data_query():
    return render_template('index.html')

@app.route('/result', methods = ['GET', 'POST'])
def data_result():
    if request.method == 'POST':
        fileName = request.form['file_name']

    # Check if file is a CSV file or JSON file
    if fileName.endswith('.csv'):
        contents = pd.read_csv(fileName)
        contents = contents.sort_values(by = contents.columns[4], ascending = False)
        return render_template('result.html', file_name = fileName, table = contents.to_html(classes='table table-bordered table-striped'))
    elif fileName.endswith('.json'):
        try:
            with open(fileName, 'r') as jsonFile:
                contents = jn.load(jsonFile)
                print(contents)
        except:
            return "Error: Invalid JSON file"
        
        # Specifying the columns to display in table
        columns_to_display = ["title", "year", "genres", "votes", "rating"]
        
        table_html = json_to_table(contents, columns_to_display, sort_column = 'rating')
        print(table_html)
            
        return render_template('result.html', file_name = fileName, table = table_html)
    else:
        return "Invalid file type"
    
    
@app.route('/plot/<fileName>')
def plot(fileName):
    if fileName.endswith('.csv'):    
        print(fileName)
        contents = pd.read_csv(fileName)
        contents = contents.sort_values(by = contents.columns[4], ascending = False)
        df20 = contents.iloc[:20]
    
        # Setting the columns for graph plotting
        x_column = 'title'
        y_column = 'rating'

        plt.figure(figsize = (12, 10))
        plt.bar(df20[x_column], df20[y_column])
        plt.xlabel('Titles')
        plt.ylabel('Ratings')
        plt.title('Top 20 Movie Titles')  # Change the title to indicate it's a bar plot
        plt.xticks(rotation = 90)  # Rotate x-axis labels for readability
        plt.subplots_adjust(bottom = 0.5)  # Adjust the bottom margin

        img_path = os.path.join('static', 'top20movies.png')
        plt.savefig(img_path)
        plt.close()

        return render_template('graph.html', img_path = img_path)
    
    if fileName.endswith('.json'):
        try:
            with open(fileName, 'r') as jsonFile:
                contents = jn.load(jsonFile)
        except:
            return "Error: Invalid JSON file"
        
        graph = generate_bar_graph(contents, sort_column = 'rating')
        return render_template('graph.html', img_path = graph)
            
if __name__ == '__main__':
    app.run()