# please-help-me
I need help.

🏀 NCAA Referee Bias – Scraping Project
Hi! I'm Satkar, and this project is part of a broader goal to understand how referee travel distance might influence foul-calling behavior in NCAA Division I Men’s Basketball.

I’ve been curious about whether refs who travel farther make different officiating decisions — possibly due to fatigue, unfamiliarity with the region, or just the grind of being on the road. Since this isn’t something you can just Google and find data for, I decided to scrape everything from scratch.

💻 What I’ve Built So Far
This repo has two main Python scripts that I wrote while learning and iterating through a lot of trial and error (with ChatGPT helping me debug more times than I can count 😅):

1. GAMEID_scraper.py
This script collects all the game IDs and dates from the 2023–24 regular season. It loops through each date, visits the NCAA stats website, and pulls out the game IDs being played that day.

2. Data_Scraper.py
Once I have the game IDs, this script scrapes detailed game data — including box scores, team stats, venue info, and referees.
Right now, it’s set up to scrape the first 100 games (in batches of 10) just to test and validate things before I go bigger.

✅ Output File
regular_season_game_ids.csv: A simple CSV file that connects game IDs to their calendar dates — kind of the foundation for all other scraping and analysis.

🚧 Why This Matters (To Me)
I’m doing this as part of a bigger research project. I want to explore how travel distance might affect referee decisions — specifically fouls. It's not just a data project; it's about bringing awareness to how subtle factors might shape fairness in sports.

It’s still early, and there’s a long way to go — like figuring out where refs live (so I can estimate how far they traveled) and running real statistical tests. But this scraping work is the backbone of the whole analysis.

🙏 Acknowledgements
This project would’ve been impossible without Python, pandas, and lots of help from ChatGPT to untangle messy HTML and bugs I ran into at 2AM. 😅

If you’re curious, working on something similar, or have feedback — feel free to reach out!
