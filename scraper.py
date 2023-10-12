from imdb import Cinemagoer
import json
import csv

#web scraper built by Caleb Lee (2301831), making use of the Cinemagoer API
#custom JSON Encoder, since type Movie in list is not JSON serializable
class MovieEncoder(json.JSONEncoder):
    def default(self, obj):
        #handle objects with __dict__ attribute
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        #handle objects that are list or tuples
        elif isinstance(obj, (list,tuple)):
            return [self.default(item) for item in obj]
        #handle objects that are strings
        else:
            return str(obj)

# create an instance of the Cinemagoer class
ia = Cinemagoer()

genre = 'Action'
top50_movies = ia.get_top50_movies_by_genres(genre)

with open(f'movie_genre_{genre}.json', 'w') as jsonfile:
    #jsonfile.write(convertjson)
    #dump method instead of dumps since we are writing the json data to file, not a json string
    json.dump(top50_movies, jsonfile, cls=MovieEncoder, indent=4)

csv_filename=f'movie_genre_{genre}.csv'

# Define the column order as a list
csv_column_order = ['title', 'year', 'genres', 'votes', 'rating', 'runtimes', 'certificates', 'cast', 'directors', 'plot']

with open(csv_filename, mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_column_order)
    writer.writeheader()

    for movie in top50_movies:
        # Provide default values for 'votes' and 'rating' if not present
        movie_data = {
            'title': movie.get('title', ''),
            'year': movie.get('year', ''),
            'genres': ', '.join(movie.get('genres', [])),  # Convert genres to a comma-separated string
            'votes': movie.get('votes', ''),
            'rating': movie.get('rating', ''),
            'runtimes': ', '.join(movie.get('runtimes', [])), # Convert runtime to a comma-separated string, it is in a list for some reason
            'certificates': ', '.join(movie.get('certificates', [])), #Certificates here refer to ratings like PG-13, M18, etc
            'cast': ', '.join(actor['name'] for actor in movie.get('cast', [])), #Extract cast names from cast list
            'directors': ', '.join(director['name'] for director in movie.get('directors', [])), #Extract director name from director list
            'plot': movie.get('plot', '')
        }
        writer.writerow(movie_data)