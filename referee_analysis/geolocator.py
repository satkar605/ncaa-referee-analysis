#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 30 23:45:24 2025

@author: satkarkarki
"""

import pandas as pd
import numpy as np
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import time
import os
import json

class RefereeTravel:
    def __init__(self):
        """Initialize the referee travel analyzer"""
        self.data_path = 'ncaa_games_data.csv'
        self.venue_cache_path = os.path.expanduser('~/Desktop/workfiles/venue_cache.json')
        self.output_dir = os.path.expanduser('~/Desktop/workfiles')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize the geocoder
        self.geolocator = Nominatim(user_agent="ncaa_referee_analysis")
        self.venue_cache = self.load_venue_cache()
    
    def load_venue_cache(self):
        """Load venue coordinates from cache file"""
        try:
            with open(self.venue_cache_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_venue_cache(self):
        """Save venue coordinates to cache file"""
        with open(self.venue_cache_path, 'w') as f:
            json.dump(self.venue_cache, f, indent=2)
    
    def get_venue_coordinates(self, venue):
        """Get coordinates for a venue with caching"""
        if not venue or pd.isna(venue):
            return None
        
        venue = str(venue).strip()
        
        # Check cache first
        if venue in self.venue_cache:
            return self.venue_cache[venue]
        
        try:
            print(f"🔍 Geocoding venue: {venue}")
            location = self.geolocator.geocode(venue)
            time.sleep(1)  # Respect API limits
            
            if location:
                coords = (location.latitude, location.longitude)
                self.venue_cache[venue] = coords
                self.save_venue_cache()
                return coords
            
            print(f"⚠️ Could not geocode: {venue}")
            return None
            
        except Exception as e:
            print(f"❌ Error geocoding {venue}: {str(e)}")
            return None
    
    def calculate_distance(self, coord1, coord2):
        """Calculate distance between two coordinates in miles"""
        if coord1 is None or coord2 is None:
            return None
        return geodesic(coord1, coord2).miles
    
    def analyze_travel(self):
        """Analyze travel distances for referees"""
        print("📊 Loading NCAA games data...")
        df = pd.read_csv(self.data_path)
        
        # Step 1: Convert date column and sort by date
        date_col = [col for col in df.columns if 'date' in col.lower()][0]
        df['Date'] = pd.to_datetime(df[date_col])
        df = df.sort_values('Date')
        
        # Step 2: Find official columns
        official_cols = [col for col in df.columns if 'official' in col.lower() and '_' in col]
        if not official_cols:
            official_cols = [col for col in df.columns if 'ref' in col.lower() and '_' in col]
        
        if not official_cols:
            print("❌ Could not find official columns in the dataset")
            return None
        
        print(f"Found official columns: {official_cols}")
        
        # Step 3: Get venue column
        venue_col = [col for col in df.columns if 'venue' in col.lower()][0]
        
        # Step 4: Start geocoding venues
        print("\n🏟️ Geocoding venues...")
        venues = df[venue_col].unique()
        venue_coords = {}
        
        for venue in venues:
            if pd.isna(venue):
                continue
            coords = self.get_venue_coordinates(venue)
            if coords:
                venue_coords[venue] = coords
        
        print(f"✅ Geocoded {len(venue_coords)} venues out of {len(venues)}")
        
        # Step 5: Calculate travel for each referee
        print("\n🧮 Calculating referee travel distances...")
        
        # Create a list of all referees
        all_refs = []
        for col in official_cols:
            refs = df[col].dropna().unique()
            all_refs.extend(refs)
        
        # Get unique referees
        unique_refs = set(all_refs)
        print(f"Found {len(unique_refs)} unique referees")
        
        # Calculate travel for each referee
        referee_travel = []
        
        for referee in unique_refs:
            # Get games for this referee
            ref_games = df[df[official_cols].eq(referee).any(axis=1)].copy()
            
            if len(ref_games) <= 1:
                continue  # Skip referees with only one game
            
            # Sort by date
            ref_games = ref_games.sort_values('Date')
            
            # Calculate travel distances
            total_distance = 0
            travel_legs = []
            
            for i in range(1, len(ref_games)):
                prev_venue = ref_games.iloc[i-1][venue_col]
                curr_venue = ref_games.iloc[i][venue_col]
                
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
            
            # Add referee travel stats
            referee_travel.append({
                'referee': referee,
                'games_officiated': len(ref_games),
                'total_travel_miles': round(total_distance, 2),
                'avg_miles_per_trip': round(total_distance / (len(ref_games) - 1), 2) if len(ref_games) > 1 else 0,
                'travel_legs': travel_legs
            })
        
        # Sort by total travel distance
        referee_travel.sort(key=lambda x: x['total_travel_miles'], reverse=True)
        
        # Step 6: Create summary DataFrame
        travel_df = pd.DataFrame([
            {
                'Referee': r['referee'],
                'Games_Officiated': r['games_officiated'],
                'Total_Travel_Miles': r['total_travel_miles'],
                'Avg_Miles_Per_Trip': r['avg_miles_per_trip'],
                'Max_Single_Trip': max([leg['distance'] for leg in r['travel_legs']]) if r['travel_legs'] else 0
            }
            for r in referee_travel
        ])
        
        # Step 7: Save results
        output_path = os.path.join(self.output_dir, 'referee_travel.csv')
        travel_df.to_csv(output_path, index=False)
        
        # Also save the detailed travel legs for further analysis
        details_path = os.path.join(self.output_dir, 'referee_travel_details.json')
        with open(details_path, 'w') as f:
            json.dump(referee_travel, f, indent=2, default=str)
        
        # Step 8: Display summary
        print("\n📊 Referee Travel Summary:")
        print(f"Total referees analyzed: {len(travel_df)}")
        print(f"Average travel per referee: {travel_df['Total_Travel_Miles'].mean():.2f} miles")
        print(f"Most traveled referee: {travel_df.iloc[0]['Referee']} ({travel_df.iloc[0]['Total_Travel_Miles']:.2f} miles)")
        print(f"Referee with most games: {travel_df.loc[travel_df['Games_Officiated'].idxmax(), 'Referee']} ({travel_df['Games_Officiated'].max()} games)")
        
        print("\nTop 10 Most Traveled Referees:")
        print(travel_df.head(10))
        
        print(f"\n✅ Results saved to '{output_path}' and '{details_path}'")
        
        return travel_df

if __name__ == "__main__":
    analyzer = RefereeTravel()
    travel_df = analyzer.analyze_travel() 