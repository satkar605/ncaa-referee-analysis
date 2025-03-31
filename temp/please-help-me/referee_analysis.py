import pandas as pd
import numpy as np
from datetime import datetime
import json

def analyze_referee_assignments():
    """Analyze basic referee statistics from the merged dataset"""
    print("📊 Loading merged dataset...")
    
    try:
        # Load the merged data
        df = pd.read_csv('ncaa_games_data.csv')
        
        # Print column names to debug
        print("\nAvailable columns:")
        print(df.columns.tolist())
        
        # Find the officials column (case insensitive)
        officials_col = None
        for col in df.columns:
            if col.lower() == 'officials':
                officials_col = col
                break
        
        if officials_col is None:
            raise KeyError("Could not find officials column in the dataset")
            
        # Convert date column to datetime
        date_col = [col for col in df.columns if 'date' in col.lower()][0]
        df['Date'] = pd.to_datetime(df[date_col])
        
        # Create referee statistics dataframe
        referee_stats = []
        
        print("\n🔍 Analyzing referee assignments...")
        
        # Split officials string into list of referees
        df['officials_list'] = df[officials_col].str.split(', ')
        
        # Get unique referees
        all_refs = set()
        for officials in df['officials_list']:
            if isinstance(officials, list):
                all_refs.update(officials)
        
        print(f"\nFound {len(all_refs)} unique referees")
        
        # Calculate statistics for each referee
        for referee in all_refs:
            # Get games for this referee
            ref_games = df[df[officials_col].str.contains(referee, na=False)]
            
            if len(ref_games) > 0:
                stats = {
                    'referee_name': referee,
                    'total_games': len(ref_games),
                    'first_game': ref_games['Date'].min(),
                    'last_game': ref_games['Date'].max()
                }
                
                # Add foul statistics if available
                if 'home_fouls' in df.columns and 'away_fouls' in df.columns:
                    stats.update({
                        'avg_home_fouls': ref_games['home_fouls'].mean(),
                        'avg_away_fouls': ref_games['away_fouls'].mean(),
                        'foul_differential': (ref_games['home_fouls'] - ref_games['away_fouls']).mean()
                    })
                
                # Add score statistics if available
                if 'home_score' in df.columns and 'away_score' in df.columns:
                    stats['home_wins'] = (ref_games['home_score'] > ref_games['away_score']).mean()
                
                referee_stats.append(stats)
        
        # Create DataFrame and save
        refs_df = pd.DataFrame(referee_stats)
        refs_df.to_csv('referee_statistics.csv', index=False)
        
        # Print summary statistics
        print("\n📊 Referee Statistics Summary:")
        print(f"Average games per referee: {refs_df['total_games'].mean():.1f}")
        print(f"Most active referee: {refs_df.loc[refs_df['total_games'].idxmax(), 'referee_name']}")
        print(f"Total games in dataset: {len(df)}")
        
        return refs_df

    except Exception as e:
        print(f"\n❌ Error analyzing referee assignments: {str(e)}")
        print("\nPlease check your data structure using check_data_structure()")
        return None

def prepare_travel_analysis(refs_df):
    """Prepare data for travel distance analysis"""
    print("\n🗺️ Preparing travel analysis data...")
    
    # Load the merged data again
    df = pd.read_csv('ncaa_games_data.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Sort games by date for each referee
    df = df.sort_values('Date')
    
    # Create a list to store referee travel sequences
    ref_sequences = []
    
    for referee in refs_df['referee_name']:
        ref_games = df[df['officials'].str.contains(referee, na=False)].copy()
        ref_games = ref_games.sort_values('Date')
        
        sequence = {
            'referee': referee,
            'game_sequence': ref_games[['Date', 'Venue']].to_dict('records'),
            'total_games': len(ref_games),
            'unique_venues': ref_games['Venue'].nunique()
        }
        ref_sequences.append(sequence)
    
    # Save the sequences for later distance calculation
    with open('referee_sequences.json', 'w') as f:
        json.dump(ref_sequences, f, default=str, indent=2)
    
    print(f"✅ Saved travel sequences for {len(ref_sequences)} referees")
    return ref_sequences

if __name__ == "__main__":
    # First analyze referee statistics
    print("Step 1: Analyzing referee statistics...")
    refs_df = analyze_referee_assignments()
    
    # Then prepare data for travel analysis
    print("\nStep 2: Preparing travel analysis...")
    ref_sequences = prepare_travel_analysis(refs_df)
    
    print("\n✅ Analysis complete!")
    print("Generated files:")
    print("1. referee_statistics.csv - Basic statistics for each referee")
    print("2. referee_sequences.json - Venue sequences for travel analysis")
    print("\nReady for distance calculations!") 