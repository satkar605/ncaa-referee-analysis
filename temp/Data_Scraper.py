# ===========================================
# 📦 Import Required Libraries
# ===========================================
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import numpy as np

# ===========================================
# 📂 Load Game Metadata CSV
# ===========================================
file_path = "regular_season_game_ids.csv"
game_data = pd.read_csv(file_path)

# For testing, only use first 10 games
#game_data = game_data.head(10)

# ===========================================
# 🗃️ Initialize Empty Lists to Store Results
# ===========================================
all_games_data = []  # Will store all game data
failed_games = []    # Will store failed game IDs

# ===========================================
# 🔄 Process Games in Batches
# ===========================================
batch_size = 5  # Process 5 games at a time
total_games = len(game_data)

def safe_convert_to_numeric(value):
    """Safely convert a value to numeric, returning None if conversion fails"""
    try:
        if pd.isna(value):
            return None
        return pd.to_numeric(str(value).replace(',', ''))
    except:
        return None

for i in range(0, total_games, batch_size):
    batch = game_data.iloc[i:i+batch_size]
    
    for _, row in batch.iterrows():
        game_id = row['Game ID']
        game_date = row['Date']
        
        try:
            print(f"🔄 Scraping Game ID: {game_id} ({i+1}/{total_games})")
            
            # -------- Box Score --------
            url_box = f'https://stats.ncaa.org/contests/{game_id}/box_score'
            box_score = pd.read_html(url_box)
            
            # -------- Team Stats --------
            url_team = f'https://stats.ncaa.org/contests/{game_id}/team_stats'
            team_stats = pd.read_html(url_team)
            time.sleep(1.5)  # Polite delay between requests
            
            # -------- Officials --------
            url_official = f'https://stats.ncaa.org/contests/{game_id}/officials'
            officials = pd.read_html(url_official)
            time.sleep(1.5)
            
            # Extract game information from box score tables
            game_info = {
                'Game_ID': game_id,
                'Date': game_date,
                'Home_Team': box_score[1].iloc[1, 0] if len(box_score) > 1 and not box_score[1].empty else None,
                'Away_Team': box_score[1].iloc[2, 0] if len(box_score) > 1 and not box_score[1].empty else None,
                'Home_Score': safe_convert_to_numeric(box_score[1].iloc[1, 3]) if len(box_score) > 1 and not box_score[1].empty else None,
                'Away_Score': safe_convert_to_numeric(box_score[1].iloc[2, 3]) if len(box_score) > 1 and not box_score[1].empty else None,
                'Venue': box_score[1].iloc[4, 0] if len(box_score) > 1 and not box_score[1].empty else None,
                'Game_Time': box_score[1].iloc[3, 0] if len(box_score) > 1 and not box_score[1].empty else None,
            }
            
            # Extract team stats
            if len(team_stats) > 3 and not team_stats[3].empty:
                period_stats = team_stats[3]
                
                # Basic stats
                game_info.update({
                    'Home_MP': period_stats.iloc[0, 1] if not period_stats.empty else None,
                    'Away_MP': period_stats.iloc[0, 2] if not period_stats.empty else None,
                    'Home_FGM': safe_convert_to_numeric(period_stats.iloc[3, 1]) if not period_stats.empty else None,
                    'Away_FGM': safe_convert_to_numeric(period_stats.iloc[3, 2]) if not period_stats.empty else None,
                    'Home_FGA': safe_convert_to_numeric(period_stats.iloc[4, 1]) if not period_stats.empty else None,
                    'Away_FGA': safe_convert_to_numeric(period_stats.iloc[4, 2]) if not period_stats.empty else None,
                    'Home_3PM': safe_convert_to_numeric(period_stats.iloc[5, 1]) if not period_stats.empty else None,
                    'Away_3PM': safe_convert_to_numeric(period_stats.iloc[5, 2]) if not period_stats.empty else None,
                    'Home_3PA': safe_convert_to_numeric(period_stats.iloc[6, 1]) if not period_stats.empty else None,
                    'Away_3PA': safe_convert_to_numeric(period_stats.iloc[6, 2]) if not period_stats.empty else None,
                })
                
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
            
            # Extract officials
            if len(officials) > 3 and not officials[3].empty:
                game_info['Officials'] = officials[3]['Official'].tolist()
            else:
                game_info['Officials'] = []
            
            all_games_data.append(game_info)
            
            # Save progress after each game (since we're only doing 10 games)
            df = pd.DataFrame(all_games_data)
            df.to_csv('ncaa_games_data.csv', index=False)
            print(f"✅ Saved progress: {len(all_games_data)} games scraped")
            
        except Exception as e:
            print(f"⚠️ Failed to scrape Game ID: {game_id}")
            print(f"Error: {str(e)}")
            failed_games.append(game_id)
            continue

# ===========================================
# 💾 Save Final Results
# ===========================================
# Save successful scrapes
df = pd.DataFrame(all_games_data)
df.to_csv('ncaa_games_data.csv', index=False)

# Save failed games
if failed_games:
    pd.DataFrame({'Failed_Game_IDs': failed_games}).to_csv('failed_games.csv', index=False)

print(f"🎉 Scraping complete!")
print(f"✅ Successfully scraped: {len(all_games_data)} games")
print(f"❌ Failed to scrape: {len(failed_games)} games")