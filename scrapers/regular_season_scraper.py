# ===========================================
# 📦 Import Required Libraries
# ===========================================
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import numpy as np
import os
from datetime import datetime

# ===========================================
# 📂 Load Game Metadata CSV
# ===========================================
file_path = "regular_season_game_ids.csv"
game_data = pd.read_csv(file_path)

# ===========================================
# ⚙️ Configuration
# ===========================================
BATCH_SIZE = 50  # Number of games to process in each batch
SAVE_DIRECTORY = "scraped_data"
RESUME_FILE = "resume_state.txt"

# Create save directory if it doesn't exist
if not os.path.exists(SAVE_DIRECTORY):
    os.makedirs(SAVE_DIRECTORY)

# ===========================================
# 📝 Helper Functions
# ===========================================
def safe_convert_to_numeric(value):
    """Safely convert a value to numeric, returning None if conversion fails"""
    try:
        if pd.isna(value):
            return None
        return pd.to_numeric(str(value).replace(',', ''))
    except:
        return None

def get_officials(officials_df):
    """Extract officials and return them as separate entries"""
    if officials_df is None or officials_df.empty or len(officials_df) < 3:
        return None, None, None
    
    officials_list = officials_df['Official'].tolist()
    # Pad the list with None values if less than 3 officials
    officials_list.extend([None] * (3 - len(officials_list)))
    # Return only the first 3 officials
    return officials_list[0], officials_list[1], officials_list[2]

def save_batch_data(batch_data, batch_num):
    """Save batch data to a CSV file"""
    batch_file = f"{SAVE_DIRECTORY}/batch_{batch_num:04d}.csv"
    pd.DataFrame(batch_data).to_csv(batch_file, index=False)
    return batch_file

def save_resume_state(last_completed_index):
    """Save the current state for resume capability"""
    with open(RESUME_FILE, 'w') as f:
        f.write(str(last_completed_index))

def load_resume_state():
    """Load the last saved state"""
    try:
        with open(RESUME_FILE, 'r') as f:
            return int(f.read().strip())
    except:
        return 0

def merge_batch_files():
    """Merge all batch files into a single final dataset"""
    all_files = sorted([f for f in os.listdir(SAVE_DIRECTORY) if f.startswith('batch_') and f.endswith('.csv')])
    if not all_files:
        return
    
    dfs = []
    for file in all_files:
        df = pd.read_csv(f"{SAVE_DIRECTORY}/{file}")
        dfs.append(df)
    
    final_df = pd.concat(dfs, ignore_index=True)
    final_df.to_csv('ncaa_games_data_complete.csv', index=False)
    return final_df

# ===========================================
# 🔄 Process Games in Batches
# ===========================================
start_index = load_resume_state()
total_games = len(game_data)
current_batch = start_index // BATCH_SIZE + 1

print(f"Total games to process: {total_games}")
print(f"Starting from game index: {start_index}")
print(f"Current batch: {current_batch}")

# Initialize batch storage
batch_data = []
failed_games = []

