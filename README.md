# NCAA Referee Bias Analysis Project

## Overview

This project aims to analyze potential biases in NCAA refereeing by examining travel distances and game statistics. The analysis is conducted using a combination of Python and R, with data sourced from various NCAA games.

### Key Components

- **Dataset**: This directory contains the data files used for the analysis. It includes detailed data scraped specifically for the NCAA referee bias analysis project.

- **Referee Analysis**: This folder holds the Python scripts responsible for calculating travel distances and cleaning the data in an organized manner. These scripts are crucial for preparing the data for further analysis.

- **Scrapers**: This section includes the scraping codes used to:
  1. Extract game IDs along with their respective dates.
  2. Gather specific data related to box scores, team statistics (particularly foul-related), and the names of officials.

- **Stats**: This directory contains the R Shiny app code, which is used to visualize and interact with the analysis results.

  <img width="1509" alt="Screenshot 2025-04-01 at 3 53 36 PM" src="https://github.com/user-attachments/assets/020d33e9-0f91-4b8f-b91a-5252a148212a" />



- **Temp**: A sandbox directory for codes generated during the development process. This is primarily used for testing and experimentation.

  

## Instructions for Technical Users

1. **Navigating the Repository**:
   - Start by exploring the `dataset` directory to understand the raw data structure.
   - Use the `referee_analysis` scripts to preprocess and clean the data.
   - The `scrapers` directory contains scripts to update or expand the dataset with new game data.
   - For visualization, refer to the `stats` directory to run the R Shiny app.

2. **Running the Analysis**:
   - Ensure all dependencies are installed.
   - Execute the Python scripts in `referee_analysis` to prepare the data.
   - Use the R Shiny app in `stats` to visualize the results.

3. **Development and Testing**:
   - Utilize the `temp` directory for any experimental code changes or testing new features.

## Getting Started

For non-technical stakeholders, this project provides insights into potential biases in NCAA refereeing, which can be crucial for decision-making and policy formulation. The visualizations in the R Shiny app offer an intuitive way to explore the data and findings.

---

Feel free to reach out for any questions or further clarifications regarding this project.
