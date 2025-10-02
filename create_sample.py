# create_sample.py
import pandas as pd

print("Creating a smaller sample file...")
df = pd.read_csv('movies_metadata.csv', low_memory=False)
df_sample = df.head(5000)
df_sample.to_csv('movies_sample.csv', index=False)
print("'movies_sample.csv' created successfully with 5000 rows.")