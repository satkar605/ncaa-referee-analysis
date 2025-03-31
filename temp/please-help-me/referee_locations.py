import pandas as pd
import json
from geopy.geocoders import Nominatim
import time

class RefereeLocationManager:
    def __init__(self):
        self.location_file = 'referee_locations.json'
        self.geolocator = Nominatim(user_agent="ncaa_referee_analysis")
        self.locations = self.load_existing_locations()
    
    def load_existing_locations(self):
        """Load existing referee locations if file exists"""
        try:
            with open(self.location_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_locations(self):
        """Save referee locations to file"""
        with open(self.location_file, 'w') as f:
            json.dump(self.locations, f, indent=2)
    
    def add_referee_location(self, referee_name, city, state):
        """Add or update a referee's location"""
        location_str = f"{city}, {state}"
        
        try:
            # Geocode the location
            location = self.geolocator.geocode(location_str)
            time.sleep(1)  # Respect rate limits
            
            if location:
                self.locations[referee_name] = {
                    'city': city,
                    'state': state,
                    'latitude': location.latitude,
                    'longitude': location.longitude,
                    'full_address': location.address
                }
                self.save_locations()
                print(f"✅ Added location for {referee_name}: {location_str}")
                return True
            else:
                print(f"❌ Could not geocode location for {referee_name}: {location_str}")
                return False
                
        except Exception as e:
            print(f"❌ Error adding location for {referee_name}: {str(e)}")
            return False

def list_referees_without_locations():
    """List all referees that need location data"""
    try:
        # Load referee statistics
        refs_df = pd.read_csv('referee_statistics.csv')
        
        # Load existing locations
        try:
            with open('referee_locations.json', 'r') as f:
                existing_locations = json.load(f)
        except FileNotFoundError:
            existing_locations = {}
        
        # Find referees without locations
        missing_locations = []
        for ref in refs_df['referee_name']:
            if ref not in existing_locations:
                missing_locations.append(ref)
        
        print(f"\n📍 Referee Location Status:")
        print(f"Total referees: {len(refs_df)}")
        print(f"Referees with locations: {len(existing_locations)}")
        print(f"Referees needing locations: {len(missing_locations)}")
        
        if missing_locations:
            print("\nReferees needing location data:")
            for ref in missing_locations:
                games = refs_df[refs_df['referee_name'] == ref]['total_games'].iloc[0]
                print(f"- {ref} ({games} games)")
        
        return missing_locations
        
    except FileNotFoundError:
        print("❌ Please run referee_analysis.py first to generate referee statistics")
        return []

def interactive_location_entry():
    """Interactive console for entering referee locations"""
    manager = RefereeLocationManager()
    missing_refs = list_referees_without_locations()
    
    if not missing_refs:
        print("✅ All referees have location data!")
        return
    
    print("\n📝 Enter referee location data")
    print("(Press Ctrl+C to exit at any time)")
    
    try:
        for referee in missing_refs:
            print(f"\nEntering location for: {referee}")
            city = input("City: ").strip()
            state = input("State (2-letter code): ").strip().upper()
            
            if city and state:
                manager.add_referee_location(referee, city, state)
            else:
                print("Skipping referee - incomplete information")
            
            print("-" * 40)
    
    except KeyboardInterrupt:
        print("\n\nSaving progress and exiting...")
        manager.save_locations()

if __name__ == "__main__":
    print("🏀 NCAA Referee Location Manager")
    print("===============================")
    interactive_location_entry() 