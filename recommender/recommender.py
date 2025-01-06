import pandas as pd
import numpy as np
import random

# Loading preprocessed data
data = pd.read_csv("data/movies.csv")

movie_titles = data['title'].tolist()
movie_genres = data['genres'].tolist()

# Function to find similarity between genres list
def genre_similarity(list1, list2):
    s1 = set(list1)
    s2 = set(list2)
    intersection = len(s1.intersection(s2))
    union = len(s1.union(s2))
    return intersection / union if union != 0 else 0

# Function to find similarity between movies
def movie_similarity(movie1_id, movie2_id, genre_weight = 0.4, vote_weight = 0.3,  popularity_weight = 0.2, language_weight = 0.1):
    genre = genre_similarity(movie_genres[movie1_id], movie_genres[movie2_id]) * genre_weight
    language = language_weight if data['original_language'].iloc[movie1_id] == data['original_language'].iloc[movie2_id] else 0
    vote = data['vote_average'].iloc[movie2_id] * vote_weight
    popularity = data['popularity'].iloc[movie2_id] * popularity_weight * 0.01
    # total_similarity = genre + language + vote + popularity
    total_similarity = genre + language + vote
    return total_similarity

# Function to get top N recommendations based on single movie
def get_recommendations(movie_title, top_n = 10, score = False):
    if not isinstance(movie_title, str):
        return "Error: Movie title must be a string."

    try:
        movie_index = movie_titles.index(movie_title)
    except ValueError:
        return f"Error: '{movie_title}' not found in the dataset."
    
    similarities = [[i, movie_similarity(movie_index, i)] for i in range(len(movie_titles)) if i != movie_index]
    similarities.sort(key = lambda x: x[1], reverse = True)

    recommendations = similarities[:top_n]

    for i in range(len(recommendations)):
        recommendations[i][0] = movie_titles[recommendations[i][0]]
    
    if not score:
        recommendations = [recommendations[i][0] for i in range(len(recommendations))]
    
    return recommendations

# Function to get top N recommendations based on many movies
def get_recommendations_many(movie_list, top_n = 10):
    selected_movies = []
    to_be_selected = 5
    if len(movie_list) >= 5:
        selected_movies = random.sample(movie_list, to_be_selected)
    else:
        selected_movies = movie_list
    
    all_recommendations = set()
    for movie in selected_movies:
        current_rec = set(get_recommendations(movie, top_n))
        all_recommendations.update(current_rec)

    if len(all_recommendations) < top_n:
        return list(all_recommendations)
    else:
        recommendations = random.sample(all_recommendations, top_n)
        return recommendations