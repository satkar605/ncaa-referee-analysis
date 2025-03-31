import pandas as pd
import glob
import os
from datetime import datetime

def merge_batches():
    """Merge all batch files into single dataset"""
    print("🔄 Starting merge process...")
    
    # Get all batch files
    batch_files = sorted(glob.glob('scraped_data/batch_*.csv'))
    
    if not batch_files:
        print("❌ No batch files found!")
        return
    
    print(f"📂 Found {len(batch_files)} batch files")
    
    # Create backup directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'data_backup_{timestamp}'
    os.makedirs(backup_dir, exist_ok=True)
    
    # Merge all batches
    all_data = []
    total_rows = 0
    
    print("\n📊 Processing batches:")
    for file in batch_files:
        batch_num = file.split('batch_')[1].split('.')[0]
        try:
            df = pd.read_csv(file)
            all_data.append(df)
            total_rows += len(df)
            print(f"✓ Batch {batch_num}: {len(df)} rows")
        except Exception as e:
            print(f"❌ Error in batch {batch_num}: {str(e)}")
    
    # Combine all data
    print("\n🔄 Merging all batches...")
    merged_df = pd.concat(all_data, ignore_index=True)
    
    # Save merged data
    output_file = 'ncaa_games_data.csv'
    merged_df.to_csv(output_file, index=False)
    
    # Print summary
    print(f"\n✅ Merge complete!")
    print(f"📊 Summary:")
    print(f"- Total games: {len(merged_df):,}")
    print(f"- Unique venues: {merged_df['Venue'].nunique():,}")
    print(f"- Date range: {merged_df['Date'].min()} to {merged_df['Date'].max()}")
    print(f"\n💾 Merged data saved to: {output_file}")
    
    # Verify data integrity
    if total_rows == len(merged_df):
        print("✅ Data integrity check passed: All rows preserved")
    else:
        print("⚠️ Warning: Number of rows in merged file doesn't match source files")
        print(f"Expected: {total_rows}, Got: {len(merged_df)}")

if __name__ == "__main__":
    merge_batches() 