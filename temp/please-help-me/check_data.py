import pandas as pd

def check_data_structure():
    """Check the structure of the merged dataset"""
    try:
        df = pd.read_csv('ncaa_games_data.csv')
        print("\n📊 Data Structure:")
        print(f"Number of rows: {len(df)}")
        print("\nColumns in dataset:")
        for col in df.columns:
            print(f"- {col}")
            
        # Print first few rows
        print("\nFirst few rows of data:")
        print(df.head())
        
    except FileNotFoundError:
        print("❌ Could not find ncaa_games_data.csv")

# Run the check
check_data_structure() 