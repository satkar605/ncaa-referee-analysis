import pandas as pd
from geopy.distance import geodesic
import numpy as np

def analyze_referee_travel_impact(games_df, venues_df, officials_df):
    """Analyze how travel distances affect officiating patterns"""
    
    ref_metrics = []
    
    for official in officials_df['official_name'].unique():
        # Get games officiated by this referee in chronological order
        official_games = games_df[games_df['officials'].str.contains(official)].sort_values('date')
        
        if len(official_games) >= 2:  # Need at least 2 games to calculate travel
            for i in range(1, len(official_games)):
                prev_game = official_games.iloc[i-1]
                curr_game = official_games.iloc[i]
                
                # Get venues
                prev_venue = venues_df[venues_df['venue'] == prev_game['Venue']].iloc[0]
                curr_venue = venues_df[venues_df['venue'] == curr_game['Venue']].iloc[0]
                
                # Calculate travel distance
                distance = geodesic(
                    (prev_venue['latitude'], prev_venue['longitude']),
                    (curr_venue['latitude'], curr_venue['longitude'])
                ).miles
                
                # Calculate foul differential (home - away)
                foul_diff = curr_game['home_fouls'] - curr_game['away_fouls']
                
                ref_metrics.append({
                    'official': official,
                    'game_date': curr_game['date'],
                    'travel_distance': distance,
                    'foul_differential': foul_diff,
                    'days_between_games': (pd.to_datetime(curr_game['date']) - 
                                         pd.to_datetime(prev_game['date'])).days
                })
    
    return pd.DataFrame(ref_metrics)

def calculate_travel_bias_metrics(ref_metrics_df):
    """Calculate bias metrics based on travel patterns"""
    
    # Group by official and calculate metrics
    official_stats = ref_metrics_df.groupby('official').agg({
        'travel_distance': ['mean', 'max', 'sum'],
        'foul_differential': ['mean', 'std'],
        'days_between_games': 'mean'
    }).round(2)
    
    # Calculate correlation between travel and foul differential
    travel_impact = ref_metrics_df.groupby('official').apply(
        lambda x: np.corrcoef(x['travel_distance'], x['foul_differential'])[0,1]
    ).round(3)
    
    return official_stats, travel_impact 