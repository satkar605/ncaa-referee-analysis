# ===========================================
# Import Required Libraries
# ===========================================
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd
import time
import json

# ===========================================
# Configuration
# ===========================================
CACHE_FILE = "venue_cache.json"
BATCH_DATA = "scraped_data/batch_0001.csv"  # First batch of games

class VenueGeocoder:
    def __init__(self):
        """Initialize geocoder with cache system"""
        self.geolocator = Nominatim(user_agent="ncaa_referee_analysis", timeout=10)
        self.cache = self.load_cache()
    
    def load_cache(self):
        """Load existing venue coordinates from cache"""
        try:
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_cache(self):
        """Save venue coordinates to cache file"""
        with open(CACHE_FILE, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def get_coordinates(self, venue):
        """Get coordinates for venue with caching"""
        if not venue:
            return None
        
        # Clean venue string
        venue = str(venue).strip()
        
        # Check cache first
        if venue in self.cache:
            print(f"📍 Cache hit: {venue}")
            return self.cache[venue]
        
        try:
            print(f"🔍 Geocoding: {venue}")
            # Format venue string (e.g., "Moby Arena (Fort Collins, CO)" -> "Moby Arena, Fort Collins, CO")
            search_venue = venue.replace(" (", ", ").replace(")", "")
            
            # Get location
            location = self.geolocator.geocode(search_venue)
            time.sleep(1.5)  # Respect rate limits
            
            if location:
                coords = {
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'address': location.address
                }
                self.cache[venue] = coords
                self.save_cache()
                print(f"✅ Found coordinates for: {venue}")
                return coords
            
            print(f"⚠️ Could not find coordinates for: {venue}")
            return None
            
        except Exception as e:
            print(f"❌ Error geocoding {venue}: {str(e)}")
            return None

def analyze_first_batch():
    """Analyze venue locations from first batch of data"""
    try:
        # Load first batch of data
        print("📊 Loading first batch data...")
        games_df = pd.read_csv(BATCH_DATA)
        print(f"Found {len(games_df)} games in batch")
        
        # Initialize geocoder
        geocoder = VenueGeocoder()
        
        # Get unique venues
        venues = games_df['Venue'].unique()
        print(f"\nFound {len(venues)} unique venues")
        
        # Process each venue
        venue_data = []
        for venue in venues:
            coords = geocoder.get_coordinates(venue)
            if coords:
                venue_data.append({
                    'venue': venue,
                    'latitude': coords['latitude'],
                    'longitude': coords['longitude'],
                    'full_address': coords['address']
                })
        
        # Create venues dataframe
        venues_df = pd.DataFrame(venue_data)
        
        # Save processed venues
        venues_df.to_csv('batch1_venues.csv', index=False)
        print(f"\n✅ Saved {len(venues_df)} venues to batch1_venues.csv")
        
        # Basic statistics
        print("\n📊 Venue Statistics:")
        print(f"Total venues processed: {len(venues_df)}")
        print(f"Venues not found: {len(venues) - len(venues_df)}")
        
        return venues_df
        
    except Exception as e:
        print(f"❌ Error processing batch: {str(e)}")
        return None

def calculate_distances(venues_df):
    """Calculate distances between all venues"""
    distances = []
    
    for i, venue1 in venues_df.iterrows():
        for j, venue2 in venues_df.iterrows():
            if i < j:  # Only calculate each pair once
                coords1 = (venue1['latitude'], venue1['longitude'])
                coords2 = (venue2['latitude'], venue2['longitude'])
                
                distance = geodesic(coords1, coords2).miles
                
                distances.append({
                    'venue1': venue1['venue'],
                    'venue2': venue2['venue'],
                    'distance_miles': round(distance, 2)
                })
    
    # Create distances dataframe
    distances_df = pd.DataFrame(distances)
    distances_df.to_csv('batch1_distances.csv', index=False)
    print(f"\n✅ Saved {len(distances_df)} venue distances to batch1_distances.csv")
    
    return distances_df

if __name__ == "__main__":
    print("🏀 NCAA Venue Geocoding Sandbox")
    print("===============================")
    
    # Process venues
    venues_df = analyze_first_batch()
    
    if venues_df is not None and not venues_df.empty:
        # Calculate distances
        print("\n📏 Calculating distances between venues...")
        distances_df = calculate_distances(venues_df)
        
        # Show sample of distances
        print("\n📊 Sample Distances:")
        print(distances_df.head()) 