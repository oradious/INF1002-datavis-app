from imdb import Cinemagoer
import csv

#test environment for the scraper to write to CSV, by Caleb Lee (2301831)
ia = Cinemagoer()

top50_movies = ia.get_top50_movies_by_genres('Action')
csv_filename = 'movie_genre_actiontest2.csv'

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

print(f'Data written to {csv_filename}')
