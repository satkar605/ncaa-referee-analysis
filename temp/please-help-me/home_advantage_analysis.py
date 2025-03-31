def analyze_home_advantage(games_df, venues_df):
    """Analyze how venue characteristics affect home court advantage"""
    
    venue_stats = []
    
    for venue in venues_df['venue'].unique():
        venue_games = games_df[games_df['Venue'] == venue]
        
        if len(venue_games) > 0:
            # Calculate venue-specific metrics
            venue_stats.append({
                'venue': venue,
                'total_games': len(venue_games),
                'avg_home_fouls': venue_games['home_fouls'].mean(),
                'avg_away_fouls': venue_games['away_fouls'].mean(),
                'home_win_pct': (venue_games['home_score'] > 
                               venue_games['away_score']).mean(),
                'latitude': venues_df[venues_df['venue'] == venue]['latitude'].iloc[0],
                'longitude': venues_df[venues_df['venue'] == venue]['longitude'].iloc[0]
            })
    
    return pd.DataFrame(venue_stats) 