import os
import pandas as pd

def find_merged_data():
    """Locate and verify the merged dataset"""
    # Common file names to check
    possible_files = [
        'ncaa_games_data.csv',
        'scraped_data/merged.csv',
        'data/merged_games.csv',
        'merged_games.csv'
    ]
    
    print("🔍 Searching for merged data file...")
    
    for file_path in possible_files:
        if os.path.exists(file_path):
            print(f"\n✅ Found merged data at: {file_path}")
            df = pd.read_csv(file_path)
            print(f"\n📊 Dataset Overview:")
            print(f"Total rows: {len(df):,}")
            print(f"Columns: {', '.join(df.columns)}")
            return file_path
    
    print("\n❌ Merged data file not found in common locations!")
    
    # Show individual batch files
    print("\n📁 Available batch files in scraped_data/:")
    if os.path.exists('scraped_data'):
        batch_files = [f for f in os.listdir('scraped_data') if f.startswith('batch_')]
        for batch in sorted(batch_files):
            print(f"  - scraped_data/{batch}")

if __name__ == "__main__":
    find_merged_data() 