import streamlit as st
import pickle
import pandas as pd
import requests
import google.generativeai as genai
import json
import re

genai.configure(api_key="AIzaSyDEbwTXl_Sdfl3jQ9WEHJbEx_YnighCpYE")


def extract_json_from_response(response_text):
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        json_match = re.search(r'\{[^}]+\}', response_text)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                print("Could not parse extracted JSON")

        return {
            "poster_url": "https://via.placeholder.com/500",
            "description": "Could not extract details",
            "year": "N/A"
        }


def fetch_movie_details(movie_title):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
        For the movie '{movie_title}', provide:
        1. A direct URL to a movie poster image from a reliable source
        2. A brief description (2-3 sentences)
        3. Year of release

        Respond with a JSON object like this:
        {{
            "poster_url": "https://example.com/poster.jpg",
            "description": "A brief movie description",
            "year": "2023"
        }}
        """

        response = model.generate_content(prompt)

        details = extract_json_from_response(response.text)

        if not details.get('poster_url') or not details.get('description'):
            raise ValueError("Incomplete movie details")

        return details

    except Exception as e:
        print(f"Error fetching movie details for {movie_title}: {e}")
        return {
            "poster_url": "https://via.placeholder.com/500",
            "description": f"Details not available for {movie_title}",
            "year": "N/A"
        }


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    movie_descriptions = []

    for i in movies_list:
        movie_title = movies.iloc[i[0]].title
        recommended_movies.append(movie_title)

        movie_details = fetch_movie_details(movie_title)

        recommended_movies_posters.append(
            movie_details.get('poster_url', "https://via.placeholder.com/500")
        )
        movie_descriptions.append(
            movie_details.get('description', "No description available")
        )

    return recommended_movies, recommended_movies_posters, movie_descriptions


# 🔹 Load movie data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# 🔹 Custom CSS for Enhanced UI
st.markdown("""
<style>
    /* Page Background */
    body {
        background: linear-gradient(to right, #141e30, #243b55);
        color: white;
    }

    /* Movie Card Styling */
    .movie-card {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.3);
        text-align: center;
        transition: transform 0.3s ease-in-out;
        margin-bottom: 25px; /* Adds spacing between rows */
    }

    .movie-card:hover {
        transform: scale(1.07);
    }

    /* Movie Title */
    .movie-title {
        color: #f1c40f;
        font-size: 20px;
        font-weight: bold;
        margin-top: 12px;
    }

    /* Movie Description */
    .movie-description {
        color: #ecf0f1;
        font-size: 15px;
        margin-top: 8px;
        text-align: justify;
    }

    /* Movie Poster */
    .movie-poster {
        border-radius: 10px;
        max-height: 250px;
        object-fit: cover;
    }

    /* Recommendation Container */
    .recommend-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 20px;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# 🔹 Streamlit UI
st.title('🎬 Movie Recommender System 🧐')

# 🔹 Movie Selection
selected_movie_name = st.selectbox(
    'Enter Your Movie Name',
    movies['title'].values
)

# 🔹 Recommendation Button
if st.button('Recommend'):
    names, posters, descriptions = recommend(selected_movie_name)

    # 🔹 Display Recommendations
    st.markdown("<div class='recommend-container'>", unsafe_allow_html=True)

    for name, poster, desc in zip(names, posters, descriptions):
        st.markdown(f"""
        <div class="movie-card">
            <img src="{poster}" class="movie-poster"/>
            <div class="movie-title">{name}</div>
            <div class="movie-description">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
