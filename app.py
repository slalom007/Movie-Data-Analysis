import streamlit as st
import pandas as pd
import ast
import matplotlib.pyplot as plt  # We need matplotlib for plotting


def extract_genres(genres_str):
    try:
        genres_list = ast.literal_eval(genres_str)
        genre_names = [genre['name'] for genre in genres_list]
        return ", ".join(genre_names)
    except (ValueError, SyntaxError):
        return ""


@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path, low_memory=False)

    numeric_cols = ['budget', 'id', 'popularity']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    df.dropna(subset=['id', 'release_date'], inplace=True)
    df['id'] = df['id'].astype(int)
    df['year'] = df['release_date'].dt.year
    df['genres_clean'] = df['genres'].apply(extract_genres)

    return df


@st.cache_data
def get_unique_genres(df):
    genres = df['genres_clean'].str.split(', ').explode()
    unique_genres = sorted(genres.dropna().unique())
    return unique_genres


# --- App Layout ---
st.title("Interactive Movie Dashboard 🎬")
df = load_data('movies_sample.csv')

# --- Sidebar for filters ---
st.sidebar.header("Filter Options")

min_year = int(df['year'].min())
max_year = int(df['year'].max())
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(2000, 2010)
)

unique_genres = get_unique_genres(df)
selected_genres = st.sidebar.multiselect(
    "Select Genre(s)",
    options=unique_genres,
    default=['Action', 'Comedy']
)

# --- Filter the data ---
filtered_df = df[
    (df['year'] >= selected_years[0]) &
    (df['year'] <= selected_years[1])
    ]

if selected_genres:
    filtered_df = filtered_df[filtered_df['genres_clean'].str.contains('|'.join(selected_genres), na=False)]

# --- Display the results ---
st.write(f"Displaying movies from **{selected_years[0]}** to **{selected_years[1]}**")
if selected_genres:
    st.write(f"Filtered by genres: **{', '.join(selected_genres)}**")

# --- Check if the filtered DataFrame is empty ---
if filtered_df.empty:
    st.warning("No movies found for the selected criteria. Please adjust your filters.")
else:
    # --- Display the formatted table ---
    columns_to_display = ['title', 'genres_clean', 'vote_average', 'budget', 'revenue', 'release_date']
    display_df = filtered_df[columns_to_display].copy()
    display_df['release_date'] = display_df['release_date'].dt.year
    for col in ['budget', 'revenue']:
        display_df[col] = display_df[col].apply(
            lambda x: "No data available" if x == 0 else f"{int(x):,}"
        )
    st.dataframe(display_df, hide_index=True)

    # --- Add dynamic charts ---
    st.header("Visualizations for Selected Period")

    # Chart 1: Top 10 Highest Rated Movies
    st.subheader("Top 10 Highest Rated Movies")
    top_10_movies = filtered_df.sort_values(by='vote_average', ascending=False).head(10)

    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.barh(top_10_movies['title'], top_10_movies['vote_average'], color='skyblue')
    ax1.set_xlabel("Average Rating (out of 10)")
    ax1.invert_yaxis()  # To display the highest rated movie at the top
    plt.tight_layout()
    st.pyplot(fig1)

    # Chart 2: Number of Movies Released Per Year
    st.subheader("Number of Movies Released Per Year")
    movies_per_year = filtered_df['year'].value_counts().sort_index()

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    ax2.plot(movies_per_year.index, movies_per_year.values, marker='o', linestyle='-')
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Number of Movies Released")
    ax2.grid(True)
    plt.tight_layout()
    st.pyplot(fig2)