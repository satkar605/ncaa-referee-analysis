import pandas as pd
import os

def analyze_referee_games():
    """
    Analyze how many games each referee officiated
    """
    # Step 1: Load the data
    print("Loading the data...")
    df = pd.read_csv('ncaa_games_data.csv')
    
    # Step 2: Let's see what our data looks like
    print("\nFirst, let's look at our columns:")
    print(df.columns.tolist())
    
    # Step 3: Get the official columns
    official_cols = ['Official_1', 'Official_2', 'Official_3']
    
    # Check if these columns exist, if not, try to find them
    for col in official_cols:
        if col not in df.columns:
            print(f"Warning: Column '{col}' not found in the dataset")
    
    # If columns not found, try to detect them
    if not all(col in df.columns for col in official_cols):
        potential_cols = [col for col in df.columns if 'official' in col.lower() or 'ref' in col.lower()]
        print(f"Potential official columns found: {potential_cols}")
        if potential_cols:
            official_cols = potential_cols[:3]  # Use the first 3 found
    
    print(f"\nUsing these columns for officials: {official_cols}")
    
    # Step 4: Create a list of all referees
    all_refs = []
    
    # Loop through each official column
    for col in official_cols:
        if col in df.columns:
            # Add non-null values to our list
            refs = df[col].dropna().tolist()
            all_refs.extend(refs)
    
    # Step 5: Count games for each referee
    ref_counts = pd.Series(all_refs).value_counts()
    
    # Step 6: Create a nice dataframe for display
    referee_stats = pd.DataFrame({
        'Referee': ref_counts.index,
        'Games_Officiated': ref_counts.values
    })
    
    # Step 7: Sort by number of games (most to least)
    referee_stats = referee_stats.sort_values('Games_Officiated', ascending=False)
    
    # Step 8: Add ranking
    referee_stats['Rank'] = range(1, len(referee_stats) + 1)
    
    # Step 9: Display results
    print("\n📊 Referee Statistics:")
    print(f"Total number of referees: {len(referee_stats)}")
    print("\nTop 10 Most Active Referees:")
    print(referee_stats.head(10))
    
    # Step 10: Save to CSV in the specified directory
    output_dir = os.path.expanduser('~/Desktop/workfiles')
    os.makedirs(output_dir, exist_ok=True)  # Create directory if it doesn't exist
    output_path = os.path.join(output_dir, 'referee_games.csv')
    referee_stats.to_csv(output_path, index=False)
    print(f"\n✅ Full results saved to '{output_path}'")
    
    return referee_stats

# Run the analysis
if __name__ == "__main__":
    referee_stats = analyze_referee_games() 