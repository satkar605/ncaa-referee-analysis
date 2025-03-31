#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 22 02:44:58 2025

@author: satkarkarki


DESCRIPTION:
------------
This script scrapes NCAA Men's Basketball game IDs from the official NCAA stats website 
(https://stats.ncaa.org) for the 2023–2024 regular season. It loops through each calendar 
date from the season's start to the defined end date and collects all Game IDs played on 
those days. The script then creates a mapping between game dates and game IDs, removes 
duplicates, and saves the final result into a CSV file called 'regular_season_game_ids.csv'.

Main Functional Steps:
----------------------
1. Define the scraping date range using `season_start` and `today`.
2. Loop through each date and:
   - Build the correct scoreboard URL
   - Send a request and scrape the HTML page
   - Extract all Game IDs embedded in the page
3. Clean the Game ID list (remove duplicates)
4. Associate each Game ID with its respective date
5. Save the final dataset to a CSV file for future scraping use.

This CSV becomes the base input for scraping game-specific stats like box scores, 
team stats, official assignments, and venues.

Note:
-----
- This script only collects Game IDs and dates — it does NOT scrape any box score or stat data.
- Run this script first in the pipeline to generate the full list of games to be used for downstream scraping.
"""

# ===============================
# 📦 Importing Required Packages
# ===============================

import pandas as pd           # For handling and analyzing tabular data
import datetime as dt         # For working with dates and date ranges
import requests               # For sending HTTP requests to fetch webpage content
import time                   # To pause the program (e.g., between web requests)

# ================================================
# 🔁 Define a generator to loop through date range
# ================================================

def daterange(start_date, end_date):
    """
    Yields each date between start_date and end_date (exclusive).
    Used to loop through all game dates in the season.
    """
    for n in range(int((end_date - start_date).days)):
        yield start_date + dt.timedelta(n)  # Add n days to start_date and return the result

# ====================================
# 📅 Set the scraping window (date range)
# ====================================

season_start = dt.date(2024, 11, 4)     # NCAA season start date
today = dt.date(2025, 3, 16)  # NCAA 2023/2024 Regular Season Date End
#today = dt.date.today()                 # Current date (or latest date to scrape)

# Optional for testing with a fixed date:
# today = dt.date(2024, 11, 6)

# ===================================
# 🗃️ Initialize list to store Game IDs
# ===================================

game_id = []  # Each sublist inside will contain game IDs for a specific day

# ===================================================
# 🔁 Loop through each date and scrape Game IDs
# ===================================================

for single_date in daterange(season_start, today):
    
    # Format the current date into needed parts
    date_val = single_date.strftime("%Y/%m/%d")       # Full date string (not used here)
    mm = "{:02d}".format(single_date.month)           # Month in MM format
    dd = "{:02d}".format(single_date.day)             # Day in DD format
    YYYY = single_date.year                           # Year as YYYY
    
    # Build the URL for that day's games using NCAA stats site
    URL = "https://stats.ncaa.org/season_divisions/18403/livestream_scoreboards?utf8=%E2%9C%93&season_division_id=&game_date=" + str(mm) + '%2F' + str(dd) + '%2F' + str(YYYY) + '&conference_id=0&tournament_id=&commit=Submit'
    
    # Set custom headers to simulate a browser (avoids bot detection)
    headers = {
        "User-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"
    }
    
    # Send the GET request to fetch HTML for the day's scoreboard
    page = requests.get(URL, headers=headers)
    
    games_today = []                 # Temporary list to hold today's game IDs
    cur = 0                          # Starting index for parsing HTML
    today_schedule = page.text      # Full HTML content of the page
    
    # Search for each occurrence of a game ID in the HTML
    while cur >= 0:
        today_schedule = today_schedule[cur:]                 # Slice remaining HTML
        g = today_schedule.find('<tr id="contest_')           # Look for start of a game row
        
        if g < 0:
            break  # If no more games found, break the loop
        
        # Extract the 7-digit game ID (right after 'contest_')
        games_today.append(today_schedule[g+16: g+23])
        
        # Move the cursor forward to search for the next game
        cur = g + 24

    # Add today's list of game IDs to the main game_id list
    game_id.append(games_today)
    
##### PLEASE DON'T RUN THE WHOLE CODE #########
##### FIRST WE EXTRACt THE GAME IDS ONLY #######    
    
# =======================================
# 🧹 Remove Duplicates from Each Day's IDs
# =======================================
gameId = []
for row in game_id:
    gameId.append(set(row)) # Convert each list to a set to remove duplicates

# Convert each set back to a list
game_ids = []
for row in gameId:
    game_ids.append(list(row))
    


# ===========================================================
# 📆 Associate Each Game ID with Its Corresponding Calendar Date
# ===========================================================
dates = []  # list of dates (repeated for each game)
game_ids_list = [] # flattened list of all game IDs

current_date=season_start

# Match each date to the game IDs played on that day
# For each list of game IDs (1 per day), repeat the current date for each game
# and append both the date and game IDs into flat lists
for x in game_ids:
    dates.extend([current_date] * len(x)) # len calculates the number of games per date as it loops
    game_ids_list.extend(x)
    current_date += dt.timedelta(days=1)
    

# ===========================================
# 📊 Create Final DataFrame of Game IDs & Dates
# ===========================================

# Build the Game ID DataFrame
game_data = pd.DataFrame({
    'Date' : dates,
    'Game ID': game_ids_list
    })
game_data.set_index('Date')

print(game_data)

# Save full regular season Game ID list
game_data.to_csv("regular_season_game_ids.csv", index=False)

print("✅ Saved full regular season Game IDs to 'regular_season_game_ids.csv'")