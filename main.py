import pandas as pd
import matplotlib.pyplot as plt

# Define the file name
file_name = 'movies_metadata.csv'

try:
    # --- 1. DATA LOADING ---
    df = pd.read_csv(file_name, low_memory=False)
    print(f"Successfully loaded '{file_name}'!")
    print(f"Original shape: {df.shape}")
    print("-" * 30)

    # --- 2. DATA CLEANING ---
    print("Starting data cleaning process...")

    # Step 1: Drop unnecessary columns
    # We remove columns that are mostly empty or not useful for our analysis
    columns_to_drop = ['belongs_to_collection', 'homepage', 'poster_path', 'tagline', 'video', 'overview', 'imdb_id']
    df.drop(columns_to_drop, axis=1, inplace=True)
    print(f"Dropped {len(columns_to_drop)} unneccessary columns.")

#   Step 2: Correct data types for numeric columns
    # We convert 'budget', 'id', and 'popularity' to numbers.
    # errors='coerce' will turn any non-numeric value into NaN (Not a Number)
    numeric_cols = ['budget', 'id', 'popularity']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    print(f"Converted {len(numeric_cols)} columns to numeric type.")

    # Step 3: Correct data type for the date column
    # We convert 'release_date' to a special datetime format.
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    print("Converted 'release_date' column to datetime type.")

    # Step 4: Drop rows with invalid critical data after conversion
    # We remove movies that don't have a valid ID or release date after our cleanup
    df.dropna(subset=['id', 'release_date'], inplace=True)

#   Finally, convert 'id' to integer as it should not have decimals
    df['id'] = df['id'].astype(int)

    print("Data cleaning finished!")
    print("-" * 30)

    # Verification
    print("DataFrame Info after cleaning:")
    df.info()
    print("\nFirst 5 rows of the cleaned dataset:")
    print(df.head())

    # INVESTIGATION: Let's check the movies with a 0.0 rating
     #print("\nInvestigating movies with 0.0 average vote...")
     #zero_rated_movies = df[df['vote_average'] == 0]
     #print("Vote counts for movies with a 0.0 rating:")
     #print(zero_rated_movies['vote_count'].value_counts())

    # --- 3. DATA FILTERING ---
    # We only keep movies with at least 10 votes to get meaningful rating
    df_filtered_ratings = df[df['vote_count']>=10].copy()
    print(f'\nOriginal movie count: {len(df)}')
    print(f'Movie count after filtering for at least 10 votes: {len(df_filtered_ratings)}')
    print("-" * 30)

    # --- 4. EXPLORATORY DATA ANALYSIS (EDA) ---
    print("Creating histogram for filtered data...")

    # Create a histogram of movie ratings ('vote_average')
    plt.figure(figsize=(10,6)) #Sets the size of the plot
    plt.hist(df_filtered_ratings['vote_average'], bins=20, color='royalblue', edgecolor='black')

    #Add titles and labels for clarity
    plt.title('Distribution of Movie Ratings (with at least 10 votes)', fontsize=16)
    plt.xlabel('Average Vote (out of 10)', fontsize=12)
    plt.ylabel('Number of Movies', fontsize=12)
    plt.grid(axis='y', alpha=0.75)
    plt.show()

    # Scatter plot of budget vs. revenue
    # First, filter out movies with 0 budget or 0 revenue for a cleaner plot
    scatter_df=df_filtered_ratings[(df_filtered_ratings['budget']>1000) &(df_filtered_ratings['revenue']>1000)].copy()

    # Create new columns for plotting in millions for better readability
    scatter_df['budget_in_millions'] = scatter_df['budget'] / 1_000_000
    scatter_df['revenue_in_millions'] = scatter_df['revenue'] / 1_000_000

    print(f"\nCreating scatter plot for budget vs. revenue...")
    print(f"Using {len(scatter_df)} movies with valid budget and revenue data.")

    #Now, let's create the scatter plot
    plt.figure(figsize=(10,6))
    plt.scatter(x=scatter_df['budget_in_millions'], y=scatter_df['revenue_in_millions'], alpha=0.5) #alpha=0.5 for transparency

    plt.title('Budget vs Revenue for Movies', fontsize=16)
    plt.xlabel('Budget (in Millions of USD)', fontsize=12)
    plt.ylabel('Revenue (in Millions of USD)', fontsize=12)
    plt.grid(True)

    # Format the axes for better readability (millions, billions)
    plt.ticklabel_format(style='plain')  # Turns off scientific notation

    plt.show()

except FileNotFoundError:
    print(f"ERROR: The file '{file_name}' was not found in the project directory.")
