import pandas as pd

def check_column_names():
    """Check the column names in the merged dataset."""
    try:
        df = pd.read_csv('ncaa_games_data.csv')
        print("Column names in the dataset:")
        print(df.columns.tolist())
    except FileNotFoundError:
        print("❌ Could not find ncaa_games_data.csv. Please ensure the file is in the correct location.")

if __name__ == "__main__":
    check_column_names() 