import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Step 1: Make 'graphs' folder if not exists
if not os.path.exists("graphs"):
    os.makedirs("graphs")

# Step 2: Load the dataset
try:
    df = pd.read_csv('netflix_titles.csv', encoding='utf-8')
    print(" Data Loaded Successfully:", df.shape)
except Exception as e:
    print(" Failed to load data:", e)
    exit()

# Step 3: Clean the dataset with robust date parsing
try:
    # Drop rows with missing values in key columns
    df.dropna(subset=['type', 'country', 'date_added'], inplace=True)
    
    # Clean and convert date_added column (handling inconsistent formats)
    df['date_added'] = df['date_added'].str.strip()  # Remove extra whitespace
    df['date_added'] = pd.to_datetime(
        df['date_added'],
        format='mixed',  # Handle multiple date formats
        errors='coerce'  # Convert unparseable dates to NaT
    )
    
    # Drop rows where date parsing failed
    initial_count = len(df)
    df = df.dropna(subset=['date_added'])
    dropped_count = initial_count - len(df)
    if dropped_count > 0:
        print(f"⚠️ Dropped {dropped_count} rows with unparseable dates")
    
    # Extract year from cleaned dates
    df['year_added'] = df['date_added'].dt.year
    
    print("Data Cleaned:", df.shape)
except Exception as e:
    print(" Error during data cleaning:", e)
    exit()

# Step 4: Create first graph - Movie vs TV Show count
try:
    plt.figure(figsize=(8, 5))  # Slightly larger figure
    ax =sns.countplot(data=df, x='type', hue='type', palette='Set2', legend=False)
    plt.title('Netflix Content: Movies vs TV Shows', pad=20)
    plt.xlabel('Content Type', labelpad=10)
    plt.ylabel('Count', labelpad=10)
    
    # Add count labels on each bar
    for p in ax.patches:
        ax.annotate(f'{p.get_height():,}', 
                   (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha='center', va='center', 
                   xytext=(0, 5), 
                   textcoords='offset points')
    
    plt.tight_layout()  # Prevent label cutoff
    plt.savefig('graphs/content_type_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print(" First graph saved successfully in 'graphs/' folder")
except Exception as e:
    print(" Error during graph creation:", e)
    exit()
# Step 5: Top Countries Analysis
plt.figure(figsize=(12, 8))

# Data Preparation
top_countries = (
    df['country']
    .str.split(', ')  # Split multiple countries
    .explode()        # Create separate row for each country
    .value_counts()   # Count by country
    .head(10)         # Top 10 countries
)

# Create the plot
ax = sns.barplot(
    x=top_countries.values,
    y=top_countries.index,
    palette='viridis',
    edgecolor='black'
)

# Customize the plot
plt.title('Top 10 Countries with Most Netflix Content', fontsize=16, pad=20)
plt.xlabel('Number of Titles', fontsize=12)
plt.ylabel('Country', fontsize=12)
plt.xticks(rotation=45)

# Add value labels
for i, v in enumerate(top_countries.values):
    ax.text(v + 20, i, f"{v:,}", color='black', ha='left', va='center')

plt.tight_layout()
plt.savefig('graphs/top_countries.png', dpi=300, bbox_inches='tight')
plt.close()

print(" Top Countries graph saved in 'graphs/' folder")
# Step: Content added by year
plt.figure(figsize=(10, 6))
df['year_added'].value_counts().sort_index().plot(kind='bar', color='skyblue')
plt.title('Netflix Content Added by Year')
plt.xlabel('Year')
plt.ylabel('Number of Titles')
plt.tight_layout()
plt.savefig('graphs/content_added_by_year.png')
plt.close()

print(" Yearly content graph saved")
# Step: Genre vs Type (Movie/TV Show) Heatmap

# Expand genre list
df_genres = df[['type', 'listed_in']].dropna()
df_genres = df_genres.assign(listed_in=df_genres['listed_in'].str.split(', '))
df_genres = df_genres.explode('listed_in')

# Create pivot table (genre vs type)
genre_type = df_genres.groupby(['listed_in', 'type']).size().unstack(fill_value=0)

# Plot heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(genre_type, annot=True, fmt='d', cmap='YlGnBu')
plt.title("Genre-wise Movie vs TV Show Distribution")
plt.tight_layout()
plt.savefig("graphs/genre_vs_type_heatmap.png")
plt.close()

print(" Genre vs Type heatmap saved")
# Step: Top 10 Most Common Genres

from collections import Counter

# Clean and extract genres
genre_series = df['listed_in'].dropna().apply(lambda x: [i.strip() for i in x.split(',')])
all_genres = [genre for sublist in genre_series for genre in sublist]

# Count top 10 genres
genre_counts = Counter(all_genres).most_common(10)
genres, counts = zip(*genre_counts)

# Plot
plt.figure(figsize=(10, 6))
sns.barplot(x=counts, y=genres, palette='mako')
plt.title('Top 10 Most Common Genres on Netflix')
plt.xlabel('Number of Titles')
plt.ylabel('Genre')
plt.tight_layout()
plt.savefig('graphs/top_10_genres.png')
plt.close()

print(" Genre graph saved (top_10_genres.png)")



