import streamlit as st
import pickle
import pandas as pd
import requests
import urllib.parse  # For encoding the movie title for URLs
import gzip

# Function to fetch movie details using The Movie Database (TMDb) API
def fetch_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        data = requests.get(url).json()
        poster_path = data['poster_path']
        full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
        overview = data['overview']
        release_date = data['release_date']
        rating = data['vote_average']
        trailer_url = fetch_trailer(movie_id)
    except Exception as e:
        st.error(f"Failed to fetch movie details: {e}")
        return None, None, None, None, None

    return full_path, overview, release_date, rating, trailer_url

# Function to fetch trailer URL using The Movie Database (TMDb) API
def fetch_trailer(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    try:
        data = requests.get(url).json()
        # Find the first trailer in the results
        for video in data['results']:
            if video['type'] == 'Trailer':
                return f"https://www.youtube.com/embed/{video['key']}"
    except Exception as e:
        st.error("Failed to fetch trailer details. Please try again later.")
        return None
    return None

# Function to recommend movies
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])),
                       reverse=True,
                       key=lambda x: x[1])
    recommended_movie_details = []
    for i in distances[1:11]:  # Start from 1 to skip the selected movie itself
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title
        poster, overview, release_date, rating, trailer_url = fetch_details(movie_id)
        recommended_movie_details.append(
            (title, poster, overview, release_date, rating, trailer_url))
    return recommended_movie_details

# Load movies and similarity matrix
@st.cache_data
def load_data():
    movies_list = pickle.load(open('movies.pkl', 'rb'))
    movies = pd.DataFrame(movies_list)
    with gzip.open('similarity.pkl.gz', 'rb') as f:
        similarity = pickle.load(f)
    return movies, similarity

movies, similarity = load_data()

# CSS for styling
page_bg_img = '''
<style>
body {
    background-color: #2c2c2c; /* Light black background */
    color: #f0f0f0; /* Light color for readability */
    font-family: 'Roboto', sans-serif; /* Modern font */
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

h1, h2, h3, h4, h5, h6 {
    color: #f5f5f5;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
}

.stButton button {
    background-color: #22c1c3; /* Primary button color */
    color: white;
    border-radius: 12px;
    padding: 0.5em 1em;
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    font-size: 16px;
    cursor: pointer;
}

.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.3);
    background-color: #1aa0a2;
}

.movie-card {
    display: flex;
    flex-direction: column;
    background-color: rgba(255, 255, 255, 0.8); /* Semi-transparent background */
    border-radius: 12px;
    padding: 1em;
    margin-bottom: 1em;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    width: 100%;
    max-width: 600px; /* Max-width for responsiveness */
}

.movie-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.2);
}

.movie-poster {
    border-radius: 8px;
    width: 100%;
    max-width: 200px; /* Adjusted size */
    transition: transform 0.2s ease;
    margin-right: 20px; /* Space between poster and details */
}

.movie-poster:hover {
    transform: scale(1.05);
}

.movie-details {
    text-align: left;
    padding: 0 20px;
}

.movie-title {
    font-size: 1.8em;
    color: #ffdb58; /* Title color */
    font-weight: bold;
    margin-bottom: 0.5em;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.4);
}

.movie-overview, .movie-info {
    color: #000000; /* Text color for visibility */
}

.movie-overview {
    font-size: 1em;
    margin-bottom: 1em;
}

.movie-info {
    font-size: 0.9em;
    margin-top: 0.5em;
}

.trailer-section {
    margin-top: 1em;
}

.sidebar-section {
    color: #f0f0f0;
    margin-bottom: 1em;
    padding: 1em;
    background-color: rgba(0, 0, 0, 0.3);
    border-radius: 10px;
}

.sidebar-section h3 {
    margin-top: 0;
    color: #ffdb58; /* Different color for emphasis */
}

.stTextInput, .stSelectbox {
    margin-bottom: 1em;
}

footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    color: #f0f0f0;
    text-align: center;
    padding: 1em 0;
}

@media (min-width: 768px) {
    .movie-card {
        display: flex;
        flex-direction: row;
    }

    .movie-details {
        text-align: left;
        max-width: calc(100% - 220px); /* Adjusted for poster width */
    }

    .movie-poster {
        margin-right: 20px; /* Space between poster and details */
    }
}

@media (max-width: 767px) {
    .movie-title {
        font-size: 1.5em; /* Adjusted size for smaller screens */
    }

    .movie-details {
        text-align: center;
    }

    .movie-card {
        flex-direction: column;
        align-items: center;
    }

    .movie-poster {
        margin-right: 0;
        margin-bottom: 15px;
    }
}
</style>
'''

# Inject CSS with Streamlit
st.markdown(page_bg_img, unsafe_allow_html=True)

# Streamlit app
st.title("🎬 Movie Recommendation System")

# Sidebar for filters and additional features
st.sidebar.header("Customize Your Experience")

st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
st.sidebar.write("### Filter Recommendations")

# Rating filter
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 10.0, 5.0)

st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Dropdown for selecting a movie
movie_list = movies['title'].values
selected_movie = st.selectbox("Choose a movie", movie_list)

# Button to get recommendations
if st.button('Recommend'):
    recommended_movies = recommend(selected_movie)

    # Filter recommendations based on minimum rating
    filtered_movies = [
        movie for movie in recommended_movies if movie[4] >= min_rating
    ]

    st.write("## Recommended Movies:")

    # Display recommended movies in a structured layout
    for title, poster, overview, release_date, rating, trailer_url in filtered_movies:
        # URL encode the movie title
        google_search_url = f"https://www.google.com/search?q={urllib.parse.quote(title)}"

        st.markdown(f"""
            <div class="movie-card">
                <img src="{poster}" class="movie-poster"/>
                <div class="movie-details">
                    <h2 class="movie-title">{title}</h2>
                    <p class="movie-overview"><strong>Overview:</strong> {overview}</p>
                    <p class="movie-info"><strong>Release Date:</strong> {release_date}</p>
                    <p class="movie-info"><strong>Rating:</strong> {rating}/10</p>
                    <div class="trailer-section">
                        {f'<iframe width="560" height="315" src="{trailer_url}" frameborder="0" allowfullscreen></iframe>' if trailer_url else "<p>Trailer not available</p>"}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True)

# Footer
st.markdown('''
    <footer>
        <p>© 2024 Movie Recommendation System | Created by Ankit Singh</p>
    </footer>
    ''',
    unsafe_allow_html=True)
