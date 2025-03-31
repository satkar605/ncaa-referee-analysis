# ===========================================
# Import Required Libraries
# ===========================================
import pandas as pd
import time
import requests
from datetime import datetime
import os

# ===========================================
# Configuration Settings
# ===========================================
DELAY_BETWEEN_REQUESTS = 1.5  # Time to wait between requests (in seconds)
SAVE_INTERVAL = 20    # Save progress after every 20 games (changed from 50)
MAX_GAMES = 1000     # Maximum number of games to scrape
OUTPUT_FOLDER = "scraped_data"  # Folder to save all output files
RESUME_FILE = "officials_resume_state.txt"

# ===========================================
# Helper Functions
# ===========================================
def create_output_folder():
    """Create folder for saving data if it doesn't exist"""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

def format_officials(officials_df):
    """
    Extract and format officials from the officials dataframe
    Returns a tuple of (official1, official2, official3)
    If less than 3 officials, remaining spots will be None
    """
    if officials_df is None or officials_df.empty:
        return None, None, None
    
    # Get list of officials
    officials_list = officials_df['Official'].tolist() if 'Official' in officials_df.columns else []
    
    # Pad list with None values if less than 3 officials
    while len(officials_list) < 3:
        officials_list.append(None)
    
    # Return only first 3 officials (some games might have more)
    return officials_list[0], officials_list[1], officials_list[2]

def save_progress(data, filename):
    """Save current progress to CSV file with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{OUTPUT_FOLDER}/{filename}_{timestamp}.csv"
    pd.DataFrame(data).to_csv(filepath, index=False)
    return filepath

def save_resume_state(index):
    """Save the current game index for resuming later"""
    with open(RESUME_FILE, 'w') as f:
        f.write(str(index))

def load_resume_state():
    """Load the last processed game index"""
    try:
        with open(RESUME_FILE, 'r') as f:
            return int(f.read().strip())
    except:
        return 0

# ===========================================
# Main Scraping Function
# ===========================================
def scrape_officials(start_from=None):
    """
    Main function to scrape officials data for all games
    start_from: Optional index to resume from
    """
    print("🏀 Starting NCAA Basketball Officials Scraper")
    
    # Create output folder
    create_output_folder()
    
    # Load game IDs from CSV
    try:
        game_data = pd.read_csv("regular_season_game_ids.csv")
        
        # Limit to MAX_GAMES
        game_data = game_data.head(MAX_GAMES)
        print(f"📊 Processing first {MAX_GAMES} games")
        
        # Determine starting point
        start_index = start_from if start_from is not None else load_resume_state()
        if start_index > 0:
            print(f"📝 Resuming from game {start_index}")
            
        # Load existing data if any
        existing_data = []
        existing_files = sorted([f for f in os.listdir(OUTPUT_FOLDER) 
                               if f.startswith('officials_progress')])
        if existing_files:
            latest_file = os.path.join(OUTPUT_FOLDER, existing_files[-1])
            existing_data = pd.read_csv(latest_file).to_dict('records')
            print(f"📊 Loaded {len(existing_data)} existing records")
        
        officials_data = existing_data
        failed_games = []
        
        # Track timing
        start_time = datetime.now()
        
        # Process each game starting from resume point
        for index, row in game_data.iloc[start_index:].iterrows():
            game_id = row['Game ID']
            game_date = row['Date']
            
            try:
                print(f"\n🔄 Processing Game {index + 1}/{MAX_GAMES}")
                print(f"   Game ID: {game_id}, Date: {game_date}")
                
                # Construct URL and fetch data
                url = f'https://stats.ncaa.org/contests/{game_id}/officials'
                officials_tables = pd.read_html(url)
                
                # Extract officials (usually in the 4th table, index 3)
                if len(officials_tables) > 3:
                    official1, official2, official3 = format_officials(officials_tables[3])
                    
                    # Store successful scrape
                    officials_data.append({
                        'Game_ID': game_id,
                        'Date': game_date,
                        'Official_1': official1,
                        'Official_2': official2,
                        'Official_3': official3
                    })
                    print(f"✅ Successfully scraped officials for game {game_id}")
                else:
                    print(f"⚠️ No officials data found for game {game_id}")
                    failed_games.append({
                        'Game_ID': game_id,
                        'Date': game_date,
                        'Error': 'No officials table found'
                    })
                
                # Save progress every 20 games
                if (index + 1) % SAVE_INTERVAL == 0:
                    filepath = save_progress(officials_data, "officials_progress")
                    print(f"\n💾 Progress saved to {filepath}")
                    print(f"   Completed {index + 1} games ({(index + 1)/MAX_GAMES*100:.1f}%)")
                    # Take a longer break every 20 games
                    print("😴 Taking a short break...")
                    time.sleep(3)  # 3-second break every 20 games
                
                # Save resume state after each game
                save_resume_state(index + 1)
                
                # Regular delay between requests
                time.sleep(DELAY_BETWEEN_REQUESTS)
                
            except Exception as e:
                print(f"❌ Error scraping game {game_id}: {str(e)}")
                failed_games.append({
                    'Game_ID': game_id,
                    'Date': game_date,
                    'Error': str(e)
                })
                save_resume_state(index + 1)
                continue
            
            # Stop if we've reached MAX_GAMES
            if index + 1 >= MAX_GAMES:
                print(f"\n🎯 Reached target of {MAX_GAMES} games")
                break
        
        # Save final results
        final_data = pd.DataFrame(officials_data)
        failed_data = pd.DataFrame(failed_games)
        
        final_path = save_progress(final_data, "officials_final")
        failed_path = save_progress(failed_data, "officials_failed")
        
        # Show summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n=== 📊 Scraping Summary ===")
        print(f"Total games processed: {len(game_data)}")
        print(f"Successfully scraped: {len(officials_data)}")
        print(f"Failed to scrape: {len(failed_games)}")
        print(f"Success rate: {len(officials_data)/len(game_data)*100:.1f}%")
        print(f"Total time: {duration}")
        print(f"\nFinal data saved to: {final_path}")
        print(f"Failed games saved to: {failed_path}")
        
        return final_data

    except FileNotFoundError:
        print("❌ Error: regular_season_game_ids.csv not found!")
        return None

# ===========================================
# Run Scraper
# ===========================================
if __name__ == "__main__":
    # Check if resuming
    if os.path.exists(RESUME_FILE):
        resume_index = load_resume_state()
        response = input(f"Found previous progress (stopped at game {resume_index}). Resume? (yes/no): ")
        if response.lower() == 'yes':
            scrape_officials(start_from=resume_index)
        else:
            scrape_officials(start_from=0)
    else:
        scrape_officials(start_from=0) 