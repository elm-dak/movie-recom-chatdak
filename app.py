import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Set the page configuration
st.set_page_config(page_title="ChatDAK", layout="wide")

# Initialize session state for dark mode
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Function to toggle dark mode
def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Load dataset of movies/series
@st.cache_data
def load_data():
    return pd.read_csv('data/movies_series_dataset.csv')

df = load_data()

# Fill NaN values in the 'genre' and 'description' columns with an empty string
df['genre'] = df['genre'].fillna('')
df['description'] = df['description'].fillna('')

# Function to recommend movies/series based on description
def recommend_movies(user_input, filtered_df):
    filtered_df['description'] = filtered_df['description'].fillna('')
    filtered_df = filtered_df[filtered_df['description'].apply(lambda x: isinstance(x, str) and x.strip() != '')]

    if filtered_df.empty:
        return pd.DataFrame()

    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(filtered_df['description'])
    user_input_tfidf = tfidf.transform([user_input])
    cosine_sim = cosine_similarity(user_input_tfidf, tfidf_matrix)
    all_matches = cosine_sim[0].argsort()[::-1]
    recommendations = filtered_df.iloc[all_matches][['title', 'year', 'genre', 'description', 'cover_image']]
    return recommendations

# Custom CSS for additional styling
def set_custom_style():
    st.markdown("""
    <style>
    .stApp {
        transition: all 0.3s ease-in-out;
    }
    .stButton > button {
        border-radius: 20px;
        padding: 10px 24px;
        transition: all 0.3s ease-in-out;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 10px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# Apply custom styling
set_custom_style()

# Streamlit app interface
st.title("🎬 ChatDAK - Movie/Series Recommendation ")

# Light/Dark mode toggle with icons
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🌙" if not st.session_state.dark_mode else "☀️", on_click=toggle_dark_mode):
        st.rerun()

# Apply the appropriate theme
if st.session_state.dark_mode:
    st.markdown("""
        <style>
        .stApp {
            background-color: #1E1E1E;
            color: #FFFFFF;
        }
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div > div > div > div > div {
            color: #FFFFFF;
            background-color: #2E2E2E;
        }
        .stSlider > div > div > div > div > div {
            color: #FFFFFF;
        }
        .stButton > button {
            color: #FFFFFF;
            background-color: #4E4E4E;
            border: 1px solid #FFFFFF;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
                h1{
                color: #000000;
                }
                h2{
                color: #000000;
                }
                h3{
                color: #000000;
                }
                .st-bb{
                color: #000000;
                }
               p{
                 color: #000000;
                }
                .st-bb {
    background-color: #FFFFFF;
            color: #000000;
}
                .st-emotion-cache-h4xjwg {
                background-color: #FFFFFF;
            color: #000000;
                }
                .st-cp{
                background-color: #FFFFFF;
            color: #000000;
        
                }
                .st-b6 {
                    color: rgba(14, 17, 23, 0.95);
                }
                .st-emotion-cache-1ppef92 {
                background-color: rgb(163, 168, 184);
                }



                .st-do {
                 background-color: #FFFFFF;
            color: #000000;
                }
        .stApp {
            background-color: #FFFFFF;
            color: #000000;
        }
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div > div > div > div > div {
            color: #000000;
            background-color: #F0F0F0;
            border: 1px solid #CCCCCC;
        }
        .stSlider > div > div > div > div > div {
            color: #000000;
        }
        .stButton > button {
            color: #000000;
            background-color: #E0E0E0;
            border: 1px solid #000000;
        }
        </style>
    """, unsafe_allow_html=True)

# Filters
st.header("Filter Options")
genres = df['genre'].unique()
years = sorted(df['year'].unique(), reverse=True)
types = df['type'].unique()

col1, col2, col3 = st.columns(3)

with col1:
    selected_genre = st.selectbox('Select Genre', options=['All'] + list(genres))

with col2:
    selected_type = st.selectbox('Select Type', options=['All'] + list(types))

with col3:
    min_year, max_year = st.slider('Select Year Range', min_value=int(df['year'].min()), max_value=int(df['year'].max()), value=(2010, 2024))

# Apply filters
filtered_df = df.copy()

if selected_genre != 'All':
    filtered_df = filtered_df[filtered_df['genre'].str.contains(selected_genre, case=False, na=False)]

filtered_df['year'] = pd.to_numeric(filtered_df['year'], errors='coerce')
filtered_df = filtered_df.dropna(subset=['year'])
filtered_df['year'] = filtered_df['year'].astype(int)
filtered_df = filtered_df[(filtered_df['year'] >= min_year) & (filtered_df['year'] <= max_year)]

if selected_type != 'All':
    filtered_df = filtered_df[filtered_df['type'] == selected_type]

# Prompt for description
user_input = st.text_area("Describe the type of movie or series you're looking for:", height=100)

# Button for recommendation
if st.button('Recommend'):
    if user_input:
        recommendations = recommend_movies(user_input, filtered_df)
        if not recommendations.empty:
            for idx, row in recommendations.iterrows():
                col1, col2 = st.columns([1, 2])
                with col1:
                    if row['cover_image']:
                        st.image(row['cover_image'], caption=row['title'], use_column_width=True)
                with col2:
                    st.subheader(f"{row['title']} ({row['year']})")
                    st.write(f"**Genre**: {row['genre']}")
                    st.write(f"**Description**: {row['description']}")
                st.write("---")
        else:
            st.warning("No recommendations found. Please try with a different description.")
    else:
        st.warning("Please enter a description to get recommendations.")
