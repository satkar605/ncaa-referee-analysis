# From Website to Dashboard

### Problem Statement  
March Madness is intense but is it always fair? I wondered: Does referee travel distance influence foul calls in NCAA Division I Men’s Basketball? But before any analysis could begin, I had to build the data foundation from scratch.

---

### Starting at Zero: Finding Game Data  
Unlike modern sports data APIs, stats.ncaa.org is old-school. It’s a static, HTML-based website with no formal API. That means there’s no structured endpoint to ping for team stats, box scores, or referee assignments. Every page load is slow, and navigating the site is like flipping through a digital blinder from the early 2000s.  

But buried in that binder is gold: every game has a unique identifier – a game ID – hidden in the URLs of schedule and results page. Once I discovered this, the scraping strategy changed. I wasn’t just crawling pages anymore; I was collecting keys.  

<img width="428" alt="Screenshot 2025-05-13 at 11 07 15 AM" src="https://github.com/user-attachments/assets/d434f74c-5415-4b3e-a200-69ca2e798e5e" />


To avoid hammering the site and overwhelming the server (and our computers), I implemented data filtering. By targeting specific days of the 2024-2025 regular season, I could scrape only the games that occurred on a given date. This made the process more efficient, scalable, and respectful of the website’s fragile load capacity.  

From there, I built a script to automate those dates, extract game IDs, and queue them up for deeper scraping. Every game ID led us to a new vault of structured data: team names, player stats, and most importantly, the list of assigned referees.

![May 13, 2025, 11_19_16 AM](https://github.com/user-attachments/assets/af1b577b-d1f2-4e0d-90f5-2cf9d88a2123)


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

This allowed me to approxoimate distance between venues across consecutive games officiated by each referee; essentially reconstructing their travel itinerary.



**Highlight:**  
- The final dataset contains travel stats for 778 unique referees  
- Keith Kimble officiated 90 games and traveled a whopping 47,459 miles, averaging over 530 miles per trip and working games in 29 states

---

### R Shiny Dashboard for Exploratory Data Analysis  
To support exploratory data analysis, I developed an interactive R Shiny dashboard focused on referee travel and workload metrics during the 2023–24 NCAA Division I Men’s Basketball season. 

You can access the live dashboard here: [NCAA Referee Analysis Dashboard](https://satkar605.shinyapps.io/ncaa-dashboard/)

The objective was to create a streamlined interface to explore referee behavior without relying on static plots or spreadsheets. By integrating multiple referee-level indicators into a single environment, we were able to observe patterns, validate assumptions, and flag inconsistencies before advancing to modeling.

This dashboard played a central role in the data exploration phase. It helped identify outliers, such as officials with concentrated venue assignments or irregular travel patterns. The visual breakdown of referee profiles also informed decisions about which features to engineer for the upcoming modeling phase.

---

### Dashboard Features  

**Overview Tab**  
- Provides a high-level snapshot of referee coverage, enabling quick assessment of total workforce, travel demands, and game allocations
- Highlights venue diversity to support logistics planning and assignment equity
- Visual tools like histograms and scatter plots help identify workload imbalances and detect outliers in officiating patterns

  ![Screenshot 2025-05-13 at 11 03 44 AM](https://github.com/user-attachments/assets/7900db4b-a6cb-4d25-ae58-4f6d6d16a2e3)


**Referee Rankings Tab**  
- Supports performance and fairness reviews by ranking referees based on travel intensity, game count, and venue diversity
- Enables data-driven staffing decisions with customizable filters (e.g., by minimum games officiated)
- Exportable tables streamline reporting and communication with scheduling or operations teams 

![Screenshot 2025-05-13 at 11 03 59 AM](https://github.com/user-attachments/assets/950df0e8-1081-4cba-882e-98993a0d2a20)


**Individual Referee Tab**  
- Offers a detailed breakdown of each referee’s travel footprint and workload distribution for performance audits
- Highlights travel extremes (shortest, average, longest trips) to assess burnout risk and plan recovery windows
- Trends in game frequency and rest time enable better workload balancing across the season

  ![Screenshot 2025-05-13 at 11 04 26 AM](https://github.com/user-attachments/assets/2e33346b-6cc3-4123-9a75-e51453b03c26)


---

### Assumptions and Caveats

- **Travel Distance Approximation**  
  Travel miles were calculated using straight-line (great-circle) distances between venues, not actual travel routes.

- **No Integration with Travel APIs**  
  More precise travel data (e.g., driving time, flight duration) would require paid APIs like Google Maps, which were not used in this project.

- **Uniform Travel Assumption**  
  The model assumes all referees used similar travel modes and routes, which may not reflect real-world variation.

- **No Time-Based Fatigue Modeling**  
  Travel timing, layovers, or rest periods were not captured—only distance and frequency were analyzed.

- **Foul Behavior Not Linked to Travel**  
  Statistical analysis found no consistent relationship between travel distance and foul calls by referees.

- **Intended Use**  
  This dashboard is most effective for monitoring travel workload and supporting equitable assignment—not for evaluating referee bias or decision quality.


**Tech Stack:**
- **Frontend:** R Shiny
- **Data Processing:** R (tidyverse), Python (pandas, numpy)
- **Visualization:** Plotly, ggplot2
- **Deployment:** Shinyapps.io
- **Version Control:** Git/GitHub

---

### Behind the Code (Distance Approximation) 
Using `geopy`, I created a Python class to:  
- Geocode venue names using Nominatim, with caching to avoid repeated lookups  
- Extract referee assignments from each game  
- Calculate total miles traveled, average trip distance, and max single trip  
- Count the number of unique venues and states visited  
- Output a full dataset of referee-specific travel statistics  

