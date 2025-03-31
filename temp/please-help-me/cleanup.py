# ===========================================
# Import Required Libraries
# ===========================================
import os
import shutil
from datetime import datetime

def cleanup_scraping_progress():
    """
    Remove all previous scraping progress and prepare for a fresh start.
    Creates a backup of removed files just in case.
    """
    print("🧹 Starting cleanup process...")
    
    # Files and directories to clean
    targets = [
        "scraped_data",          # Main data directory
        "resume_state.txt",      # Resume state file
        "officials_data.csv",    # Previous officials data
        "ncaa_games_data.csv",   # Previous combined data
        "failed_games.csv"       # Previous failure logs
    ]
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_{timestamp}"
    
    try:
        # Create backup directory
        os.makedirs(backup_dir)
        print(f"📁 Created backup directory: {backup_dir}")
        
        # Process each target
        for target in targets:
            if os.path.exists(target):
                try:
                    # If it's a directory
                    if os.path.isdir(target):
                        # Copy to backup then remove
                        shutil.copytree(target, os.path.join(backup_dir, target))
                        shutil.rmtree(target)
                        print(f"✅ Backed up and removed directory: {target}")
                    # If it's a file
                    else:
                        # Copy to backup then remove
                        shutil.copy2(target, backup_dir)
                        os.remove(target)
                        print(f"✅ Backed up and removed file: {target}")
                except Exception as e:
                    print(f"⚠️ Error processing {target}: {str(e)}")
            else:
                print(f"ℹ️ {target} not found - skipping")
    
        print("\n=== 🎉 Cleanup Complete ===")
        print(f"Backup saved to: {backup_dir}")
        print("Ready for fresh scraping!")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")
        print("Cleanup failed - please check manually")

if __name__ == "__main__":
    # Ask for confirmation before proceeding
    response = input("⚠️ This will remove all previous scraping progress. Continue? (yes/no): ")
    if response.lower() == 'yes':
        cleanup_scraping_progress()
    else:
        print("Cleanup cancelled") 