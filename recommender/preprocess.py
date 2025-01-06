import numpy as np
import pandas as pd

# Loading data
movies = pd.read_csv("data/full_movies_dataset.csv")

# Filtering out unreleased and non-voted movies
movies = movies[(movies['status'] == 'Released') & (movies['vote_count'] > 0)]
print(movies[movies['title'] == ''])

# Selecting required columns
data = movies.loc[:, ['id', 'title', 'genres', 'original_language', 'vote_average', 'vote_count', 'popularity', 'release_date']]
# Dropping rows with NULL values
data = data.dropna()
# Changing index to id of movies and sorting rows according to index
data.sort_index(inplace = True)
data.sort_values(by = 'title', ascending = True, inplace = True)

# Function to convert comma separated strings to lists
def to_list(value):
    if isinstance(value, str):
        return value.split(',') if value else []
    else:
        raise(ValueError)
# Function to change list values into lowercase and strip blankspaces from the individual values
def clean(x):
    if isinstance(x, list):
        return [str.lower(i.strip()) for i in x]
    else:
        return []

# Applying the functions to genres column
data['genres'] = data['genres'].apply(to_list)
data['genres'] = data['genres'].apply(clean)

# Scaling the values of popularity column
data['popularity'] = ((data['popularity'] - data['popularity'].mean()) / data['popularity'].std()).round(1)

# Saving the dataset
# data.to_csv("data/movies.csv", index = False)