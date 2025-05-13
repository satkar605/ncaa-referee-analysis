# From Website to Dashboard

### Problem Statement  
March Madness is intense but is it always fair? I wondered: Does referee travel distance influence foul calls in NCAA Division I Men’s Basketball? But before any analysis could begin, I had to build the data foundation from scratch.

---

### Starting at Zero: Finding Game Data  
Unlike modern sports data APIs, stats.ncaa.org is old-school. It’s a static, HTML-based website with no formal API. That means there’s no structured endpoint to ping for team stats, box scores, or referee assignments. Every page load is slow, and navigating the site is like flipping through a digital blinder from the early 2000s.  

But buried in that binder is gold: every game has a unique identifier – a game ID – hidden in the URLs of schedule and results page. Once I discovered this, the scraping strategy changed. I wasn’t just crawling pages anymore; I was collecting keys.  

To avoid hammering the site and overwhelming the server (and our computers), I implemented data filtering. By targeting specific days of the 2024-2025 regular season, I could scrape only the games that occurred on a given date. This made the process more efficient, scalable, and respectful of the website’s fragile load capacity.  

From there, I built a script to automate those dates, extract game IDs, and queue them up for deeper scraping. Every game ID led us to a new vault of structured data: team names, player stats, and most importantly, the list of assigned referees.

---

### Inside the Dataset: One Table, All the Insights  
After indexing thousands of NCAA basketball games and scraping them one by one, I consolidated everything into a single, analysis-ready table. Each row represents a unique game, and every column carries some piece of the story. Whether it’s who played, who officiated, where it happened, or what unfolded on the court.  

**A brief data summary is as follows:**  
- Rows (games): 5,922  
- Columns (features): 34  
- Referees tracked per game: 3  
- Foul stats captured: by team, by half, by type (personal, technical)  

By centralizing referee names, foul patterns, and game context into one structured table, I laid the foundation for deeper analysis without constantly joining multiple tables.

---

### Mapping the Miles: Measuring Referee Travel  
After collecting game data, the next step was to approximate how far referees traveled over the course of the 2024–25 NCAA season. To do this, I used Nominatim, a geocoding tool powered by OpenStreetMap, to convert venue names into latitude and longitude coordinates.  

This allowed me to calculate the geodesic distance between venues across consecutive games officiated by each referee; essentially reconstructing their travel itinerary.

---

### Behind the Code  
Using `geopy`, I created a Python class to:  
- Geocode venue names using Nominatim, with caching to avoid repeated lookups  
- Extract referee assignments from each game  
- Calculate total miles traveled, average trip distance, and max single trip  
- Count the number of unique venues and states visited  
- Output a full dataset of referee-specific travel statistics  

**Highlight:**  
- The final dataset contains travel stats for 778 unique referees  
- Keith Kimble officiated 90 games and traveled a whopping 47,459 miles, averaging over 530 miles per trip and working games in 29 states

---

### R Shiny Dashboard for Exploratory Data Analysis  
To support exploratory data analysis, I developed an interactive R Shiny dashboard focused on referee travel and workload metrics during the 2023–24 NCAA Division I Men’s Basketball season.  

The objective was to create a streamlined interface to explore referee behavior without relying on static plots or spreadsheets. By integrating multiple referee-level indicators into a single environment, we were able to observe patterns, validate assumptions, and flag inconsistencies before advancing to modeling.

**Tools and Libraries Used:**  
- `shiny`, `shinydashboard`: layout and reactive functionality  
- `plotly`: dynamic charts with hover capabilities  
- `DT`: searchable, exportable tables for referee data  
- `bslib` and custom CSS: styling and layout enhancements  

This dashboard played a central role in the data exploration phase. It helped identify outliers, such as officials with concentrated venue assignments or irregular travel patterns. The visual breakdown of referee profiles also informed decisions about which features to engineer for the upcoming modeling phase.

---

### Dashboard Features  

**Overview Tab**  
- Summarizes key metrics: total referees analyzed, average travel distance, total games  
- Computes unique venue counts  
- Includes a travel distribution histogram and a scatter plot comparing games officiated and travel miles  

**Rankings Tab**  
- Enables sorting by travel miles, number of games, or venue diversity  
- Includes a filter for minimum games officiated  
- Displays rankings in an interactive table with export options  

**Individual Referee Tab**  
- Allows selection of any referee from the dataset  
- Displays detailed profile including trip statistics, most visited venue, and diversity ratio  
- Visualizes estimated shortest, average, and longest travel segments  
- Includes workload trends: average distance per game, games per week, and recovery time

---

### Future Research Direction  
This project establishes the groundwork for analyzing how referee travel may influence officiating behavior. The next step is to build models that examine the relationship between travel distance and decisions such as foul calls or technical fouls.  

We also plan to compare regular season data with the later stages of the season. These include conference tournaments and the NCAA tournament. Referee selection in these stages is more controlled and less regionally influenced. This comparison may reveal whether the selection process affects consistency in officiating.  

The goal is to use these insights to better understand the operational factors behind officiating patterns. This could help inform future decisions about referee assignments and scheduling in high-stakes games.