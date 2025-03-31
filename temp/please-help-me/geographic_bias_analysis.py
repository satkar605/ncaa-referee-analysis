def analyze_regional_bias(games_df, venues_df):
    """Analyze officiating patterns based on geographic regions"""
    
    # Add region information to venues
    def get_region(lat, lon):
        if lat > 39:
            return 'North'
        elif lon < -98:
            return 'West'
        elif lon > -80:
            return 'East'
        else:
            return 'Central'
    
    venues_df['region'] = venues_df.apply(
        lambda x: get_region(x['latitude'], x['longitude']), axis=1
    )
    
    regional_stats = []
    
    for official in games_df['officials'].unique():
        official_games = games_df[games_df['officials'].str.contains(official)]
        
        for region in venues_df['region'].unique():
            region_games = official_games[
                official_games['Venue'].isin(
                    venues_df[venues_df['region'] == region]['venue']
                )
            ]
            
            if len(region_games) > 0:
                regional_stats.append({
                    'official': official,
                    'region': region,
                    'games_officiated': len(region_games),
                    'avg_home_fouls': region_games['home_fouls'].mean(),
                    'avg_away_fouls': region_games['away_fouls'].mean(),
                    'home_win_pct': (region_games['home_score'] > 
                                   region_games['away_score']).mean()
                })
    
    return pd.DataFrame(regional_stats) 