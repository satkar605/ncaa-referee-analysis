import pandas as pd
import numpy as np
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import time
import os
import json
from collections import Counter

class RefereeTravel:
    def __init__(self):
        """Initialize the referee travel analyzer"""
        # Define file paths and directories
        self.data_path = 'ncaa_games_data.csv'  # Main data file with game information
        self.venue_cache_path = os.path.expanduser('~/Desktop/workfiles/venue_cache.json')  # Cache for venue coordinates
        self.output_dir = os.path.expanduser('~/Desktop/workfiles')  # Output directory
        os.makedirs(self.output_dir, exist_ok=True)  # Create output directory if it doesn't exist
        
        # Initialize the geocoder for converting venue names to coordinates
        self.geolocator = Nominatim(user_agent="ncaa_referee_analysis")
        self.venue_cache = self.load_venue_cache()  # Load existing venue coordinate cache
    
    def load_venue_cache(self):
        """Load previously geocoded venue coordinates from cache file"""
        try:
            with open(self.venue_cache_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # If file doesn't exist, start with empty cache
            return {}
    
    def save_venue_cache(self):
        """Save venue coordinates to cache file to avoid redundant API calls"""
        with open(self.venue_cache_path, 'w') as f:
            json.dump(self.venue_cache, f, indent=2)
    
    def get_venue_coordinates(self, venue):
        """Get latitude/longitude coordinates for a venue name"""
        # Handle empty or null values
        if not venue or pd.isna(venue):
            return None
        
        venue = str(venue).strip()
        
        # Check if venue is already in cache to avoid unnecessary API calls
        if venue in self.venue_cache:
            return self.venue_cache[venue]
        
        try:
            # Geocode the venue using Nominatim
            print(f"🔍 Geocoding venue: {venue}")
            location = self.geolocator.geocode(venue)
            time.sleep(1)  # Pause to respect API rate limits
            
            if location:
                # Store as (latitude, longitude) tuple
                coords = (location.latitude, location.longitude)
                self.venue_cache[venue] = coords
                self.save_venue_cache()
                return coords
            
            print(f"⚠️ Could not geocode: {venue}")
            return None
            
        except Exception as e:
            print(f"❌ Error geocoding {venue}: {str(e)}")
            return None
    
    def get_state_from_venue(self, venue):
        """Extract state from venue name if possible"""
        if not venue or pd.isna(venue):
            return "Unknown"
        
        # Look for state code in parentheses at the end
        venue = str(venue).strip()
        if '(' in venue and ')' in venue:
            possible_state = venue.split('(')[-1].split(')')[0].strip()
            # If it looks like a state code (2 letters)
            if len(possible_state) == 2 and possible_state.isalpha():
                return possible_state
            
            # If it's a "City, ST" format
            if ',' in possible_state and len(possible_state.split(',')[-1].strip()) == 2:
                return possible_state.split(',')[-1].strip()
        
        return "Unknown"
    
    def calculate_distance(self, coord1, coord2):
        """Calculate distance between two coordinates in miles"""
        if coord1 is None or coord2 is None:
            return None
        # Use geodesic distance (as the crow flies)
        return geodesic(coord1, coord2).miles
    
    def analyze_travel(self):
        """Main function to analyze referee travel patterns"""
        print("📊 Loading NCAA games data...")
        df = pd.read_csv(self.data_path)
        
        # Step 1: Find and convert date column to datetime format
        date_col = [col for col in df.columns if 'date' in col.lower()][0]
        df['Date'] = pd.to_datetime(df[date_col])
        df = df.sort_values('Date')  # Sort games chronologically
        
        # Step 2: Find columns containing referee information
        official_cols = [col for col in df.columns if 'official' in col.lower() and '_' in col]
        # Fallback if "official" columns not found
        if not official_cols:
            official_cols = [col for col in df.columns if 'ref' in col.lower() and '_' in col]
        
        if not official_cols:
            print("❌ Could not find official columns in the dataset")
            return None
        
        print(f"Found official columns: {official_cols}")
        
        # Step 3: Find venue column
        venue_col = [col for col in df.columns if 'venue' in col.lower()][0]
        
        # Step 4: Geocode all unique venues and extract states
        print("\n🏟️ Geocoding venues and extracting states...")
        venues = df[venue_col].unique()
        venue_coords = {}
        venue_states = {}
        
        for venue in venues:
            if pd.isna(venue):
                continue
            coords = self.get_venue_coordinates(venue)
            if coords:
                venue_coords[venue] = coords
            
            # Extract state from venue
            state = self.get_state_from_venue(venue)
            venue_states[venue] = state
        
        print(f"✅ Geocoded {len(venue_coords)} venues out of {len(venues)}")
        
        # Step 5: Prepare to calculate travel for each referee
        print("\n🧮 Calculating referee travel distances...")
        
        # Create comprehensive list of all referees mentioned in the dataset
        all_refs = []
        for col in official_cols:
            refs = df[col].dropna().unique()
            all_refs.extend(refs)
        
        # Remove duplicates
        unique_refs = set(all_refs)
        print(f"Found {len(unique_refs)} unique referees")
        
        # Calculate travel distances for each referee
        referee_travel = []
        
        for referee in unique_refs:
            # Find all games officiated by this referee
            ref_games = df[df[official_cols].eq(referee).any(axis=1)].copy()
            
            # Skip referees who only officiated one game (no travel to calculate)
            if len(ref_games) <= 1:
                continue
            
            # Sort the referee's games by date to get chronological travel path
            ref_games = ref_games.sort_values('Date')
            
            # Calculate distances between consecutive game venues
            total_distance = 0
            travel_legs = []
            
            # Track unique venues and states
            unique_venues = set()
            venue_frequencies = Counter()
            states_visited = set()
            
            for i in range(len(ref_games)):
                # Add venue to unique venues list
                current_venue = ref_games.iloc[i][venue_col]
                if not pd.isna(current_venue):
                    unique_venues.add(current_venue)
                    venue_frequencies[current_venue] += 1
                    
                    # Add state to visited states
                    state = venue_states.get(current_venue, "Unknown")
                    if state != "Unknown":
                        states_visited.add(state)
                
                # Calculate distance for legs after the first game
                if i > 0:
                    prev_venue = ref_games.iloc[i-1][venue_col]
                    curr_venue = current_venue
                    
                    prev_coords = venue_coords.get(prev_venue)
                    curr_coords = venue_coords.get(curr_venue)
                    
                    if prev_coords and curr_coords:
                        distance = self.calculate_distance(prev_coords, curr_coords)
                        if distance:
                            total_distance += distance
                            travel_legs.append({
                                'date': ref_games.iloc[i]['Date'],
                                'from_venue': prev_venue,
                                'to_venue': curr_venue,
                                'distance': round(distance, 2)
                            })
            
            # Find most frequently visited venue
            most_common_venue = venue_frequencies.most_common(1)[0][0] if venue_frequencies else "None"
            most_common_count = venue_frequencies.most_common(1)[0][1] if venue_frequencies else 0
            
            # Compile statistics for this referee
            referee_travel.append({
                'referee': referee,
                'games_officiated': len(ref_games),
                'total_travel_miles': round(total_distance, 2),
                'avg_miles_per_trip': round(total_distance / (len(ref_games) - 1), 2) if len(ref_games) > 1 else 0,
                'unique_venues': len(unique_venues),
                'unique_states': len(states_visited),
                'states_visited': list(states_visited),
                'most_visited_venue': most_common_venue,
                'most_visited_count': most_common_count,
                'venue_diversity': len(unique_venues) / len(ref_games) if len(ref_games) > 0 else 0,
                'travel_legs': travel_legs
            })
        
        # Sort referees by total travel distance (highest first)
        referee_travel.sort(key=lambda x: x['total_travel_miles'], reverse=True)
        
        # Step 6: Create summary DataFrame for easy analysis
        travel_df = pd.DataFrame([
            {
                'Referee': r['referee'],
                'Games_Officiated': r['games_officiated'],
                'Total_Travel_Miles': r['total_travel_miles'],
                'Avg_Miles_Per_Trip': r['avg_miles_per_trip'],
                'Unique_Venues': r['unique_venues'],
                'Unique_States': r['unique_states'],
                'Most_Visited_Venue': r['most_visited_venue'],
                'Times_At_Most_Visited': r['most_visited_count'],
                'Venue_Diversity_Ratio': round(r['venue_diversity'], 2),
                'Max_Single_Trip': max([leg['distance'] for leg in r['travel_legs']]) if r['travel_legs'] else 0
            }
            for r in referee_travel
        ])
        
        # Step 7: Save results to files
        output_path = os.path.join(self.output_dir, 'referee_travel.csv')
        travel_df.to_csv(output_path, index=False)
        
        # Save detailed travel information for deeper analysis
        details_path = os.path.join(self.output_dir, 'referee_travel_details.json')
        with open(details_path, 'w') as f:
            json.dump(referee_travel, f, indent=2, default=str)
        
        # Step 8: Display summary statistics
        print("\n📊 Referee Travel Summary:")
        print(f"Total referees analyzed: {len(travel_df)}")
        print(f"Average travel per referee: {travel_df['Total_Travel_Miles'].mean():.2f} miles")
        print(f"Average unique venues per referee: {travel_df['Unique_Venues'].mean():.2f}")
        print(f"Average states visited per referee: {travel_df['Unique_States'].mean():.2f}")
        print(f"Most traveled referee: {travel_df.iloc[0]['Referee']} ({travel_df.iloc[0]['Total_Travel_Miles']:.2f} miles)")
        print(f"Referee with most games: {travel_df.loc[travel_df['Games_Officiated'].idxmax(), 'Referee']} ({travel_df['Games_Officiated'].max()} games)")
        
        print("\nTop 10 Most Traveled Referees:")
        print(travel_df[['Referee', 'Games_Officiated', 'Total_Travel_Miles', 'Unique_Venues', 'Unique_States']].head(10))
        
        # Step 9: Find referees with most geographic diversity
        diverse_refs = travel_df.sort_values('Venue_Diversity_Ratio', ascending=False).head(10)
        print("\nTop 10 Referees with Most Venue Diversity:")
        print(diverse_refs[['Referee', 'Games_Officiated', 'Unique_Venues', 'Venue_Diversity_Ratio']])
        
        print(f"\n✅ Results saved to '{output_path}' and '{details_path}'")
        
        return travel_df

if __name__ == "__main__":
    analyzer = RefereeTravel()
    travel_df = analyzer.analyze_travel() 