from flask import Flask, render_template, request, redirect
from dash import dash, html, dash_table, dcc, Output, Input
import pandas as pd
import plotly.express as px
import  base64
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Secret key for Flask'

df = None

#Home page
@app.route('/', methods=['GET','POST'])
def movie_main():
    global df
    if request.method == 'POST':
        file = request.files.get('file')
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file, encoding="latin-1")
        elif file.filename.endswith('.json'):
            df = pd.read_json(file)
        
            movies_data = df['data'].tolist()
            
            movie_list = []
            for movie_data in movies_data:
                title = movie_data.get('title', 'N/A')
                overview = movie_data.get('plot', 'N/A')
                vote_average = movie_data.get('rating', 'N/A')
                

                #Get Directors name 
                director_data = movie_data.get('directors', [{}])[0].get('data', {})
                director_name = director_data.get('name', 'N/A')

                #Put a commna between the genres on the table
                genres = movie_data.get('genres',[])
                genres_seperate  = ','.join(genres)

                #Get Votes
                votes = movie_data.get('votes','N/A')


                
                #Decide what to display on the table when uploading json file
                movie_list.append({'title': title, 
                                   'Description': overview, 
                                   'rating': vote_average, 
                                   'genres':genres_seperate,
                                   'directors': director_name,
                                   'votes' : votes,})
            df=pd.DataFrame(movie_list)

        else:
            return "Unsupported file type"
        return redirect('/plot/')  #direct to /plot to display table&graph
    return render_template('home.html')  

# Dash Setup for displaying graph

dash_app = dash.Dash(__name__, server=app, url_base_pathname='/plot/')

#Config of the graph and table
def graph_layout():
    global df
    if df is None:
        return html.Div("Please upload a file.")
    else:
        
       
        df_sorted = df.sort_values(by="title" if 'title' in df.columns else df.columns[0]) 
        
        # Get specific genres from the DF 
        genres = df_sorted['genres'].explode().unique() if 'genres' in df_sorted.columns else[]
        
        return html.Div([
            html.Div(children='Movie with Data', style={'fontFamily': 'Courier New', 'fontSize': 45, 'textAlign': 'center'}),
            #To change the y axis labels
            
            
            dcc.RadioItems(options=[{'label': 'Directors', 'value': 'directors'}, {'label': 'Title', 'value': 'title'}],value='title', id='controls-and-radio-item'),
            
            #To change the x axis labels
            dcc.RadioItems(options=[{'label':'Rating','value':'rating'},{'label':'votes','value':'votes'}],value='rating',id='xaxis_change'),
            
            
            dcc.Dropdown(
                id='genre-dropdown',
                options=[{'label': genre, 'value': genre} for genre in genres],
                multi=False,
                placeholder='Select genre(s)'
            ),
            
            
            dash_table.DataTable(data=df_sorted.to_dict('records'),
                                 columns=[{"name": i, "id": i} for i in df_sorted.columns], 
                                 page_size=5, style_cell={'textAlign': 'center', 'width': '100px','overflow':'hidden','textOverflow':'ellipsis','maxWidth':0},
                                 
                                 
                                 #allow user to hover over the table and read the full content
                                 tooltip_data=[{column:{'value':str(value),'type':'markdown'}
                                                for column,value in row.items()
                                                }for row in df_sorted.to_dict('records')],
                                                tooltip_duration =None,
                                 
                                 #allow user to filter the content of the table
                                 filter_action="native",sort_action="native",id='movie-table'),
            
            dcc.Graph(figure={}, id='controls-and-graph'),
            
            html.Button('Download CSV', id='download-csv-button'),#a button for CSV download
            dcc.Download(id="download-csv"),
            
            
            html.Button('Download JSON', id='download-json-button'),#a button for JSON download
            dcc.Download(id="download-json")
            
        ])

@dash_app.callback(
    Output('movie-table', 'data'),
    Input('genre-dropdown', 'value'),
    prevent_initial_call=True
)
def update_table_by_genre(selected_genre):
    global df
    if not selected_genre:
        raise PreventUpdate
    
    filtered_df = df[df['genres'].apply(lambda x: selected_genre in x)]
    return filtered_df.to_dict('records')

def update_table(contents):
    global df
    if contents is None:
        raise PreventUpdate

    content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    try:
        df = pd.read_json(decoded)

        
        data_df = df.get('data', {})
        
      
        if isinstance(data_df, pd.DataFrame):
            df_sorted = data_df.sort_values(['title', 'genres'])
            return df_sorted.to_dict('records')
        else:
            print("JSON structure is wrong.")
            return []
    except Exception as e:
        print(e)
        return []

def serve_layout():
        return graph_layout()
dash_app.layout = serve_layout

@dash_app.callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    [Input(component_id='controls-and-radio-item', component_property='value'),
     Input(component_id='movie-table', component_property='data'),
     Input(component_id='xaxis_change',component_property='value')
    ]
)

def update_graph_axis(col_chosen, table_data,xaxis_change):
    if not table_data:
        raise PreventUpdate
        


    
    # Change ratings from object to int/float then 
    df_filtered = pd.DataFrame(table_data)
    df_filtered[xaxis_change] = pd.to_numeric(df_filtered[xaxis_change], errors='coerce')
    
    #Remove the movies with no data as the movie is not released yet
    df_filtered=df_filtered.dropna(subset=[xaxis_change])
    
    #get the average rating if the director has directed more than one movie in the csv/json file 
    df_group_by_ratings=df_filtered.groupby(col_chosen)[xaxis_change].mean().reset_index()
    
    #Set the ratings in the graph so that the highest rating movie/director is on top
    df_group_by_ratings=df_group_by_ratings.sort_values(by=xaxis_change,ascending=True)

    if df_filtered is not None:
        try:

            fig = px.bar(df_group_by_ratings, x=xaxis_change, y=col_chosen, title=f"Ratings by {col_chosen}")
            fig.update_layout(height=1000, width=1000)
            
            
            return fig
        except Exception as e:
            print(f"Error updating graph: {e}")
    return {}

#Functions for downloading CSV and JSON File
@dash_app.callback(
    Output('download-csv', 'data'),
    Input('download-csv-button', 'n_clicks'),
    Input('movie-table','data'),
    prevent_initial_call=True
)
def generate_csv(n_clicks,table_data):
    if n_clicks:
        df_download =pd.DataFrame(table_data)
    
    return dcc.send_data_frame(df_download.to_csv, "Movies_dataset.csv")

@dash_app.callback(
    Output('download-json', 'data'),
    Input('download-json-button', 'n_clicks'),
    Input('movie-table','data'),
    prevent_initial_call=True
)
def generate_json(n_clicks,table_data):
    if n_clicks:
        df_download=pd.DataFrame(table_data)
    return dcc.send_data_frame(df_download.to_json,"Movies_dataset.json")

if __name__ == '__main__':
    app.run(debug=True)






