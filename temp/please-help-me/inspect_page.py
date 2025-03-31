import requests
from bs4 import BeautifulSoup
import pandas as pd

def inspect_page(game_id):
    """Inspect the structure of different pages for a given game ID"""
    
    # URLs for different pages
    urls = {
        'box_score': f'https://stats.ncaa.org/contests/{game_id}/box_score',
        'team_stats': f'https://stats.ncaa.org/contests/{game_id}/team_stats',
        'officials': f'https://stats.ncaa.org/contests/{game_id}/officials'
    }
    
    # Headers to mimic a browser
    headers = {
        "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"
    }
    
    for page_type, url in urls.items():
        print(f"\n{'='*50}")
        print(f"INSPECTING {page_type.upper()} PAGE")
        print(f"{'='*50}")
        
        try:
            # Get the page content
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to read tables using pandas
            tables = pd.read_html(url)
            
            print(f"\nNumber of tables found: {len(tables)}")
            
            for i, table in enumerate(tables):
                print(f"\nTable {i+1}:")
                print("Columns:", table.columns.tolist())
                print("Shape:", table.shape)
                print("\nFirst few rows:")
                print(table.head())
                print("\n")
            
        except Exception as e:
            print(f"Error inspecting {page_type}: {str(e)}")

# Test with a known game ID
test_game_id = "5730943"  # Use the first game ID that failed
inspect_page(test_game_id) 