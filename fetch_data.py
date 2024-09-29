import requests
import pandas as pd
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Your TMDB API key
api_key = os.getenv('TMDB_API_KEY')
base_url = 'https://api.themoviedb.org/3'
image_base_url = 'https://image.tmdb.org/t/p/w500/'

# Create a folder to save the data if it doesn't exist
os.makedirs('data', exist_ok=True)

# Fetch genres for movies
def fetch_genres(media_type='movie'):
    url = f'{base_url}/genre/{media_type}/list?api_key={api_key}'
    response = requests.get(url)

    if response.status_code == 200:
        genre_data = response.json()['genres']
        return {genre['id']: genre['name'] for genre in genre_data}
    else:
        print(f"Failed to fetch genres: {response.status_code}")
        return {}

# Fetch popular movies and series data
def fetch_media_data(media_type='movie', page_limit=10):
    all_data = []
    for page in range(1, page_limit + 1):
        url = f'{base_url}/{media_type}/popular?api_key={api_key}&page={page}'
        response = requests.get(url)

        if response.status_code == 200:
            media_list = response.json()['results']
            for media in media_list:
                title = media['title'] if media_type == 'movie' else media['name']
                release_date = media['release_date'] if media_type == 'movie' else media.get('first_air_date', 'Unknown')
                year = release_date.split('-')[0] if release_date else 'Unknown'
                genre_ids = media.get('genre_ids', [])
                genres = [genre_mapping.get(g_id, "Unknown") for g_id in genre_ids]

                # Get the cover image URL
                cover_image = image_base_url + media.get('poster_path', '') if media.get('poster_path') else None

                all_data.append({
                    'title': title,
                    'description': media.get('overview', 'No description available.'),
                    'year': year,
                    'genre': ', '.join(genres),
                    'type': 'Movie' if media_type == 'movie' else 'Series',
                    'cover_image': cover_image  # Add cover image to the data
                })
        else:
            print(f"Failed to fetch {media_type} data: {response.status_code}")
            break

    return pd.DataFrame(all_data)

# Fetch genre mappings for movies and TV series
movie_genres = fetch_genres(media_type='movie')
tv_genres = fetch_genres(media_type='tv')

# Combine movie and TV genres into one mapping
genre_mapping = {**movie_genres, **tv_genres}

# Fetch movie and series data
movies_df = fetch_media_data(media_type='movie', page_limit=10)
series_df = fetch_media_data(media_type='tv', page_limit=10)

# Combine datasets and handle missing or invalid year values
df = pd.concat([movies_df, series_df])

# Replace 'Unknown' years with NaN
df['year'] = pd.to_numeric(df['year'], errors='coerce')

# Drop rows where the year is NaN (optional: you can also choose to fill with a default value)
df = df.dropna(subset=['year'])

# Convert year back to integers after handling NaN
df['year'] = df['year'].astype(int)

# Save cleaned data to CSV
df.to_csv('data/movies_series_dataset.csv', index=False)

print("Data fetched, cleaned, and saved successfully.")