try:
    for i in range(start_index, total_games):
        game_id = game_data.iloc[i]['Game ID']
        game_date = game_data.iloc[i]['Date']
        
        try:
            print(f"\n🔄 Scraping Game ID: {game_id} ({i+1}/{total_games})")
            
            # -------- Box Score --------
            url_box = f'https://stats.ncaa.org/contests/{game_id}/box_score'
            print(f"  Fetching box score...")
            box_score = pd.read_html(url_box)
            
            # -------- Team Stats --------
            url_team = f'https://stats.ncaa.org/contests/{game_id}/team_stats'
            print(f"  Fetching team stats...")
            team_stats = pd.read_html(url_team)
            time.sleep(1.5)  # Polite delay between requests
            
            # -------- Officials --------
            url_official = f'https://stats.ncaa.org/contests/{game_id}/officials'
            print(f"  Fetching officials...")
            officials = pd.read_html(url_official)
            time.sleep(1.5)
            
            # Get officials
            official1, official2, official3 = get_officials(officials[3] if len(officials) > 3 else None)
            
            # Extract game information from box score tables
            game_info = {
                'Game_ID': game_id,
                'Date': game_date,
                'Home_Team': box_score[1].iloc[1, 0] if len(box_score) > 1 and not box_score[1].empty else None,
                'Away_Team': box_score[1].iloc[2, 0] if len(box_score) > 1 and not box_score[1].empty else None,
                'Home_Score_1H': safe_convert_to_numeric(box_score[1].iloc[1, 1]) if len(box_score) > 1 and not box_score[1].empty else None,
                'Home_Score_2H': safe_convert_to_numeric(box_score[1].iloc[1, 2]) if len(box_score) > 1 and not box_score[1].empty else None,
                'Home_Score_Final': safe_convert_to_numeric(box_score[1].iloc[1, 3]) if len(box_score) > 1 and not box_score[1].empty else None,
                'Away_Score_1H': safe_convert_to_numeric(box_score[1].iloc[2, 1]) if len(box_score) > 1 and not box_score[1].empty else None,
                'Away_Score_2H': safe_convert_to_numeric(box_score[1].iloc[2, 2]) if len(box_score) > 1 and not box_score[1].empty else None,
                'Away_Score_Final': safe_convert_to_numeric(box_score[1].iloc[2, 3]) if len(box_score) > 1 and not box_score[1].empty else None,
                'Venue': box_score[1].iloc[4, 0] if len(box_score) > 1 and not box_score[1].empty else None,
                'Game_Time': box_score[1].iloc[3, 0] if len(box_score) > 1 and not box_score[1].empty else None,
                'Official_1': official1,
                'Official_2': official2,
                'Official_3': official3
            }
            
            # Extract team stats
            if len(team_stats) > 3 and not team_stats[3].empty:
                period_stats = team_stats[3]
                
                # Foul-related stats
                game_info.update({
                    # Personal Fouls
                    'Home_Personal_Fouls': safe_convert_to_numeric(period_stats.iloc[9, 1]) if not period_stats.empty else None,
                    'Away_Personal_Fouls': safe_convert_to_numeric(period_stats.iloc[9, 2]) if not period_stats.empty else None,
                    
                    # Free Throws
                    'Home_FTM': safe_convert_to_numeric(period_stats.iloc[7, 1]) if not period_stats.empty else None,
                    'Away_FTM': safe_convert_to_numeric(period_stats.iloc[7, 2]) if not period_stats.empty else None,
                    'Home_FTA': safe_convert_to_numeric(period_stats.iloc[8, 1]) if not period_stats.empty else None,
                    'Away_FTA': safe_convert_to_numeric(period_stats.iloc[8, 2]) if not period_stats.empty else None,
                    
                    # Free Throw Percentage
                    'Home_FT_Percentage': safe_convert_to_numeric(period_stats.iloc[8, 1]) if not period_stats.empty else None,
                    'Away_FT_Percentage': safe_convert_to_numeric(period_stats.iloc[8, 2]) if not period_stats.empty else None,
                    
                    # Technical Fouls
                    'Home_Technical_Fouls': safe_convert_to_numeric(period_stats.iloc[10, 1]) if not period_stats.empty else None,
                    'Away_Technical_Fouls': safe_convert_to_numeric(period_stats.iloc[10, 2]) if not period_stats.empty else None,
                    
                    # Flagrant Fouls
                    'Home_Flagrant_Fouls': safe_convert_to_numeric(period_stats.iloc[11, 1]) if not period_stats.empty else None,
                    'Away_Flagrant_Fouls': safe_convert_to_numeric(period_stats.iloc[11, 2]) if not period_stats.empty else None,
                    
                    # Fouls by Period
                    'Home_Fouls_1H': safe_convert_to_numeric(period_stats.iloc[12, 1]) if not period_stats.empty else None,
                    'Away_Fouls_1H': safe_convert_to_numeric(period_stats.iloc[12, 2]) if not period_stats.empty else None,
                    'Home_Fouls_2H': safe_convert_to_numeric(period_stats.iloc[13, 1]) if not period_stats.empty else None,
                    'Away_Fouls_2H': safe_convert_to_numeric(period_stats.iloc[13, 2]) if not period_stats.empty else None,
                })
                
                # Calculate derived foul statistics
                if game_info['Home_Personal_Fouls'] is not None and game_info['Away_Personal_Fouls'] is not None:
                    game_info['Foul_Differential'] = game_info['Home_Personal_Fouls'] - game_info['Away_Personal_Fouls']
                    game_info['Total_Fouls'] = game_info['Home_Personal_Fouls'] + game_info['Away_Personal_Fouls']
                
                if game_info['Home_FTA'] is not None and game_info['Away_FTA'] is not None:
                    game_info['Free_Throw_Differential'] = game_info['Home_FTA'] - game_info['Away_FTA']
            
            batch_data.append(game_info)
            
            # Save batch when it reaches BATCH_SIZE
            if len(batch_data) >= BATCH_SIZE:
                batch_file = save_batch_data(batch_data, current_batch)
                print(f"\n✅ Saved batch {current_batch} to {batch_file}")
                batch_data = []  # Reset batch data
                current_batch += 1
            
            # Save resume state
            save_resume_state(i)
            
            # Add a longer delay between batches
            if len(batch_data) == 0:
                print("😴 Taking a short break between batches...")
                time.sleep(5)  # 5 second break between batches
            else:
                time.sleep(1.5)  # Regular delay between games
                
        except Exception as e:
            print(f"⚠️ Failed to scrape Game ID: {game_id}")
            print(f"Error: {str(e)}")
            failed_games.append({'Game_ID': game_id, 'Error': str(e)})
            continue

    # Save any remaining games in the last batch
    if batch_data:
        batch_file = save_batch_data(batch_data, current_batch)
        print(f"\n✅ Saved final batch {current_batch} to {batch_file}")

except KeyboardInterrupt:
    print("\n\n⚠️ Script interrupted by user!")
    print("Don't worry - progress has been saved and you can resume later.")
    # Save the current batch before exiting
    if batch_data:
        batch_file = save_batch_data(batch_data, current_batch)
        print(f"✅ Saved current batch {current_batch} to {batch_file}")

finally:
    # Save failed games
    if failed_games:
        failed_file = f"{SAVE_DIRECTORY}/failed_games.csv"
        pd.DataFrame(failed_games).to_csv(failed_file, index=False)
        print(f"\n❌ Saved {len(failed_games)} failed games to {failed_file}")
    
    # Merge all batches into final dataset
    print("\n🔄 Merging all batches into final dataset...")
    final_df = merge_batch_files()
    
    print("\n📊 Final Statistics:")
    print(f"Total games processed: {len(final_df) if final_df is not None else 0}")
    print(f"Failed games: {len(failed_games)}")
    print(f"Success rate: {(len(final_df) / total_games * 100 if final_df is not None else 0):.2f}%")
    
python merge_batches.py