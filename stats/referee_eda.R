install.packages("jsonlite")
?json
# Basic import and exploration
library(tidyverse)
library(jsonlite)

# Import the referee travel summary data
ref_travel <- read_csv("~/Desktop/workfiles/referee_travel.csv")

# Import the detailed travel data
travel_details <- fromJSON("~/Desktop/workfiles/referee_travel_details.json")

# Quick summary
summary(ref_travel)

# Initial plots
ggplot(ref_travel, aes(x = Games_Officiated, y = Total_Travel_Miles)) +
  geom_point() +
  geom_smooth(method = "lm") +
  labs(title = "Relationship Between Games Officiated and Travel Distance")

